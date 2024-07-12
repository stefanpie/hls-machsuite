import argparse
import os
import re
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path

from joblib import Parallel, delayed


def get_vitis_hls_clang_pp_path() -> Path:
    vitis_hls_bin_path_str = shutil.which("vitis_hls")
    if vitis_hls_bin_path_str is None:
        raise RuntimeError("vitis_hls not found in PATH")
    vitis_hls_bin_path = Path(vitis_hls_bin_path_str)
    vitis_hls_clang_pp_path = (
        vitis_hls_bin_path.parent.parent
        / "lnx64"
        / "tools"
        / "clang-3.9"
        / "bin"
        / "clang++"
    )
    if not vitis_hls_clang_pp_path.exists():
        raise RuntimeError(
            f"Could not find vitis_hls clang++ bin at {vitis_hls_clang_pp_path}"
        )
    return vitis_hls_clang_pp_path


def get_vitis_hls_include_dir() -> Path:
    vitis_hls_bin_path_str = shutil.which("vitis_hls")
    if vitis_hls_bin_path_str is None:
        raise RuntimeError("vitis_hls not found in PATH")
    vitis_hls_bin_path = Path(vitis_hls_bin_path_str)
    vitis_hls_include_dir = vitis_hls_bin_path.parent.parent / "include"
    return vitis_hls_include_dir


class SuppressOutput:
    def __enter__(self):
        # Save the current stdout and stderr
        self.save_stdout = sys.stdout
        self.save_stderr = sys.stderr

        # Redirect stdout and stderr to devnull
        self.devnull = open(os.devnull, "w")
        sys.stdout = self.devnull
        sys.stderr = self.devnull

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore stdout and stderr
        sys.stdout = self.save_stdout
        sys.stderr = self.save_stderr

        # Close the devnull file
        self.devnull.close()

        # Handle any exception that occurred in the block
        if exc_type is not None:
            print(f"Exception occurred: {exc_type}, {exc_val}")


def gather_kernel_description() -> dict[str, str]:
    kernel_descriptions: dict[str, str] = {}
    kernel_description_md = (
        Path(__file__).parent / "kernel_descriptions" / "kernel_descriptions.md"
    )
    kernel_description_md_text = kernel_description_md.read_text()
    kernel_description_md_text = kernel_description_md_text.replace(
        "# Kernel Descriptions", ""
    )

    kernel_header_matches = list(re.finditer("## (.+)", kernel_description_md_text))
    kernel_header_match_text = [match.group(1) for match in kernel_header_matches]
    kernel_header_locs_start = [match.span()[0] for match in kernel_header_matches]
    for i in range(len(kernel_header_locs_start)):
        if i < len(kernel_header_locs_start) - 1:
            kernel_descriptions[kernel_header_match_text[i]] = (
                kernel_description_md_text[
                    kernel_header_locs_start[i] : kernel_header_locs_start[i + 1]
                ]
            )
        else:
            kernel_descriptions[kernel_header_match_text[i]] = (
                kernel_description_md_text[kernel_header_locs_start[i] :]
            )

    kernel_descriptions = {k: v.strip() for k, v in kernel_descriptions.items()}

    return kernel_descriptions


KERNEL_PATHS = [
    "aes/aes",
    "bfs/bulk",
    "bfs/queue",
    "fft/strided",
    "fft/transpose",
    "gemm/ncubed",
    "gemm/blocked",
    "kmp/kmp",
    "md/knn",
    "md/grid",
    "nw/nw",
    "sort/merge",
    "sort/radix",
    "spmv/crs",
    "spmv/ellpack",
    "stencil/stencil2d",
    "stencil/stencil3d",
    "viterbi/viterbi",
]


def main(args):
    n_jobs: int = args.jobs

    benchmark_distribution_fp: Path = args.benchmark_distribution
    output_dir: Path = args.output_directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file: Path = args.output_file

    # vitis_hls_include_dir = get_vitis_hls_include_dir()
    # vitis_clang_pp_bin_path = get_vitis_hls_clang_pp_path()

    if not benchmark_distribution_fp.exists():
        raise FileNotFoundError(
            "Benchmark distribution not found at {}".format(benchmark_distribution_fp)
        )

    # if not tarfile.is_tarfile(benchmark_distribution_fp):
    #     raise ValueError(
    #         "Benchmark distribution is not a tar.gz file: {}".format(
    #             benchmark_distribution_fp
    #         )
    #     )

    # # check for zip file
    # if not zipfile.is_zipfile(benchmark_distribution_fp):
    #     raise ValueError(
    #         "Benchmark distribution is not a zip file: {}".format(
    #             benchmark_distribution_fp
    #         )
    #     )

    is_zip = zipfile.is_zipfile(benchmark_distribution_fp)
    is_tar = tarfile.is_tarfile(benchmark_distribution_fp)

    if not is_zip and not is_tar:
        raise ValueError(
            "Benchmark distribution is not a zip or tar file: {}".format(
                benchmark_distribution_fp
            )
        )

    tmp_dir = output_dir / "tmp"
    new_benchmarks_dir = output_dir / "benchmarks"

    if is_zip:
        with zipfile.ZipFile(benchmark_distribution_fp, "r") as zip_ref:
            zip_ref.extractall(tmp_dir)
    if is_tar:
        raise NotImplementedError(
            "Tar file extraction not implemented for this benchmark distribution"
        )

    for file in tmp_dir.glob("MachSuite-master/*"):
        os.rename(file, tmp_dir / file.name)
    os.rmdir(tmp_dir / "MachSuite-master")

    source_benchmark_dirs = [tmp_dir / path for path in KERNEL_PATHS]
    print(source_benchmark_dirs)

    kernel_descriptions = gather_kernel_description()

    def process_benchmark(benchmark: Path):
        makefile_fp = benchmark / "Makefile"
        if not makefile_fp.exists():
            raise FileNotFoundError(f"Makefile not found at {makefile_fp}")
        var_kern_match = re.search(r"KERN=(\w+)", makefile_fp.read_text())
        var_alg_match = re.search(r"ALG=(\w+)", makefile_fp.read_text())
        if var_kern_match is None or var_alg_match is None:
            raise ValueError(f"Could not find KERN or ALG in Makefile at {makefile_fp}")
        var_kern = var_kern_match.group(1)
        var_alg = var_alg_match.group(1)

        kernel_full_name = f"{var_kern}_{var_alg}"
        new_benchmark_dir = new_benchmarks_dir / kernel_full_name
        if new_benchmark_dir.exists():
            shutil.rmtree(new_benchmark_dir)
        new_benchmark_dir.mkdir(parents=True, exist_ok=True)

        # copy the kern.h and kern.c files to the new benchmark directory
        kern_h_fp = benchmark / f"{var_kern}.h"
        kern_c_fp = benchmark / f"{var_kern}.c"

        if not kern_h_fp.exists():
            raise FileNotFoundError(f"kern.h not found at {kern_h_fp}")
        if not kern_c_fp.exists():
            raise FileNotFoundError(f"kern.c not found at {kern_c_fp}")

        shutil.copy(kern_h_fp, new_benchmark_dir)
        shutil.copy(kern_c_fp, new_benchmark_dir)

        new_h_fp: Path = new_benchmark_dir / f"{var_kern}.h"
        new_c_fp: Path = new_benchmark_dir / f"{var_kern}.c"

        # rename to be cpp inssted of c
        new_kern_cpp_fp = new_benchmark_dir / f"{var_kern}.cpp"
        os.rename(new_benchmark_dir / f"{var_kern}.c", new_kern_cpp_fp)
        new_c_fp = new_kern_cpp_fp

        # rename both to be full name
        os.rename(new_h_fp, new_benchmark_dir / f"{kernel_full_name}.h")
        os.rename(new_c_fp, new_benchmark_dir / f"{kernel_full_name}.cpp")
        new_h_fp = new_benchmark_dir / f"{kernel_full_name}.h"
        new_c_fp = new_benchmark_dir / f"{kernel_full_name}.cpp"

        # cleaning the header file
        h_text = new_h_fp.read_text()

        # line_idx = None
        # for i, line in enumerate(h_text.splitlines()):
        #     if len(line) >= 8 and line.startswith("/" * 8):
        #         line_idx = i
        #         break
        # if line_idx is not None:
        #     h_text = "\n".join(h_text.splitlines()[:line_idx])

        # remove any lines with more than 8 slashes in a row
        h_text = "\n".join(
            line
            for line in h_text.splitlines()
            if len(line) < 8 or not line.startswith("/" * 8)
        )
        h_text = h_text.replace("// Test harness interface code.", "")

        h_text = re.sub(r"struct bench_args_t {(.|\s)*};", "", h_text)

        # remove "#include "support.h"
        h_text = h_text.replace('#include "support.h"', "")

        # add stdint.h to top of file
        h_text = "#include <stdint.h>\n\n" + h_text

        new_h_fp.write_text(h_text)

        # cleaning the cpp file
        c_text = new_c_fp.read_text()
        c_text = c_text.replace(
            f'#include "{var_kern}.h"', f'#include "{kernel_full_name}.h"'
        )
        new_c_fp.write_text(c_text)

        # preprocess the header file with

        # copy common.h into each kernel
        # common_h_fp = tmp_dir / "common" / "support.h"
        # common_c_fp = tmp_dir / "common" / "support.c"
        # if not common_h_fp.exists() or not common_c_fp.exists():
        #     raise FileNotFoundError(f"common.h or common.c not found at {common_h_fp}")
        # shutil.copy(common_h_fp, new_benchmark_dir)
        # shutil.copy(common_c_fp, new_benchmark_dir)

        # new_common_cpp_fp = new_benchmark_dir / "support.cpp"
        # os.rename(new_benchmark_dir / "support.c", new_common_cpp_fp)

        # hls_tcl_fp = benchmark / "hls.tcl"
        # if not hls_tcl_fp.exists():
        #     raise FileNotFoundError(f"hls.tcl not found at {hls_tcl_fp}")
        # shutil.copy(hls_tcl_fp, new_benchmark_dir)

        hls_dir_search = list(benchmark.glob("*_dir"))
        if hls_dir_search is None or len(hls_dir_search) == 0:
            raise FileNotFoundError(f"{var_alg}_dir not found at {benchmark}")
        hls_dir_fp = hls_dir_search[0]
        if not hls_dir_fp.exists():
            raise FileNotFoundError(f"{var_alg}_dir not found at {hls_dir_fp}")
        shutil.copy(hls_dir_fp, new_benchmark_dir)

        new_hls_dir_fp = new_benchmark_dir / (hls_dir_fp.name + ".tcl")
        os.rename(new_benchmark_dir / hls_dir_fp.name, new_hls_dir_fp)

        # find function definitions in heder
        RE_FUNC_DEF = re.compile(r"^(?!#define).+\w+ (\w+)\((.|\s)*?\);", re.MULTILINE)
        func_def_matches = list(RE_FUNC_DEF.finditer(h_text))
        if len(func_def_matches) == 0:
            raise ValueError(f"No function definitions found in {new_h_fp}")
        top_fn_name = func_def_matches[-1].group(1).strip()
        print(top_fn_name)

        # make a top.txt
        top_txt_fp = new_benchmark_dir / "top.txt"
        top_txt_fp.write_text(top_fn_name)

        # make a kernel_description.md
        kernel_description = kernel_descriptions[kernel_full_name]
        kernel_description_fp = new_benchmark_dir / "kernel_description.md"
        kernel_description_fp.write_text(kernel_description)

    Parallel(n_jobs=n_jobs)(
        delayed(process_benchmark)(benchmark) for benchmark in source_benchmark_dirs
    )

    shutil.rmtree(tmp_dir)
    for folder in new_benchmarks_dir.glob("*"):
        shutil.move(folder, output_dir)
    shutil.rmtree(new_benchmarks_dir)

    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(output_dir, arcname=output_dir.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "benchmark_distribution",
        type=Path,
        nargs="?",
        default=Path("./MachSuite-master-6236e59.zip"),
        help="Path to the input benchmark distribution",
    )
    parser.add_argument(
        "output_directory",
        type=Path,
        nargs="?",
        default=Path("./hls-machsuite/"),
        help="Generated output directory with processed benchmarks",
    )
    parser.add_argument(
        "output_file",
        type=Path,
        nargs="?",
        default=Path("./hls-machsuite.tar.gz"),
        help="Generated output tar.gz file with processed benchmarks",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        nargs="?",
        default=1,
        help="Number of jobs to run in parallel",
    )

    args = parser.parse_args()
    main(args)

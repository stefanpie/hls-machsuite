import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

import joblib


def hls_synth_benchmark(
    benchmark_directory: Path, temp_dir_overide: Path | None = None
) -> int:
    benchmark_name = benchmark_directory.stem

    if temp_dir_overide is None:
        temp_dir = tempfile.TemporaryDirectory()
        temp_dir_path = Path(temp_dir.name)
    else:
        temp_dir_path = temp_dir_overide / benchmark_name
        temp_dir_path.mkdir(exist_ok=True, parents=True)

    benchmark_name = benchmark_directory.stem
    benchmark_name_c = benchmark_name.replace("-", "_")

    top_fn_fp = benchmark_directory / "top.txt"
    top_fn = top_fn_fp.read_text().strip()

    all_files = list(benchmark_directory.glob("*"))
    for file in all_files:
        shutil.copy(file, temp_dir_path)

    print(f"Running HLS Synthesis : {benchmark_name} : {temp_dir_path}")

    tcl_script = temp_dir_path / "build.tcl"
    tcl_script_txt = ""
    tcl_script_txt += f"open_project -reset test_proj_{benchmark_name}\n"
    tcl_script_txt += f"add_files {(benchmark_name + '.cpp')}\n"
    tcl_script_txt += f"add_files {(benchmark_name + '.h')}\n"
    # tcl_script_txt += f"add_files {(benchmark_name + '_tb.cpp')} -tb\n"
    tcl_script_txt += "open_solution solution1\n"
    tcl_script_txt += f"set_top {top_fn}\n"
    tcl_script_txt += "set_part {xc7z020clg484-1}\n"
    tcl_script_txt += "create_clock -period 10 -name default\n"
    tcl_script_txt += "csynth_design\n"
    tcl_script_txt += "exit\n"
    tcl_script.write_text(tcl_script_txt)

    p = subprocess.run(
        ["vitis_hls", "-f", tcl_script.resolve()],
        cwd=temp_dir_path,
        text=True,
        capture_output=True,
    )
    print(f"{benchmark_name}: {p.returncode}")

    if p.returncode == 0:
        csynth_rpt_fp = (
            temp_dir_path
            / f"test_proj_{benchmark_name}"
            / "solution1"
            / "syn"
            / "report"
            / "csynth.rpt"
        )
        shutil.copy(csynth_rpt_fp, temp_dir_path / "csynth.rpt")

    return p.returncode


def get_vitis_hls_include_dir() -> Path:
    vitis_hls_bin_path_str = shutil.which("vitis_hls")
    if vitis_hls_bin_path_str is None:
        raise RuntimeError("vitis_hls not found in PATH")
    vitis_hls_bin_path = Path(vitis_hls_bin_path_str)
    vitis_hls_include_dir = vitis_hls_bin_path.parent.parent / "include"
    return vitis_hls_include_dir


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
    return vitis_hls_clang_pp_path


def get_vitis_hls_install_dir() -> Path:
    vitis_hls_bin_path_str = shutil.which("vitis_hls")
    if vitis_hls_bin_path_str is None:
        raise RuntimeError("vitis_hls not found in PATH")
    vitis_hls_bin_path = Path(vitis_hls_bin_path_str)
    vitis_hls_install_dir = vitis_hls_bin_path.parent.parent
    return vitis_hls_install_dir


def main(args):
    n_jobs = args.jobs

    error_dir = Path("./errors")
    if error_dir.exists():
        shutil.rmtree(error_dir)

    output_dir = Path("./output")
    if output_dir.exists():
        shutil.rmtree(output_dir)

    temp_dir_compile = Path("./test_temp_compile")
    if temp_dir_compile.exists():
        shutil.rmtree(temp_dir_compile)

    temp_dir_synth = Path("./test_temp_synth")
    if temp_dir_synth.exists():
        shutil.rmtree(temp_dir_synth)

    benchmarks_directory = args.benchmarks_directory
    benchmarks = sorted(list(benchmarks_directory.glob("*")))

    benchmarks_to_test = [benchmark for benchmark in benchmarks]

    ### HLS Synthesis ###
    return_data_hls = joblib.Parallel(n_jobs=n_jobs, backend="multiprocessing")(
        joblib.delayed(hls_synth_benchmark)(benchmark, temp_dir_overide=temp_dir_synth)
        for benchmark in benchmarks_to_test
    )
    return_codes_hls_synthesis = return_data_hls
    for return_code, benchmark in zip(return_codes_hls_synthesis, benchmarks_to_test):
        if return_code != 0:
            print(f"Failed to synthesize benchmark {benchmark.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "benchmarks_directory", type=Path, nargs="?", default=Path("./hls-machsuite/")
    )
    parser.add_argument("-j", "--jobs", type=int, default=16)
    parser.add_argument("-r", "--report", action="store_true", default=False)
    parser.add_argument("-rf", "--report-file", type=Path, default=Path("./report.txt"))
    args = parser.parse_args()
    main(args)

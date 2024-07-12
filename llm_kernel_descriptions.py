from pathlib import Path
from pprint import pp
from string import Template
from textwrap import dedent

from dotenv import dotenv_values

from models import (
    LLM_LLAMA_3_70B_CHAT_HF,
    ModelWithSettings,
)

prompt_template = Template(
    dedent("""
    Help me write a natural description of this high-level synthesis hardware design.

    The description should cover the algorithm and functionality as well as the high level dataflow and architecture of the design.
    We already know the code is for HLS and written in C++, so that doesn't need to be mentioned.
    Include the list of top-level function inputs and outputs as well as a brief description of the functionality the kernel represents.
    All arguments in the top-level function should be described in the inputs and outputs sections with details about the data type and layout.
    Include a list of any important data structures and data types used in the design.
    Include a list of sub-components and a brief description of the functionality of each sub-component.
    
    Make sure descriptions about the high-level algorithm, inputs, outputs, data structures, and sub-components are detailed and through and include information about implementation, data type size layout, and architecture.
    Each description can be multiple sentences long.
    
    The top level kernel function is: `${top_name}`
    
    Only output the description in a code block representing markdown.
    
    The output should be formatted as follows:
    ```
    Description:
    A high level natural language description of the design... (be detailed and thorough)
    
    Top-Level Function: `name_of_top_level_function`
           
    Inputs:
    - `input_1`: description of input_1...
    - ....

    Outputs:
    - `output_1`: description of output_1...
    - ....
    
    Important Data Structures and Data Types:
    - `data_structure_1`: description of data_structure_1... (description of the data structure, data type, size, layout, felids, use in the design, etc. are required)
    
    Sub-Components:
    - `subcomponent_1`: natural language description of subcomponent_1...
    - ...
    ```
    
    Input Kernel Code:
    
    ${kernel_code}
    
    Description in requested markdown code block format:
    """).strip()
)

code_file_template = Template(
    dedent("""
    File Name: `${file_name}`
    ```${md_code_block_type}
    ${file_contents}
    ```
    """).strip()
)


def gen_description(design_dir_fp: Path, model_and_settings: ModelWithSettings) -> str:
    design_name = design_dir_fp.name
    kernel_fp = design_dir_fp / f"{design_name}.cpp"
    header_fp = design_dir_fp / f"{design_name}.h"
    top_fp = design_dir_fp / "top.txt"

    kernel_fp_name = kernel_fp.name
    kernel_contents = kernel_fp.read_text().strip()
    kernel_md_code_block_type = "cpp"

    header_fp_name = header_fp.name
    header_contents = header_fp.read_text().strip()
    header_md_code_block_type = "cpp"

    top_name = top_fp.read_text().strip()

    kernel_code_formatted = code_file_template.substitute(
        file_name=kernel_fp_name,
        md_code_block_type=kernel_md_code_block_type,
        file_contents=kernel_contents,
    )
    header_code_formatted = code_file_template.substitute(
        file_name=header_fp_name,
        md_code_block_type=header_md_code_block_type,
        file_contents=header_contents,
    )

    code_formatted = f"{kernel_code_formatted}\n\n{header_code_formatted}"

    prompt = prompt_template.substitute(
        top_name=top_name,
        kernel_code=code_formatted,
    )

    model = model_and_settings.model
    model_settings = model_and_settings.settings
    model_response = model.prompt(prompt, **model_settings)
    model_response_txt = model_response.text()

    return model_response_txt


if __name__ == "__main__":
    design_dir_fp = Path("./hls-machsuite/")
    dirs = sorted(list(design_dir_fp.glob("*")))

    API_KEY_TAI = dotenv_values(".env")["TOGETHER_API_KEY"]
    assert API_KEY_TAI

    # model_with_settings = LLM_TAI_MIXTRAL_8X22B_INSTRUCT(API_KEY_TAI)
    model_with_settings = LLM_LLAMA_3_70B_CHAT_HF(API_KEY_TAI)

    description_dir = Path("./generated_descriptions/")
    description_dir.mkdir(exist_ok=True)
    for design_dir_fp in dirs:
        design_name = design_dir_fp.name
        print(f"Getting description for {design_name}")
        description_fp = description_dir / f"{design_name}.md"
        if description_fp.exists():
            description_fp.unlink()
        description_txt = gen_description(design_dir_fp, model_with_settings)
        description_fp.write_text(description_txt)
        print(f"Description for {design_name} written to {description_fp}")

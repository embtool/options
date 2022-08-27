#!/usr/bin/env python3

import csv
import re
import os
from typing import Dict, List, Optional, Tuple

FileName = str

decl_dict = {
    "BOOL": "bool @NAME@",
    "CHAR": "char @NAME@",
    "INT8": "int8_t @NAME@",
    "INT16": "int16_t @NAME@",
    "INT32": "int32_t @NAME@",
    "INT64": "int64_t @NAME@",
    "INTPTR": "intptr_t @NAME@",
    "UINT8": "uint8_t @NAME@",
    "UINT16": "uint16_t @NAME@",
    "UINT32": "uint32_t @NAME@",
    "UINT64": "uint64_t @NAME@",
    "UINTPTR": "uintptr_t @NAME@",
    "FLOAT": "float @NAME@",
    "DOUBLE": "double @NAME@",
    "CHAR_ARRAY": "char @NAME@[]",
}

testing_reset_toggles_decl = f"""\
/** @brief Reset toggles to the initialization values.
 *
 * Call this function in the setup of a test suite to start every
 * test with consistent values.
 *
 * This function is available only when testing is enabled (when
 * `TESTING` is defined as 1).
 */
void testing_reset_toggles(void);
"""


def read_csv_file(
    csv_input: FileName, delimiter="\t", quotechar='"'
) -> Tuple[List[str], List[str]]:
    """Read from CSV file, return tuple with header and data."""
    with open(csv_input) as csv_file:
        defaults = list(
            csv.reader(csv_file, delimiter=delimiter, quotechar=quotechar)
        )
    defaults = csv_fix_chars(defaults)
    header, data = defaults[0], defaults[1:]
    return header, data


def csv_fix_chars(data: List[List[str]]) -> List[List[str]]:
    """Fix some characters that commonly appear in CSV files."""
    sub = {
        # LibreOffice Calc
        "“": '"',  # Opening quote
        "”": '"',  # Closing quote
        "–": "-",  # Long dash
    }
    for num_rows, row in enumerate(data):
        for i, v in enumerate(row):
            for k, d in sub.items():
                if k in v:
                    data[num_rows][i] = data[num_rows][i].replace(k, d)
    return data


def read_defaults(
    csv_input: FileName = "csv/defaults.csv",
) -> Dict[str, Dict[str, str]]:
    """Read default values from CSV file, return dict with name and data."""
    defaults = {}

    # Read from CSV file
    header, data = read_csv_file(csv_input)
    assert header[0] == "NAME", "NAME is expected as first column"

    # Insert data in the dict
    for row in data:
        if len(row) == 0 or row[0] == "":
            # Ignore empty rows.
            continue
        elif len(row) < len(header):
            # Fill row with missing columns.
            # Tools like pre-commit remove trailing whitespace (tabs).
            num = len(header) - len(row)
            row += ["" for _ in range(num)]

        name = row[0]
        assert name not in defaults, f"NAME '{name}' is repeated"

        defaults[name] = dict(zip(header, row))

    return defaults


def read_char_ids(
    csv_input: FileName = "csv/char_ids.csv",
) -> Dict[str, Dict[str, str]]:
    """
    Read characterizations from CSV file, return dict with char_id and data.
    """
    defaults = {}

    # Read from CSV file
    header, data = read_csv_file(csv_input)
    assert header[0] == "CHAR_ID", "CHAR_ID is expected as first column"

    # Insert data in the dict
    for row in data:
        char_id = row[0]
        assert char_id not in defaults, f"CHAR_ID '{char_id}' is repeated"

        defaults[char_id] = dict(zip(header, row))

    return defaults


def write_characterization_header(
    defaults: Dict[str, Dict[str, str]],
    char_ids: Dict[str, Dict[str, str]],
    code_output: FileName = "include/toggle.h",
):
    ####################################################################
    # Code begin
    code_begin = """\
#ifndef TOGGLE_H
#define TOGGLE_H

#ifdef __cplusplus
extern "C"
{
#endif

/** @file toggle.h
 * @brief Toggle definitions.
 *
 * This file validates the macro CHAR_ID and includes the corresponding
 * Toggle header.
 *
 * In the list of CHAR_IDS, always add to the end of the list and
 * increment NUM_CHAR_IDS.
 *
 * Numbering starts with 1 because the compiler would treat an undefined
 * CHAR_ID as 0.
 */

#include <stdbool.h>
#include <stdint.h>

#ifdef DOXYGEN
    /** @brief Characterization ID (int).
     *
     * Define the device characterization: the options and features enabled.
     *
     * The characterization ID should be defined when calling CMake (ex:
     * `cmake -D CHAR_ID=...`) or when calling the compiler (ex:
     * `gcc -D CHAR_ID=...`).
     */
    #define CHAR_ID CHAR_ID_EXAMPLE
#endif

#ifndef CHAR_ID
    #define CHAR_ID CHAR_ID_EXAMPLE
    #warning "CHAR_ID is not defined. Using default."
#endif

"""

    ####################################################################
    # Code end
    code_end = """\
#ifdef __cplusplus
}
#endif

#endif /* TOGGLE_H */
"""

    ####################################################################
    # Options documentation and default values
    code_option_doc = """\
/* Options documentation. */

#ifdef DOXYGEN

"""
    for name, data in defaults.items():
        code_option_doc += f"""\
{apply_indent(format_brief_descr_comment(data['BRIEF'], data['DESCRIPTION']), indent=4)}
{apply_indent(format_h_declaration(data), indent=4)}

"""
    code_option_doc += apply_indent(testing_reset_toggles_decl, indent=4)
    code_option_doc += """
#endif /* DOXYGEN */

"""

    ####################################################################
    # Characterization IDs
    code_char_ids = """\
/* List of CHAR_IDs. */
"""
    num = -1  # Set variable for empty char_ids
    for num, items in enumerate(char_ids.items()):
        char_id, data = items
        code_char_ids += (
            f"#define {char_id} {num+1} /**< @brief {data['BRIEF']} */\n"
        )
    code_char_ids += f"""
#define NUM_CHAR_IDS {num+1} /**< @brief Number of char IDs. */

/* Validate CHAR_ID range. */
#if (CHAR_ID < 1 || CHAR_ID > NUM_CHAR_IDS)
    #error "Macro CHAR_ID is not in the valid range."
#endif

"""

    ####################################################################
    # Characterization inclusions
    code_char_includes = """\
/* Include the characterization. */
#ifdef DOXYGEN
    /* Nothing to include for Doxygen. */
"""
    for char_id in char_ids:
        code_char_includes += (
            f"#elif (CHAR_ID == {char_id})\n"
            f'    #include "characterizations/{char_id.lower()}.h"\n'
        )
    code_char_includes += f"#endif\n\n"

    ####################################################################
    # Fit everything together and write
    code = (
        code_begin
        + code_option_doc
        + code_char_ids
        + code_char_includes
        + code_end
    )
    code = clean_code(code)
    create_directory(code_output)
    with open(code_output, "w") as fp:
        fp.write(code)


def create_directory(filename: FileName):
    directory = re.sub(r"/[^/]*$", r"", filename)
    os.makedirs(directory, exist_ok=True)


def format_brief_descr_comment(
    brief: str, descr: str, mid_comment: bool = False
) -> str:
    comment = "" if mid_comment else "/** "

    if descr == "":
        comment += f"@brief {brief}"
        comment += "" if mid_comment else " */"
    else:
        comment += f"@brief {brief}" + format_comment("\n" + descr)
        comment += "" if mid_comment else f"\n */"

    return comment


def apply_indent(code: str, indent: int) -> str:
    indent = " " * indent
    return indent + ("\n" + indent).join(code.split("\n"))


def write_characterization_source(
    defaults: Dict[str, Dict[str, str]],
    char_ids: Dict[str, Dict[str, str]],
    code_output: FileName = "src/toggle.c",
):
    ####################################################################
    # Code begin
    code_begin = """\
#include "toggle.h"

"""

    ####################################################################
    # Code end
    code_end = ""

    ####################################################################
    # Characterization inclusions
    code_char_includes = """\
#ifdef DOXYGEN
    /* Nothing to include for Doxygen. */
"""
    for char_id in char_ids:
        code_char_includes += (
            f"#elif (CHAR_ID == {char_id})\n"
            f'    #include "characterizations/{char_id.lower()}.c"\n'
        )
    code_char_includes += f"#endif\n"

    ####################################################################
    # Fit everything together and write
    code = code_begin + code_char_includes + code_end
    code = clean_code(code)
    create_directory(code_output)
    with open(code_output, "w") as fp:
        fp.write(code)


def write_char_id_source(
    defaults: Dict[str, Dict[str, str]],
    char_id: Dict[str, Dict[str, str]],
):
    file_name = char_id["CHAR_ID"].lower() + ".c"
    code_output = f"src/characterizations/{file_name}"

    ####################################################################
    # Code begin
    code_begin = ""

    ####################################################################
    # Code end
    code_end = ""

    ####################################################################
    # Options value
    code_option = ""
    for name, data in defaults.items():
        code_option += f"""\
{format_c_definition(data, char_id)}
"""

    ####################################################################
    # Testing functions

    if is_testing(char_id):
        code_option += """
void testing_reset_toggles(void)
{
"""
        for name, data in defaults.items():
            code_option += f"""\
{apply_indent(format_c_assignment(data, char_id), indent=4)}
"""
        code_option += "}\n"

    ####################################################################
    # Necessary headers

    necessary_headers = ""
    found_headers = re.findall(
        r"TOP_C: (.*?)(?:\s*\*\/)?$", code_option, re.MULTILINE
    )
    # necessary_headers += "\n/*\n" + str(found_headers) + "\n*/\n"
    necessary_headers += "\n".join(found_headers)
    necessary_headers += "\n"

    ####################################################################
    # Fit everything together and write
    code = code_begin + necessary_headers + code_option + code_end
    code = clean_code(code)
    create_directory(code_output)
    with open(code_output, "w") as fp:
        fp.write(code)


def write_char_id_header(
    defaults: Dict[str, Dict[str, str]],
    char_id: Dict[str, Dict[str, str]],
):
    file_name = char_id["CHAR_ID"].lower() + ".h"
    header_guard = "CHARACTERIZATIONS_" + char_id["CHAR_ID"].upper() + "_H"
    code_output = f"include/characterizations/{file_name}"

    ####################################################################
    # Code begin
    code_begin = f"""\
#ifndef {header_guard}
#define {header_guard}

/** @file {file_name}
 * {format_brief_descr_comment(
        char_id['BRIEF'], char_id["DESCRIPTION"], mid_comment=True
    )}
 */

"""

    ####################################################################
    # Code end
    code_end = f"""
#endif /* {header_guard} */
"""

    ####################################################################
    # Options value
    code_option = ""
    for name, data in defaults.items():
        code_option += f"""\
{format_brief_descr_comment(data['BRIEF'], data['DESCRIPTION'])}
{format_h_declaration(data, char_id)}

"""

    ####################################################################
    # Testing functions

    if is_testing(char_id):
        code_option += apply_indent(testing_reset_toggles_decl, indent=0)

    ####################################################################
    # Fit everything together and write
    code = code_begin + code_option + code_end
    code = clean_code(code)
    create_directory(code_output)
    with open(code_output, "w") as fp:
        fp.write(code)


def format_comment(comment: str, *, indent: int = 0) -> str:
    lines = ["", *comment.split("\n")]
    comment = f"\n{' ' * indent} * ".join(lines)
    return comment


def format_h_declaration(
    defaults: Dict[str, str], char_id: Optional[Dict[str, str]] = None
) -> str:
    code = defaults["H"]
    return format_ch_def_decl(code, defaults, char_id, format="decl")


def format_c_definition(
    defaults: Dict[str, str], char_id: Optional[Dict[str, str]] = None
) -> str:
    code = defaults["C"]
    return format_ch_def_decl(code, defaults, char_id, format="def")


def format_c_assignment(
    defaults: Dict[str, str], char_id: Optional[Dict[str, str]] = None
) -> str:
    code = defaults["C_ASSIGN"]
    return format_ch_def_decl(code, defaults, char_id, format="assign")


def is_testing(char_id: Optional[Dict[str, str]] = None) -> bool:
    if char_id is None or "TESTING" not in char_id or char_id["TESTING"] == "":
        testing = False
    else:
        testing = bool(int(char_id["TESTING"]))
    return testing


def get_value(
    name: str,
    defaults: Dict[str, str],
    char_id: Optional[Dict[str, str]] = None,
) -> str:
    # Get value from characterization or defaults
    if char_id is None or name not in char_id or char_id[name] == "":
        value = defaults["DEFAULT"]
    else:
        value = char_id[name]
    return value


def error_if_value_option_is_set_on_characterization_file(
    name: str,
    defaults: Dict[str, str],
    char_id: Dict[str, str],
) -> str:
    # Error if a "VALUE option" is being set on the characterization.
    if char_id is None:
        pass
    elif defaults["TYPE"].startswith("VALUE") and name in char_id:
        assert name not in char_id, (
            f"{name} is declared with TYPE = VALUE and cannot be "
            "redefined in the characterization. Remove the column "
            f"{name} from the file csv/char_ids.csv."
        )


def format_ch_def_decl(
    code: str,
    defaults: Dict[str, str],
    char_id: Dict[str, str],
    *,
    format: str,
):
    typ = defaults["TYPE"]
    decl = defaults["DECL"]
    name = defaults["NAME"]
    value = get_value(name, defaults, char_id)
    testing = is_testing(char_id)
    testing_changes = False

    error_if_value_option_is_set_on_characterization_file(
        name, defaults, char_id
    )

    # No custom code. Generate default.

    # TYPE and DECL
    if typ == "VALUE":
        testing_changes = False
    elif typ == "OPTION":
        testing_changes = True
    else:
        raise NotImplementedError(
            f'TYPE = "{typ}" is not implemented. ' 'Valid: ["VALUE", "OPTION"].'
        )

    # DECL part 1
    if decl == "MACRO":
        # MACRO (without type) cannot be tested
        testing_changes = False
    elif decl == "CUSTOM":
        # CUSTOM cannot be tested
        testing_changes = False

    if code == "":
        # DECL part 2
        if decl == "MACRO":
            # MACRO (without type) cannot be tested
            base = "MACRO"
            decl = "MACRO"
        elif decl == "CUSTOM":
            # CUSTOM cannot be tested
            # Nothing to do for custom
            return code
        elif (
            decl.startswith("MACRO_")
            or decl.startswith("CONST_")
            or decl.startswith("VAR_")
        ):
            # MACRO_*, CONST_* or VAR_*
            base, decl = decl.split("_", 1)

            if decl in decl_dict:
                decl = decl_dict[decl]
            else:
                raise NotImplementedError(
                    f'DECL = "{decl}" is not implemented. '
                    'Valid: ["*_UINT8", etc].'
                )
        else:
            raise NotImplementedError(
                f'DECL = "{decl}" is not implemented. '
                'Valid: ["MACRO_*", "CONST_*", "VAR_*"].'
            )

        # Changes when testing
        if base == "MACRO":
            if testing and testing_changes:
                if format == "decl":
                    code = f"extern {decl};"
                elif format == "def":
                    code = f"{decl} = @VALUE@;"
                elif format == "assign":
                    code = f"@NAME@ = @VALUE@;"
            else:
                if format == "decl":
                    code = f"#define @NAME@ @VALUE@"
                elif format == "def":
                    code = ""
                elif format == "assign":
                    code = ""
        elif base == "CONST":
            if format == "decl":
                code = f"extern @CONST@ {decl};"
            elif format == "def":
                code = f"@CONST@ {decl} = @VALUE@;"
            elif format == "assign":
                code = f"@NAME@ = @VALUE@;"
        elif base == "VAR":
            if format == "decl":
                code = f"extern {decl};"
            elif format == "def":
                code = f"{decl} = @VALUE@;"
            elif format == "assign":
                code = f"@NAME@ = @VALUE@;"

    # Update values on the code
    code = code.replace("@NAME@", name)
    code = code.replace("@VALUE@", value)

    const = "" if testing and testing_changes else "const"
    if const == "":
        code = code.replace("@CONST@ ", const)
        code = code.replace(" @CONST@", const)
    else:
        code = code.replace("@CONST@", const)

    return code


def clean_code(code: str) -> str:
    # One LF at the end of the file
    code = code.strip() + "\n"

    # Remove trailing whitespace
    code = re.sub(r"[ \t]+$", r"", code, flags=re.MULTILINE)

    # One new line before and after braces
    code = re.sub(r"\n\n+}", r"\n}", code)
    code = re.sub(r"{\n\n+", r"{\n", code)

    # No multiple new lines
    code = re.sub(r"\n\n\n+", r"\n\n", code)

    return code


def main():
    defaults = read_defaults()
    char_ids = read_char_ids()

    write_characterization_header(defaults, char_ids)
    write_characterization_source(defaults, char_ids)

    for name, char_id in char_ids.items():
        write_char_id_header(defaults, char_id)
        write_char_id_source(defaults, char_id)


if __name__ == "__main__":
    main()

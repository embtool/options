# [Toggle - Hardware and Feature Toggles](https://github.com/embtool/toggle)

by [Djones A. Boni](https://github.com/djboni)

A big issue on embedded software development is the ability to manage
changes in hardware and changes in the software itself.

Time to market and backwards compatibility are often concerns, raising
the importance of the ability to reuse working/older code in the
new hardware revisions and to use new code in working/older hardware.

The software systems are getting larger, with lots of "moving parts",
and becoming themselves the moving parts of even bigger systems.

Therefore the design and progression of the software architecture
(long term) and of the new features (short term) are indispensable
for the maintainability and testability of the code.

This project is an attempt to solve this issue, enabling the continuous
evolution, operation and maintenance of long lived embedded software
systems.

C/C++ Feature Toggles:

- Support multiple hardware revisions in a single repository
  - Select the hardware version at build time
- Support enable/disable features under development
  - Essential for teams using Trunk Based Development
- Flexibility:
  - Compile-time toggles (macro or constant)
  - Run-time toggles (variable)
  - Testing support (all toggles as variables, allow changes in run-time)

More Features:

- Automate the generation of characterizations:
  - Simple to add new options/features.
  - Simple to add new characterizations/versions.
  - Avoid the error prone and tedious work of updating several files
    with similar definitions.
  - Avoid missing some definition.
- Simple file format, easy to edit, review and source control:
  - Characterizations are defined in two YAML files.
  - YAMLs are simple text files that can be diffed, reviewed, and source
    controlled.
- Flexible:
  - Default declaration and definitions.
  - Customize declaration and definitions every option.
- Characterizations documented with Doxygen comments.

Dependencies:

- Python 3

## Using (manual generation)

Using Toggle is just a matter of editing two YAML files, where you define
the options available for the characterizations (yaml/defaults.yaml)
and define the characterizations with the values for the options
(yaml/char_ids.yaml).

1. Edit the YAML files:
   - `yaml/defaults.yaml`: Define the option name, default value,
     type, declaration type, brief description, full description,
     custom header declaration, and custom source definition.
   - `yaml/char_ids.yaml`: Define the characterization (char IDs),
     brief description, full description, and values for the options.
     - Options not present use the default value.
2. Run `generate.py`.
   - Generate `include/toggle.h`, `src/toggle.c`, and files specific for
     the characterizations.
3. Include `toggle.h` in the source.
4. Build and link `toggle.c` in the executable.
5. Compile defining the characterization:
   - Add `-D CHAR_ID=CHAR_ID_TEST` to compile with the test
     characterization
   - Add `-D CHAR_ID=CHAR_ID_EXAMPLE` to compile with the example
     characterization

See the example/.

## Using with CMake (automated generation)

To use Toggle in a CMake project allows automated generation of the
characterization code, every time one of the YAML files change.

Add Toggle as an external project (see example/CMakeLists.txt),
or add it as a subdirectory (using add_subdirectory()),
create a characterization library (using add_toggle_library()),
then link the library to the executable.

```cmake
cmake_minimum_required(VERSION 3.10)
project(toggle_example VERSION 1.0)

# Set default CHAR_ID
set(CHAR_ID
    CHAR_ID_EXAMPLE
    CACHE STRING "Characterization")

# Option A:
# Add Toggle as an external project
include(FetchContent)
FetchContent_Declare(
  toggle
  GIT_REPOSITORY https://github.com/embtool/toggle
  GIT_TAG main # or use a tag, eg. v1.0
)
FetchContent_MakeAvailable(toggle)

# Option B:
# Add subdirectory
add_subdirectory(components/characterization)

# Create a characterization library using Toggle
add_toggle_library(characterization ${CMAKE_CURRENT_SOURCE_DIR})

# Link the characterization library to an executable or library
add_executable(main main.c)
target_link_libraries(main PRIVATE characterization)
```

See the example/.

## Details of File: `yaml/defaults.yaml`

The file `yaml/defaults.yaml` defines the list of options for the
characterizations. The description of the columns is provide below.

- **NAME**: Option name
- **DEFAULT**: Default value
- **TYPE**: OPTION or VALUE
- **DECL**: Declaration type
- **BRIEF**: Brief description
- **DESCRIPTION**: Full description
- **H**: Custom header declaration
- **C**: Custom source definition
- **TEST_ASSIGN**: Custom assignment for tests

Example of yaml/defaults.yaml file:

```yaml
- NAME: TESTING
  DEFAULT: 0
  TYPE: OPTION
  DECL: MACRO
  BRIEF: Testing support.
  DESCRIPTION: |
    0: dev or prod; 1: unit-test.

- NAME: SERIAL_DEBUG
  DEFAULT: NO_SER_DBG
  TYPE: OPTION
  DECL: MACRO_INT8
  BRIEF: Serial debug.

- NAME: NO_SER_DBG
  DEFAULT: 0
  TYPE: VALUE
  DECL: MACRO_INT8
  BRIEF: No serial debug.
  DESCRIPTION: |
    @see SERIAL_DEBUG.

- NAME: SER_DBG_UART3
  DEFAULT: 1
  TYPE: VALUE
  DECL: MACRO_INT8
  BRIEF: Serial debug on UART3.
  DESCRIPTION: |
    @see SERIAL_DEBUG.

- NAME: SER_DBG_UART2
  DEFAULT: 2
  TYPE: VALUE
  DECL: MACRO_INT8
  BRIEF: Serial debug on UART2.
  DESCRIPTION: |
    @see SERIAL_DEBUG.
```

| NAME          | DEFAULT    | TYPE   | DECL       | BRIEF                  | DESCRIPTION                   |
| ------------- | ---------- | ------ | ---------- | ---------------------- | ----------------------------- |
| TESTING       | 0          | OPTION | MACRO      | Testing support.       | 0: dev or prod; 1: unit-test. |
| SERIAL_DEBUG  | NO_SER_DBG | OPTION | MACRO_INT8 | Serial debug.          |                               |
| NO_SER_DBG    | 0          | VALUE  | MACRO_INT8 | No serial debug.       | @see SERIAL_DEBUG.            |
| SER_DBG_UART3 | 1          | VALUE  | MACRO_INT8 | Serial debug on UART3. | @see SERIAL_DEBUG.            |
| SER_DBG_UART2 | 2          | VALUE  | MACRO_INT8 | Serial debug on UART2. | @see SERIAL_DEBUG.            |

**NAME**: Option name of the option/feature. Must be a valid C/C++
identifier (`[a-zA-Z][a-za-z0-9]*`).

**DEFAULT**: Default value. The default value for the option. This value
is used in all characterizations that leave the option empty and
for the options that are not present in the characterization file.

When adding a new option, the default value can be selected to allow most
of the current characterizations to continue working with the least effort.

Let's say you are in need of a serial port to print debug information
and in hardware v1.0 no serial port is routed. You decide then
to route the serial port UART3 in the hardware v2.0.

Then you create an option named `SERIAL_DEBUG`, and a good default
value would be 0 (disabled), while 1 (enabled) is defined
only in the v2.0 characterization.

yaml/defaults.yaml:

| NAME         | DEFAULT | TYPE   | DECL       | BRIEF | DESCRIPTION |
| ------------ | ------- | ------ | ---------- | ----- | ----------- |
| SERIAL_DEBUG | 0       | OPTION | MACRO_INT8 |       |             |

```cpp
if (SERIAL_DEBUG)
{
    // Initialize UART3
}
```

**TYPE**: OPTION or VALUE. An option can be changed in the
characterization, while a value cannot be changed by the
characterization.

Values can be used to compare with options and be assured the
characterizations cannot change them.

Suppose that in hardware v3.0 you added USB and it uses one of the pins
from UART3, so you cannot use it for debug anymore. You decide to route
UART2 for this purpose.

Now, just a 0/1 meaning NO/YES is not enough, so it is better to give
actual names for the values of the option, adding `NO_SER_DBG` (0 - meaning
disabled, v1.0), `SER_DBG_UART3` (1 - meaning to use UART3, v2.0), and
`SER_DBG_UART2` (2 - meaning to use UART2, V3.0).

yaml/defaults.yaml:

| NAME          | DEFAULT    | TYPE   | DECL       | BRIEF | DESCRIPTION |
| ------------- | ---------- | ------ | ---------- | ----- | ----------- |
| SERIAL_DEBUG  | NO_SER_DBG | OPTION | MACRO_INT8 |       |             |
| NO_SER_DBG    | 0          | VALUE  | MACRO_INT8 |       |             |
| SER_DBG_UART3 | 1          | VALUE  | MACRO_INT8 |       |             |
| SER_DBG_UART2 | 2          | VALUE  | MACRO_INT8 |       |             |

```cpp
if (SERIAL_DEBUG == SER_DBG_UART3)
{
    // Initialize UART3
}
else if (SERIAL_DEBUG == SER_DBG_UART2)
{
    // Initialize UART2
}
else
{
    // Nothing to initialize
}
```

**DECL**: Declaration of the option. Specifies the default declaration
(H - for headers), the default definition (C - for sources).

The declaration need a base and a type joined by an underscore `_`.
The base can be:

- `MACRO` - Create a macro (non-testable)
- `MACRO_type` - Create a macro (testable)
- `CONST_type` - Create a constant global variable (testable)
- `VAR_type` - Create a global variable (testable)

And the type can be:

- `BOOL` - `bool` - boolean
- `INT32` - `int32_t` - 32 bit signed integer
- `UINT32` - `uint32_t` - 32 bit unsigned integer
- etc (see table below)

| DECL            | Type in the code       |
| --------------- | ---------------------- |
| MACRO           | #define @NAME@ @VALUE@ |
| base_BOOL       | bool                   |
| base_CHAR       | char                   |
| base_INT8       | int8_t                 |
| base_INT16      | int16_t                |
| base_INT32      | int32_t                |
| base_INT64      | int64_t                |
| base_INTPTR     | intptr_t               |
| base_UINT8      | uint8_t                |
| base_UINT16     | uint16_t               |
| base_UINT32     | uint32_t               |
| base_UINT64     | uint64_t               |
| base_UINTPTR    | uintptr_t              |
| base_FLOAT      | float                  |
| base_DOUBLE     | double                 |
| base_CHAR_ARRAY | char []                |

Type of macro? It is nice to document the expected type for the macro,
even if it is not used in the code itself. An additional reason is
related to the testability (see below).

Testable and non-testable? In the characterization you can define
a special option named `TESTING` as 1. In this case all options that are
"testable macros" (`MACRO_type`) will be converted to variables of that
type and all options that are "constants" (`CONST_type`) will be
converted to non-constants.

Note that only `TYPE=OPTION` are modified when `TESTING=1`.
`TYPE=VALUE` are NOT converted, to assure they do not change.

The table below shows the the resulting type of an option or value and
marks with a plus (+) when it is is testable (can be changed at run
time).

| TYPE   | TESTING   | MACRO | MACRO_type | CONST_type | VAR_type |
| ------ | --------- | ----- | ---------- | ---------- | -------- |
| OPTION | TESTING=0 | macro | macro      | const type | type (+) |
| OPTION | TESTING=1 | macro | type (+)   | type (+)   | type (+) |
| VALUE  | TESTING=0 | macro | macro      | const type | type (+) |
| VALUE  | TESTING=1 | macro | macro      | const type | type (+) |

**BRIEF**: Brief description to be added as documentation.

**DESCRIPTION**: Additional description to be added as documentation.

**H**: Custom header declaration. Specifies how to declare the option in
the header `toggle.h`. Use `@NAME@` as a placeholder for the
option name, `@VALUE@` as a placeholder for the option value, and
`@CONST@` as a placeholder for the constness.

Therefore, if you are not happy with the default header declaration,
you can DIY.

Examples:

- Macro: `#define @NAME@ @VALUE@`
- Boolean: `extern @CONST@ bool @NAME@;`
- Integer: `extern @CONST@ int @NAME@;`
- String: `extern @CONST@ char @NAME@[];`

Why a placeholder for constness? When `TESTING=1` the constness is
removed to enable testing.

**C**: Custom source definition. Specifies how to define the option in
the source `toggle.c`. Works the same way as in the header, using
`@NAME@`, `@VALUE@`, and `@CONST@` as placeholders.

Examples:

- Macro: (nothing)
- Boolean: `@CONST@ bool @NAME@ = @VALUE@;`
- Integer: `@CONST@ int @NAME@ = @VALUE@;`
- String: `@CONST@ char @NAME@[] = @VALUE@;`

If there is a need to include or define something at before the
definitions (in the C file) write a comment in the form: `TOP_C: ...`.

```cpp
/* TOP_C: #include <stddef.h> */

/* TOP_C: #ifndef MY_ASSERT
 * TOP_C:     #define MY_ASSERT(x) if (!(x)) { for (;;) {} }
 * TOP_C: #endif
 */

// TOP_C: typedef unsigned char my_size;
```

**TEST_ASSIGN**: Custom assignment for tests. Specifies how to assign
values to the options, so they can be reset to the original values
when testing, allowing the tests to start with consistent options.
Works the same way as in the header, using `@NAME@`, `@VALUE@`, and
`@CONST@` as placeholders.

When `TESTING=1` is the function `testing_reset_toggles()` is available
and uses this (or the default) assignment recipe to assign the original
value to the options.

Examples:

- Macro: (nothing)
- Boolean: `@NAME@ = @VALUE@;`
- Integer: `@NAME@ = @VALUE@;`
- String:
  - Resetting a string is a bit cumbersome. Include `<string.h>` and use
    `strncpy()` or write a loop yourself.
  ```
  /* TOP_C: #include <string.h> */
  strncpy(@NAME@, @VALUE@, sizeof(@NAME@));
  ```

## Details of File: `yaml/char_ids.yaml`

The file `yaml/char_ids.yaml` defines the list of characterizations and
their values. The description of the columns is provide below.

- **CHAR_ID**: Characterization name
- **BRIEF**: Brief description
- **DESCRIPTION**: Full description
- **TESTING**: Special option for testing
- **Other options**: Additional options set for the characterizations

Example of yaml/char_ids.yaml file:

```yaml
- CHAR_ID: CHAR_ID_TEST
  BRIEF: Unit-tests.
  DESCRIPTION: Unit-tests.
  TESTING: 1

- CHAR_ID: HW_V1
  BRIEF: Hardware v1.0.
  DESCRIPTION: First version.

- CHAR_ID: HW_V2
  BRIEF: Hardware v2.0.
  DESCRIPTION: Serial debug.
  SERIAL_DEBUG: SER_DBT_UART3

- CHAR_ID: HW_V3
  BRIEF: Hardware v3.0.
  DESCRIPTION: Serial debug on UART2.
  SERIAL_DEBUG: SER_DBT_UART2
```

| CHAR_ID      | BRIEF          | DESCRIPTION            | TESTING | SERIAL_DEBUG  |
| ------------ | -------------- | ---------------------- | ------- | ------------- |
| CHAR_ID_TEST | Unit-tests.    |                        | 1       |               |
| HW_V1        | Hardware v1.0. | First version.         |         |               |
| HW_V2        | Hardware v2.0. | Serial debug.          |         | SER_DBT_UART3 |
| HW_V3        | Hardware v3.0. | Serial debug on UART2. |         | SER_DBT_UART2 |

**CHAR_ID**: Characterization name. Must be a valid C/C++
identifier (`[a-zA-Z][a-za-z0-9]*`).

**BRIEF**: Brief description to be added as documentation.

**DESCRIPTION**: Full description to be added as documentation.

**TESTING**: Special option that specifies if the characterization needs
testing support.

Options defined as macros or constants are transformed in non-constant
variables.

**Other options**: Additional options set for the characterizations.

# Minimal Configuration

- yaml/defaults.yaml:
  - It is recommended to leave the option "TESTING" in the defaults file.
  - Add other options as you need.

```yaml
- NAME: TESTING
  DEFAULT: 0
  TYPE: OPTION
  DECL: MACRO
  BRIEF: Specifies if the code needs testing support (bool).
  DESCRIPTION: |
    - 0 Development and production.
    - 1 Unit-tests.
```

- yaml/char_ids.yaml:
  - It is recommended to leave the characterizations "CHAR_ID_TEST" and
    "CHAR_ID_EXAMPLE" in the characterizations file.
  - Add characterizations as you need.

```yaml
- CHAR_ID: CHAR_ID_TESTS
  BRIEF: Testing.
  DESCRIPTION: Characterization for unit-tests.
  TESTING: 1

- CHAR_ID: CHAR_ID_EXAMPLE
  BRIEF: Example.
  DESCRIPTION: Characterization with default values.
```

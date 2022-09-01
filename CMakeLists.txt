cmake_minimum_required(VERSION 3.10)
project(toggle VERSION 1.1)

# Generate Toggle files with automatic update and add Toggle libraries.
#
# The generated files are updated whenever the files yaml/defaults.yaml or
# yaml/char_ids.yaml change.
#
# Pass the library name and the path to the yaml/ directory. The generated files
# are created in include/ and src/ in that directory.
#
# Usage: add_toggle_library(mycharids path/to/chars)
#
# The usage example above adds two Toggle libraries:
#
# * mycharids - requested library that uses the toggles according to the CHAR_ID
#   provided to CMake.
# * mycharids_test - test library that uses the default testing toggles
#   (CHAR_ID=CHAR_ID_TEST).
#
# Link the requested library to the executable:
#
# target_link_libraries(main PRIVATE mycharids)
#
# Link the test library with the test executable:
#
# target_link_libraries(test PRIVATE mycharids_test)
function(add_toggle_library target directory)
  # Generate files when the dependencies change
  add_custom_command(
    OUTPUT ${directory}/include/toggle.h ${directory}/src/toggle.c
    COMMAND ${toggle_SOURCE_DIR}/generate.py
    WORKING_DIRECTORY ${directory}
    DEPENDS ${directory}/yaml/defaults.yaml ${directory}/yaml/char_ids.yaml
    COMMENT "Generating Toggle files for \"${target}\"")

  # Requested library
  add_library("${target}" ${directory}/include/toggle.h
                          ${directory}/src/toggle.c)
  target_include_directories("${target}" PUBLIC ${directory}/include)
  target_compile_definitions("${target}" PUBLIC -DCHAR_ID=${CHAR_ID})

  # Test library
  add_library("${target}_test" ${directory}/include/toggle.h
                               ${directory}/src/toggle.c)
  target_include_directories("${target}_test" PUBLIC ${directory}/include)
  target_compile_definitions("${target}_test" PUBLIC -DCHAR_ID=CHAR_ID_TEST)
endfunction()

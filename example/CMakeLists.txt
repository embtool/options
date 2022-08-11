cmake_minimum_required(VERSION 3.10)
project(toggle_example VERSION 1.0)

# Set default CHAR_ID
set(CHAR_ID
    CHAR_ID_EXAMPLE
    CACHE STRING "Characterization")

# Add Toggle as an external project
#
# ~~~
# include(FetchContent)
# FetchContent_Declare(
#   toggle
#   GIT_REPOSITORY https://github.com/embtool/toggle
#   GIT_TAG main # or use a tag, eg. v1.0
# )
# FetchContent_MakeAvailable(toggle)
# ~~~

# For this example we add Toggle as a subdirectory
add_subdirectory(.. toggle)

# Create a characterization library using Toggle
add_toggle_library(characterization ${CMAKE_CURRENT_SOURCE_DIR})

# Link the characterization library to an executable or library
add_executable(main main.c)
target_link_libraries(main PRIVATE characterization)

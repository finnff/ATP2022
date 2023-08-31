cmake_minimum_required(VERSION 3.4)
project(aaaa)

# Add hiredis library and include directories
link_directories(/usr/lib64)
include_directories(/usr/include/hiredis)

# Add pybind11
add_subdirectory(pybind11)

# Create the module
add_library(wsp_mod MODULE aaaa.cpp bindings.cpp)

# Link against hiredis and pybind11
target_link_libraries(wsp_mod PRIVATE pybind11::module hiredis)

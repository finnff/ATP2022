cmake_minimum_required(VERSION 3.12)
project(mysensor)

set(CMAKE_CXX_STANDARD 14)

add_subdirectory(pybind11)
add_library(mysensor MODULE binding.cpp speed_sensor.cpp)

target_link_libraries(mysensor PRIVATE pybind11::module hiredis)

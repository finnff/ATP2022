cmake_minimum_required(VERSION 3.12)
project(WSS_binded)

# Add the path to the pybind11 package if not globally installed
# list(APPEND CMAKE_PREFIX_PATH "path/to/pybind11/share/cmake/pybind11")

find_package(pybind11 REQUIRED)

# Specify the paths for your installed Redis library and headers
include_directories(/usr/include/hiredis)  # include path for redis headers
link_directories(/usr/lib64)  # lib path for redis

add_library(WSS_binded MODULE WheelSpeedSensor.cpp bindings.cpp)

# Link against the Redis and pybind11 libraries
target_link_libraries(WSS_binded PRIVATE pybind11::module hiredis)

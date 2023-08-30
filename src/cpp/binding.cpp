// binding.cpp
#include "speed_sensor.cpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(mysensor, m) {
  py::class_<SpeedSensor>(m, "SpeedSensor")
      .def(py::init<>())
      .def("read_speed", &SpeedSensor::read_speed)
      .def("set_two_floats", &SpeedSensor::set_two_floats);
}

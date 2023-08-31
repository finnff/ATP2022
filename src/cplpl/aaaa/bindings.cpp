#include "aaaa.h"
#include <hiredis/hiredis.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(wsp_mod, m)
{
    py::class_<WheelSpeedSensor>(m, "WheelSpeedSensor")
        .def(py::init<>())
        .def("read_speed", &WheelSpeedSensor::read_speed)
        .def("set_cpr", &WheelSpeedSensor::set_cpr)
        .def("set_diameter", &WheelSpeedSensor::set_diameter);
}

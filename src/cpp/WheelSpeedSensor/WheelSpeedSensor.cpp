#include "WheelSpeedSensor.h"

WheelSpeedSensor::WheelSpeedSensor() {}

WheelSpeedSensor::~WheelSpeedSensor() {}

float WheelSpeedSensor::read_speed() {
  // Implement Redis calls and calculations here.
  // Just a mock value for now.
  return 42.0;
}

void WheelSpeedSensor::set_cpr(float cpr) {
  // Implement setting of CPR value here.
}

void WheelSpeedSensor::set_diameter(float diameter) {
  // Implement setting of diameter value here.
}

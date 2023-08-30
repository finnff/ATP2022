#pragma once

#include <string>

class WheelSpeedSensor {
public:
  WheelSpeedSensor();
  ~WheelSpeedSensor();

  float read_speed();
  void set_cpr(float cpr);
  void set_diameter(float diameter);
};

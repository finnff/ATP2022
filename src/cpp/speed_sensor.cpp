#include "hiredis/hiredis.h" // Redis C client
#include <iostream>
#include <string>

class SpeedSensor {
private:
  redisContext *context;
  float vehicle_speed;

public:
  SpeedSensor() {
    context = redisConnect("127.0.0.1", 6379);
    vehicle_speed = 0.0;
  }

  ~SpeedSensor() { redisFree(context); }

  float read_speed() {
    redisReply *reply = (redisReply *)redisCommand(
        context, "HGET Sensor_Actuator WheelSpeedSensorHz");
    if (reply->type == REDIS_REPLY_STRING) {
      vehicle_speed = std::stof(reply->str);
    }
    freeReplyObject(reply);
    return vehicle_speed;
  }

  void set_two_floats(float a, float b) {
    // Do something with a and b
    std::cout << "Float A: " << a << ", Float B: " << b << std::endl;
  }
};

#pragma once

#include <hiredis/hiredis.h>
#include <string>

class WheelSpeedSensor {
public:
    WheelSpeedSensor(redisContext* redis_client);
    ~WheelSpeedSensor();
    float read_speed();
    void set_cpr(float cpr);
    void set_diameter(float diameter);

private:
    float vehicle_speed;
    float cpr;
    float diameter;
    redisContext* redis_client; // Redis client context
};

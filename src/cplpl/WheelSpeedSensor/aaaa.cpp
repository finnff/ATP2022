#include "aaaa.h"
#include <cstdlib> // for std::atof

WheelSpeedSensor::WheelSpeedSensor(redisContext* redis_client)
    : vehicle_speed(0.0)
    , cpr(0.0)
    , diameter(0.0)
    , redis_client(redis_client)
{
    // Constructor logic here
}

WheelSpeedSensor::~WheelSpeedSensor()
{
    // Destructor logic here
}

float WheelSpeedSensor::read_speed()
{
    redisReply* reply = (redisReply*)redisCommand(redis_client, "HGET Sensor_Actuator WheelSpeedSensorHz");

    if (reply->type == REDIS_REPLY_STRING) {
        vehicle_speed = std::atof(reply->str);
    } else {
        vehicle_speed = 0.0;
    }

    freeReplyObject(reply);

    return vehicle_speed;
}

void WheelSpeedSensor::set_cpr(float cpr)
{
    this->cpr = cpr;
}

void WheelSpeedSensor::set_diameter(float diameter)
{
    this->diameter = diameter;
}

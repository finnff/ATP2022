
#include "aaaa.h"
#include <hiredis/hiredis.h>

WheelSpeedSensor::WheelSpeedSensor()
    : cpr(1.0)
    , diameter(1.0)
{
    redis_client = redisConnect("127.0.0.1", 6379);
    if (redis_client == NULL || redis_client->err) {
        // Handle error
    }
}

WheelSpeedSensor::~WheelSpeedSensor()
{
    if (redis_client) {
        redisFree(redis_client);
    }
}

float WheelSpeedSensor::read_speed()
{
    redisReply* reply = (redisReply*)redisCommand(redis_client, "HGET Sensor_Actuator WheelSpeedSensorHz");

    float encoder_pulses_per_second = 0.0;

    if (reply->type == REDIS_REPLY_STRING) {
        encoder_pulses_per_second = std::atof(reply->str);
    }

    freeReplyObject(reply);

    // Convert pulses per second to rotations per second
    float rotations_per_second = encoder_pulses_per_second / this->cpr;

    // Calculate the wheel circumference we use this instead of math.h pi good enough
    float wheel_circumference = 3.141592 * this->diameter;

    // Convert to speed in meters per second
    float true_vehicle_speed = rotations_per_second * wheel_circumference;

    return true_vehicle_speed;
}

void WheelSpeedSensor::set_cpr(float cpr)
{
    this->cpr = cpr;
}

void WheelSpeedSensor::set_diameter(float diameter)
{
    this->diameter = diameter;
}

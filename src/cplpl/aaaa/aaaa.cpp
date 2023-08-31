
#include "aaaa.h"
#include <hiredis/hiredis.h>

WheelSpeedSensor::WheelSpeedSensor()
    : cpr(0.0)
    , diameter(0.0)
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

    float speed = 0.0;

    if (reply->type == REDIS_REPLY_STRING) {
        speed = std::atof(reply->str);
    }

    freeReplyObject(reply);

    return speed;
}

void WheelSpeedSensor::set_cpr(float cpr)
{
    this->cpr = cpr;
}

void WheelSpeedSensor::set_diameter(float diameter)
{
    this->diameter = diameter;
}

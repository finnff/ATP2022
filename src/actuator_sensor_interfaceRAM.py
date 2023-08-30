import random
import json
import time
import redis


import random
import time
import redis

class SpeedSensor:
    def __init__(self, redis_client):
        self.vehicle_speed = 0  # starting speed
        self.redis_client = redis_client

    def read_speed(self):
        self.vehicle_speed = float(self.redis_client.hget("Sensor_Actuator", "WheelSpeedSensorHz") or 0.0)
        return self.vehicle_speed


class RadarDistanceMeter:
    def __init__(self, redis_client):
        self.distance_to_voorligger = 999  # starting distance
        self.redis_client = redis_client

    def read_distance(self):
        self.distance_to_voorligger = float(self.redis_client.hget("Sensor_Actuator", "Front_radar_measurable") or 999.0)
        return self.distance_to_voorligger


class SensorInterface:
    def __init__(self, speed_sensor, RadarDistanceMeter):
        self.speed_sensor = speed_sensor
        self.RadarDistanceMeter = RadarDistanceMeter

    def get_speed(self):
        return self.speed_sensor.read_speed()

    def get_distance(self):
        return self.RadarDistanceMeter.read_distance()


# Actuators

class ActuatorInterface:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def receive_data(self):
        gas_rem_percentage = self.redis_client.hget("actuator_data", "GasRemPedalPosPercentage")
        return float(gas_rem_percentage) if gas_rem_percentage else None

    def set_gas_pedal_force(self, force):
        if 0 <= force <= 100:
            self.redis_client.hset("actuator_data", "GasRemPedalPosPercentage", force)
        else:
            print("Speed must be between 0 and 100.")

    def set_braking_pedal_force(self, force):
        if -100 <= force <= 0:
            self.redis_client.hset("actuator_data", "GasRemPedalPosPercentage", force)
        else:
            print("Force must be between -100 and 0.")


def main():
    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    speed_sensor = SpeedSensor(redis_client)
    radar_distance_meter = RadarDistanceMeter(redis_client)

    sensor_interface = SensorInterface(speed_sensor, radar_distance_meter)
    actuator_interface = ActuatorInterface(redis_client)

    while True:
        current_speed = sensor_interface.get_speed()
        current_distance = sensor_interface.get_distance()

        # Here, replace with your logic to decide gas and braking force
        gas_force = random.randint(0, 100)
        brake_force = random.randint(-100, 0)

        actuator_interface.set_gas_pedal_force(gas_force)
        actuator_interface.set_braking_pedal_force(brake_force)

        print(
            f"Current Speed: {current_speed}, Current Distance: {current_distance}, Gas Force: {gas_force}, Brake Force: {brake_force}"
        )

        time.sleep(1)  # Simulate a time delay


if __name__ == "__main__":
    main()
#
# class SpeedSensor:
#     def __init__(self):
#         self.vehicle_speed = 0  # starting speed
#
#     def read_speed(self):
#         self.vehicle_speed += random.randint(
#             -1, 1
#         )  # Simulate slight changes in vehicle speed.
#         return self.vehicle_speed
#
#
# class RadarDistanceMeter:
#     def __init__(self):
#         self.distance_to_voorligger = 999  # starting distance
#
#     def read_distance(self):
#         self.distance_to_voorligger += random.randint(
#             -1, 1
#         )  # Simulate changes in distance to voorligger.
#         return self.distance_to_voorligger
#
#
# class SensorInterface:
#     def __init__(self, speed_sensor, RadarDistanceMeter):
#         self.speed_sensor = speed_sensor
#         self.RadarDistanceMeter = RadarDistanceMeter
#
#     def get_speed(self):
#         return self.speed_sensor.read_speed()
#
#     def get_distance(self):
#         return self.RadarDistanceMeter.read_distance()
#
#
# # Actuators
#
#
# class ActuatorInterface:
#     def __init__(self):
#         self.redis_client = redis.Redis(host="localhost", port=6379, db=0)
#
#     def receive_data(self):
#         gas_rem_percentage = self.redis_client.hget(
#             "actuator_data", "GasRemPedalPosPercentage"
#         )
#         return float(gas_rem_percentage) if gas_rem_percentage else None
#
#     def set_gas_pedal_force(self, force):
#         if 0 <= force <= 100:
#             self.redis_client.hset("actuator_data", "GasRemPedalPosPercentage", force)
#         else:
#             print("Speed must be between 0 and 100.")
#
#     def set_braking_pedal_force(self, force):
#         if -100 <= force <= 0:
#             self.redis_client.hset("actuator_data", "GasRemPedalPosPercentage", force)
#         else:
#             print("Force must be between -100 and 0.")
#
#
# def main():
#     speed_sensor = SpeedSensor()
#     radar_distance_meter = RadarDistanceMeter()
#
#     sensor_interface = SensorInterface(speed_sensor, radar_distance_meter)
#     actuator_interface = ActuatorInterface()
#
#     while True:
#         current_speed = sensor_interface.get_speed()
#         current_distance = sensor_interface.get_distance()
#
#         # Here, replace with your logic to decide gas and braking force
#         gas_force = random.randint(0, 100)
#         brake_force = random.randint(-100, 0)
#
#         actuator_interface.set_gas_pedal_force(gas_force)
#         actuator_interface.set_braking_pedal_force(brake_force)
#
#         print(
#             f"Current Speed: {current_speed}, Current Distance: {current_distance}, Gas Force: {gas_force}, Brake Force: {brake_force}"
#         )
#
#         time.sleep(1)  # Simulate a time delay
#
#
# if __name__ == "__main__":
#     main()

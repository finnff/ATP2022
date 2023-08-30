import random
import time
import redis


import "cpp/build/libmysensor.so"



sensor = mysensor.SpeedSensor()
speed = sensor.read_speed()
sensor.set_two_floats(1.0, 2.0)


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
        gas_rem_percentage = self.redis_client.hget("Sensor_Actuator", "GasRemPedalPosPercentage")
        return float(gas_rem_percentage) if gas_rem_percentage else None

    def set_gas_pedal_force(self, force):
        if 0 <= force <= 100:
            self.redis_client.hset("Sensor_Actuator", "GasRemPedalPosPercentage", force)
        else:
            print("Speed must be between 0 and 100.")

    def set_braking_pedal_force(self, force):
        if -100 <= force <= 0:
            self.redis_client.hset("Sensor_Actuator", "GasRemPedalPosPercentage", force)
        else:
            print("Force must be between -100 and 0.")


    def set_combined_pedal_force(self, gas_force, brake_force):
        # Logic to pick the stronger force and apply it while canceling the weaker one
        if abs(gas_force) > abs(brake_force):
            self.set_gas_pedal_force(gas_force)
        elif abs(brake_force) > abs(gas_force):
            self.set_braking_pedal_force(brake_force)
        else:  # both forces are equal in magnitude
            self.set_gas_pedal_force(0)      
# def set_combined_pedal_force(self, gas_force, brake_force):
#         # Logic to pick the stronger force and apply it while canceling the weaker one
#         if abs(gas_force) > abs(brake_force):
#             self.set_gas_pedal_force(gas_force)
#             self.set_braking_pedal_force(0)  # Explicitly set to 0
#         elif abs(brake_force) > abs(gas_force):
#             self.set_braking_pedal_force(brake_force)
#             self.set_gas_pedal_force(0)  # Explicitly set to 0
#         else:  # both forces are equal in magnitude
#             self.set_gas_pedal_force(0)
#             self.set_braking_pedal_force(0)
#
class CombinedInterface:
    def __init__(self):
        self.redis_client = redis.Redis(host="localhost", port=6379, db=0)
        self.speed_sensor = SpeedSensor(self.redis_client)
        self.radar_distance_meter = RadarDistanceMeter(self.redis_client)
        self.sensor_interface = SensorInterface(self.speed_sensor, self.radar_distance_meter)
        self.actuator_interface = ActuatorInterface(self.redis_client)
        
    def get_distance(self):
        return self.sensor_interface.get_distance()
    
    def get_speed(self):
        return self.sensor_interface.get_speed()
    
    def set_gas_pedal_force(self, force):
        self.actuator_interface.set_gas_pedal_force(force)
        
    def set_braking_pedal_force(self, force):
        self.actuator_interface.set_braking_pedal_force(force)
        
    def receive_data(self):
        return self.actuator_interface.receive_data()


def main():
    combined_interface = CombinedInterface()

    while True:
        current_speed = combined_interface.get_speed()
        current_distance = combined_interface.get_distance()

        # Here, replace with your logic to decide gas and braking force
        gas_force = random.randint(0, 100)
        brake_force = random.randint(-100, 0)

        combined_interface.actuator_interface.set_combined_pedal_force(gas_force, brake_force)
        resultforce =   combined_interface.actuator_interface.receive_data()

        print(
            f"Current Speed: {current_speed}, Current Distance: {current_distance}, Gas Force: {gas_force}, Brake Force: {brake_force},Result Force: {resultforce}"

        )

        time.sleep(1)  # Simulate a time delay

if __name__ == "__main__":
    main()



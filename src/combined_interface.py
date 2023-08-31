import random
import time
import redis
import re
import subprocess
from CarParamsManager import ext_load_car_from_redis


class dashboard_log_logger:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def extract_numbers_from_log(self, log_text):
        lines = log_text.strip().split("\n")
        for line in lines:
            elapsed_time = re.search(r"Elapsed time: ([\d.]+)", line)
            function_args = re.search(
                r"Function \[control_logic\] arguments were \(([^)]+),?[^)]*\)\)", line
            )
            function_result = re.search(
                r"Function \[control_logic\] result was \(([^)]+)\)", line
            )

            if elapsed_time:
                self.redis_client.hset(
                    "FRPloggedInfo", "Elapsed_time", elapsed_time.group(1)
                )

            if function_args:
                args = function_args.group(1).split(", ")
                for i, arg in enumerate(args):
                    field_name = f"arg{i+1}"
                    self.redis_client.hset("FRPloggedInfo", field_name, arg)

            if function_result:
                result = function_result.group(1).split(", ")
                for i, res in enumerate(result):
                    field_name = f"result{i+1}"
                    self.redis_client.hset("FRPloggedInfo", field_name, res)

    def process_log_file(self, log_file_path):
        tail_command = ["tail", "-n", "5", log_file_path]
        tail_output = subprocess.run(
            tail_command, capture_output=True, text=True
        ).stdout
        self.extract_numbers_from_log(tail_output)


class SpeedSensor:
    def __init__(self, redis_client):
        self.vehicle_speed = 0  # starting speed
        self.redis_client = redis_client

    def read_speed(self):
        self.vehicle_speed = float(
            # self.redis_client.hget("Sensor_Actuator", "WheelSpeedSensorHz") or 0.0
            self.redis_client.hget("sim_state", "true_vehicle_speed")
            or 0.0
        )
        return self.vehicle_speed


class RadarDistanceMeter:
    def __init__(self, redis_client):
        self.distance_to_voorligger = 999  # starting distance
        self.redis_client = redis_client

    def read_distance(self):
        self.distance_to_voorligger = float(
            self.redis_client.hget("Sensor_Actuator", "Front_radar_measurable") or 999.0
        )
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
        gas_rem_percentage = self.redis_client.hget(
            "Sensor_Actuator", "GasRemPedalPosPercentage"
        )
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


class CombinedInterface:
    def __init__(self):
        self.redis_client = redis.Redis(host="localhost", port=6379, db=0)
        self.speed_sensor = SpeedSensor(self.redis_client)
        self.radar_distance_meter = RadarDistanceMeter(self.redis_client)
        self.sensor_interface = SensorInterface(
            self.speed_sensor, self.radar_distance_meter
        )
        self.car_par_sec = -1
        self.car_par_CPR = -1
        self.car_par_Diameter = -1
        self.update_param_every_x_calls = 50
        self.counter = 9999
        self.actuator_interface = ActuatorInterface(self.redis_client)
        self.loglogger = dashboard_log_logger(self.redis_client)

    def GetUpdatedCarParams(self):
        _temp_carpars = ext_load_car_from_redis(self.redis_client)
        self.car_par_sec = _temp_carpars.seconds_distance
        self.car_par_CPR = _temp_carpars.encoder_cpr
        self.car_par_Diameter = _temp_carpars.wheel_diameter

    def get_desiredSeconds(self):
        if self.update_param_every_x_calls < self.counter:
            self.GetUpdatedCarParams()
            self.counter = 0
        self.counter += 1
        return self.car_par_sec

    def updateFRPLogs(self, log_file_name):
        self.loglogger.process_log_file(log_file_name)

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
        print(combined_interface.GetUpdatedCarParams())
        current_speed = combined_interface.get_speed()
        current_distance = combined_interface.get_distance()

        # Here, replace with your logic to decide gas and braking force
        gas_force = random.randint(0, 100)
        brake_force = random.randint(-100, 0)

        combined_interface.actuator_interface.set_combined_pedal_force(
            gas_force, brake_force
        )
        resultforce = combined_interface.actuator_interface.receive_data()

        print(
            f"Current Speed: {current_speed}, Current Distance: {current_distance}, Gas Force: {gas_force}, Brake Force: {brake_force},Result Force: {resultforce}"
        )

        time.sleep(1)  # Simulate a time delay


if __name__ == "__main__":
    main()

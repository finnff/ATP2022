import redis
import os
import random
import time
import json


class CarParams:
    def __init__(
        self,
        param_name,
        max_acceleration,
        max_deceleration,
        wheel_diameter,
        encoder_cpr,
        seconds_distance,
    ):
        self.param_name = param_name
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.wheel_diameter = wheel_diameter
        self.encoder_cpr = encoder_cpr
        self.seconds_distance = seconds_distance


def load_car_from_json(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
        return CarParams(
            data["Param Name"],
            data["Max Acceleration"],
            data["Max Deceleration"],
            data["Wheel Diameter"],
            data["Encoder CPR"],
            data["Seconds Distance"],
        )


def load_all_cars(folder_path):
    Loaded_Car_Parameters = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            Loaded_Car_Parameters.append(load_car_from_json(file_path))
    return Loaded_Car_Parameters


def get_sim_params(redis):
    A = float(redis.hget("RealitySimReplay", "RealityTimeScaleFactor"))
    B = float(redis.hget("RealitySimReplay", "reality_frequency"))
    C = float(redis.hget("RealitySimReplay", "reality_update_frequency"))
    return A, B, C


class Reality:
    def __init__(
        self,
        car_parameters,
        true_vehicle_speed,
        true_distance_to_voorligger,
        true_voorligger_speed,
        true_vehicle_acceleration,
        redis_client,
    ):
        self.car_parameters = car_parameters
        self.true_vehicle_speed = true_vehicle_speed
        self.true_distance_to_voorligger = true_distance_to_voorligger
        self.true_voorligger_speed = true_voorligger_speed
        self.true_vehicle_acceleration = true_vehicle_acceleration
        self.GasRemPedalPosPercentage = 0.0
        self.iteration = 0
        self.time_since_reality_update = 0.11
        self.radar_counter = 0
        self.redis = redis_client
        print(
            f"  myVel  |  myAc  |  diff  |  dist2Voor  | VoorVel | lastPedalPos | Elapsed Time"
        )

       def update_sim_params(self):
        (
            self.realChangeFactor,
            self.reality_frequency,
            self.reality_update_frequency,
        ) = get_sim_params(self.redis)

    def save_state_to_redis(self):
        self.redis.hset(
            "sim_state", "true_distance_to_voorligger", self.true_distance_to_voorligger
        )
        self.redis.hset("sim_state", "true_vehicle_speed", self.true_vehicle_speed)
        self.redis.hset(
            "Sensor_Actuator", "GasRemPedalPosPercentage", self.GasRemPedalPosPercentage
        )

    def load_state_from_redis(self):
        self.true_distance_to_voorligger = float(
            self.redis.hget("sim_state", "true_distance_to_voorligger") or 0.0
        )
        self.true_vehicle_speed = float(
            self.redis.hget("sim_state", "true_vehicle_speed") or 0.0
        )
        self.GasRemPedalPosPercentage = float(
            self.redis.hget("Sensor_Actuator", "GasRemPedalPosPercentage") or 0.0
        )

    def alternate_voorligger_speed(self):
        if self.iteration % 2 == 0:
            self.true_voorligger_speed = 110
        else:
            self.true_voorligger_speed = 80

    def dummyHzWheelSpeedSensor(self):
            1. takes   true_vehicle_speed (in meter per second)(use scaled_elapsed_time)
            takes.self.car_parameters.wheel_diameter

    def bosch_radar_update(self):
        if self.radar_counter >= 500:  # Check if 500ms have passed
            self.radar_counter = 0  # Reset the counter
            if self.true_distance_to_voorligger < 210:
                radar_meas = round(
                    self.true_distance_to_voorligger + random.choice([-0.1, 0, 0.1]), 1
                )
                radar_meas = round(radar_meas / 0.2) * 0.2
                self.redis.hset("Sensor_Actuator", "Front_radar_measurable", radar_meas)
            else:
                self.redis.hset("Sensor_Actuator", "Front_radar_measurable", 999)

    def update(self, elapsed_time, speed_scale_factor=1):
        self.update_sim_params()
        scaled_elapsed_time = elapsed_time * speed_scale_factor
        # Update the radar counter based on scaled time
        self.radar_counter += int(scaled_elapsed_time * 1000)  # convert to ms
        # Increment the time since the last update
        self.time_since_reality_update += scaled_elapsed_time  # Accumulate the time
        # 10ms interval
        if self.time_since_reality_update >= (1 / self.reality_update_frequency):
            self.time_since_reality_update = 0  # Reset the accumulated time
            realChangeFactor = 0.01
            if self.GasRemPedalPosPercentage >= 0:
                realChange = (
                    (self.GasRemPedalPosPercentage / 100)
                    * self.car_parameters.max_acceleration
                    * realChangeFactor
                )
            if self.GasRemPedalPosPercentage < 0:
                realChange = (
                    (self.GasRemPedalPosPercentage / 100)
                    * self.car_parameters.max_deceleration
                    * realChangeFactor
                )
            self.true_vehicle_acceleration += realChange
            self.true_vehicle_speed += self.true_vehicle_acceleration
            relative_speed = self.true_vehicle_speed - self.true_voorligger_speed
            self.true_distance_to_voorligger -= relative_speed
            # piggybacking of radar_counter for 100ms timer
            if self.radar_counter >= 100:
                self.iteration += 1
                self.alternate_voorligger_speed()
                values_line = (
                    f"{self.true_vehicle_speed:.3f}".ljust(9)
                    + f"| {self.true_vehicle_acceleration:.3f}".ljust(9)
                    + f"| {realChange:.3f}".ljust(9)
                    + f"| {self.true_distance_to_voorligger:.3f}".ljust(9)
                    + f"| {self.true_voorligger_speed:.3f}".ljust(9)
                    + f"| {self.GasRemPedalPosPercentage:.3f}".ljust(9)
                    + f"| {elapsed_time:.3f}".ljust(9)
                )
                print(values_line, end="\r")
            self.bosch_radar_update()
        else:
            self.time_since_reality_update += elapsed_time  # ?


if __name__ == "__main__":
    redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)

    speed_scale_factor, reality_frequency, reality_update_frequency = get_sim_params(
        redis_client
    )

    Loaded_Car_Parameters = load_all_cars("./car_constants")
    print(f"Loaded car parameters for: {[i.param_name for i in Loaded_Car_Parameters]}")
    default_car_param = Loaded_Car_Parameters[0] if Loaded_Car_Parameters else None

    if default_car_param:
        reality = Reality(default_car_param, 100, 2000, 100, 1, redis_client)
        last_update_time = time.time()

        while True:
            start_time = time.time()
            reality.load_state_from_redis()

            elapsed_time = (time.time() - start_time) * reality_frequency
            last_update_time = start_time

            reality.update(elapsed_time)
            reality.save_state_to_redis()

            sleep_duration = max(
                0, 1 / reality_frequency - elapsed_time
            )  # Ensure a cycle as per reality_frequency
            time.sleep(sleep_duration)

    else:
        print("No car parameters loaded. Exiting.")
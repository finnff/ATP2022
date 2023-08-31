import sys
import redis
import random
import math
import time
import select  # This is to check for user input within the 5-second window

from inputReality import InputReality  # Import the InputReality class
from CarParamsManager import CarParamsManager


MAX_VEHICLE_SPEED = 100
MIN_VEHICLE_SPEED = 2
MAX_VOORLIGGER_SPEED = 100
MIN_VOORLIGGER_SPEED = 0
MAX_VEHICLE_ACCELERATION = 153
MIN_VEHICLE_ACCELERATION = -10
MAX_TIME_BETWEEN = 15


def get_sim_params(redis):
    A = float(redis.hget("RealitySimReplay", "RealityTimeScaleFactor") or -1.0)
    B = float(redis.hget("RealitySimReplay", "reality_frequency") or -1.0)
    C = float(redis.hget("RealitySimReplay", "reality_update_frequency") or -1.0)
    if int(redis.hget("RealitySimReplay", "RESET_FLAG") or 0):
        redis.hset("RealitySimReplay", "CRASHED_FLAG", 0)
        print("\n\n RESET_FLAG: re-initializing...\n")
        reality.initialize()
        reality.update(0)
    return A, B, C


class Reality:
    def __init__(self, carmanager, redis_client):
        self.redis = redis_client
        self.reality_input = InputReality(redis_client)
        self.car_manager = carmanager
        self.initialize()

    def initialize(self):
        self.GasRemPedalPosPercentage = 0.0
        self.iteration = 0
        self.time_since_reality_update = 0.01
        self.radar_counter = 0
        self.simulation_start_time = time.time()

        self.load_state_from_redis()
        self.update_sim_params()
        self.update_car_params()

        # Check if values are all zero (rare case)
        if all(
            val <= 0
            for val in [
                self.true_distance_to_voorligger,
                self.true_vehicle_speed,
                self.true_voorligger_speed,
            ]
        ) or int(self.redis.hget("RealitySimReplay", "RESET_FLAG")):
            print("Warning: All Redis values were zero. Setting to preset values.")
            (
                self.true_distance_to_voorligger,
                self.true_vehicle_speed,
                self.true_voorligger_speed,
                self.true_vehicle_acceleration,
            ) = [10, 10, 10, 0.3]
        print(
            "Running sim with sim param: ",
            self.RealityTimeScaleFactor,
            self.reality_frequency,
            self.reality_update_frequency,
        )
        print(self.car_parameters)
        print("\n\n\n")
        self.redis.hset("RealitySimReplay", "RESET_FLAG", 0)
        print(
            f"  myVel  |  myAc  |lastPedal%|  diff  | t2voor | dist2Voor| VelVoo | loopHz"
        )

    #######################################
    def update_car_params(self):
        self.car_parameters = self.car_manager.load_car_from_redis()

    def update_sim_params(self):
        try:
            (
                self.RealityTimeScaleFactor,
                self.reality_frequency,
                self.reality_update_frequency,
            ) = get_sim_params(self.redis)
        except Exception as e:
            print(
                f"Warning: Exception {e} encountered while updating sim params. Setting to default values."
            )
            self.RealityTimeScaleFactor = 1
            self.reality_frequency = 10
            self.reality_update_frequency = 1

    def load_state_from_redis(self):
        try:
            self.true_distance_to_voorligger = float(
                self.redis.hget("sim_state", "true_distance_to_voorligger") or 0.0
            )
            self.true_vehicle_speed = float(
                self.redis.hget("sim_state", "true_vehicle_speed") or 0.0
            )
            self.true_voorligger_speed = float(
                self.redis.hget("sim_state", "true_voorligger_speed") or 0.0
            )
            self.true_vehicle_acceleration = float(
                self.redis.hget("sim_state", "true_vehicle_acceleration") or 0.0
            )
            self.GasRemPedalPosPercentage = float(
                self.redis.hget("Sensor_Actuator", "GasRemPedalPosPercentage") or 0.0
            )
        except TypeError:
            print(
                "Warning: TypeError encountered while loading from Redis. Setting all values to 0."
            )
            self.true_distance_to_voorligger = 0.0
            self.true_vehicle_speed = 0.0
            self.true_voorligger_speed = 0.0
            self.true_vehicle_acceleration = 0.0

    def save_state_to_redis(self):
        self.redis.hset(
            "sim_state", "true_distance_to_voorligger", self.true_distance_to_voorligger
        )
        self.redis.hset("sim_state", "true_vehicle_speed", self.true_vehicle_speed)
        self.redis.hset(
            "sim_state", "true_voorligger_speed", self.true_voorligger_speed
        )
        self.redis.hset(
            "sim_state", "true_vehicle_acceleration", self.true_vehicle_acceleration
        )
        self.redis.hset("RealitySimReplay", "realityHZ", 1 / (time.time() - start_time))

    def dummyHzWheelSpeedSensor(self, scaled_elapsed_time):
        # Step 1: Get true_vehicle_speed in meters per second
        speed_mps = self.true_vehicle_speed
        # Step 2: Calculate wheel circumference in meters
        wheel_circumference = math.pi * self.car_parameters.wheel_diameter
        # Step 3: Calculate rotations per scaled time unit
        rotations_per_time_unit = (
            speed_mps * scaled_elapsed_time
        ) / wheel_circumference
        # Step 4: Calculate encoder pulses per time unit
        encoder_pulses_per_time_unit = (
            rotations_per_time_unit * self.car_parameters.encoder_cpr
        )
        # Step 5: Convert this to Hz (pulses per second)
        encoder_pulses_per_second = encoder_pulses_per_time_unit / scaled_elapsed_time
        encoder_pulses_per_second *= 1 + random.choice(
            [-0.003, 0.003]
        )  # Add random choice of +- 0.3%
        # Step 6: Save to Redis
        self.redis.hset(
            "Sensor_Actuator", "WheelSpeedSensorHz", encoder_pulses_per_second
        )
        # Create f-string explaining the math and send that to Redis
        explanation = (
            f"Speed (m/s): {speed_mps}, "
            f"Wheel Diameter (m): {self.car_parameters.wheel_diameter}, "
            f"Wheel Circumference (m): {wheel_circumference}, "
            f"Rotations/Time Unit: {rotations_per_time_unit}, "
            f"Encoder Pulses/Time Unit: {encoder_pulses_per_time_unit}, "
            f"Encoder Pulses/s (Hz): {encoder_pulses_per_second}"
        )
        # print(explanation)

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

    def check_crashed(self):
        if self.true_distance_to_voorligger < 0:
            return True

        # Calculate the time to cover the distance at the current speed.
        # Avoid division by zero.
        if self.true_vehicle_speed != 0:
            time_to_reach = self.true_distance_to_voorligger / self.true_vehicle_speed
            if time_to_reach > MAX_TIME_BETWEEN:
                return True

        return False

    def log_crash_info(self):
        # Check if fresh_dump exists and is 0
        fresh_dump = self.redis.hget("RealitySimReplay", "fresh_dump")
        if fresh_dump is not None and int(fresh_dump) != 0:
            return  # Return early if fresh_dump is not 0
        print("\n ---CRASHED----\n")

        crash_reasons = []

        if self.true_distance_to_voorligger < 0:
            crash_reasons.append("!!!! Negative distance to voorligger")

        if self.true_vehicle_speed != 0:
            time_to_reach = self.true_distance_to_voorligger / self.true_vehicle_speed
            if time_to_reach > MAX_TIME_BETWEEN:
                crash_reasons.append(
                    f"!!!! Time to reach {time_to_reach} voorligger exceeds {MAX_TIME_BETWEEN} seconds"
                )

        duration = time.time() - self.simulation_start_time
        print(f"Crash detected after {duration:.2f} seconds of simulation.")
        print(f"State at time of crash:")

        # Log crash info in Redis and print
        crash_data = {
            "true_distance_to_voorligger": self.true_distance_to_voorligger,
            "true_vehicle_speed": self.true_vehicle_speed,
            "true_voorligger_speed": self.true_voorligger_speed,
            "true_vehicle_acceleration": self.true_vehicle_acceleration,
            "crash_reasons": ", ".join(crash_reasons),
        }
        for key, value in crash_data.items():
            self.redis.hset("crash_info", key, value)
            print(f"  {key}: {value}")

    def update(self, elapsed_time, speed_scale_factor=1):
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
                self.update_sim_params()
                self.update_car_params()
                values_line = (
                    f"{self.true_vehicle_speed:.3f}".ljust(9)
                    + f"| {self.true_vehicle_acceleration:.3f}".ljust(9)
                    + f"| {realChange:.3f}".ljust(9)
                    + f"| {self.GasRemPedalPosPercentage:.1f}".ljust(9)
                    + f"| {self.true_distance_to_voorligger/self.true_vehicle_speed:.2f}".ljust(
                        9
                    )
                    + f"| {self.true_distance_to_voorligger:.2f}".ljust(9)
                    + f"| {self.true_voorligger_speed:.3f}".ljust(9)
                    + f"| {1 / (time.time() - start_time):1f}".ljust(5)
                )
                print(values_line, end="\r")
            self.bosch_radar_update()
            self.dummyHzWheelSpeedSensor(scaled_elapsed_time)

            self.true_vehicle_speed = max(
                min(self.true_vehicle_speed, MAX_VEHICLE_SPEED), MIN_VEHICLE_SPEED
            )
            self.true_voorligger_speed = max(
                min(self.true_voorligger_speed, MAX_VOORLIGGER_SPEED),
                MIN_VOORLIGGER_SPEED,
            )
            self.true_vehicle_acceleration = max(
                min(self.true_vehicle_acceleration, MAX_VEHICLE_ACCELERATION),
                MIN_VEHICLE_ACCELERATION,
            )

            # Check crash condition
            if self.check_crashed():
                self.log_crash_info()  # Log crash info only if fresh_dump is 0
                self.redis.hset(
                    "RealitySimReplay", "CRASHED_FLAG", 1
                )  # Set CRASHED_FLAG
                # Wait until fresh_dump is 0
                while True:
                    fresh_dump = int(
                        self.redis.hget("RealitySimReplay", "fresh_dump") or 0
                    )
                    if fresh_dump == 0:
                        break
                    print("Waiting for fresh_dump to be reset...", end="\r")
                    time.sleep(1)


if __name__ == "__main__":
    redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)

    input_reality = InputReality(redis_client)

    carmanager = CarParamsManager("../car_constants", param_no_to_set=0)
    loaded_cars = carmanager.load_all_cars()
    print(f"Loaded car parameters for: {[car.param_name for car in loaded_cars]}")

    reality = Reality(carmanager, redis_client)

    (
        speed_scale_factor,
        reality_frequency,
        reality_update_frequency,
    ) = get_sim_params(redis_client)

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

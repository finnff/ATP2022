import redis
import random
import math
import time

from car_parameters import car_parameters


def set_sim_params(redis, speed=1.0, frequency=100, update_frequency=1.0):
    redis.hset("RealitySimReplay", "RealityTimeScaleFactor", speed)
    redis.hset("RealitySimReplay", "reality_frequency", frequency)
    redis.hset("RealitySimReplay", "reality_update_frequency", update_frequency)


def get_sim_params(redis):
    A = float(redis.hget("RealitySimReplay", "RealityTimeScaleFactor") or -1.0)
    B = float(redis.hget("RealitySimReplay", "reality_frequency") or -1.0)
    C = float(redis.hget("RealitySimReplay", "reality_update_frequency") or -1.0)
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
        print(self.car_parameters)
        self.true_vehicle_speed = true_vehicle_speed
        self.true_distance_to_voorligger = true_distance_to_voorligger
        self.true_voorligger_speed = true_voorligger_speed
        self.true_vehicle_acceleration = true_vehicle_acceleration
        self.GasRemPedalPosPercentage = 0.0
        self.iteration = 0
        self.time_since_reality_update = 0.01
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
            "sim_state", "true_voorligger_speed", self.true_voorligger_speed
        )
        self.redis.hset(
            "sim_state", "true_vehicle_acceleration", self.true_vehicle_acceleration
        )
        self.redis.hset("RealitySimReplay", "realityHZ", 1 / (time.time() - start_time))

    def load_state_from_redis(self):
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

    def alternate_voorligger_speed(self):
        if self.iteration % 2 == 0:
            self.true_voorligger_speed = 110
        else:
            self.true_voorligger_speed = 90

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
            self.dummyHzWheelSpeedSensor(scaled_elapsed_time)
        else:
            self.time_since_reality_update += elapsed_time  # ?


if __name__ == "__main__":
    redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)

    set_sim_params(redis_client, speed=1.00, frequency=100.00, update_frequency=1.00)
    Loaded_Car_Parameters = load_all_cars("./car_constants")
    print(f"Loaded car parameters for: {[i.param_name for i in Loaded_Car_Parameters]}")
    reality = Reality(Loaded_Car_Parameters[0], 100, 2000, 100, 0, redis_client)
    time.sleep(10)
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

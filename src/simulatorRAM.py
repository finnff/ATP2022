import redis
import time
import json


class CarParams:
    def __init__(
        self,
        parameter_file_name,
        max_acceleration,
        max_deceleration,
        wheel_diameter,
        encoder_CPR,
        seconds_distance,
    ):
        self.parmeter_file_name = parameter_file_name
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.wheel_diameter = wheel_diameter
        self.encoder_CPR = encoder_CPR
        self.seconds_distance = seconds_distance

    def __str__(self):
        return (
            f"\nCar Parameters for {self.parmeter_file_name}:\n"
            f"Max Acceleration: {self.max_acceleration}\n"
            f"Max Deceleration: {self.max_deceleration}\n"
            f"Wheel Diameter: {self.wheel_diameter}\n"
            f"Encoder CPR: {self.encoder_CPR}\n"
            f"Seconds Distance: {self.seconds_distance}"
        )


def load_car_from_json(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
        return CarParams(
            file_path,
            data["Max Acceleration"],
            data["Max Deceleration"],
            data["Wheel Diameter"],
            data["Encoder CPR"],
            data["Seconds Distance"],
        )


car_hatchback = load_car_from_json("./car_constants/hatchback.json")
car_suv = load_car_from_json("./car_constants/suv.json")
car_ferrari = load_car_from_json("./car_constants/ferrari.json")


class True_Sim_Values:
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
        print(f"Starting Sim..... loaded car Parameters --- {self.car_parameters} \n")
        self.true_vehicle_speed = true_vehicle_speed
        self.true_distance_to_voorligger = true_distance_to_voorligger
        self.true_voorligger_speed = true_voorligger_speed
        self.true_vehicle_acceleration = true_vehicle_acceleration
        self.GasRemPedalPosPercentage = 0.0
        self.iteration = 0
        self.redis = redis_client
        print(f"  myVel  |  myAc  |  diff  |  dist2Voor  | VoorVel | lastPedalPos")

    def save_state_to_redis(self):
        self.redis.hset(
            "sim_state", "true_distance_to_voorligger", self.true_distance_to_voorligger
        )
        self.redis.hset("sim_state", "true_vehicle_speed", self.true_vehicle_speed)
        self.redis.hset(
            "sim_state", "GasRemPedalPosPercentage", self.GasRemPedalPosPercentage
        )

    def load_state_from_redis(self):
        self.true_distance_to_voorligger = float(
            self.redis.hget("sim_state", "true_distance_to_voorligger") or 0.0
        )
        self.true_vehicle_speed = float(
            self.redis.hget("sim_state", "true_vehicle_speed") or 0.0
        )
        self.GasRemPedalPosPercentage = float(
            self.redis.hget("sim_state", "GasRemPedalPosPercentage") or 0.0
        )

    #
    # def save_state_to_redis(self):
    #     state = {
    #         "true_distance_to_voorligger": self.true_distance_to_voorligger,
    #         "true_vehicle_speed": self.true_vehicle_speed,
    #         "GasRemPedalPosPercentage": self.GasRemPedalPosPercentage,
    #     }
    #     self.redis.hset("sim_state", state)
    #
    # def load_state_from_redis(self):
    #     state = self.redis.hgetall("sim_state")
    #     if state:
    #         self.GasRemPedalPosPercentage = float(
    #             state.get(b"GasRemPedalPosPercentage", 0)
    #         )

    def alternate_voorligger_speed(self):  # for now before we load voorligger profile
        if self.iteration % 2 == 0:  # Alternating behavior every other iteration
            self.true_voorligger_speed = 110
        else:
            self.true_voorligger_speed = 80

    def update(self):
        if self.GasRemPedalPosPercentage >= 0:
            realChange = (
                self.GasRemPedalPosPercentage / 100
            ) * self.car_parameters.max_acceleration
            self.true_vehicle_acceleration += realChange
            self.true_vehicle_speed += self.true_vehicle_acceleration
        if self.GasRemPedalPosPercentage < 0:
            realChange = (
                self.GasRemPedalPosPercentage / 100
            ) * self.car_parameters.max_deceleration
            self.true_vehicle_acceleration -= realChange
            self.true_vehicle_speed += self.true_vehicle_acceleration

        values_line2 = f"{self.true_vehicle_speed:.3f}, {self.true_vehicle_acceleration:.3f}, {realChange:.3f}, {self.true_distance_to_voorligger:.3f}, {self.true_voorligger_speed:.3f}, {self.GasRemPedalPosPercentage:.3f}"
        values_line = (
            f"{self.true_vehicle_speed:.3f}".ljust(9)
            + f"| {self.true_vehicle_acceleration:.3f}".ljust(9)
            + f"| {realChange:.3f}".ljust(9)
            + f"| {self.true_distance_to_voorligger:.3f}".ljust(9)
            + f"| {self.true_voorligger_speed:.3f}".ljust(9)
            + f"| {self.GasRemPedalPosPercentage:.3f}".ljust(9)
        )
        print(values_line, end="\r")
        self.alternate_voorligger_speed()
        self.iteration += 1  # Increment the iteration after each update
        # print(f" myV: {self.true_vehicle_speed:.3f}, myAc: {self.true_vehicle_acceleration:.3f} (diff: {realChange:.3f}), dist2Voo: {self.true_distance_to_voorligger:.3f}, speedVoo: {self.true_voorligger_speed:.3f}")
        # Adjust the distance to the voorligger based on relative speed:
        relative_speed = self.true_vehicle_speed - self.true_voorligger_speed
        self.true_distance_to_voorligger -= relative_speed

    # ... (rest of your methods like `update`, `alternate_voorligger_speed`, etc. remain unchanged)


if __name__ == "__main__":
    # Initialize Redis client
    redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)

    # car_hatchback = YourCarParametersHere (Initialize it before this line)
    reality = True_Sim_Values(car_hatchback, 100, 2000, 100, 1, redis_client)

    TIME_STEP = 0.1  # Example time step value of 0.1 seconds.

    while True:
        start_time = time.time()

        # Load the latest state from Redis
        reality.load_state_from_redis()

        # Update the simulation
        reality.update()

        # Save the updated state to Redis
        reality.save_state_to_redis()

        # Sleep to ensure that we're not updating faster than our TIME_STEP.
        elapsed_time = time.time() - start_time
        sleep_duration = max(0, TIME_STEP - elapsed_time)
        time.sleep(sleep_duration)

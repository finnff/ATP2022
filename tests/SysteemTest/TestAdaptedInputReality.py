import redis
import time
import logging
import numpy as np

import random

# import CarParamsManager

default_values = {
    "RealitySimReplay": {
        "RealityTimeScaleFactor": "1.0",
        "reality_frequency": "100.0",
        "reality_update_frequency": "1.0",
    },
    "Sensor_Actuator": {
        "GasRemPedalPosPercentage": "0.0",
        "Front_radar_measurable": "0.0",
        "WheelSpeedSensorHz": "0.0",
    },
    "sim_state": {
        "true_distance_to_voorligger": "100.0",
        "true_vehicle_speed": "10.0",
        "true_voorligger_speed": "10.0",
        "true_vehicle_acceleration": "0.0",
    },
}


def reset_valuesnosc(r):
    for _ in range(3):  # Three times in a row
        for key in ["RealitySimReplay", "Sensor_Actuator", "sim_state"]:
            r.hset(name=key, mapping=default_values[key])


def reverse_poison_random(min_val, max_val):
    scale = (max_val - min_val) / 2
    skewed_value = np.random.exponential(scale)
    return max(min_val, max_val - skewed_value)


def generate_valid_test_cases(num_cases=10):
    # Constants
    MAX_VEHICLE_SPEED = CarParamsManager.load_car_from_redis.true_vehicle_speed
    MIN_VEHICLE_SPEED = 0.1
    MAX_VOORLIGGER_SPEED = 15
    MIN_VOORLIGGER_SPEED = 0.1
    MAX_VEHICLE_ACCELERATION = (
        CarParamsManager.load_car_from_redis.MAX_VEHICLE_ACCELERATION
    )
    MIN_VEHICLE_ACCELERATION = (
        CarParamsManager.load_car_from_redis.MAX_VEHICLE_ACCELERATION
    )

    generated_test_cases = []

    for _ in range(num_cases):
        # Generate valid starting conditions
        myVel = round(reverse_poison_random(MIN_VEHICLE_SPEED, MAX_VEHICLE_SPEED), 2)
        myAcc = round(
            reverse_poison_random(MIN_VEHICLE_ACCELERATION, MAX_VEHICLE_ACCELERATION),
            2,
        )
        voVel = round(
            reverse_poison_random(MIN_VOORLIGGER_SPEED, MAX_VOORLIGGER_SPEED), 2
        )
        dist2vo = round(reverse_poison_random(10, 500), 2)

        start_conditions = [myVel, myAcc, voVel, dist2vo]

        # Generate valid actions
        num_actions = random.randint(1, 7)  # assuming we want between 1 and 5 actions
        actions = []
        total_pause_time = 0

        for _ in range(num_actions):
            action_type = random.choice(["mV", "mAX", "vV"])

            value = random.uniform(
                MIN_VEHICLE_SPEED
                if action_type in ["mV", "vV"]
                else MIN_VEHICLE_ACCELERATION,
                MAX_VEHICLE_SPEED
                if action_type in ["mV", "vV"]
                else MAX_VEHICLE_ACCELERATION,
            )
            actions.append(f"{action_type}={value:.2f}")

            # Insert a pause action after each other action
            pause_time = reverse_poison_random(
                1, 5
            )  # assuming pause times between 1 and 5 seconds
            total_pause_time += pause_time
            actions.append(f"p={pause_time:.2f}")

        if total_pause_time <= 30:
            actions += ["cc", "R"]  # Add checkCrashed and reset at the end
            generated_test_cases.append((start_conditions, actions))
            print(total_pause_time, (start_conditions, actions))

    return generated_test_cases


class InputReality:
    def __init__(self, redis_client):
        self.redis = redis_client

    def save_state_to_redis(self, key, value, overrideStateHash="sim_state"):
        self.redis.hset(overrideStateHash, key, value)

    def load_state_from_redis(self, key, overrideStateHash="sim_state"):
        return float(self.redis.hget(overrideStateHash, key) or 0.0)

    def set_starting_conditions(self, myVel=25.0, myAcc=0.0, voVel=20.0, dist2vo=300.0):
        self.save_state_to_redis("true_vehicle_speed", myVel)
        self.save_state_to_redis("true_vehicle_acceleration", myAcc)
        self.save_state_to_redis("true_voorligger_speed ", voVel)
        self.save_state_to_redis("true_distance_to_voorligger", dist2vo)

    def reset(self):
        self.redis.hset("RealitySimReplay", "RESET_FLAG", 1)  # initialize()

    def checkCrashed(self):
        return bool(
            self.load_state_from_redis(
                "CRASHED_FLAG", overrideStateHash="RealitySimReplay"
            )
        )


def run_test_case(start_conditions, test_case, input_reality, redis_client):
    print(
        f"Starting test case with conditions: {start_conditions}, actions: {test_case}"
    )

    total_pause_time = sum(
        float(action.split("=")[1]) for action in test_case if action.startswith("p")
    )
    print(f"Total pause time: {total_pause_time} seconds")

    if total_pause_time > 30:
        print("Total pause time exceeds 30 seconds. Skipping this test case.")
        return 1

    myVel, myAcc, voVel, dist2vo = start_conditions
    input_reality.set_starting_conditions(
        myVel=myVel, myAcc=myAcc, voVel=voVel, dist2vo=dist2vo
    )

    redis_client.hset("RealitySimReplay", "CRASHED_FLAG", "0")
    redis_client.hset("RealitySimReplay", "RESET_FLAG", "0")

    sum_ps = 0  # Initialize sum of pauses
    last_key = None  # Initialize the last key used
    last_value = None  # Initialize the last value used

    for action in test_case:
        if input_reality.checkCrashed():
            return 1  # Return 1 immediately if a crash is detected

        cmd, *args = action.split("=")
        if cmd == "p":
            time_to_pause = float(args[0])
            sum_ps += time_to_pause  # Update sum of pauses
            time.sleep(time_to_pause)
        elif cmd in ["mV", "mAX", "vV", "d2v"]:
            input_reality.save_state_to_redis(cmd, float(args[0]))
            last_key = cmd  # Record the last key used
            last_value = float(args[0])  # Record the last value used
        elif cmd == "cc":
            if input_reality.checkCrashed():
                return 1
        elif cmd == "R":
            input_reality.reset()
        elif cmd == "+=":
            if last_key:
                last_value += float(args[0])
                input_reality.save_state_to_redis(last_key, last_value)
        elif cmd == "-=":
            if last_key:
                last_value -= float(args[0])
                input_reality.save_state_to_redis(last_key, last_value)

    return 0  # Returns 0 if it reaches this point without crashing


def get_crash_info(redis_client):
    # Fetch all keys and values from the "crash_info" hash map in Redis
    crash_info_raw = redis_client.hgetall("crash_info")

    # Decode byte strings to UTF-8 and convert them to a Python dictionary
    crash_info = {
        k.decode("utf-8"): v.decode("utf-8") for k, v in crash_info_raw.items()
    }

    # You may need to convert numerical values back to floats or integers, if needed
    for key in [
        "true_distance_to_voorligger",
        "true_vehicle_speed",
        "true_voorligger_speed",
        "true_vehicle_acceleration",
    ]:
        crash_info[key] = float(crash_info[key])

    # Now, crash_info is a dictionary containing all the logged crash information
    return crash_info


# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[logging.FileHandler("random_test_cases.log"), logging.StreamHandler()],
)

if __name__ == "__main__":
    redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
    input_reality = InputReality(redis_client)

    carmanager = CarParamsManager("../car_constants", param_no_to_set=0)
    loaded_cars = carmanager.load_all_cars()

    for car in loaded_cars:
        list_of_test_cases = generate_valid_test_cases()

        pass_list = []
        fail_list = []

        for start_conditions, case in list_of_test_cases:
            sum_ps = 0
            start_time = time.time()
            result = run_test_case(start_conditions, case, input_reality, redis_client)
            end_time = time.time()
            elapsed_time = end_time - start_time

            if result == 1:
                # Check if crash information is available
                crashed_flag = int(
                    redis_client.hget("RealitySimReplay", "CRASHED_FLAG") or 0
                )
                if crashed_flag:
                    # Read crash information and append to fail_list
                    crash_info = get_crash_info(redis_client)
                    fail_list.append((elapsed_time, sum_ps, case, crash_info))
                    redis_client.hset("RealitySimReplay", "CRASHED_FLAG", "0")
                    redis_client.hset("RealitySimReplay", "RESET_FLAG", "1")

                    logging.error(
                        f"Test case failed. Elapsed time: {elapsed_time}, Sum of pauses: {sum_ps}, Test case: {case}, Crash Info: {crash_info}"
                    )
                else:
                    fail_list.append((elapsed_time, sum_ps, case))

                    logging.error(
                        f"Test case failed. Elapsed time: {elapsed_time}, Sum of pauses: {sum_ps}, Test case: {case}"
                    )
            else:
                pass_list.append((elapsed_time, sum_ps, case))
                redis_client.hset("RealitySimReplay", "RESET_FLAG", "1")

                logging.info(
                    f"Test case passed. Elapsed time: {elapsed_time}, Sum of pauses: {sum_ps}, Test case: {case}"
                )

        logging.info(
            f"Failed cases: {len(fail_list)}, / {len(fail_list) + len(pass_list)}"
        )
        logging.info(
            f"Passed cases: {len(pass_list)}, / {len(fail_list) + len(pass_list)}"
        )

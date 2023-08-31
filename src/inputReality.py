from os import walk
import redis
import time
import json


#
# import CarParamsManager
#     carmanager = CarParamsManager("../car_constants", param_no_to_set=0)
#     loaded_cars = carmanager.load_all_cars()


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
        self.save_state_to_redis("true_voorligger_speed", voVel)
        self.save_state_to_redis("true_distance_to_voorligger", dist2vo)

    def reset(self):
        self.redis.hset("RealitySimReplay", "RESET_FLAG", 1)  # initialize()
        self.redis.hset("RealitySimReplay", "CRASHED_FLAG", 0)  # Reset the crash flag

    def checkCrashed(self):
        return bool(
            self.load_state_from_redis(
                "CRASHED_FLAG", overrideStateHash="RealitySimReplay"
            )
        )


if __name__ == "__main__":
    redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
    input_reality = InputReality(redis_client)
    counterfailed = 0
    counterPassed = 0

    # while not input_reality.checkCrashed():
    print("\n-----------starting test run---------\n")
    while True:
        # Set initial conditions: car is standing still and there is a stationary vehicle 100 meters ahead
        input_reality.set_starting_conditions(myVel=10, myAcc=0.0, voVel=11, dist2vo=50)
        while True:
            input_reality.save_state_to_redis("true_voorligger_speed", 11)
            time.sleep(2)  # Wait 5 seconds
            input_reality.save_state_to_redis("true_voorligger_speed", 9)
            time.sleep(2)  # Wait 5 seconds
        # time.sleep(5)  # Allow the simulation to run for 5 seconds
        # input_reality.save_state_to_redis("true_vehicle_acceleration", 3)
        # time.sleep(5)  # Wait 5 seconds
        # input_reality.save_state_to_redis("true_vehicle_acceleration", -3)
        # time.sleep(5)  # Wait 5 seconds
        # Suddenly accelerate to 30 m/s
        #

    # input_reality.reset()

#
# counterfailed = 0
# counterPassed = 0
#
# while not input_reality.checkCrashed():
#     print("\n-----------starting test run---------\n")
#     input_reality.set_starting_condtions(myVel=25, myAcc=1, voVel=30, dist2vo=300)
#     time.sleep(5)
#     input_reality.save_state_to_redis("true_vehicle_speed", 16)
#     time.sleep(3)
#     input_reality.save_state_to_redis(
#         "true_distance_to_voorligger",
#         (input_reality.load_state_from_redis("true_distance_to_voorligger") + 1000),
#     )
#     input_reality.save_state_to_redis("true_vehicle_speed", 50)
#     time.sleep(5)
#     ## eval testrun
#     if input_reality.checkCrashed():
#         counterfailed += 1
#     else:
#         counterPasse += 1
#     input_reality.reset()

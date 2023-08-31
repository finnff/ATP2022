import wsp_mod  # The shared object you built
import redis
import time

import sys

sys.path.append("../src/")  # OR SO LIB WONT LOAD
from CarParamsManager import (
    ext_load_car_from_redis,
    load_car_from_json,
    save_car_to_redis,
)


class SpeedSensor:
    def __init__(self):
        self.wss = wsp_mod.WheelSpeedSensor()

    def read_speed(self):
        start_time = time.time()
        speed = self.wss.read_speed()
        elapsed_time = time.time() - start_time
        return speed, elapsed_time

    def set_CPR(self, CPR):
        self.wss.set_cpr(CPR)  # Set CPR in the C++ object

    def set_diameter(self, diameter):
        self.wss.set_diameter(diameter)  # Set diameter in the C++ object


class TestMeasuredSpeedCalculator:
    def __init__(self):
        self.setUp()

    def setUp(self):
        self.redis_client = redis.Redis(host="localhost", port=6379, db=0)
        save_car_to_redis(self.redis_client, load_car_from_json(CAR_LIST_ITERATOR))
        newCarPar = ext_load_car_from_redis(self.redis_client)

        self.speed_sensor = (
            SpeedSensor()
        )  # get loaded values and set them inside the CPP binding directly
        self.speed_sensor.set_CPR(newCarPar.encoder_cpr)
        self.speed_sensor.set_diameter(newCarPar.wheel_diameter)
        self.margin_of_error = 0.02

    def fetch_redis_data(self, key, field):
        return float(self.redis_client.hget(key, field))

    def set_redis_data(self, key, field, value):
        self.redis_client.hset(key, field, value)

    def test_speed_calculation(self, iteration):
        if not self.redis_client.hget(
            "RealitySimReplay", "RESET_FLAG"
        ) or not self.redis_client.hget("RealitySimReplay", "CRASHED_FLAG"):
            return

        true_vehicle_speed = self.fetch_redis_data("sim_state", "true_vehicle_speed")
        calculated_speed, elapsed_time = self.speed_sensor.read_speed()

        delta = abs(true_vehicle_speed - calculated_speed)
        delta_percentage = delta / true_vehicle_speed

        self.set_redis_data(
            f"TestResults:{iteration}", "CalculatedSpeed", calculated_speed
        )
        self.set_redis_data(
            f"TestResults:{iteration}", "TrueVehicleSpeed", true_vehicle_speed
        )
        self.set_redis_data(f"TestResults:{iteration}", "ElapsedTime", elapsed_time)

        print(
            f"True Speed: {true_vehicle_speed}, Calculated Speed: {calculated_speed}, Delta: {delta}, Delta %: {delta_percentage * 100}, Elapsed Time: {elapsed_time}, 1/Elapsed Time: {1/elapsed_time}"
        )

        if delta_percentage > self.margin_of_error:
            print(f"Error: Delta % is higher than acceptable margin of error.")


def clear_redis_data(redis_client):
    # Clear the Redis hashes
    for i in range(100):
        redis_client.delete(f"TestResults:{i}")


def perform_unit_test_on_aggregated_data():
    redis_client = redis.Redis(host="localhost", port=6379, db=0)

    # Initialize variables to store aggregated data
    total_calculated_speed = 0
    total_true_speed = 0
    total_elapsed_time = 0

    for i in range(100):
        calculated_speed = float(
            redis_client.hget(f"TestResults:{i}", "CalculatedSpeed")
        )
        true_speed = float(redis_client.hget(f"TestResults:{i}", "TrueVehicleSpeed"))
        elapsed_time = float(redis_client.hget(f"TestResults:{i}", "ElapsedTime"))

        total_calculated_speed += calculated_speed
        total_true_speed += true_speed
        total_elapsed_time += elapsed_time

    average_calculated_speed = total_calculated_speed / 100
    average_true_speed = total_true_speed / 100
    average_elapsed_time = total_elapsed_time / 100

    TestResultsList.append(
        f"Average Calculated Speed: {average_calculated_speed}, Average True Speed: {average_true_speed}, Average Elapsed Time: {average_elapsed_time}"
    )
    print(
        f"Average Calculated Speed: {average_calculated_speed}, Average True Speed: {average_true_speed}, Average Elapsed Time: {average_elapsed_time}"
    )


if __name__ == "__main__":
    TestResultsList = []
    car_list = [
        "../car_constants/suv.json",
        "../car_constants/ferrari.json",
        "../car_constants/hatchback.json",
    ]

    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    clear_redis_data(redis_client)
    for CAR_LIST_ITERATOR in car_list:
        print(f"Testing car configuration from {CAR_LIST_ITERATOR}")
        x = TestMeasuredSpeedCalculator()
        for i in range(100):
            x.test_speed_calculation(i)
            time.sleep(0.1)  # Pause for 0.1 second between iterations

        perform_unit_test_on_aggregated_data()

        # Clear Redis data and any state variables before the next iteration
        clear_redis_data(redis_client)

import wsp_mod  # The shared object you built
import redis
import unittest


class SpeedSensor:
    def __init__(self):
        self.wss = wsp_mod.WheelSpeedSensor()  # Initialize the C++ object

    # def read_speed(self):
    # return self.wss.read_speed()  # Fetch and return processed speed from C++ code

    def read_speed(self):  # timed code for testing
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
        self.speed_sensor = SpeedSensor()  # Initialize the C++ object
        self.margin_of_error = 0.02  # 2% error

    def fetch_redis_data(self, key, field):
        return float(self.redis_client.hget(key, field))

    def set_redis_data(self, key, field, value):
        self.redis_client.hset(key, field, value)

    def test_speed_calculation(self):
        # Check for flags
        if not self.redis_client.hget(
            "RealitySimReplay", "RESET_FLAG"
        ) or not self.redis_client.hget("RealitySimReplay", "CRASHED_FLAG"):
            return

        # Fetch data from Redis
        true_vehicle_speed = self.fetch_redis_data("sim_state", "true_vehicle_speed")
        wheel_diameter = self.fetch_redis_data(
            "CurrentlyLoadedCarParams", "wheel_diameter"
        )
        encoder_cpr = self.fetch_redis_data("CurrentlyLoadedCarParams", "encoder_cpr")

        # Set parameters in C++ object
        self.speed_sensor.set_CPR(encoder_cpr)
        self.speed_sensor.set_diameter(wheel_diameter)

        # Calculate speed and measure time
        calculated_speed, elapsed_time = self.speed_sensor.read_speed()

        # Store these in Redis for comparison and history
        self.set_redis_data("TestResults", "CalculatedSpeed", calculated_speed)
        self.set_redis_data("TestResults", "ElapsedTime", elapsed_time)
        self.set_redis_data("TestResults", "TrueVehicleSpeed", true_vehicle_speed)

        # ... (no changes in the remaining code)
        # Compare with true_vehicle_speed
        delta = abs(true_vehicle_speed - calculated_speed)
        delta_percentage = delta / true_vehicle_speed

        # Print the comparison (or log it)
        print(
            f"True Speed: {true_vehicle_speed}, Calculated Speed: {calculated_speed}, Delta: {delta}, Delta %: {delta_percentage * 100}, Elapsed Time: {elapsed_time}, 1/Elapsed Time: {1/elapsed_time}"
        )

        # Validate if within margin of error
        if delta_percentage > self.margin_of_error:
            print(f"Error: Delta % is higher than acceptable margin of error.")


if __name__ == "__main__":
    x = TestMeasuredSpeedCalculator()
    while True:
        x.test_speed_calculation()

    # class TestMeasuredSpeedCalculator(unittest.TestCase):

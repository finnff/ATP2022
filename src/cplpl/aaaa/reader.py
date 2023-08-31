import wsp_mod  # The shared object you built
import redis  # Import the redis package


class SpeedSensor:
    def __init__(self):
        self.wss = wsp_mod.WheelSpeedSensor()  # Initialize the C++ object

    def read_speed(self):
        return self.wss.read_speed()  # Fetch and return processed speed from C++ code

    def set_CPR(self, CPR):
        self.wss.set_cpr(CPR)  # Set CPR in the C++ object

    def set_diameter(self, diameter):
        self.wss.set_diameter(diameter)  # Set diameter in the C++ object


# Initialize the Redis connection
r = redis.Redis(host="localhost", port=6379, db=0)

# Test the Python-C++ binding
if __name__ == "__main__":
    sensor = SpeedSensor()
    sensor.set_CPR(1.0)
    sensor.set_diameter(1.2)

    # Here you could set some initial values in Redis using Python
    # For example, to set the wheel speed:
    r.hset("Sensor_Actuator", "WheelSpeedSensorHz", "50.0")

    print(f"Speed: {sensor.read_speed()}")  # This should now print the processed speed

import wsp_mod  # The shared object you built
import redis  # Import the redis package


class SpeedSensor:
    def __init__(self, redis_context):
        self.vehicle_speed = 0.0  # Starting speed
        self.CPR = 1.0  # Cycles per Revolution
        self.diameter = 1.0  # Wheel diameter
        self.wss = wsp_mod.WheelSpeedSensor(
            redis_context
        )  # Initialize the C++ object with the Redis context

    def read_speed(self):
        raw_speed = self.wss.read_speed()  # Fetch raw speed from C++ code
        self.vehicle_speed = raw_speed / self.CPR / self.diameter  # Apply the dividers
        return self.vehicle_speed

    def set_CPR(self, CPR):
        self.CPR = CPR
        self.wss.set_cpr(CPR)  # Set in the C++ object if needed

    def set_diameter(self, diameter):
        self.diameter = diameter
        self.wss.set_diameter(diameter)  # Set in the C++ object if needed


# Initialize the Redis connection
r = redis.Redis(host="localhost", port=6379, db=0)

# Initialize the Redis context (this would ideally be done in a way that it can be passed to C++)
redis_context = None  # Replace with actual initialization code if needed

# Test the Python-C++ binding
if __name__ == "__main__":
    sensor = SpeedSensor(redis_context)
    sensor.set_CPR(2.0)
    sensor.set_diameter(1.2)

    # Here you could set some initial values in Redis using Python
    # For example, to set the wheel speed:
    r.hset("Sensor_Actuator", "WheelSpeedSensorHz", "50.0")

    print(f"Speed: {sensor.read_speed()}")

import WSS_binded
import wssPy


class SpeedSensor:
    def __init__(self):
        self.vehicle_speed = 0.0  # Starting speed
        self.CPR = 1.0  # Cycles per Revolution
        self.diameter = 1.0  # Wheel diameter
        self.wss = WSS_binded.WheelSpeedSensor()  # Initialize the C++ object

    def read_speed(self):
        raw_speed = self.wss.read_speed()  # Fetch raw speed from C++ code
        self.vehicle_speed = raw_speed / self.CPR / self.diameter  # Apply the dividers
        return self.vehicle_speed
    
    def set_CPR(self, CPR):
        self.CPR = CPR
        self.wss.set_CPR(CPR)  # Set in the C++ object if needed

    def set_diameter(self, diameter):
        self.diameter = diameter
        self.wss.set_diameter(diameter)  # Set in the C++ object if needed

# Test the Python-C++ binding
if __name__ == "__main__":
    sensor = SpeedSensor()
    sensor.set_CPR(2.0)
    sensor.set_diameter(1.2)
    print(f"Speed: {sensor.read_speed()}")

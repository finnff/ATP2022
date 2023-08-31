import wsp_mod  # The shared object you built


class SpeedSensor:
    def __init__(self):
        self.wss = wsp_mod.WheelSpeedSensor()  # Initialize the C++ object

    def read_speed(self):
        return self.wss.read_speed()  # Fetch and return processed speed from C++ code

    def set_CPR(self, CPR):
        self.wss.set_cpr(CPR)  # Set CPR in the C++ object

    def set_diameter(self, diameter):
        self.wss.set_diameter(diameter)  # Set diameter in the C++ object

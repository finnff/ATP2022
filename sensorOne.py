from hardwareAbstraction import hardwareDummy


class sensorOne(hardwareDummy.hardwareDummy):
    def __init__(self):
        super().__init__("SensorOne", 0.0)
    
    def RaiseValue(self):
        self.value += (0.1)

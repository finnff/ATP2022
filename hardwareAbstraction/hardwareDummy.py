class hardwareDummy:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def print(self):
        print("Sensor ", self.type, " with value: ", self.value)
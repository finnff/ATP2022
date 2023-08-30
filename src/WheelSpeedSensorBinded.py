import sys
sys.path.append("/home/ponkie/ATP2022/src/cpp/build/")
import mysensor

sensor = mysensor.SpeedSensor()
speed = sensor.read_speed()
print(f"Speed: {speed}")

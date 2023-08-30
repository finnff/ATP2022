import time
from actuator_sensor_interface import SensorInterface, SpeedSensor,  RadarDistanceMeter,  ActuatorInterface

# Create the SensorInterface
speed_sensor = SpeedSensor()
RadarDistanceMeter = RadarDistanceMeter()
sensor_interface = SensorInterface(speed_sensor, RadarDistanceMeter)

# Create and connect the GasRemSender
# gas_rem_sender = GasRemSender()
actuator_interface = ActuatorInterface()


# Giving it a slight delay to ensure a stable connection
time.sleep(0.5)  # Sleep for 500 milliseconds (adjust as needed)


# ... initialization and setup ...

try:
    while True:
        # Fetch data from sensors
        distance = sensor_interface.get_distance()
        speed = sensor_interface.get_speed()

        # Control logic
        if distance > 100:
            actuator_interface.set_gas_pedal_force(20)
        elif distance < 100:
            actuator_interface.set_braking_pedal_force(-20)
        
        # Wait for a response
        received_data = actuator_interface.receive_data()
        if received_data:
            print(f"Received data from server: {received_data}")

        # Sleep for control loop delay
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nStopping the control loop...")



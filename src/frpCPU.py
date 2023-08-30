import time
from combined_interface import CombinedInterface

# Create the Combined Interface
combined_interface = CombinedInterface()

try:
    while True:
        # Fetch data from sensors
        distance = combined_interface.get_distance()
        speed = combined_interface.get_speed()
        
        # Control logic
        if distance > 200:
            combined_interface.set_gas_pedal_force(20)
        elif distance < 200:
            combined_interface.set_braking_pedal_force(-20)
        elif distance < 100:
            combined_interface.set_braking_pedal_force(-50)

        received_data = combined_interface.receive_data()
        if received_data:
            print(f"Received data from server: {received_data}")
        # Sleep for control loop delay
        time.sleep(0.05)
        
except KeyboardInterrupt:
    print("\nStopping the control loop...")


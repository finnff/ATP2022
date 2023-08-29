import select
import random
import socket
import json
import time


class SpeedSensor:
    def __init__(self):
        self.vehicle_speed = 0  # starting speed
    
    def read_speed(self):
        # Simulate slight changes in vehicle speed.
        self.vehicle_speed += random.randint(-1, 1)  
        return self.vehicle_speed

class RadarDistanceMeter:
    def __init__(self):
        self.distance_to_voorligger = 999  # starting distance
    
    def read_distance(self):
        # Simulate changes in distance to voorligger.
        self.distance_to_voorligger += random.randint(-1, 1)
        return self.distance_to_voorligger

class SensorInterface:
    def __init__(self, speed_sensor, RadarDistanceMeter):
        self.speed_sensor = speed_sensor
        self.RadarDistanceMeter = RadarDistanceMeter

    def get_speed(self):
        return self.speed_sensor.read_speed()

    def get_distance(self):
        return self.RadarDistanceMeter.read_distance()


# Actuatoren

class ActuatorInterface:
    # def __init__(self, gas_rem_sender):

    def __init__(self):
        self.gas_rem_sender = GasRemSender(10)

    def receive_data(self, timeout=0.05):
        return self.gas_rem_sender.receive_data(timeout)

    def set_gas_pedal_force(self, force ):
        if 0 <= force <= 100:
            self.gas_rem_sender.send_gas_rem_percentage(gas_rem_percentage=force)
        else:
            print("Speed must be between 0 and 100.")

    def set_braking_pedal_force(self, force):
        if -100 <= force <= 0:
            self.gas_rem_sender.send_gas_rem_percentage(gas_rem_percentage=force)
        else:
            print("Force must be between -100 and 0.")



class GasRemSender:
    def __init__(self, max_retries=10):
        self.server_address = ('localhost', 12345)
        self.client_socket = None
        self.connect_to_server(max_retries)

    def connect_to_server(self, max_retries):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        retries = 0
        while retries < max_retries:
            try:
                time.sleep(0.2)  # Sleep for 200 milliseconds
                self.client_socket.connect(self.server_address)
                time.sleep(0.2)  # Sleep for 200 milliseconds
                break
            except ConnectionRefusedError:
                print("Connection refused. Make sure the server is running.")
                self.client_socket = None
                retries += 1
                if retries >= max_retries:
                    print("Maximum retries reached. Failed to connect to the server.")
                    return

    def send_data(self, data):
        try:
            self.client_socket.sendall(json.dumps(data).encode())
        except socket.error as e:
            print(f"Socket error while sending: {e}")




    
    def receive_data(self, timeout=0.05):
        accumulated_data = ""
        ready_to_read, _, _ = select.select([self.client_socket], [], [], timeout)
    
        if ready_to_read:
            chunk = self.client_socket.recv(1024).decode()
            accumulated_data += chunk

            if "\n" in accumulated_data: 
                message, accumulated_data = accumulated_data.split("\n", 1)
                try:
                    return json.loads(message)
                except json.JSONDecodeError:
                    print("Failed to decode incoming data.")
                    return None
        else:
            return None

    def send_gas_rem_percentage(self, gas_rem_percentage=0, distance_to_voorligger=0):
        if self.client_socket is None:
            print("Not connected to the server. Trying to reconnect...")
            self.connect_to_server(max_retries=3)  # 3 retries for in-operation reconnections.
            if self.client_socket is None:
                return

        if -100 <= gas_rem_percentage <= 100:
            data = {
                'GasRemPedalPosPercentage': gas_rem_percentage,
                'DistanceToVoorligger': distance_to_voorligger
            }
            self.send_data(data)
            received_data = self.receive_data()
            if received_data:
                print(f"Received data from server: {received_data}")
        else:
            print("Gas/rem percentage must be between -100 and 100.")

#
# import socket
# import json
# import time
#
#
# class GasRemSender:
#     def __init__(self):
#         self.server_address = ('localhost', 12345)
#         self.client_socket = None
#         self.connect_to_server()
#
#     def connect_to_server(self):
#         self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         try:
#             time.sleep(0.2)  # Sleep for 200 milliseconds (adjust as needed)
#             self.client_socket.connect(self.server_address)
#             time.sleep(0.2)  # Sleep for 200 milliseconds (adjust as needed)
#         except ConnectionRefusedError:
#             print("Connection refused. Make sure the server is running.")
#             self.client_socket = None
#
#     def send_gas_rem_percentage(self, gas_rem_percentage=0):
#         if self.client_socket is None:
#             print("Not connected to the server. Please connect first.")
#             return
#
#         if -100 <= gas_rem_percentage <= 100:
#             data = {
#                 'GasRemPedalPosPercentage': gas_rem_percentage
#             }
#             try:
#                 self.client_socket.sendall(json.dumps(data).encode())
#                 received_data = self.client_socket.recv(1024)
#                 if not received_data:
#                     print("No data received from server or connection was closed.")
#                     return
#                 print(f"Received data from server: {received_data.decode()}")
#             except socket.error as e:
#                 print(f"Socket error: {e}")
#         else:
#             print("Gas/rem percentage must be between -100 and 100.")
#

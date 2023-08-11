# import socket
# import json
#
# class GasRemSender:
#     def __init__(self):
#         self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server_address = ('localhost', 12345)
#         self.client_socket.connect(self.server_address)
#
#     def send_gas_rem_percentage(self):
#         while True:
#             try:
#                 gas_rem_percentage = int(input("Enter gas/rem percentage (-100 to 100): "))
#                 assert -100 <= gas_rem_percentage <= 100, "Gas/rem percentage must be between -100 and 100."
#             except ValueError:
#                 print("Invalid input. Please enter an integer between -100 and 100.")
#                 continue
#             except AssertionError as e:
#                 print(e)
#                 continue
#
#             data = {
#                 'GasRemPedalPosPercentage': gas_rem_percentage
#             }
#             self.client_socket.sendall(json.dumps(data).encode())
#
#             # Receive data from the server
#             data = self.client_socket.recv(1024)
#             print(f"Received data from server: {json.loads(data.decode())}")
#
#     def close_connection(self):
#         self.client_socket.close()
#
# gas_rem_sender = GasRemSender()
# try:
#     gas_rem_sender.send_gas_rem_percentage()
# except KeyboardInterrupt:
#     print("\nStopping the client...")
# finally:
#     gas_rem_sender.close_connection()
#
# import socket
# import json

# class GasRemSender:
#     def __init__(self):
#         self.server_address = ('localhost', 12345)
#
#     def send_gas_rem_percentage(self):
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
#             try:
#                 client_socket.connect(self.server_address)
#                 while True:
#                     gas_rem_percentage = self.get_gas_rem_percentage()
#                     data = {
#                         'GasRemPedalPosPercentage': gas_rem_percentage
#                     }
#                     client_socket.sendall(json.dumps(data).encode())
#
#                     # Receive data from the server
#                     # received_data = client_socket.recv(1024)
#                     # received_data = json.loads(received_data.decode())
#                     # gas_rem_server_percentage = received_data.get('GasRemPedalPosPercentage', 0)
#                     # Receive data from the server
#                     received_data = client_socket.recv(1024)
#                     print(f"Received data from server: {json.loads(received_data.decode())}")
#                     # print(f"Received Gas Rem Pedal Position from server: {gas_rem_server_percentage:.3f}")
#             except ConnectionRefusedError:
#                 print("Connection refused. Make sure the server is running.")
#             except json.JSONDecodeError:
#                 print("Received invalid JSON data from the server.")
#             except Exception as e:
#                 print(f"An error occurred: {e}")
#
#     def get_gas_rem_percentage(self):
#         while True:
#             try:
#                 gas_rem_percentage = int(input("Enter gas/rem percentage (-100 to 100): "))
#                 assert -100 <= gas_rem_percentage <= 100, "Gas/rem percentage must be between -100 and 100."
#                 return gas_rem_percentage
#             except ValueError:
#                 print("Invalid input. Please enter an integer between -100 and 100.")
#             except AssertionError as e:
#                 print(e)
#
# gas_rem_sender = GasRemSender()
# try:
#     gas_rem_sender.send_gas_rem_percentage()
# except KeyboardInterrupt:
#     print("\nStopping the client...")

import socket
import json
import time

class GasRemSender:
    def __init__(self):
        self.server_address = ('localhost', 12345)
        self.client_socket = None

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            time.sleep(0.5)  # Sleep for 500 milliseconds (adjust as needed)
            self.client_socket.connect(self.server_address)
        except ConnectionRefusedError:
            print("Connection refused. Make sure the server is running.")
            self.client_socket = None


    def send_gas_rem_percentage(self, gas_rem_percentage=0):
        if self.client_socket is None:
            print("Not connected to the server. Please connect first.")
            return



        # if -100 <= gas_rem_percentage <= 100:
        #     data = {
        #         'GasRemPedalPosPercentage': gas_rem_percentage
        #     }
        #     self.client_socket.sendall(json.dumps(data).encode())
        #     received_data = self.client_socket.recv(1024)
        #     print(f"Received data from server: {received_data.decode()}")
        else:
            print("Gas/rem percentage must be between -100 and 100.")

# Example usage
gas_rem_sender = GasRemSender()
gas_rem_sender.connect_to_server()
time.sleep(0.5)  # Sleep for 500 milliseconds (adjust as needed)

try:
    while True:
        try:
            # gas_rem_percentage = int(input("Enter gas/rem percentage (-100 to 100): "))
            # gas_rem_sender.send_gas_rem_percentage(gas_rem_percentage)
            gas_rem_sender.send_gas_rem_percentage(1)
            time.sleep(0.005)  # Sleep for 500 milliseconds (adjust as needed)
        except ValueError:
            print("Invalid input. Please enter an integer between -100 and 100.")
except KeyboardInterrupt:
    print("\nStopping the client...")

        

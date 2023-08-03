import socket
import json

class GasRemSender:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 12345)
        self.client_socket.connect(self.server_address)

    def send_gas_rem_percentage(self):
        while True:
            try:
                gas_rem_percentage = int(input("Enter gas/rem percentage (-100 to 100): "))
                assert -100 <= gas_rem_percentage <= 100, "Gas/rem percentage must be between -100 and 100."
            except ValueError:
                print("Invalid input. Please enter an integer between -100 and 100.")
                continue
            except AssertionError as e:
                print(e)
                continue

            data = {
                'GasRemPedalPosPercentage': gas_rem_percentage
            }
            self.client_socket.sendall(json.dumps(data).encode())

            # Receive data from the server
            data = self.client_socket.recv(1024)
            print(f"Received data from server: {json.loads(data.decode())}")

    def close_connection(self):
        self.client_socket.close()

gas_rem_sender = GasRemSender()
try:
    gas_rem_sender.send_gas_rem_percentage()
except KeyboardInterrupt:
    print("\nStopping the client...")
finally:
    gas_rem_sender.close_connection()

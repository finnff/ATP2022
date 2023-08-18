import json
import socket
import time
import select

class CarParams:
    def __init__(self, parameter_file_name, max_acceleration, max_deceleration, wheel_diameter, encoder_CPR, seconds_distance):
        self.parmeter_file_name = parameter_file_name 
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.wheel_diameter = wheel_diameter
        self.encoder_CPR = encoder_CPR
        self.seconds_distance = seconds_distance


    def __str__(self):
        return f"\nCar Parameters for {self.parmeter_file_name}:\n" \
               f"Max Acceleration: {self.max_acceleration}\n" \
               f"Max Deceleration: {self.max_deceleration}\n" \
               f"Wheel Diameter: {self.wheel_diameter}\n" \
               f"Encoder CPR: {self.encoder_CPR}\n" \
               f"Seconds Distance: {self.seconds_distance}"

def load_car_from_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        return CarParams(file_path,data['Max Acceleration'], data['Max Deceleration'], data['Wheel Diameter'], data['Encoder CPR'], data['Seconds Distance'])

car_hatchback = load_car_from_json('./car_constants/hatchback.json')
car_suv = load_car_from_json('./car_constants/suv.json')
car_ferrari = load_car_from_json('./car_constants/ferrari.json')


class SocketServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        print("Server is listening for incoming connections...")
        self.client_socket, self.addr = self.server_socket.accept()
        print(f"Connection established with {self.addr}")

    def send_data(self, data):
        try:
            message = json.dumps(data) + "\n"
            self.client_socket.sendall(message.encode())
        except socket.error as e:
            print("Error sending data:", e)

    def receive_data(self):
        try:
            data = self.client_socket.recv(1024).decode()
            return json.loads(data)
        except json.JSONDecodeError:
            print("Failed to decode incoming data.")
            self.client_socket.close()  # Close the current socket
            return {}
        except socket.error as e:
            print("Error receiving data:", e)
            print("Connection was reset by the client. Waiting for a new connection...")
            self.client_socket.close()  # Close the current socket
            self.client_socket, _ = self.server_socket.accept()  # Accept a new connection
            return None  # Or handle this situation differently based on your use case
       
    def message_received(self):
        # Non-blocking check for data
        return bool(select.select([self.client_socket], [], [], 0)[0])
#
#     def send_data(self, data):
#         self.client_socket.sendall(json.dumps(data).encode())
#
#
#             return data




class True_Sim_Values:
    def __init__(self, car_parameters, true_vehicle_speed, true_distance_to_voorligger, true_voorligger_speed, true_vehicle_acceleration, sockserver):
        self.car_parameters = car_parameters 
        print(f"Starting Sim..... loaded car Parameters --- {self.car_parameters}")
        self.true_vehicle_speed = true_vehicle_speed
        self.true_distance_to_voorligger = true_distance_to_voorligger
        self.true_voorligger_speed = true_voorligger_speed
        self.true_vehicle_acceleration = true_vehicle_acceleration
        self.GasRemPedalPosPercentage = 0.0
        self.sockserver = sockserver
        self.iteration = 0
        print(f"  myVel  |  myAc  |  diff  |dist2Voo|  VooV  | lastPedalPos")


    def alternate_voorligger_speed(self): # for now before we load voorligger profile
        if self.iteration % 2 == 0: # Alternating behavior every other iteration
            self.true_voorligger_speed = 110
        else:
            self.true_voorligger_speed = 80
    

    def update(self):
        if self.GasRemPedalPosPercentage >= 0:
            realChange = (self.GasRemPedalPosPercentage / 100) * self.car_parameters.max_acceleration
            self.true_vehicle_acceleration += realChange
            self.true_vehicle_speed += self.true_vehicle_acceleration
        if self.GasRemPedalPosPercentage < 0:
            realChange = (self.GasRemPedalPosPercentage / 100) * self.car_parameters.max_deceleration
            self.true_vehicle_acceleration -= realChange
            self.true_vehicle_speed += self.true_vehicle_acceleration

        values_line2 = f"{self.true_vehicle_speed:.3f}, {self.true_vehicle_acceleration:.3f}, {realChange:.3f}, {self.true_distance_to_voorligger:.3f}, {self.true_voorligger_speed:.3f}, {self.GasRemPedalPosPercentage:.3f}"
        values_line = f"{self.true_vehicle_speed:.3f}".ljust(9) + \
                      f"| {self.true_vehicle_acceleration:.3f}".ljust(9) + \
                      f"| {realChange:.3f}".ljust(9) + \
                      f"| {self.true_distance_to_voorligger:.3f}".ljust(9) + \
                      f"| {self.true_voorligger_speed:.3f}".ljust(9) + \
                      f"| {self.GasRemPedalPosPercentage:.3f}".ljust(9)
        print(values_line, end="\r")
        self.alternate_voorligger_speed()
        self.iteration += 1 # Increment the iteration after each update
        # print(f" myV: {self.true_vehicle_speed:.3f}, myAc: {self.true_vehicle_acceleration:.3f} (diff: {realChange:.3f}), dist2Voo: {self.true_distance_to_voorligger:.3f}, speedVoo: {self.true_voorligger_speed:.3f}")
        # Adjust the distance to the voorligger based on relative speed:
        relative_speed = self.true_vehicle_speed - self.true_voorligger_speed
        self.true_distance_to_voorligger -= relative_speed

    def wait(self):
        # Send true_distance_to_voorligger and true_vehicle_speed via socket
        data = {
            'true_distance_to_voorligger': self.true_distance_to_voorligger,
            'true_vehicle_speed': self.true_vehicle_speed
        }
        self.sockserver.send_data(data)

        # Receive data from the client
        data = self.sockserver.receive_data()
        GasRemPedalPosPercentage = data["GasRemPedalPosPercentage"]
        self.GasRemPedalPosPercentage = GasRemPedalPosPercentage
        # print(f"Received Gas Rem Pedal Position: {self.GasRemPedalPosPercentage:.3f}")




TIME_STEP = 0.1  # Example time step value of 0.1 seconds.

sockserver = SocketServer()
print("Server is listening for incoming connections...")
reality = True_Sim_Values(car_hatchback, 100, 2000, 100, 1, sockserver)
print("Connection established with", sockserver.client_socket.getpeername())  # Fixed: get the address from the client_socket

while True:
    start_time = time.time()

    reality.update()

    # Send current state to client.
    data = {
        'true_distance_to_voorligger': reality.true_distance_to_voorligger,
        'true_vehicle_speed': reality.true_vehicle_speed
    }
    sockserver.send_data(data)

    # Check for incoming messages and update the simulation state if necessary.
    if sockserver.message_received():
        data = sockserver.receive_data()
        GasRemPedalPosPercentage = data.get("GasRemPedalPosPercentage")
        if GasRemPedalPosPercentage is not None:
            reality.GasRemPedalPosPercentage = GasRemPedalPosPercentage

    # Sleep to ensure that we're not updating faster than our TIME_STEP.
    elapsed_time = time.time() - start_time
    sleep_duration = max(0, TIME_STEP - elapsed_time)
    time.sleep(sleep_duration)



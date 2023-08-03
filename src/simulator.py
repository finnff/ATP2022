import json
import socket

class CarParams:
    def __init__(self, max_acceleration, max_deceleration, wheel_diameter, encoder_CPR, seconds_distance):
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.wheel_diameter = wheel_diameter
        self.encoder_CPR = encoder_CPR
        self.seconds_distance = seconds_distance


    def __str__(self):
        return f"Car Parameters:\n" \
               f"Max Acceleration: {self.max_acceleration}\n" \
               f"Max Deceleration: {self.max_deceleration}\n" \
               f"Wheel Diameter: {self.wheel_diameter}\n" \
               f"Encoder CPR: {self.encoder_CPR}\n" \
               f"Seconds Distance: {self.seconds_distance}"

def load_car_from_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        return CarParams(data['Max Acceleration'], data['Max Deceleration'], data['Wheel Diameter'], data['Encoder CPR'], data['Seconds Distance'])

car_hatchback = load_car_from_json('./car_constants/hatchback.json')
car_suv = load_car_from_json('./car_constants/suv.json')
car_ferrari = load_car_from_json('./car_constants/ferrari.json')



class SocketServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 12345)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(1)
        print("Server is listening for incoming connections...")
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"Connection established with {self.client_address}")

    def send_data(self, data):
        self.client_socket.sendall(json.dumps(data).encode())

    def receive_data(self):
        data = self.client_socket.recv(1024)
        return json.loads(data.decode())



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

    def update(self):
        if self.GasRemPedalPosPercentage >= 0:
            realChange = (self.GasRemPedalPosPercentage / 100) * self.car_parameters.max_acceleration
            self.true_vehicle_acceleration += realChange
            self.true_vehicle_speed += self.true_vehicle_acceleration
        if self.GasRemPedalPosPercentage < 0:
            realChange = (self.GasRemPedalPosPercentage / 100) * self.car_parameters.max_deceleration
            self.true_vehicle_acceleration -= realChange# considering the deceleration as negative acceleration
            self.true_vehicle_speed += self.true_vehicle_acceleration  # if acceleration is negative, speed will decrease
        
        print(f" myV: {self.true_vehicle_speed}, myAc: {self.true_vehicle_acceleration} (diff: {realChange}) , dist2Voo: {self.true_distance_to_voorligger}, speedVoo: {self.true_voorligger_speed}")
        self.wait()

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
        print(f"Received Gas Rem Pedal Position: {self.GasRemPedalPosPercentage}")

        self.update()

sockserver = SocketServer()
reality = True_Sim_Values(car_hatchback,100,200,100,1, sockserver)
reality.update()
#
#
# class True_Sim_Values:
#     def __init__(self, car_parameters, true_vehicle_speed, true_distance_to_voorligger, true_voorligger_speed, true_vehicle_acceleration):
#         self.car_parameters = car_parameters 
#         self.true_vehicle_speed = true_vehicle_speed
#         self.true_distance_to_voorligger = true_distance_to_voorligger
#         self.true_voorligger_speed = true_voorligger_speed
#         self.true_vehicle_acceleration = true_vehicle_acceleration
#         self.GasRemPedalPosPercentage = 0.0
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server_address = ('localhost', 12345)
#         self.server_socket.bind(self.server_address)
#         self.server_socket.listen(1)
#         print("Server is listening for incoming connections...")
#
#     def update(self):
#         if self.GasRemPedalPosPercentage >= 0:
#             realAccel = (self.GasRemPedalPosPercentage / 100) * self.car_parameters.max_acceleration
#             self.true_vehicle_acceleration += realAccel
#             self.true_vehicle_speed += self.true_vehicle_acceleration
#         elif self.GasRemPedalPosPercentage < 0:
#             realDecel = (self.GasRemPedalPosPercentage / 100) * self.car_parameters.max_deceleration
#             self.true_vehicle_acceleration += realDecel  # considering the deceleration as negative acceleration
#             self.true_vehicle_speed += self.true_vehicle_acceleration  # if acceleration is negative, speed will decrease
#
#         print(f"True Vehicle Speed: {self.true_vehicle_speed}")
#         print(f"True Distance To Voorligger: {self.true_distance_to_voorligger}")
#         print(f"True Voorligger Speed: {self.true_voorligger_speed}")
#         print(f"True Vehicle Acceleration: {self.true_vehicle_acceleration}")
#         self.wait()
#
#     def wait(self):
#         # Accept a connection from a client
#         client_socket, client_address = self.server_socket.accept()
#         print(f"Connection established with {client_address}")
#
#         # Send true_distance_to_voorligger and true_vehicle_speed via socket
#         data = {
#             'true_distance_to_voorligger': self.true_distance_to_voorligger,
#             'true_vehicle_speed': self.true_vehicle_speed
#         }
#         client_socket.sendall(json.dumps(data).encode())
#
#         # Receive data from the client
#         data = client_socket.recv(1024)
#         GasRemPedalPosPercentage = json.loads(data.decode())["GasRemPedalPosPercentage"]
#         self.GasRemPedalPosPercentage = GasRemPedalPosPercentage
#         print(f"Received Gas Rem Pedal Position: {self.GasRemPedalPosPercentage}")
#
#         # Close the connection
#         client_socket.close()
#         self.update()
#
# reality = True_Sim_Values(car_hatchback,100,200,100,1)
# reality.update()
# reality.wait()
#
#
#
# class True_Sim_Values:
#     def __init__(self, true_vehicle_speed, true_distance_to_voorligger, true_voorligger_speed, true_vehicle_acceleration):
#         self.true_vehicle_speed = true_vehicle_speed
#         self.true_distance_to_voorligger = true_distance_to_voorligger
#         self.true_voorligger_speed = true_voorligger_speed
#         self.true_vehicle_acceleration = true_vehicle_acceleration
#         self.GasRemPedalPosPercentage = 0.0
#
#     def update(self):
#         # calculate realAccel ((GasRemPedalPosition)/100 * max_acceleration) if GasRemPedalPosition > 0 and 
#         # calculate realDecel ((GasRemPedalPosition)/100 * max_deceleration) if GasRemPedalPosition < 0 
#         # then apply either value to self.true_vehicle_acceleration (value in meters*seconds^-2) and update
#         # self.true_vehicle_speed (value in meters*seconds^-1) to match this change
#         wait() 
#
#     def wait(self):
#         # send true_distance_to_voorligger and true_vehicle_speed via socket
#         # wait untill message Received
#         # this message will contain GasRemPedalPosition (intgervalue between -100 to 100)
#         # change self.GasRemPedalPosPercentage to what we recieve in message 
#
# import socket
#
# def start_server():
#     # Create a socket object
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#     # Bind the socket to a specific address and port
#     server_address = ('localhost', 12345)
#     server_socket.bind(server_address)
#
#     # Listen for incoming connections
#     server_socket.listen(1)
#     print("Server is listening for incoming connections...")
#
#     # Accept a connection from a client
#     client_socket, client_address = server_socket.accept()
#     print(f"Connection established with {client_address}")
#
#     # Receive data from the client
#     data = client_socket.recv(1024)
#     print(f"Received data from client: {data.decode()}")
#
#     # Send a response back to the client
#     response = "Hello from the server!"
#     client_socket.sendall(response.encode())
#
#     # Close the connection
#     client_socket.close()
#     server_socket.close()
#
#
# reality = True_Sim_Values(100,200,100,1)
# reality.update()

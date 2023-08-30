import json
import os
import redis


class CarParams:
    def __init__(
        self,
        param_name,
        max_acceleration,
        max_deceleration,
        wheel_diameter,
        encoder_cpr,
        seconds_distance,
    ):
        self.param_name = param_name
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.wheel_diameter = wheel_diameter
        self.encoder_cpr = encoder_cpr
        self.seconds_distance = seconds_distance

    def __str__(self):
        return (
            f"Using Parameters: {self.param_name}\n"
            f"MaxAcc: {self.max_acceleration}\n"
            f"MaxDec: {self.max_deceleration}\n"
            f"Wheel_size: {self.wheel_diameter}\n"
            f"WheelSpeed CPR: {self.encoder_cpr}\n"
            f"Sec Dist: {self.seconds_distance}\n\n"
        )


class CarParamsManager:
    def __init__(
        self,
        param_folder_path,
        param_no_to_set=0,
        redis_host="localhost",
        redis_port=6379,
        redis_db=0,
    ):
        self.redis_client = redis.StrictRedis(
            host=redis_host, port=redis_port, db=redis_db
        )
        self.param_folder = param_folder_path
        self.jsonloadedparams = self.load_all_cars()
        self.save_car_to_redis(self.jsonloadedparams[param_no_to_set])

    def load_car_from_json(self, file_path):
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
            return CarParams(
                data["Param Name"],
                data["Max Acceleration"],
                data["Max Deceleration"],
                data["Wheel Diameter"],
                data["Encoder CPR"],
                data["Seconds Distance"],
            )

    def save_car_to_redis(self, car_params):
        field_values = {
            "param_name": car_params.param_name,
            "max_acceleration": car_params.max_acceleration,
            "max_deceleration": car_params.max_deceleration,
            "wheel_diameter": car_params.wheel_diameter,
            "encoder_cpr": car_params.encoder_cpr,
            "seconds_distance": car_params.seconds_distance,
        }
        self.redis_client.hset("CurrentlyLoadedCarParams", mapping=field_values)

    def load_car_from_redis(self):
        raw_data = self.redis_client.hgetall("CurrentlyLoadedCarParams")
        if not raw_data:
            print("No data found in Redis for the key 'CurrentlyLoadedCarParams'.")
            return None
        try:
            car_params = CarParams(
                raw_data[b"param_name"].decode("utf-8"),
                float(raw_data[b"max_acceleration"]),
                float(raw_data[b"max_deceleration"]),
                float(raw_data[b"wheel_diameter"]),
                int(raw_data[b"encoder_cpr"]),
                float(raw_data[b"seconds_distance"]),
            )
            return car_params
        except KeyError as e:
            print(f"KeyError: {e} not found in Redis data.")
            return None

    def load_all_cars(self):
        loaded_car_parameters = []
        for filename in os.listdir(self.param_folder):
            if filename.endswith(".json"):
                file_path = os.path.join(self.param_folder, filename)
                loaded_car_parameters.append(self.load_car_from_json(file_path))
        return loaded_car_parameters

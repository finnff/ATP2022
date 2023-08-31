import multiprocessing
import math
import rx
from rx.core.observable.observable import Observable
from rx.scheduler.threadpoolscheduler import ThreadPoolScheduler
from rx import operators as ops
from functools import wraps
import time
from combined_interface import CombinedInterface
import logging

LOG_FILE_NAME = "frp.log"

# Logged nu naar bestand, zodat code stateless FRP blijft
logging.basicConfig(filename=LOG_FILE_NAME, level=logging.INFO)


def log_data_every_second(interface):
    interface.updateFRPLogs(LOG_FILE_NAME)
    return ("LOGGING_DONE",)  # Returning a single-element tuple with a sentinel value


# Aspect-Oriented decorator to measure time
def timing_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"Elapsed time: {elapsed_time}")
        return elapsed_time, result

    return wrapper


# Aspect-Oriented decorator for logging args and retun values
def logging_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        logging.info(f"Function [{f.__name__}] arguments were {args} and {kwargs}")
        logging.info(f"Function [{f.__name__}] result was {result}")
        return result

    return wrapper


def Proportional_controller(
    desire_seconds_to_voorligger, current_speed, distance_to_vehicle_in_front
):
    if current_speed != 0:
        current_seconds_to_voorligger = distance_to_vehicle_in_front / current_speed
    else:
        current_seconds_to_voorligger = float("inf")

    timeDelta = current_seconds_to_voorligger - desire_seconds_to_voorligger
    print("[Propo Cont] TimeDelta: ", timeDelta)

    Kp = 10  # Proportional gain constant

    force_value = 1 / (1 + math.exp(-Kp * timeDelta)) * 100  # Scaled between 0 and 100
    # clamping as weird math happens above with small /large floats
    force_value = min(max(force_value, -100), 100)

    if timeDelta >= 0:
        return ("gas", int(force_value))
    else:
        return ("brake", int(force_value))


# Function to get sensor data
def get_sensor_data(interface):
    desire_seconds = interface.get_desiredSeconds()
    distance = interface.get_distance()
    speed = interface.get_speed()
    print(
        f"[get_sensor_data] desire_seconds: {desire_seconds}, distance: {distance}, speed: {speed}"
    )
    return desire_seconds, distance, speed


# Function for control logic
@logging_decorator
def control_logic(data):
    desire_seconds, distance, speed = data
    print(
        f"[control_logic] Input data: desire_seconds: {desire_seconds}, distance: {distance}, speed: {speed}"
    )
    control_data = Proportional_controller(desire_seconds, speed, distance)
    print(f"[control_logic] Output control_data: {control_data}")
    return control_data


# Function to apply control
def apply_control(interface, control_data):
    control, value = control_data
    print(f"[apply_control] control: {control}, value: {value}")

    if control == "gas":
        print("[apply_control] Setting gas_pedal_force")
        interface.set_gas_pedal_force(value)
    elif control == "brake":
        print("[apply_control] Setting braking_pedal_force")
        interface.set_braking_pedal_force(value)


# Pure Function to get sensor data
# # @timing_decorator
# def get_sensor_data(interface):
#     print("xxx")
#     desire_seconds = interface.get_desiredSeconds()
#     distance = interface.get_distance()
#     speed = interface.get_speed()
#     print("re", desire_seconds, distance, speed)
#     return desire_seconds, distance, speed
#
#
# # Pure Function for control logic
# @logging_decorator
# def control_logic(data):
#     desire_seconds, distance, speed = data
#     control_data = Proportional_controller(desire_seconds, speed, distance)
#     return control_data
#
#
# # Function to apply control
# def apply_control(interface, control_data):
#     control, value = control_data
#     if control == "gas":
#         interface.set_gas_pedal_force(value)
#     elif control == "brake":
#         interface.set_braking_pedal_force(value)
#

# Create the Combined Interface
combined_interface = CombinedInterface()

# Create a ThreadPoolScheduler
pool_scheduler = ThreadPoolScheduler(2)
#
# # main 100hz Observable sequence
sens_acc_observable = rx.interval(0.01).pipe(
    ops.map(lambda x: get_sensor_data(combined_interface))
)
# # quasi frp way of sending values to redis and dashboard as we are doing it via a log file.
log_observable = rx.interval(1).pipe(
    ops.map(lambda y: log_data_every_second(combined_interface))
)
#
# Create individual observables
# sens_acc_observable = create_sensor_observable(combined_interface)
# log_observable = create_log_observable(combined_interface)

# Merge observables
merged_observable = rx.merge(sens_acc_observable, log_observable)

# Create disposable
# disposable = merged_observable.subscribe(

disposable = merged_observable.subscribe(
    on_next=lambda s: (
        print(f"Received: {s}, Type: {type(s)}"),
        apply_control(combined_interface, control_logic(s)),
    )
    if isinstance(s, tuple) and s != ("LOGGING_DONE",)
    else 1 + 1,
    # print(f"Skipped: {s}, Type: {type(s)}"),
    on_error=lambda e: print(f"Error Occurred: {e}"),
    on_completed=lambda: print("Done!"),
    scheduler=pool_scheduler,
)
try:
    input("FRP is running, check frp.log ,Press any key to exit\n")
finally:
    disposable.dispose()


#
# merged_observable = rx.merge(sens_acc_observable, log_observable)
#
# disposable = merged_observable.subscribe(
#     on_next=lambda s: apply_control(combined_interface, control_logic(s))
#     if isinstance(s, tuple)
#     else None,
#     on_error=lambda e: print(f"Error Occurred: {e}"),
#     on_completed=lambda: print("Done!"),
#     scheduler=pool_scheduler,
# )
# try:
#     print(get_sensor_data(combined_interface))
#     print(get_sensor_data(combined_interface))
#     print(get_sensor_data(combined_interface))
#     print(get_sensor_data(combined_interface))
#     input("FRP is running, check frp.log ,Press any key to exit\n")
# finally:
#     disposable.dispose()

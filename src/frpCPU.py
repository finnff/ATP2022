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
# PID_CONTOLLER = True
PID_CONTOLLER = True
# PID_CONTOLLER = False

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


# PID Controller Logic
# Werkt functioneel maar kost te veel tijd (ben nu 3 uur bezig)
# om deze zo te tunen om voor alle 3 de type autos te laten werken
def pid_controller(
    kp,
    ki,
    kd,
    prev_integral,
    prev_error,
    desire_seconds_to_voorligger,
    current_speed,
    distance_to_vehicle_in_front,
):
    if current_speed != 0:
        current_seconds_to_voorligger = distance_to_vehicle_in_front / current_speed
    else:
        current_seconds_to_voorligger = float("inf")

    error = current_seconds_to_voorligger - desire_seconds_to_voorligger

    integral = prev_integral + error
    derivative = error - prev_error

    output = kp * error + ki * integral + kd * derivative

    output = min(max(output, -100), 100)

    if output >= 0:
        control = "gas"
        return (control, int(abs(output))), integral, error
    else:
        control = "brake"
        return (control, int(output)), integral, error


def bang_bang_pid_controller(
    kp,
    ki,
    kd,
    prev_integral,
    prev_error,
    desire_seconds_to_voorligger,
    current_speed,
    distance_to_vehicle_in_front,
):
    if current_speed != 0:
        current_seconds_to_voorligger = distance_to_vehicle_in_front / current_speed
    else:
        current_seconds_to_voorligger = float("inf")

    error = current_seconds_to_voorligger - desire_seconds_to_voorligger
    print(f"Error: {error}")

    integral = prev_integral + error
    derivative = error - prev_error

    output = kp * error + ki * integral + kd * derivative
    output = min(max(output, -100), 100)

    output_level = 10 if abs(error) >= 0.5 else 30

    if current_seconds_to_voorligger > desire_seconds_to_voorligger:
        control = "gas"
        return (control, int(output_level)), integral, error
    else:
        control = "brake"
        return (control, int(-output_level)), integral, error


# Function to get sensor data
@logging_decorator
def get_sensor_data(interface):
    desire_seconds = interface.get_desiredSeconds()
    distance = interface.get_distance()
    speed = interface.get_speed()

    print(desire_seconds, distance, speed)
    return desire_seconds, distance, speed


#
@logging_decorator
def control_logic(data, prev_integral, prev_error, interface):
    print("Entering control_logic")

    desire_seconds, distance, speed = data
    print("Before calling getScalars")

    scalars = interface.getScalars()
    if scalars is not None:
        kp, ki, kd = scalars
    else:
        # Handle error here, maybe set defaults or raise exception
        # deze defaults werken aleen voor ferrari
        kp, ki, kd = 0.01, 0.00131, 0.031

    print(f"After calling getScalars: kp={kp}, ki={ki}, kd={kd}")
    if PID_CONTOLLER:
        control_data, new_integral, new_error = pid_controller(
            kp, ki, kd, prev_integral, prev_error, desire_seconds, speed, distance
        )
    else:
        control_data, new_integral, new_error = bang_bang_pid_controller(
            kp, ki, kd, prev_integral, prev_error, desire_seconds, speed, distance
        )

    print("Exiting control_logic")

    return control_data, new_integral, new_error


# Function to apply control
def apply_control(interface, full_control_data):
    print("[apply_control] Function called")

    control_data, new_integral, new_error = full_control_data
    control, value = control_data
    if control == "gas":
        print("[apply_control] Setting gas_pedal_force")
        interface.set_gas_pedal_force(value)
    elif control == "brake":
        print("[apply_control] Setting braking_pedal_force")
        interface.set_braking_pedal_force(value)


if __name__ == "__main__":
    interface = CombinedInterface()
    pool_scheduler = ThreadPoolScheduler(2)

    # Initialize integral and error
    integral, error = 0.0, 0.0

    # Using rx.interval to generate sensor data
    sens_acc_observable = rx.interval(0.01).pipe(
        ops.map(lambda x: get_sensor_data(interface)),
    )

    log_observable = rx.interval(0.1).pipe(
        ops.map(lambda x: "Logging..."),
    )

    merged_observable = rx.merge(sens_acc_observable, log_observable)

    disposable = merged_observable.subscribe(
        on_next=lambda s: apply_control(
            interface, control_logic(s, integral, error, interface)
        )
        if isinstance(s, tuple)
        else None,
        on_error=lambda e: print(f"Error Occurred: {e}"),
        on_completed=lambda: print("Done!"),
        scheduler=pool_scheduler,
    )

    try:
        input("FRP is running. Press any key to exit\n")
    finally:
        disposable.dispose()

# ##
#
#
# # Create the Combined Interface
# combined_interface = CombinedInterface()
#
# # Create a ThreadPoolScheduler
# pool_scheduler = ThreadPoolScheduler(2)
# #
# # # main 100hz Observable sequence
# sens_acc_observable = rx.interval(0.01).pipe(
# ops.map(lambda x: get_sensor_data(combined_interface))
# )
# # # quasi frp way of sending values to redis and dashboard as we are doing it via a log file.
# log_observable = rx.interval(1).pipe(
#     ops.map(lambda y: log_data_every_second(combined_interface))
# )
#
# # Merge observables
# merged_observable = rx.merge(sens_acc_observable, log_observable)
#
# # Create disposable
# # disposable = merged_observable.subscribe(
#
# disposable = merged_observable.subscribe(
#     on_next=lambda s: (
#         print(f"Received: {s}, Type: {type(s)}"),
#         apply_control(combined_interface, control_logic(s)),
#     )
#     if isinstance(s, tuple) and s != ("LOGGING_DONE",)
#     else 1 + 1,
#     # print(f"Skipped: {s}, Type: {type(s)}"),
#     on_error=lambda e: print(f"Error Occurred: {e}"),
#     on_completed=lambda: print("Done!"),
#     scheduler=pool_scheduler,
# )
# try:
#     input("FRP is running, check frp.log ,Press any key to exit\n")
# finally:
#     disposable.dispose()
#
#
# #
# merged_observable = rx.merge(sens_acc_observable, log_observable)
#
#  disposable = merged_observable.subscribe(
#      on_next=lambda s: apply_control(combined_interface, control_logic(s))
#      if isinstance(s, tuple)
#      else None,
#      on_error=lambda e: print(f"Error Occurred: {e}"),
#      on_completed=lambda: print("Done!"),
#      scheduler=pool_scheduler,
#  )
# # try:
# #     print(get_sensor_data(combined_interface))
# #     print(get_sensor_data(combined_interface))
# #     print(get_sensor_data(combined_interface))
# #     print(get_sensor_data(combined_interface))
# #     input("FRP is running, check frp.log ,Press any key to exit\n")
# # finally:
# #     disposable.dispose()

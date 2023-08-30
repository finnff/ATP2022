import rx
from rx.core.observable.observable import Observable
from rx.scheduler.threadpoolscheduler import ThreadPoolScheduler
from rx import operators as ops
from functools import wraps
import time
from combined_interface import CombinedInterface
import logging


# Logged nu naar bestand, zodat code stateless FRP blijft
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


# Pure Function to get sensor data
@timing_decorator
def get_sensor_data(interface):
    seconds = interface.get_desiredSeconds()
    distance = interface.get_distance()
    speed = interface.get_speed()
    return distance, speed


# Pure Function for control logic
@logging_decorator
def control_logic(data):
    distance, speed = data
    if distance > 200:
        return ("gas", 20)
    elif distance < 200:
        return ("brake", -20)
    elif distance < 100:
        return ("brake", -50)


# Function to apply control
def apply_control(interface, control_data):
    control, value = control_data
    if control == "gas":
        interface.set_gas_pedal_force(value)
    elif control == "brake":
        interface.set_braking_pedal_force(value)


# Create the Combined Interface
combined_interface = CombinedInterface()

# Create a ThreadPoolScheduler
pool_scheduler = ThreadPoolScheduler(2)

# Create an Observable sequence
observable = rx.interval(0.05).pipe(
    ops.map(lambda x: get_sensor_data(combined_interface))
)
# observable = Observable.interval(50).map(lambda x: get_sensor_data(combined_interface))

# Subscribe to the observable
disposable = observable.subscribe(
    on_next=lambda s: apply_control(combined_interface, control_logic(s)),
    on_error=lambda e: print(f"Error Occurred: {e}"),
    on_completed=lambda: print("Done!"),
    scheduler=pool_scheduler,
)

try:
    input("Press any key to exit\n")
finally:
    disposable.dispose()

import redis
import time
import torch
from torch.optim import SGD

from combined_interface import CombinedInterface

# Initialize Redis client
redis_client = redis.Redis(host="localhost", port=6379, db=0)


# Function to set PID values in Redis
def set_pid_values(kp, ki, kd):
    redis_client.set("PIDValues", f"{kp} {ki} {kd}")


# Function to get the current system output from Redis
def get_system_output():
    distance_to_voorligger = float(
        redis_client.hget("sim_state", "true_distance_to_voorligger")
    )
    vehicle_speed = float(redis_client.hget("sim_state", "true_vehicle_speed"))

    if vehicle_speed == 0:
        return float("inf")  # To handle division by zero

    return distance_to_voorligger / vehicle_speed


# Initialize PID gains as PyTorch tensors with gradient computation enabled
kp = torch.tensor(1000.0, requires_grad=True)
ki = torch.tensor(0.0, requires_grad=True)
kd = torch.tensor(0.0, requires_grad=True)

optimizer = torch.optim.SGD([kp, ki, kd], lr=0.01)

prev_integral = 0.0
prev_error = 0.0

interface = CombinedInterface()


def apply_control(full_control_data):
    print("[apply_control] Function called")
    control_data, new_integral, new_error = full_control_data
    print(f"[apply_control] Full control data: {full_control_data}")
    control, value = control_data

    if control == "gas":
        print("[apply_control] Setting gas_pedal_force")
        interface.set_gas_pedal_force(value)
    elif control == "brake":
        print("[apply_control] Setting braking_pedal_force")
        interface.set_braking_pedal_force(value)


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


for epoch in range(10000):  # Number of optimization steps
    # Zero the gradients
    optimizer.zero_grad()

    set_pid_values(kp.item(), ki.item(), kd.item())
    # Run the PID controller logic
    desired_seconds_to_voorligger = interface.get_desiredSeconds()
    distance_to_vehicle_in_front = interface.get_distance()
    current_speed = interface.get_speed()

    (control, output), new_integral, new_error = pid_controller(
        kp.item(),
        ki.item(),
        kd.item(),
        prev_integral,
        prev_error,
        desired_seconds_to_voorligger,
        current_speed,
        distance_to_vehicle_in_front,
    )

    print(f"Current PID gains: Kp = {kp.item()}, Ki = {ki.item()}, Kd = {kd.item()}")

    # Apply control
    apply_control(((control, output), new_integral, new_error))

    # Update integral and error
    prev_integral = new_integral
    prev_error = new_error

    # Calculate error and variance (Replace with your own logic)
    error = abs(desired_seconds_to_voorligger - current_speed)
    variance = 0.0  # Compute the variance based on your own logic

    # Convert error and variance to PyTorch tensors
    loss = torch.tensor(error + variance, requires_grad=True)

    # Backward pass to compute gradients
    loss.backward()

    # Update the PID gains
    optimizer.step()

    print(f"Epoch: {epoch+1}, Error: {error}, Variance: {variance}")

# Finally set the optimized PID values in the system
#
#

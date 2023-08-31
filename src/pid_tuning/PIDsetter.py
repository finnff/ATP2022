import redis


def set_starting_conditions(myVel=10.0, myAcc=0.0, voVel=10.0, dist2vo=50.0):
    save_state_to_redis("true_vehicle_speed", myVel)
    save_state_to_redis("true_vehicle_acceleration", myAcc)
    save_state_to_redis("true_voorligger_speed", voVel)
    save_state_to_redis("true_distance_to_voorligger", dist2vo)


def save_state_to_redis(key, value, overrideStateHash="sim_state"):
    redis_client.hset(overrideStateHash, key, value)


def set_pid_values():
    while True:
        try:
            kp, ki, kd = map(
                float,
                input(
                    "Enter the three PID values separated by a space (or 'quit' to exit): "
                ).split(),
            )
            redis_client.set("PIDValues", f"{kp} {ki} {kd}")
        except ValueError:
            set_starting_conditions()
            print("Invalid input. Please enter three floats separated by a space.")
        except KeyboardInterrupt:
            print("\nExiting.")
            break


if __name__ == "__main__":
    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    set_pid_values()

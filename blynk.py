#!/usr/bin/env python3.7
"""Small python script to interact with the blynk HTTP api."""
import sys
import requests

# If you are hosting your own blynk-server, add the url here.

server = "http://blynk-cloud.com"

# Configure your devices here.
# If your devices are wired so that a pin value of LOW is the "on" state,
# change the <default state> field in the tuple for that device from 0 to 1.
# This might happen if your relays are wired as normally closed.

devices = {"<device name>": ("<pin>", "<auth_token>", "<default_state>"),
           "bedroom_light": ("V3", "<auth_token>", 0),
           "kitchen_light": ("d2", "<auth_token>", 1),
           "temperature": ("V6", "<auth_token>"),
           "humidity": ("V5", "<auth_token>")}


# Add the names of devices that are not supposed to be toggled on/off here.

exclude = ("temperature", "humidity")


def set_to_state(device, value):
    """Set a device to the required state."""
    value = value ^ devices[device][2]
    pin, auth_token = devices[device][0], devices[device][1]
    requests.get(f"{server}/{auth_token}/update/{pin}?value={value}")


def get_state(device):
    """Get device state."""
    pin, auth_token = devices[device][0], devices[device][1]
    r = requests.get(f"{server}/{auth_token}/get/{pin}")
    state = int(float(r.json()[0]))

    return state if state not in (0, 1) else int(device not in exclude and state ^ devices[device][2])


def flip_state(device):
    """Invert device state."""
    set_to_state(device, get_state(device) ^ 1)


def apply_function(devices, func, *args):
    """Given a function as an argument, apply function to all given devices.

    Extra arguments, if given, are passed to the function.
    """
    for device in devices:
        func(device, *args)


def get_status_as_dict(devices):
    """Return status of given devices in dict format."""
    status = {}
    for device in devices:
        status[device] = get_state(device)

    return status


def print_status(devices):
    """Prettyprint status of devices."""
    status_dict = get_status_as_dict(args)
    table = ""
    max_len = max(len(x) for x in status_dict) + 1
    for device, status in status_dict.items():
        table += f"{device: <{max_len}}: {status: <{3}} \n"
    table = table[:-1:]
    return table


if __name__ == "__main__":
    *args, action = sys.argv[1:]   # last argument is action to take, others are devices

    if args in (["all"], ["a"]):
        args = [device for device in devices.keys() if device not in exclude or action[:1] in ("s", "p")]

    if action[:1] == "f":          # flip
        apply_function(args, flip_state)
    elif action[:2] == "of":       # off
        apply_function(args, set_to_state, 0)
    elif action == "on":           # on
        apply_function(args, set_to_state, 1)
    elif action[:1] == "j":        # just
        apply_function(args, set_to_state, 1)
        apply_function([device for device in devices.keys() if device not in exclude and device not in args], set_to_state, 0)
    elif action[:1] == "p":        # print
        print(print_status(args))
    elif action[:1] == "s":        # status
        if len(args) != 1:
            print(get_status_as_dict(args))
        else:
            status = get_state(*args)
            print(status)
            sys.exit(status if status in (0, 1) else 0)

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


def toggle(device, value):
    """Toggle a device to required state."""
    value = value ^ devices[device][2]
    pin, auth_token = devices[device][0], devices[device][1]
    requests.get(f"{server}/{auth_token}/update/{pin}?value={value}")


def get(device):
    """Get device state."""
    pin, auth_token = devices[device][0], devices[device][1]
    r = requests.get(f"{server}/{auth_token}/get/{pin}")
    state = int(float(r.json()[0]))

    return state if state not in (0, 1) else state ^ devices[device][2]


def flip(device):
    """Invert device state."""
    toggle(device, get(device) ^ 1)


def apply_func(devices, func, *args):
    """Given a function as an argument, apply function to all given devices.

    Extra arguments, if given, are passed to the function.
    """
    for device in devices:
        func(device, *args)


def getter(devices):
    """Return status of given devices in dict format."""
    status = {}
    for device in devices:
        status[device] = get(device)

    return status


def pretty_status(statusdict):
    """Prettyprint status of all devices."""
    table = ""
    maxlen = max(len(x) for x in statusdict) + 1
    for device, status in statusdict.items():
        table += f"{device: <{maxlen}}: {status: <{3}} \n"
    table = table[:-1:]
    return table


if __name__ == "__main__":
    *args, action = sys.argv[1:]  # last argument is action to take, others are devices

    if args in (["all"], ["a"]):
        args = [device for device in devices.keys() if device not in exclude or action[:1] in ("s", "p")]

    if action[:1] == "f":          # flip
        apply_func(args, flip)
    elif action[:2] == "of":       # off
        apply_func(args, toggle, 0)
    elif action == "on":           # on
        apply_func(args, toggle, 1)
    elif action[:1] == "j":        # just
        apply_func(args, toggle, 1)
        apply_func([device for device in devices.keys() if device not in exclude and device not in args], toggle, 0)
    elif action[:1] == "s":        # status
        if len(args) != 1:
            print(getter(args))
        else:
            status = get(*args)
            print(status)
            sys.exit(int(status))
    elif action[:1] == "p":        # pretty
        print(pretty_status(getter(args)))

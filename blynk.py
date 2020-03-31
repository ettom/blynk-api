#!/usr/bin/env python3
"""Small python script to interact with the blynk HTTP api."""
import sys
import requests
import itertools
import json

# If you are hosting your own blynk-server, change the url here.

server = "http://blynk-cloud.com"

# Configure your devices here.
# If your devices are wired so that a pin value of LOW is the "on" state,
# change the "default" field in the dict for that device from 0 to 1.
# This might happen if your relays are wired as normally closed.
all_devices = {
    "bedroom_light": {"pin": "V3", "auth": "<auth_token>", "default":  0, "group": "bedroom"},
    "kitchen_light": {"pin": "d2", "auth": "<auth_token>", "default":  1, "group": "kitchen"},
    "temperature":   {"pin": "V6", "auth": "<auth_token>", "group": "bedroom_subgroup_1"},
    "humidity":      {"pin": "V5", "auth": "<auth_token>", "group": "bedroom_subgroup_2"}}


# Add the names of devices that are not supposed to be toggled on/off here.
# If a device is listed here, it will only respond to state-changing commands
# if the device is explicitly specified. It will not respond to e.g 'all flip'.
# If a device is not listed here it must have a 0/1 in its "default" field.
exclude = ("temperature", "humidity")

# Add the names of device groups/rooms here. All devices that have the name of
# the group in the corresponding field will respond. Groups can have subgroups,
# which can have subgroups of their own and so on. Avoiding loops is up to the user.
groups = {"bedroom": ["bedroom_subgroup_1"],
          "bedroom_subgroup_1": ["bedroom_subgroup_2"],
          "kitchen": []}


help = """Usage: blynk.py [TARGET(S)] [ACTION]

Small python script to interact with the blynk HTTP api.

Actions:
  on         Turn the device(s) on
  of(f)      Turn the device(s) off
  f(lip)     Flip the device(s)
  j(ust)     Turn the device(s) on and turn off every other device in the same group
  p(rint)    Print the status of the device(s) as a table
  s(tatus)   Print the status of the device(s) in dict/json format
  any int/float for setting a pin to an arbitrary value"""


def process_pin(value, default_state=0):
    """Modify a pin value according to its default state."""
    value = float(value)
    if value.is_integer():
        value = int(value) ^ default_state
    return value


def set_to_state(device, value):
    """Set a device to the required state."""
    value = process_pin(value, all_devices[device]["default"])
    pin, auth_token = all_devices[device]["pin"], all_devices[device]["auth"]
    requests.get(f"{server}/{auth_token}/update/{pin}?value={value}")


def get_state(device):
    """Get device state."""
    pin, auth_token = all_devices[device]["pin"], all_devices[device]["auth"]
    r = requests.get(f"{server}/{auth_token}/get/{pin}")
    default_state = all_devices[device]["default"] if "default" in all_devices[device] else 0
    return process_pin(r.json()[0], default_state)


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
    """Get status of given devices in dict format."""
    return {device: get_state(device) for device in devices}


def print_status(devices):
    """Prettyprint status of devices."""
    status_dict = get_status_as_dict(devices)
    table = ""
    max_len = max(len(x) for x in status_dict) + 1
    for device, status in status_dict.items():
        table += f"{device: <{max_len}}: {status: <{3}}\n"
    table = table[:-1:]
    return table


def get_devices_in_group(group):
    """Find every device in the given group and its subgroups, recursively."""
    devices = list(filter(lambda x: all_devices[x].get("group") == group,
                          all_devices.keys()))
    for subgroup in groups[group]:
        devices += get_devices_in_group(subgroup)

    return devices


def filter_devices(action, devices):
    """Filter a list of devices according to the action and the list of excluded devices."""
    return list(filter(lambda x: x not in exclude or action[:1] in ("s", "p"), devices))


def choose_devices(action, devices):
    """Choose which devices to modify."""
    if len({"all", "al", "a"} & set(devices)) > 0:
        return filter_devices(action, all_devices.keys())
    else:
        return list(itertools.chain(
            *map(lambda x: filter_devices(action, get_devices_in_group(x)) if x in groups else [x], devices)))


def take_action(action, devices):
    """Take action on given devices."""
    if action[:1] == "f":          # flip
        apply_function(devices, flip_state)
    elif action[:2] == "of":       # off
        apply_function(devices, set_to_state, 0)
    elif action == "on":           # on
        apply_function(devices, set_to_state, 1)
    elif action[:1] == "j":        # just
        groups_to_modify = map(lambda x: get_devices_in_group(all_devices[x]["group"]), devices)
        devices_to_turn_off = [device for device in list(itertools.chain(*groups_to_modify))
                               if device not in devices
                               and device not in exclude]

        apply_function(devices_to_turn_off, set_to_state, 0)
        apply_function(devices, set_to_state, 1)
    elif action[:1] == "p":        # print
        print(print_status(devices))
    elif action[:1] == "s":        # status
        print(json.dumps(get_status_as_dict(devices)) if len(devices) != 1 else get_state(*devices))
    else:                          # set
        action = float(action)
        apply_function(devices, set_to_state, action)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(help)
    else:
        *args, action = sys.argv[1:]

        devices_to_modify = choose_devices(action, args)
        take_action(action, devices_to_modify)

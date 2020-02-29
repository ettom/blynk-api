# blynk-lightswitch
Small python script to interact with the blynk HTTP api.

## Requirements

Python 3.6+ <br>
The `requests` library is needed for communication with the server.

## Usage

The general syntax for arguments is:

`./blynk.py target action`

where `target` can be a single device name, any combination of device names, a name of a
group or `all` / `a` for targeting every device.

The `action` part can be any of the following:
```
on        # Turn the device(s) on
of(f)     # Turn the device(s) off
f(lip)    # Flip the device(s)
j(ust)    # Turn the device(s) on and turn off every other device in the same group
p(rint)   # Print the status of the device(s) as a table
s(tatus)  # Print the status of the device(s) in dict/json format
any int/float for setting a pin to an arbitrary value
```

Some usage examples:

```
./blynk.py all on
./blynk.py bedroom_light kitchen_light off
./blynk.py kitchen f
./blynk.py a p
```

## Installation
To install the `requests` library:

`pip3 install requests`

Open `blynk.py` in a text editor and define your devices there, then copy the script to a directory in your `$PATH`.

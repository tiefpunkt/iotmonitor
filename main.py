import sensors
import csv
import time
import pushjet

import config


def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in all_subclasses(s)]


# Find all device types
devtypes = {}
for devtype in all_subclasses(sensors.Device):
    devtypes[devtype.__name__] = devtype

# Read devices
devices = []
with open(config.devices_file, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        devices.append(devtypes[row[1]](row[0], row[2]))

# Get offline devices
offline_devices = {}
try:
    with open(config.offline_file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            offline_devices[row[0]] = row[1]
except FileNotFoundError:
    pass

# Init pushjet
pj_service = pushjet.Service(config.pushjet_key)
#
# for device in devices:
#    state = device.getState()
#
#    state_out = "X" if state else " "
#    print("[%s]  %s" % (state_out, device.name))

for key, devtype in devtypes.items():
    filtered_devices = [device for device in devices if type(device) == devtype]
    if len(filtered_devices) > 0:
        print(devtype.__name__)
        for device in filtered_devices:
            state = device.getState()

            state_out = "X" if state else " "
            print("[%s]  %s" % (state_out, device.name))

            state_prev = device.name not in offline_devices
            if state_prev != state:
                if state:
                    offline_devices.pop(device.name)
                    text = "%s (%s) is back online" % (device.name, devtype.__name__)
                    pj_service.send(text)
                    print(text)
                else:
                    offline_devices[device.name] = time.time()
                    text = "%s (%s) is now offline" % (device.name, devtype.__name__)
                    pj_service.send(text)
                    print(text)

with open(config.offline_file, 'w') as csvfile:
    for name, timestamp in offline_devices.items():
        csvfile.write("%s,%s\n" % (name, timestamp))

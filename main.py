import sensors

import csv

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in all_subclasses(s)]

# Find all device types
devtypes = {}
for devtype in all_subclasses(sensors.Device):
    devtypes[devtype.__name__] = devtype

# Read devices
devices = []
with open('devices.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        devices.append(devtypes[row[1]](row[0], row[2]))
#
#for device in devices:
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

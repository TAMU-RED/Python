"""
Base Session Class
author: Adam Johnston

Each testing session will be an instance of this class. It will be responsible
for the following:
    Sensor Data: Session.sensors will hold a list of Sensor objects as such:
        [sensor_1, sensor_2, None, sensor_3]
        where None represents an empty port
    Conversions: each sensor will have a corresponding conversion function:
        data = sensor_1.convert(raw_data)
        (see Sensor class for more info)
    Check Thresholds / Trigger Shutdown: On each cycle this class will check for
        sensors outside their acceptable values and keep track of how long (in ms)
        they are outside this range. If this time is larger than the acceptable
        time (saved as Sensor.shutdown_time), the shutdown sequence will begin.
    Logging Data: Will write to a log file every Session.log_interval cycles
    Managing Data Buffer: Will hold Session.buffer_length cycles of data
    Prepare Data for GUI: Label data and encode to JSON

Like the Sensor class, the Session class can take a dict input as such:
    my_session = Session(**dict)
where dict can be a parsed JSON object. This will allow us to create and save
templates for different testing setups.

TODOS:
    Ensure Arduino is giving data in correct order:
        IDEA: Send data in form port:data, i.e. '12:134,25:150' would be
              port 12 = 134, port 25 = 150

CONSIDERATIONS:
    Should ports be zero indexed?
    Should we keep track of every delta t for more accurate time series?
    Should we create a microcontroller class to attach and determine ports?
"""
import numpy as np
import json
from datetime import datetime

class Session:
    def __init__(self, name, ports, log_dir, log_interval, buffer_length):
        # TODO: Hash ID
        # Name of session
        self.name = name
        # List of available ports i.e. [12, 13, 15, 19]
        self.ports = ports
        # Init empty sensor List
        self.sensors = [None] * len(ports)
        # List to track threshold times
        self.threshold_times = np.array([[0, 0]] * len(ports))
        # Name of log directory
        self.log_dir = log_dir
        # Frequency of logging in cycles
        self.log_interval = log_interval
        # Number of cycles to hold in buffer
        self.buffer_length = buffer_length
        # TODO: Initialize buffer (circular?)
        # Init cycle_number
        self.cycle_number = 0
        # Init times list
        self.times = [0]

    # Begin session
    def start(self):
        # TODO: Check for existing log_dir / create directory
        self.clock = datetime.now()

    # TODO: End session

    # Attach a sensor to a specified port
    def attach(self, sensor, port):
        # Check if port is in use
        if self.sensors[port]:
            raise ConnectionError('Port %d in use' % port)
        # Attach sensor
        self.sensors[port] = sensor
        # TODO: create or lookup conversion function

    # Complete a cycle of data collection
    def cycle(self):
        # Init empty cycle list
        cycle_data = [None] * len(self.ports)
        # TODO: Create collection function to communicate with Arduino.
        #       Should return string of form "123,345,..."
        # TODO: Parse Arduino output
        #       Should return np.array([123, 345, ...]) in same order as self.ports
        #       Save as variable data
        # Get time since last reading
        time_diff = datetime.now() - self.clock
        # Convert to milliseconds
        cycle_time = time_diff.seconds * 1000 + time_diff.microseconds // 1000
        # Append to times
        self.times.append(self.times[self.cycle_number] + cycle_time)
        # Update cycle number
        self.cycle_number += 1
        # Init iterator to track sensors and skip empty ports
        i = 0
        # Loop thru sensors
        # NOTE: port is an index corresponding to self.ports, not the actual
        #       port number
        for port, sensor in enumerate(self.sensors):
            # Check if port has sensor
            if sensor:
                # Check threshold
                # NOTE: When should we reset times?
                if data[i] - sensor.precision * data[i] < sensor.threshold[0]:
                    self.threshold_times[port][0] += cycle_time
                elif data[i] + sensor.precision * data[i] > sensor.threshold[1]:
                    self.threshold_times[port][1] += cycle_time
                # TODO: check for shutdown
                # Get data from parsed Arduino output
                # NOTE: Should we convert here or later?
                cycle_data[port] = sensor.convert(data[i])
                # TODO: Add to buffer
                # TODO: If self.cycle_number % self.log_interval write to log
                # Move to next item in data
                i += 1
        # Reset clock
        self.clock = datetime.now()

    # Get data going back (cycle_number - last_cycle) cycles (to be sent to GUI)
    # Returns JSON of form:
    #   {"sensor_1": {"data": [123, 456, 788], "units": "Pa"},..., "times": [1024, 1037,...]}
    def get_data(self, last_cycle):
        # Determine how far to go back
        num_cycles = self.cycle_number - last_cycle
        # Create dict
        data_dict = {}
        # NOTE: port is an index corresponding to self.ports, not the actual
        #       port number
        for port, sensor in enumerate(self.sensors):
            data_dict[sensor.name] = {'data': self.buffer[port][-num_cycles:],
                                      'units': sensor.units}
            data_dict['times'] = self.times[-num_cycles:]
        # Encode and return JSON data and most recent cycle_number
        # NOTE: cycle_number will become last_cycle on next call from GUI
        return json.JSONEncoder().encode(data_dict), self.cycle_number

    # TODO: initiate shutdown sequence

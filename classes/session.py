"""
Base Session Class
author: Adam Johnston

Each testing session will be an instance of this class. It will be responsible
for the following:
    Sensor Data: Session.sensors will hold a list of Sensor objects as such:
        [sensor_1, sensor_2, None, sensor_3]
        where None represents an empty port
    Conversions: each sensor will have corresponding conversion functions:
        data = sensor_1.convert(raw_data, index)
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
import os
import numpy as np
import h5py
import json
from time import time
import serial

class Session:
    def __init__(self, name, ports, log_dir, log_interval, buffer_length, com_port, log_size=10e3):
        # TODO: Hash ID
        # Name of session
        self.name = name
        # List of available ports i.e. [12, 13, 15, 19]
        self.ports = ports
        # Init empty sensor List
        self.sensors = [None]*len(ports)
        # Sub sensor list
        self.sub_sensors = [None]*len(ports)
        # List to track threshold times
        self.threshold_times = np.array([None]*len(ports))
        # Name of log directory
        self.log_dir = log_dir
        # Frequency of logging in cycles
        self.log_interval = log_interval
        # Resize interval / initial length of log file (per sensor + times)
        self.log_size = log_size
        # Counter of resizes
        self.num_log_resizes = 1
        # Number of cycles to hold in buffer
        self.buffer_length = buffer_length
        # Init empty buffer
        self.buffer = np.array([None]*len(ports))
        # Cursor for circular buffer
        # NOTE: Points to NEXT index of buffer such that
        # buffer[cursor - 1] is the most recent item
        self.cursor = 0
        # Init cycle_number
        self.cycle_number = 0
        # Init trial number
        self.trial = 0
        # Init times list
        self.times = np.zeros(self.buffer_length)
        # TODO: Use board class
        self.board = serial.Serial(com_port, 9600)

    # Begin session
    def start(self):
        connected = False
        # TODO: Send confirmation signal
        # while not connected:
        #     serial_in = self.board.readline()
        #     break
        # TODO: Check for existing log_dir / create directory
        self.trial += 1
        self.init_log()
        self.clock = time()
        print('Started')
    # TODO: End session

    # Attach a sensor to a specified port
    def attach(self, sensor, port):
        # Check if port is in use
        if self.sensors[port]:
            raise ConnectionError('Port %d in use' % port)
        # Attach sensor
        self.sensors[port] = sensor
        # Create threshold counters for each sub sensor
        self.threshold_times[port] = [np.array([0, 0])]*len(sensor.sub_sensors)
        # TODO: create or lookup conversion function
        # Add individual sensor names
        self.sub_sensors[port] = [name for name in sensor.sub_sensors]
        # TODO: Initialize buffer (circular?)
        # Buffer of form [ [sensor 1 data],
        #                  [sensor 2 data],
        #                   ...          ]
        self.buffer[port] = np.array([ [None]*len(sensor.sub_sensors) ]*self.buffer_length)

    # Complete a cycle of data collection
    def cycle(self, first_run=False):
        # Wait until start of next cycle to ensure we are in sync
        if first_run:
            print('Syncing...')
            c = self.board.read().decode('utf-8', 'ignore')
            while c != '?':
                c = self.board.read().decode('utf-8', 'ignore')
            return
        # Init empty string
        data_string = self.read_serial()
        # Init data array
        data = np.array([None]*len(self.ports))
        # Get time since last reading (in ms)
        cycle_time = (time() - self.clock) * 1000
        # Loop through data
        for port_data in data_string.split(';'):
            # Parse data
            parse_error, port_index, temp_data = self.parse_serial(port_data)
            # Data not read
            if not temp_data:
                continue
            # Check for parsing error
            if parse_error[0]:
                print('Parsing Error:', parse_error[1])
                continue
            # Convert data and check thresholds
            conversion_error, converted_data, should_shutdown = self.check_thresholds(port_index, temp_data, cycle_time)
            # Check for shutdown
            if should_shutdown:
                print('SHUT IT DOWN!')
                # TODO: Actual shutdown sequence
            # Check for conversion error
            if conversion_error[0]:
                print('Conversion Error:', conversion_error[1])
                # TODO: Possibly replace value
            # Add to data buffer
            print(converted_data)
            self.buffer[port_index][self.cursor] = converted_data
        print('Current:')
        print(self.buffer[0][self.cursor])
        print('')
        print('Last 5:')
        print(self.get_last_n_indices(5))
        print(self.buffer[0][self.get_last_n_indices(5)])
        print('')
        # Append to times
        self.times[self.cursor] = self.times[self.cursor-1] + cycle_time
        # Add data to log file
        if self.cycle_number % self.log_interval == 0:
            print('Logging...')
            self.log_data()
        # Update cycle number
        self.cycle_number += 1
        # Update buffer cursor
        self.cursor = self.cycle_number % self.buffer_length
        # Reset clock
        self.clock = time()

    # Get data from Arduino
    def read_serial(self):
        # Init empty string
        data_string = ''
        # Read first character
        c = self.board.read().decode('utf-8', 'ignore')
        # Read until end char (?) is reached
        while c != '?':
            # Add to string
            data_string += c
            # Get next char
            c = self.board.read().decode('utf-8', 'ignore')
        return data_string

    # Parse string from Arduino, returns [(error, message), port_index, data]
    def parse_serial(self, port_data):
        # Error flag
        error = False
        # Get port number
        port_number = port_data.split(':')[0]
        # Check if port is found (if not skip)
        if len(port_number) == 0:
            return (error, None), None, None
        else:
            # string -> integer
            port_number = int(port_number)
        try:
            # Get index of port
            port_index = self.ports.index(port_number)
        # Port not found in list of ports
        # TODO: More thorough handling of error
        except ValueError as e:
            error = True
            print(e)
            return (error, e), None, None
        # Get data from port
        temp_data = port_data.split(':')[1]
        return (error, None), port_index, temp_data

    # Check tresholds
    def check_thresholds(self, port_index, temp_data, cycle_time):
        # Shutdown flag
        shutdown = False
        # Error flag
        error = False
        # Get corresponding sensor information
        sensor = self.sensors[port_index]
        # With quick cycles, data is sometimes corrupted
        try:
            # assign value(s) to index of port in data array
            temp_data = np.array([float(x) for x in temp_data.split(',')])
            # Convert data
            converted_data = np.array([sensor.convert(x, i) for i, x in enumerate(temp_data)])
            # Check thresholds
            for i, threshold in enumerate(sensor.thresholds):
                # Below min
                if converted_data[i] - sensor.precisions[i] * converted_data[i] < threshold[0]:
                     self.threshold_times[port_index][i][0] += cycle_time
                # Above max
                elif converted_data[i] + sensor.precisions[i] * converted_data[i] > threshold[1]:
                     self.threshold_times[port_index][i][1] += cycle_time
            # TODO: check for shutdown
        except ValueError as e:
            # TODO: Maybe repeat previous value?
            error = True
            converted_data = np.array([None])
            return (error, e), converted_data, shutdown
        return (error, None), converted_data, shutdown

    # Initialize log file
    def init_log(self):
        # Try to create log directory
        try:
            os.makedirs(self.log_dir)
        # TODO: Better error handling
        except OSError:
            print('Creation of log directory %s failed' % self.log_dir)
        else:
            print('Created log directory %s' % self.log_dir)
        # Create .hdf5 file
        filename = 'trial_' + str(self.trial) + '.hdf5'
        self.filename = filename
        try:
            with h5py.File(self.log_dir + '/' + filename, 'x') as f:
                # Create main groups
                times = f.create_group('times')
                times.create_dataset('t', (self.log_size,), maxshape=(None,))
                # NOTE: port is index of port
                # Loop thru sensors and create groups / sub-groups
                # TODO: More than just data, i.e. thresholds
                for port, sensor in enumerate(self.sensors):
                    if sensor:
                        group = f.create_group(sensor.name)
                        for i, sub_sensor in enumerate(sensor.sub_sensors):
                            sub_group =group.create_group(sub_sensor)
                            sub_group.create_dataset('data', (self.log_size,), maxshape=(None,))
        # TODO: Send error to GUI
        # File exists
        except OSError:
            print('Trying to overwrite file %s in directory %s' % (filename, self.log_dir))


    # Log data to log file
    def log_data(self):
        indices = self.get_last_n_indices(self.log_interval)
        with h5py.File(self.log_dir + '/' + self.filename, 'a') as f:
            should_resize = False
            try:
                f['times']['t'][indices[0]:indices[-1]+1] = self.times[indices]
            except TypeError as e:
                # Add to resize counter
                self.num_log_resizes += 1
                # TODO: Grab actual error
                new_size = (self.log_size * self.num_log_resizes)
                f['times']['t'].resize()
                should_resize = True
            for port_index, sensor in enumerate(self.sensors):
                # Transpose so that sub sensors are rows
                port_data = self.buffer[port_index][indices].T
                for i, sub_sensor in enumerate(sensor.sub_sensors):
                    dset = f[sensor.name][sub_sensor]['data']
                    if should_resize:
                        dset.resize(new_size)
                    # TODO: Replace None entries
                    dset[self.cycle_number-self.log_interval:self.cycle_number] = np.array([d if d else 0 for d in port_data[i]])

    # Get data going back (cycle_number - last_cycle) cycles (to be sent to GUI)
    # Returns JSON of form:
    #   {"sensor_1": {"data": [123, 456, 788], "units": "Pa"},..., "times": [1024, 1037,...]}
    def get_gui_data(self, last_cycle):
        # Get current cycle
        current_cycle = self.cycle_number
        # Determine how far to go back
        num_cycles = current_cycle - last_cycle
        # Create dict
        data_dict = {}
        # Get data from buffer
        indices = self.get_last_n_indices(num_cycles)
        # NOTE: port is an index corresponding to self.ports, not the actual
        #       port number
        for port, sensor in enumerate(self.sensors):
            data_dict[sensor.name] = {'data': self.buffer[port][indices]}
            data_dict['times'] = self.times[indices]
        # Encode and return JSON data and most recent cycle_number
        # NOTE: current_cycle will become last_cycle on next call from GUI
        return json.JSONEncoder().encode(data_dict), current_cycle

    # TODO: initiate shutdown sequence
    # Possibly set shutdown pin to HIGH

    # Get last n indices from buffer using cursor
    def get_last_n_indices(self, n):
        cursor = self.cursor
        indices = np.arange(self.buffer_length)
        # Need to wrap back to beginning
        if cursor - n < 0:
            return np.concatenate((indices[cursor-n:], indices[:cursor]))
        # Do not need to wrap
        else:
            return indices[cursor-n:cursor]

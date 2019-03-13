"""
Base Client Class
author: Adam Johnston

Class for client side (computer) to log data and handle GUI communication
"""

import numpy as np
import asyncio
import websockets
import os
import h5py
import json

class Client:
    def __init__(self, sensors, ip, port, log_dir, log_file, log_size=10e3):
        # List of sensors from session (instance of Sensor class)
        self.sensors = sensors
        # IP Address of RPi
        self.ip = ip
        # Websocket port for RPi
        self.port = port
        # Name of log directory
        self.log_dir = log_dir
        # Name of log file
        self.log_file = log_file
        # Resize interval / initial length of log file (per sensor + times)
        # Default: 1 kB per sensor
        self.log_size = log_size
        # Counter of resizes
        self.num_log_resizes = 1
        # Initialize log
        self.init_log()

    # Start client
    def start(self):
        asyncio.get_event_loop().run_until_complete(self.listen())

    # Open port and listen
    async def listen(self):
        async with websockets.connect('ws://' + str(self.ip) + ':' + str(self.port)) as websocket:
            print('Connected to port %s' % self.port)
            while True:
                print('Listening...')
                json_data = await websocket.recv()
                print('Received data...')
                data = json.JSONDecoder().decode(json_data)
                print(data)
                if data['action'] == 'LOG_UPDATE':
                    self.log_data(data)

    # Initialize log file
    def init_log(self):
        # Loop until successful
        dir_error = True
        dir_name = self.log_dir
        if dir_name[-1] == '/':
            dir_name = dir_name[:-1]
        while dir_error:
            # Try to create log directory
            try:
                os.makedirs(dir_name)
            # TODO: Better error handling
            except OSError as e:
                print(e)
                print('Creation of log directory %s failed' % dir_name)
                # Prompt for new directory name
                # TODO: Select from GUI
                add_to_existing_dir = input('Add logs to existing directory %s? [y/n] ' % dir_name)
                if add_to_existing_dir and add_to_existing_dir.lower()[0] == 'y':
                    print('Adding log to directory %s' % dir_name)
                    break
                dir_name = input('New directory name: ')

            else:
                self.log_dir = dir_name
                print('Created log directory %s' % self.log_dir)
                dir_error = False
        # Create .hdf5 file
        # TODO: Select in GUI
        if not self.log_file:
            filename = input('Log file name: ')
        else:
            filename = self.log_file
        # Check for file extension
        if filename[-5:] != '.hdf5':
            filename += '.hdf5'
        # Loop until successful
        filename_error = True
        # Create new, error if exists
        open_type = 'x'
        while filename_error:
            try:
                with h5py.File(self.log_dir + '/' + filename, open_type) as f:
                    # Create main groups
                    times = f.create_group('times')
                    times.create_dataset('t', (self.log_size,), maxshape=(None,))
                    # NOTE: port is index of port
                    # Loop thru sensors and create groups / sub-groups
                    # TODO: More than just data, i.e. thresholds
                    for port, sensor in enumerate(self.sensors):
                        if sensor:
                            group = f.create_group(sensor.name)
                            for sub_sensor in sensor.sub_sensors:
                                sub_group = group.create_group(sub_sensor)
                                sub_group.create_dataset('data', (self.log_size,), maxshape=(None,))
            # TODO: Send error to GUI
            # File exists
            # TODO: Create metadata for files so that logs can be continued
            except OSError:
                print('File %s already exists in directory %s' % (filename, self.log_dir))
                should_overwrite = input('Overwrite log file? [y/n] ')
                if should_overwrite and should_overwrite.lower()[0] == 'y':
                    confirm_overwrite = input('Are you sure? All previous data will be lost [y/n] ')
                    if confirm_overwrite and confirm_overwrite.lower()[0] == 'y':
                        print('Overwriting data in log file %s' % filename)
                        self.log_file = filename
                        # Overwrite old file
                        open_type = 'w'
                        break
                filename = input('New filename: ')

            else:
                self.log_file = filename
                print('Created log file %s in directory %s' % (self.log_file, self.log_dir))
                filename_error = False

    # Log data to log file
    def log_data(self, dataset):
        # Write to hdf5 file
        with h5py.File(self.log_dir + '/' + self.log_file, 'a') as f:
            should_resize = False
            start_index = len(f['times']['t'][:])
            end_index = start_index + len(dataset['times']['t'])
            # Try writing to file (to check if full)
            try:
                f['times']['t'][start_index:end_index] = dataset['times']['t']
            except TypeError as e:
                # Add to resize counter
                self.num_log_resizes += 1
                # TODO: Grab actual error
                # Calc new size
                new_size = self.log_size * self.num_log_resizes
                # Resize and write times
                f['times']['t'].resize(new_size)
                f['times']['t'][start_index:end_index] = self.times[indices]
                # Flag for other dsets
                should_resize = True
            # Loop thru sensors
            for main_key, sensor_data in dataset.items():
                # Ignore non-sensor data
                if main_key in [s.name for s in self.sensors]:
                    # Loop thru each sub sensor
                    for sub_key, sub_data in sensor_data.items():
                        dset = f[main_key][sub_key]['data']
                        # Resize if necessary
                        if should_resize:
                            dset.resize(new_size)
                        # Write data
                        dset[start_index:end_index] = sub_data

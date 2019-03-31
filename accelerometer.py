accelerometer = {'name': 'Accelerometer',
                 'sub_sensors': ['temp'],
                 'model': 'AC5000',
                 'ranges': [[-90, 90]],
                 'precisions': [0.01],
                 'thresholds': [[0, 100]],
                 'shutdown_times': [[500, 500]],
                 'conversions': ['x * 2'],
                 'units': ['Kevins'],
                 'documentation': 'google.com',
                 'position': [0, 0]}

session = {'name': 'Test Session',
           'ports': [17],
           'log_dir': 'Logs',
           'log_interval': 5,
           'buffer_length': 100000,
           'com_port': 'COM11'}

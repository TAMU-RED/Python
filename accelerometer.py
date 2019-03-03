accelerometer = {'name': 'Accelerometer',
                 'sub_sensors': ['temp', 'pressure'],
                 'model': 'AC5000',
                 'ranges': [[-90, 90], [-100, 100]],
                 'precisions': [0.01, 0.02],
                 'thresholds': [[0, 100], [100, 200]],
                 'shutdown_times': [[500, 500], [500, 500]],
                 'conversions': ['x * 2', None],
                 'units': ['Kevins', 'JiggaPascals'],
                 'documentation': 'google.com',
                 'position': [0, 0]}

session = {'name': 'Test Session',
           'ports': [17],
           'log_dir': 'Logs',
           'log_interval': 5,
           'buffer_length': 100000,
           'com_port': 'COM11'}

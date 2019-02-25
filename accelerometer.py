accelerometer = {'name': 'Accelerometer',
                 'model': 'AC5000',
                 'range': [-90, 90],
                 'precision': 0.01,
                 'threshold': [0, 100],
                 'shutdown_time': [500, 500],
                 'conversion': 'x * 2',
                 'units': 'JiggaPascals',
                 'documentation': 'google.com',
                 'position': [0, 0]}

session = {'name': 'Test Session',
           'ports': [17, 18],
           'log_dir': 'Logs',
           'log_interval': 20,
           'buffer_length': 100000}

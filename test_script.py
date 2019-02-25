from sensational import Sensor, Session
from accelerometer import accelerometer, session
import numpy as np

# Init sensors
accelerometer = Sensor(**accelerometer)

# Init test session
sess = Session(**session)

# Start session
sess.start()
# Attach sensors
sess.attach(accelerometer, 0)

# Read data
i = 0
sess.cycle(first_run=True)
while True:
    sess.cycle()
    # print('data:', sess.buffer[-np.min(len(sess.buffer), 5):])
    print('time:', sess.times[i] - sess.times[i-1])
    i += 1

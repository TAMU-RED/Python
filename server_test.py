from sensational import Sensor, Session, Server
from accelerometer import accelerometer, session

# Init sensors
accelerometer = Sensor(**accelerometer)

# Init test session
sess = Session(**session)

# Attach sensors
sess.attach(accelerometer, 0)

# Create server
server = Server(sess, 5000)

# Start server
server.start()

from sensational import Sensor, Session, Server
from accelerometer import accelerometer, session
import argparse

# Commmand line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', help='Serial port of Arduino', required=True)
args = parser.parse_args()
session['com_port'] = args.port

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

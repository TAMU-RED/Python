from sensational import Sensor, Session, Server
from accelerometer import accelerometer, session
import argparse

# Commmand line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--serial', help='Serial port of Arduino', required=True)
parser.add_argument('-p', '--port', help='Websocket port', required=True)
parser.add_argument('--log_interval', help='Number of cycles between logs', default='20')
args = parser.parse_args()
session['com_port'] = args.serial
session['log_interval'] = int(args.log_interval)

# Init sensors
accelerometer = Sensor(**accelerometer)

# Init test session
sess = Session(**session)

# Attach sensors
sess.attach(accelerometer, 0)

# Create server
server = Server(sess, args.port)

# Start server
server.start()

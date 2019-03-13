from sensational import Sensor, Client
from accelerometer import accelerometer, session
import argparse

# Commmand line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip_address', help='IP address of server', default='localhost')
parser.add_argument('-p', '--port', help='Websocket port', required=True)
parser.add_argument('--log_dir', help='Directory for log files', default='Logs')
parser.add_argument('--log_file', help='Log file name (no extension)', default='test')
args = parser.parse_args()

# Get sensor info
acc = Sensor(**accelerometer)
# Create client
client = Client([acc], args.ip_address, args.port, args.log_dir, args.log_file)

# Start client
client.start()

from sensational import Sensor, Client
from accelerometer import accelerometer, session

# Get sensor info
acc = Sensor(**accelerometer)
# Create client
client = Client([acc], '192.168.1.2', 5000, 'Logs', 'test', 20)

# Start client
client.start()

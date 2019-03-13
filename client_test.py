from sensational import Client
from accelerometer import accelerometer, session

client = Client([accelerometer], 5000, 'Logs', 'test', 20)

client.start()

"""
Base Server Class
author: Adam Johnston

Class for server side (RPi) to initiate session and send data to client
"""

import numpy as np
import asyncio
import websockets
import json

class Server:
    def __init__(self, session, port):
        # Fully initialized Session instance
        self.session = session
        # Websocket port
        self.port = port
        # Clients
        self.clients = set()

    # Start server
    def start(self):
       asyncio.get_event_loop().run_until_complete(
           websockets.serve(self.main, '', self.port)
       )
       asyncio.get_event_loop().run_forever()
#       while True:
#           self.session.start()
#           while True:
#               self.session.cycle()

    # Main server function
    async def main(self, websocket, path):
        await self.add_client(websocket)
        try:
            while True:
                if not self.session.is_running:
                    print('Starting Session...')
                    # Init session
                    self.session.start()
                    self.session.is_running = True
                # Execute next cycle
                print('Reading Serial...')
                print('')
                data, time, should_log = next(self.session.__iter__())
                if should_log:
                    await self.send_log_data(websocket)
                # Listen for client requests
                self.request_handler(websocket)
        finally:
            # Disconnect client
            await self.remove_client(websocket)

    async def add_client(self, websocket):
        self.clients.add(websocket)
        print('Added client')

    async def remove_client(self, websocket):
        self.clients.remove(websocket)
        print('Client disconnected')

    # Handle sending log data
    async def send_log_data(self, websocket):
        dset, _ = self.session.get_log_data()
        dset['action'] = 'LOG_UPDATE'
        if self.clients:
            print('Sending data...')
            await asyncio.wait([client.send(json.JSONEncoder().encode(dset)) for client in self.clients])
            print('Data sent')

    # Handle client requests
    async def request_handler(self, websocket):
        # Get requests
        request = await websocket.recv()
        # Split request
        action, payload = request.split('::')
        # Event handler
        if action == 'GET_DATA':
            data = self.session.get_gui_data(payload)
            await websocket.send(data)

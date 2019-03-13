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
            websockets.serve(self.main, '127.0.0.1', self.port)
        )
        asyncio.get_event_loop().run_forever()

    # Main server function
    async def main(self, websocket, path):
        await self.add_client(websocket)
        try:
            if not self.session.is_running:
                self.session.is_running = True
                await self.run_session(websocket)
                await self.request_handler(websocket)
        finally:
            await self.remove_client(websocket)

    async def add_client(self, websocket):
        self.clients.add(websocket)
        print('Added client')

    async def remove_client(self, websocket):
        self.clients.remove(websocket)
        print('Client disconnected')

    # Run test session
    async def run_session(self, websocket):
        # Start session
        self.session.start()
        # Begin cycling
        for data, time, should_log in self.session:
            if should_log:
                await self.send_log_data(websocket)

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
        while True:
            message = await websocket.recv()
            # Split request
            action, payload = request.split('::')
            # Event handler
            if action == 'GET_DATA':
                websocket.send(self.session.get_gui_data(payload))

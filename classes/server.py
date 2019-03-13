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
        self.run_session()
        asyncio.get_event_loop().run_until_complete(
            websockets.serve(self.main, 'localhost', self.port)
        )
        asyncio.get_event_loop().run_forever()

    # Main server function
    async def main(self, websocket, path):
        await self.add_client(websocket)
        try:
            self.request_handler(websocket)
        finally:
            self.remove_client(websocket)

    def add_client(self, websocket):
        self.clients.add(websocket)

    def remove_client(self, websocket):
        self.clients.remove(websocket)

    # Run test session
    def run_session(self):
        # Start session
        self.session.start()
        # Begin cycling
        for data, time, should_log in self.session:
            if should_log:
                self.send_log_data()

    # Handle sending log data
    async def send_log_data(self):
        dset, _ = self.session.get_log_data()
        dset['action'] = 'LOG_UPDATE'
        if self.clients:
            asyncio.wait([client.send(json.JSONEncoder.encode(dset)) for client in self.clients])

    # Handle client requests
    async def request_handler(self, websocket):
        # Get requests
        async for request in websocket:
            # Split request
            action, payload = request.split('::')
            # Event handler
            if action == 'GET_DATA':
                websocket.send(self.session.get_gui_data(payload))

#!/usr/bin/env python

# WS server example

import asyncio
import websockets
import argparse

import messages_pb2

parser = argparse.ArgumentParser(description='Launch the Resource Manager Master')
parser.add_argument('--host', required=True, help='the LAN IP to bind to.')
parser.add_argument('--port', required=True, help='the local machine port to bind to.')
args = parser.parse_args()

STATE = {"counter": 0}
SLAVES = dict()

async def register_slave(websocket, wrapper):
	print("Registering slave...")
	STATE['counter'] += 1
	
	# build slave info
	slave_info = {"id":STATE['counter']}
	for resource in wrapper.register_slave.slave.resources:
		slave_info[resource.name] = resource.scalar.value

	# set info
	SLAVES[websocket] = slave_info

	print("Current slaves:", SLAVES)

	# send response message
	response = messages_pb2.WrapperMessage()
	response.slave_registered.slave_id.value = str(slave_info['id'])
	await websocket.send(response.SerializeToString())

async def unregister_slave(websocket):
	del SLAVES[websocket]
	print("Slave disconnected...")

async def entry(websocket, path):
	try:
		while True:
			msg = await websocket.recv()

			wrapper = messages_pb2.WrapperMessage()
			wrapper.ParseFromString(msg)

			if wrapper.HasField('register_slave'):
				await register_slave(websocket, wrapper)
			else:
				print("Unsupported message...")
	except websockets.exceptions.ConnectionClosedError:
		pass
	finally:
		await unregister_slave(websocket)


start_server = websockets.serve(entry, host=args.host, port=args.port)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
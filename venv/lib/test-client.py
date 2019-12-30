import asyncio
import websockets as ws
import json


async def connectAndSend(msg='default'):
    async with ws.connect('ws://50.18.144.216:5000') as websocket:

        await websocket.send(msg)

        receive = await websocket.recv()
        print(receive)




asyncio.get_event_loop().run_until_complete(connectAndSend('input'))



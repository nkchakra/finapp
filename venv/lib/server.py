import os,sys
import asyncio
import websockets as ws
import json

from threading import Thread, ThreadError
from multiprocessing.pool import ThreadPool


async def process_request(websocket, path):
    request = await websocket.recv()
    await websocket.send(ThreadPool(processes=1).apply_async(threaded_request, (request,)).get())

def threaded_request(request):

    return json.dumps({'temp':'temp'})

def main():
    server = ws.serve(process_request, 'localhost',5555)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

if __name__=='__main__':
    main()

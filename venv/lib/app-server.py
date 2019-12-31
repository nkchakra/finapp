import websockets

import os,sys
import asyncio
import websockets as ws
import json

from threading import Thread, ThreadError
from multiprocessing.pool import ThreadPool


hostname = '0.0.0.0'
portno = 5000


async def process_request(websocket,path):
    request = await websocket.recv()
    global COUNT
    COUNT += 1
    await websocket.send(ThreadPool(processes=1).apply_async(threaded_request, (request,)).get())

def threaded_request(request):

def main():
    server = ws.serve(process_request, hostname,portno)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()




if __name__=='__main__':
    main()

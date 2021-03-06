import os,sys
import asyncio
import websockets as ws
import json

from threading import Thread, ThreadError
from multiprocessing.pool import ThreadPool

COUNT = 0
hostname = '0.0.0.0'
portno = 5000

folder = 'sent_data/'

async def process_request(websocket,path):
    request = await websocket.recv()
    global COUNT
    COUNT += 1
    await websocket.send(ThreadPool(processes=1).apply_async(threaded_request, (request,)).get())

def threaded_request(request):
    try:
        f = open(folder+str(COUNT)+'.txt','w+')
        f.write(str(request))
        f.close()
        return json.dumps({'result':'success'})
    except Exception(e):
        print(e)
        return json.dumps({'result': 'failure'})
def main():
    server = ws.serve(process_request, hostname,portno)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

if __name__=='__main__':
    main()

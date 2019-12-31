from urllib.request import urlopen
import json
import requests
from bs4 import BeautifulSoup
from threading import Thread, ThreadError
import queue
import time, datetime
from threading import Timer
import os,sys



SALT = "4nco37bj3,c945"
base_url = 'https://financialmodelingprep.com/api/v3/stock/real-time-price'
api_url = "https://financialmodelingprep.com" \
          "/api/company/real-time-price/" \
          ""+SALT+"" \
          "?datatype=json"
batch_url = "https://financialmodellingprep.com/api/v3/stock/"+SALT

data_folder = 'collected_data/'
error_log_folder = 'errorlogs/'
def get_batch_data():

        response = urlopen(base_url)
        return json.loads(response.read().decode('utf-8'))



def get_co_data(ticker):
    try:
        response = urlopen(api_url.replace(SALT,ticker))
        return json.loads(response.read().decode("utf-8"))
    except Exception(e):
        print('failed on ticker '+ticker)
        print(e)
        return {'symbol':'FAILURE on '+ticker}

def get_500_data():
    ticker_list = obtain_current_500()
    data500 = {}
    threads = []
    que = queue.Queue()

    for ticker in ticker_list:

        t = Thread(target=lambda q, arg1: q.put(get_co_data(arg1)), args=(que,ticker,))
        t.start()
        threads.append(t)

    for thr in threads:
        thr.join()
    while not que.empty():
        result = que.get()
        if not 'Error' in result.keys():
            data500[result['symbol']]=result
    return data500

def get_most_delta(type='gain'):
    if type =='gain':
        repl = 'gainers'
    elif type == 'loss':
        repl = 'losers'
    else:
        return {'result':'invalid type'}
    return json.loads(urlopen(batch_url.replace(SALT,repl)).read().decode("utf-8"))

def obtain_current_500():
    page = requests.get('https://www.slickcharts.com/sp500')
    soup = BeautifulSoup(page.text,'html.parser')
    co_list = soup.find(class_='table-responsive')
    tick_list = co_list.find_all('a')
    tickers = []
    for idx,item in enumerate(tick_list):
        if (idx+1)%2==0:
            stritem = str(item)
            tickers.append(stritem[stritem.find('>')+1:stritem.find('</')])
        if(len(tickers)>=10):
            break
    return tickers

def write_data():

    try:
        timestr = str(datetime.datetime.now())
        ticker_data = get_500_data()
        f = open(data_folder+timestr+'.json','w+')
        f.write(json.dumps(ticker_data))
        f.close()

    except Exception(e):
        print(e)
        f = open(error_log_folder+timestr+'.log','w+')
        f.write("failure at time: "+timestr)
        f.write('errpr:\n'+str(e))
        f.close()

def main():

    x = datetime.datetime.today()
    y= x.replace(day=x.day, hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    delta_seconds = (y-x).seconds +1
    t = Timer(delta_seconds,write_data)
    t.start()


if __name__=='__main__':
    main()




from urllib.request import urlopen
import json
import requests
from bs4 import BeautifulSoup
from threading import Thread, ThreadError
import queue
import time, datetime
import schedule
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

file = open('available_tickers.json','r')
ticker_json = json.loads(file.read())

good_tickers=([res['symbol'] for res in ticker_json['symbolsList']])


def clean_ticker_list(ticker_list):
    for tick in ticker_list:

        if(tick not in good_tickers):
            ticker_list.remove(tick)
    return ticker_list


def get_batch_data(ticker_list):

    try:
        ticker_string = ','.join(ticker_list)
        response = urlopen((api_url.replace(SALT,ticker_string)))
        api_result = json.loads(response.read().decode('utf-8'))

        if(type(api_result) is dict) and 'Error' in dict.keys():
            print('failure on ticker list: '+str(ticker_list))
        return api_result
    except Exception as e:
        print('failed on ticker list: '+str(ticker_list))
        print(e)
        raise
        return {'Error':ticker_list}


# def get_co_data(ticker):
#     try:
#         response = urlopen(api_url.replace(SALT,ticker))
#         return json.loads(response.read().decode("utf-8"))
#     except Exception as e:
#         print('failed on ticker '+ticker)
#         print(e)
#         return {'symbol':'FAILURE on '+ticker,'Error':'FAILURE on '+ticker}

def get_500_data():
    ticker_list = clean_ticker_list(obtain_current_500())
    data500 = {}
    threads = []
    que = queue.Queue()
    for t in ticker_list:
        if ('.' in t):
            ticker_list.remove(t)
    for idx,ticker in enumerate(ticker_list):
        if(idx != 0 and idx%50==0) or (idx+1 == len(ticker_list)):
            ticker_sublist = clean_ticker_list(ticker_list[idx-50:idx])
            t = Thread(target=lambda q, arg1: q.put(get_batch_data(arg1)), args=(que,ticker_sublist,))
            t.start()
            threads.append(t)

    for thr in threads:
        thr.join()
    while not que.empty():
        result = que.get()
        if type(result) is list:
            for res in result:
                data500[res['symbol']] = res
        elif type(result) is dict and 'Error' in result.keys():
            print('error: missing data due to bad ticker symbol')
            print(result)

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
        if(len(tickers)>=500):
            break
    return tickers

def write_data():

    try:
        timestr = str(datetime.datetime.now())
        ticker_data = get_500_data()
        #print(ticker_data)
        print(len(ticker_data.keys()))
        f = open(data_folder+timestr+'.json','w+')
        f.write(json.dumps(ticker_data))
        f.close()

    except Exception as e:
        print(e)
        f = open(error_log_folder+timestr+'.log','w+')
        f.write("failure at time: "+timestr)
        f.write('errpr:\n'+str(e))
        f.close()

def main():
    schedule.every().day.at('00:00').do(write_data)
    while True:
        schedule.run_pending()
        time.sleep(300)


if __name__=='__main__':
    main()




from bs4 import BeautifulSoup
import requests
import json
from multiprocessing.dummy import Pool as ThreadPool 
from time import time

margin_volume_threshold = 100

def grab_data(line):
    
    wtb = 0
    wts = 0
    req = requests.get(line)

    soup = BeautifulSoup(req.content,'html.parser')

    try:
        script = soup.find_all('script')[2]
    except:
        return True
    
    data = json.loads(str(script)[55:-9])
    
    for order in data['payload']['orders']:
        if order['region'] == 'en' and order['visible'] == True and order['user']['status'] == 'ingame':
            if order['order_type'] == 'sell':
                if order['platinum'] < wts or wts == 0:
                        wts = order['platinum']
            if order['order_type'] == 'buy':
                if order['platinum'] > wtb:
                        wtb = order['platinum']

    url = line + "/statistics"

    req = requests.get(url)

    soup = BeautifulSoup(req.content,'html.parser')

    try:
        script = soup.find_all('script')[2]
    except:
        return True

    data = json.loads(str(script)[55:-9])

    volume = 0
    
    for hour in data['payload']['statistics_closed']['48hours']:
        volume += hour['volume']

    if wts != 0 and wtb != 0 and volume > 10 and volume * ((wts-1) - (wtb+1)) > margin_volume_threshold: #
        print(line)
        print("WTS: " + str(wts))
        print("WTB: " + str(wtb))
        print("48 Hour Volume: " + str(volume))
        print("48 hour profit:" + str(volume * ((wts-1) - (wtb+1))))

    return True

if __name__ == "__main__":
    with open ("warframe.txt", "rb") as myfile:
        data=myfile.readlines()[0]
        lines = data.decode().split()
        urls_to_check =[]
        for line in lines:
            if line.find('https://warframe.market/items/') != -1:
                
                urls_to_check.append(line)
                
        print("There are " + str(len(urls_to_check)) + " items to check")
                
        pool = ThreadPool(4)  #Make the Pool of workers
        results = pool.map(grab_data, urls_to_check) #Open the urls in their own threads
        pool.close() #close the pool and wait for the work to finish 
        pool.join() 


import requests
import sys
from datetime import datetime
from pytz import timezone
from tabulate import tabulate
from ascii_graph import Pyasciigraph

count = 10 #How far back
sep_count = 61 #Separator between bids and asks

ts = ["result","sell","buy","rate","quantity"]
cf = ["data","asks","bids","price","size"]

try:
    if (len(sys.argv) == 3 and sys.argv[1] == "depth"):
        if (sys.argv[2].lower() == "ts"):
            orders = requests.get("https://tradesatoshi.com/api/public/getorderbook?market=GRLC_BTC&type=both&depth={}".format(count), timeout=10)
            print("TRADESATOSHI ORDERS")
            a = ts
        elif (sys.argv[2].lower() == "cf"):
            orders = requests.get("https://coinfalcon.com/api/v1/markets/GRLC-BTC/orders", params={'level':'2'}, timeout=10)
            print("COINFALCON ORDERS")
            a = cf

        data = []
        orders = orders.json()[a[0]]

        graph = Pyasciigraph(line_length=30,separator_length=1,graphsymbol='|')
        for x in [a[1],a[2]]:
            for i in range(count):
                order = orders[x][i]
                data.append((str(round(float(order[a[3]])*1e8)),float(order[a[4]])))
            if(x==a[1]): data = data[::-1] #Reverse if bids (order it from max to min)
            for line in graph.graph(label=None, data=data):
                print(line)
            data = []
            if (x==a[1]): print('-'*sep_count)

    elif (len(sys.argv) == 2):
        print("Unrecognised exchange (2nd arg should be TS or CF)")

    else:
        ts_history = requests.get("https://tradesatoshi.com/api/public/getmarkethistory?market=GRLC_BTC&count={}".format(count), timeout=10)
        cf_history = requests.get("https://coinfalcon.com/api/v1/markets/GRLC-BTC/trades", timeout=10)
        nanex      = requests.get("https://nanex.co/api/public/ticker/grlcnano", timeout=10)
        nano_conv  = requests.get("https://api.coinmarketcap.com/v2/ticker/1567/?convert=BTC", timeout=10)

        ts_history = ts_history.json()["result"]
        cf_history = cf_history.json()["data"]
        data = []

        for i in range(count):
            trade = cf_history[i]
            time = datetime.strptime(trade["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone('UTC'))
            cf = "{} {} {} @ {}sat".format(datetime.strftime(time.astimezone(timezone('Australia/Canberra')), "%H:%M"),
                trade["side"].ljust(4,' '),
                str(round(float(trade["size"]))).ljust(5,' '),
                round(float(trade["price"])*1e8))

            trade = ts_history[i]
            time = datetime.strptime(trade["timeStamp"], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone('UTC'))
            ts = "{} {} {} @ {}sat".format(datetime.strftime(time.astimezone(timezone('Australia/Canberra')), "%H:%M"),
                trade["orderType"].lower().ljust(4,' '),
                str(round(trade["quantity"])).ljust(5,' '),
                round(trade["price"]*1e8))

            data.append([cf,ts])

        nano_conv = float(nano_conv.json()["data"]["quotes"]["BTC"]["price"])
        nanex_price = float(nanex.json()["last_trade"])
        nanex_price_sat = round(nanex_price * nano_conv * 1e8,1)
        table = tabulate(data, headers=["Coinfalcon","TradeSatoshi\n(Nanex: {}/{}sat)".format(nanex_price, nanex_price_sat)], tablefmt="orgtbl")
        print(table)

except requests.Timeout:
    print("Could not get market info")

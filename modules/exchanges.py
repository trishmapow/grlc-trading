import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

data = []
try:
    ex = requests.get("https://coinmarketcap.com/currencies/garlicoin/#markets", timeout=10)
    price = requests.get("https://api.coinmarketcap.com/v2/ticker/2475?convert=BTC", timeout=10)
except requests.Timeout:
    ex = None
    price = None

if ex and price:
    price_usd = float(price.json()["data"]["quotes"]["USD"]["price"])
    price_btc = float(price.json()["data"]["quotes"]["BTC"]["price"])
    change_24h = float(price.json()["data"]["quotes"]["USD"]["percent_change_24h"])
    mcap = float(price.json()["data"]["quotes"]["USD"]["market_cap"])

    total_v = 0 #Total volume
    total_vd = 0 #Total volume (dollars)

    soup = BeautifulSoup(ex.text, 'html.parser')
    table = soup.find('table', attrs={'id': 'markets-table'})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        #print(row)
        p = row.find('span', class_="price")
        v = row.find('span', class_="volume")
        price_n = float(p.attrs['data-native'])
        vol_n = float(v.attrs['data-native'])
        total_v += vol_n

        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]

        total_vd += float(cols[3][1:].replace(",", "")) #Remove $ sign and commas

        d = [cols[0], cols[1], cols[2], cols[3] + " ({})".format(str(vol_n)),
             cols[4]]
        data.append(d)

    total_vd = str(round(total_vd))
    total_v = str(round(total_v))

    #Add extra info
    data.append(["","","","",""])
    data.append(["",""," Aggregate:","${0} {1}₲".format(total_vd, total_v),"${0} ฿{1:.8f}".format(price_usd, price_btc)])
    data.append(["","","24h change:","{}%".format(change_24h),"",""])
    data.append(["","","Market cap:","${}".format(mcap)])
    table = tabulate(data, headers=["No", "Exchange", "Pair", "Volume (native)", "Price (native)"])

    print("{}".format(table))
else:
    print("Error : Couldn't reach CoinMarketCap (timeout)")

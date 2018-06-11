from tabulate import tabulate
from bs4 import BeautifulSoup
import requests

price = ""
price_usd = ""

def get_data():
    try:
        ex = requests.get("https://coinmarketcap.com/currencies/garlicoin/#markets", timeout=10)
        price = requests.get("https://api.coinmarketcap.com/v1/ticker/garlicoin/", timeout=10)
    except requests.Timeout:
        return "Could not connect to CMC"

    price = price.json()[0]
    price_usd = price["price_usd"]
    price_btc = float(price["price_btc"])
    change_24h = price["percent_change_24h"]
    mcap = price["market_cap_usd"]
    data = []
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
        total_vd += float(cols[3][1:].replace(",", ""))
        d = [cols[0],cols[1],cols[2],cols[3] + f" ({str(vol_n)})",cols[4] + f" ({price_n:.8f})"]
        data.append(d)

    total_vd = str(round(total_vd))
    total_v = str(round(total_v))
    data.append(["","","","",""])
    data.append(["",""," Aggregate:",f"${total_vd} {total_v}₲",f"${price_usd} ฿{price_btc:.8f}"])
    data.append(["","","24h change:",f"{change_24h}%","",""])
    data.append(["","","Market cap:",f"${mcap}"])
    table = tabulate(data, headers=["No", "Exchange", "Pair", "Volume (native)", "Price (native)"])
    return table

if __name__ == "__main__":
    print(get_data())

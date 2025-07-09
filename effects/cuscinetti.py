import requests

""" def goldPrice():
    goldUrl="https://api.gold-api.com/price/XAU"   
    return float(requests.get(goldUrl).json()["price"])
    
def btcPrice():
    btcUrl="https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDC"
    return float(requests.get(btcUrl).json()["price"])

 """


def gold_price():
    url = "https://api.gold-api.com/price/XAU"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        # Cerca l'entry con "gold"
        for entry in data:
            if entry=="price":
                return float(data["price"])
        raise ValueError("Prezzo dell'oro non trovato nella risposta")
    except Exception as e:
        print("Errore recupero prezzo oro:", e)
        return None

print(gold_price())

def btc_price():
    btc_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDC"

    try:
        response = requests.get(btc_url)
        response.raise_for_status()
        data = response.json()
        return float(data["price"])
    except Exception as e:
        print("Errore durante il recupero del prezzo del BTC:", e)
        return None
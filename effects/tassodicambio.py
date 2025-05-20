import requests
from collections import defaultdict

# FONTI DATI: (URL, chiave nel JSON contenente i tassi)
FONTI = [
    ("https://v6.exchangerate-api.com/v6/635b1b63c19c4f138ea549eb/latest/USD", "conversion_rates"),
    ("https://api.fxfeed.io/v1/latest?base=USD&currencies=USD,EUR,GBP,JPY,AUD,CAD,CHF,CNY,SEK,NZD&api_key=fxf_U2GAfe5vyNEis8wF3IGA", "rates"),
    ("https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json", "usd"),
    ("https://api.exconvert.com/fetchAll?from=USD&access_key=ca810f03-0b0ee55d-2ef85fea-5454cd09", "rates"),
]

# Set di valute fiat ISO 4217 (puoi aggiornare o filtrare)
VALUTE_FIAT = {
    "AED","AFN","ALL","AMD","ANG","AOA","ARS","AUD","AWG","AZN","BAM","BBD","BDT",
    "BGN","BHD","BIF","BMD","BND","BOB","BRL","BSD","BTN","BWP","BYN","BZD","CAD",
    "CDF","CHF","CLP","CNY","COP","CRC","CUC","CUP","CVE","CZK","DJF","DKK","DOP",
    "DZD","EGP","ERN","ETB","EUR","FJD","FKP","FOK","GBP","GEL","GHS","GIP","GMD",
    "GNF","GTQ","GYD","HKD","HNL","HRK","HTG","HUF","IDR","ILS","IMP","INR","IQD",
    "IRR","ISK","JMD","JOD","JPY","KES","KGS","KHR","KID","KMF","KRW","KWD","KYD",
    "KZT","LAK","LBP","LKR","LRD","LSL","LYD","MAD","MDL","MGA","MKD","MMK","MNT",
    "MOP","MRU","MUR","MVR","MWK","MXN","MYR","MZN","NAD","NGN","NIO","NOK","NPR",
    "NZD","OMR","PAB","PEN","PGK","PHP","PKR","PLN","PYG","QAR","RON","RSD","RUB",
    "RWF","SAR","SBD","SCR","SDG","SEK","SGD","SHP","SLE","SLL","SOS","SRD","STN",
    "SYP","SZL","THB","TJS","TMT","TND","TOP","TRY","TTD","TVD","TWD","TZS","UAH",
    "UGX","USD","UYU","UZS","VES","VND","VUV","WST","XAF","XCD","XDR","XOF","XPF",
    "YER","ZAR","ZMW","ZWL"
}

def scarica_dati_fonte(url, key):
    """Scarica i tassi da una singola fonte, ritorna dict valuta -> valore"""
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        dati = r.json()
        raw_rates = dati.get(key, {})
        # Normalizza chiavi e filtra solo valute fiat con valore numerico valido
        return {k.upper(): float(v) for k, v in raw_rates.items() if k.upper() in VALUTE_FIAT and isinstance(v, (int, float))}
    except Exception as e:
        print(f"[ERRORE] Recupero dati da {url} fallito: {e}")
        return {}

def media_tassi_cambio():
    """Recupera dati da tutte le fonti, media i tassi per ogni valuta e ritorna dict valuta->media"""
    raccolta_valori = defaultdict(list)
    
    # Raccogli i valori da tutte le fonti
    for url, key in FONTI:
        dati = scarica_dati_fonte(url, key)
        for valuta, valore in dati.items():
            raccolta_valori[valuta].append(valore)
    
    # Calcola la media solo per valute con almeno un dato disponibile
    medie = {}
    for valuta in VALUTE_FIAT:
        valori = raccolta_valori.get(valuta)
        if valori:
            medie[valuta] = sum(valori) / len(valori)
        else:
            medie[valuta] = None  # Nessun dato per questa valuta
    
    return medie

# Esempio d’uso:
if __name__ == "__main__":
    tassi_medi = media_tassi_cambio()
    print("Tassi di cambio medi (base USD):")
    for v, val in sorted(tassi_medi.items()):
        if val is not None:
            print(f"{v}: {val:.6f}")
        else:
            print(f"{v}: dati non disponibili")

import requests

# Scarica tutti i dati una sola volta
def scarica_dati_storici():

    urls_old = [
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2024-07-06/v1/currencies/usd.json",
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2024-06-06/v1/currencies/usd.json",
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2024-05-06/v1/currencies/usd.json",
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2024-04-06/v1/currencies/usd.json",
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2024-03-06/v1/currencies/usd.json",
    ]
    url_new = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2025-03-06/v1/currencies/usd.json"

    old_data = [requests.get(url).json()["usd"] for url in urls_old]
    new_data = requests.get(url_new,headers={"Cache-Control": "no-cache"}).json()["usd"]
    return old_data, new_data


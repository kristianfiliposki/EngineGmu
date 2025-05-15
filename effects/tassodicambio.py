import requests


def tassodicambio():
    exchange_rate_api_url = "https://v6.exchangerate-api.com/v6/635b1b63c19c4f138ea549eb/latest/USD"
    exchange_response = requests.get(exchange_rate_api_url)
    return exchange_response.json()['conversion_rates']

def tassidicambio3():
    cdnjsdeliver="https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json"
    cdnjsdeliver_response = requests.get(cdnjsdeliver,headers={"Cache-Control": "no-cache"})
    return cdnjsdeliver_response.json()["usd"]



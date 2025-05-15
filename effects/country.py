import requests

def dataCountry():
    countries_api_url = "https://restcountries.com/v3.1/all"
    response = requests.get(countries_api_url)
    data = response.json()
    result = []
    
    for el in data:
        name = el["name"]["common"]
        population = el["population"]
        
        # Ottieni le valute, sempre come lista
        currencies = list(el["currencies"].keys()) if "currencies" in el else []
        
        result.append({
            "name": name,
            "population": population,
            "currency": currencies
        })
    
    return result

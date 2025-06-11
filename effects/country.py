import requests

def dataCountry():
    # Dataset da GitHub
    population_url = "https://raw.githubusercontent.com/samayo/country-json/master/src/country-by-population.json"
    currency_url = "https://raw.githubusercontent.com/samayo/country-json/master/src/country-by-currency-code.json"
    
    try:
        # Scarica i dati
        population_data = requests.get(population_url).json()
        currency_data = requests.get(currency_url).json()
        
        # Combina i dati
        result = []
        for country in population_data:
            country_name = country["country"]
            # Trova la valuta corrispondente
            currency = next(
                (c["currency_code"] for c in currency_data if c["country"] == country_name),
                "N/A"  # Default se non trovata
            )
            result.append({
                "name": country_name,
                "population": country["population"],
                "currency": [currency] if currency != "N/A" else []
            })
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Errore nel caricamento dei dati: {e}")
        return []

# Test
print(dataCountry())
def populationCoin(coin, countries):
    coin = coin.upper()
    total_population = 0
    
    for country in countries:
        if coin in country["currency"]:
            total_population += int(country["population"])
    
    return total_population
import statistics

# Calcola il rating partendo da dati già scaricati
def ratingCoin(coin, old_data, new_data):
    coin = coin.lower()
    try:
        new_rate = new_data[coin]
        variations = []
        for data in old_data:
            old_rate = data[coin]
            variation = abs((new_rate - old_rate) / old_rate)
            variations.append(variation)

        std_dev = statistics.stdev(variations)
        score = max(0, round(1 - std_dev , 4))

        return {
            "currency": coin.upper(),
            "variation_std_dev": round(std_dev * 10, 4),
            "stability_score": score
        }
    except KeyError:
        return {
            "currency": coin.upper(),
            "variation_std_dev": 1.0,
            "stability_score": 0
        }



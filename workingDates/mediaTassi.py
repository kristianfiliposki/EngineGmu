
import workingDates.ratingDate

# Modifica mediaTassi per usare i dati scaricati
def mediaTassi(tassi, old_data, new_data):
    sommaTassi = 0

    for k in tassi:
        variazione = workingDates.ratingDate.ratingCoin(k, old_data, new_data)["variation_std_dev"]
        sommaTassi += float(tassi[k]) * variazione 

    mediaValori = sommaTassi / len(tassi)
    return mediaValori


import math
import effects.country
import effects.worldPopulationDate
import workingDates
import workingDates.mediaTassi
import effects
import effects.history_dates
import effects.cuscinetti
import effects.tassodicambio
import workingDates.populationCoin
import workingDates.ratingDate

def GMU():
    gmu=0

    """ peso della popolazione """
    alpha=0.5
    """ peso stabilita della moneta """
    beta=0.5
    """ peso della riserva in BTC """
    omega=0.003
    """ peso della riserva in ORO """
    delta=0.0023

    """ dati calcolati """
    countries=effects.country.dataCountry()
    tassi=effects.tassodicambio.tassidicambio3()
    old, new = effects.history_dates.scarica_dati_storici()
    mediaValValutari=workingDates.mediaTassi.mediaTassi(tassi,old,new)
    #btcprice=effects.cuscinetti.btcPrice()
    #goldprice=effects.cuscinetti.goldPrice()
    sommaTOT=Sommatoria(tassi,mediaValValutari,countries,alpha,beta,old,new)
    

    """ NOTA BENE ALPHA+BETA+GAMMA+DELTA == 1 """

    """ risoluzione della formula """
    gmu=((1-delta-omega)*sommaTOT)
    
    """ L'INDICE MONDIALE HA UN NOME ||||GMU||||| """
    return gmu

def Sommatoria(tassi,media,countries,alpha,beta,oldData,newData):
    sommatoria=0
    totUS=0
    totSt=0
    poptot=effects.worldPopulationDate.pop_world_number()
    for coin in tassi:
        pop=workingDates.populationCoin.populationCoin(coin,countries)
        if pop==0:
            continue
        
        rapporto = tassi[coin] / media
        if rapporto <= 0:
             continue  # salta valuta anomala
        tassoNormalizzato = rapporto
         # Limitiamo gli estremi per maggiore stabilità (anti-outlier)
        tassoNormalizzato = max(min(tassoNormalizzato, 0.3), -0.3)
        usabilita=math.log(pop)/math.log(poptot)
        totUS+=usabilita
        stabilita=workingDates.ratingDate.ratingCoin(coin,oldData,newData)["stability_score"]
        totSt+=stabilita
        sommatoria+=tassoNormalizzato*(1+((alpha*usabilita)+(beta*stabilita)))
    print(totSt,totUS)
    return sommatoria 



    
print("il valore attuale della GLOBAL MONEY UNIT È: ",GMU(), "!!!!")
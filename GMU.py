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
    tassi=effects.tassodicambio.media_tassi_cambio()
    old, new = effects.history_dates.scarica_dati_storici()
    mediaValValutari=workingDates.mediaTassi.mediaTassi(tassi,old,new)
    print("media mondiale delle valute: ",mediaValValutari)

    #btcprice=effects.cuscinetti.btcPrice()
    #goldprice=effects.cuscinetti.goldPrice()
    sommaTOT=Sommatoria(tassi,mediaValValutari,countries,alpha,beta,old,new)
    

    """ NOTA BENE ALPHA+BETA+GAMMA+DELTA == 1 """

    """ risoluzione della formula """
    gmu=((1-delta-omega)*sommaTOT)
    """ L'INDICE MONDIALE HA UN NOME ||||GMU||||| """
    print("GMU NOW",gmu)
    return gmu

def Sommatoria(tassi,media,countries,alpha,beta,oldData,newData):
    if not "BTC" in tassi:
        tassi["BTC"]=effects.cuscinetti.btc_price()
    if not "XAU" in tassi:
        tassi["XAU"]=effects.cuscinetti.gold_price()
    sommatoria=0
    totUS=0
    totSt=0
    poptot=effects.worldPopulationDate.pop_world_number()
    for coin in tassi:
        stabilita=workingDates.ratingDate.ratingCoin(coin,oldData,newData)["stability_score"]
        if  0.4<=stabilita<=1:
            pop=workingDates.populationCoin.populationCoin(coin,countries)
            if coin=="XAU":
                print(coin,": dsadsasd ",pop)
            if pop==0:
                continue
            rapporto = tassi[coin] / media

            if rapporto <= 0:
                continue  # salta valuta anomala
            tassoNormalizzato = rapporto
            # Limitiamo gli estremi per maggiore stabilità (anti-outlier)
            usabilita=pop/poptot
            totUS+=usabilita
            totSt+=stabilita
            sommatoria+=tassoNormalizzato*(1+((alpha*usabilita)+(beta*stabilita)))
        else: continue
        
    print(sommatoria)
    return sommatoria 



def ratingList():
    tassi=effects.tassodicambio.media_tassi_cambio()
    old, new = effects.history_dates.scarica_dati_storici()
    return workingDates.ratingDate.listratingcoin(tassi,old,new)




if __name__ == "__main__":
    print("il valore attuale della GLOBAL MONEY UNIT È: ", GMU(), "!!!!")

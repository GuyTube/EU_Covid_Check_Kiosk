from datetime import datetime, timedelta

mois_fr = ["janvier","février","mars","avril","mai","juin","juillet","aout","septembre","octobre","novembre","décembre"]

def getJour(date):
    print(date[8:10])
    return date[8:10]
   
def getMois(date):
    mois=date[5:7]
    print(mois)
    return mois_fr[int(mois)-1]
    
def getAnnee(date):
    print(date[0:4])
    return date[0:4]

def getHeure(date):
    print(date[11:13])
    return date[11:13]

def getMinutes(date):
    print(date[14:16])
    return date[14:16]
    
def getDatePlus(d, n):
    toParse = ""
    if "T" in d:
        toParse = d[:18]
    else:
        toParse = d+"T00:00:00"
    date = datetime.strptime(toParse, "%Y-%m-%dT%H:%M:%S")
    modified_date = date + timedelta(days=n)
    return datetime.strftime(modified_date, "%Y-%m-%dT%H:%M:%S")

def getDateReadable(d):
    date = getJour(d).lstrip("0")+" "+getMois(d)+" "+getAnnee(d)
    if "T" in d:
        hm=""
        if getHeure(d)=="00" and getMinutes(d)=="00":
            hm = "minuit"
        elif getHeure(d)=="00":
            hm="minuit et "+getMinutes(d).lstrip("0")
        elif getMinutes(d)=="00":
            hm=getHeure(d).lstrip("0")
        else:
            hm=getHeure(d).lstrip("0")+" heures et "+getMinutes(d).lstrip("0")+" minutes"
        date = date + " à " + hm
    return date


from datetime import datetime, timedelta, date

mois_fr = ["janvier","février","mars","avril","mai","juin","juillet","aout","septembre","octobre","novembre","décembre"]

def getDatetime(d):
    if d is None:
        return None
    toParse = ""
    if "T" in d:
        toParse = d[:18]
    else:
        toParse = d+"T00:00:00"
    adate = datetime.strptime(toParse, "%Y-%m-%dT%H:%M:%S")
    return adate

def getDatetimeReadable(d: datetime):
    adate = str(d.day)+" "+mois_fr[d.month-1]+" "+str(d.year)+" à "+str(d.hour)+" heure et "+str(d.minute)+" minutes"
    return adate
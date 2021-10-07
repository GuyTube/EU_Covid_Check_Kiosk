from flask import Flask, render_template, Response, send_file, request
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import base45
import cbor2
import zlib
import json
import subprocess
import os
import time
from playsound import playsound
from cose.messages import CoseMessage
from datetime import datetime, timedelta
import threading


os="WINDOWS"

import win32com.client
speaker = win32com.client.Dispatch("SAPI.SpVoice")
# install flask https://linuxize.com/post/how-to-install-flask-on-ubuntu-18-04/
#pip install cryptography==2.8 sur windows pip install cryptography
#pip install cose
#pip install cbor2
#pip install base45
#pip3 install opencv-python
#pip3 install pyzbar
#pip3 install playsound
#pip install pygobject Marche pour sous windows
#pip install pywin32 pour windows uniquement

class CovidTest:
    def __init__(self, date, pays) :
        self.date, self.pays = date, pays

    def getDate(self):
        return self.date

    def getPays(self):
        return self.pays

class CovidVaccine:
    def __init__(self, date, nbDoseFull, nbDose, product) :
        self.date, self.nbDoseFull, self.nbDose, self.product = date, nbDoseFull, nbDose, product
        
    def getDate(self):
        return self.date
        
    def getProduct(self):
        return self.product

class CovidRecovery:
    def __init__(self, valid_start, valid_end, first_positive_test) :
        self.valid_from, self.valid_to, self.first_positive_test = valid_start, valid_end, first_positive_test

    def getValidFrom(self):
        return self.valid_from
        
    def getValidTo(self):
        return self.valid_to
        
class CovidCertif:

    def __init__(self, name, surname, c_name, c_surname, dateOfBirth):
        self.name, self.surname, self.correctedName, self.correctedSurname, self.dateOfBirth = name, surname, c_name, c_surname, dateOfBirth
        self.covidTests = {}
        self.covidVaccines = {}
        self.covidRecoveries = {}

    def addVaccine(self, vaccine):
        self.covidVaccines[vaccine.getDate()] = vaccine
        
    def addTest(self, test):
        self.covidTests[test.getDate()] = test
        
    def addRecovery(self, recovery):
        self.covidRecoveries[recovery.getValidTo()] = recovery
	
    def getType(self):
        if len(self.covidTests) > 0 :
            return "test"
        elif len(self.covidVaccines) > 0 :
            return "vaccine"
        elif len(self.covidRecoveries) > 0:
            return "recovery"
	
    def getLastVaccine(self) :
        if len(self.covidVaccines) > 0 :
            maxDate = ""
            for d in self.covidVaccines :
                if d > maxDate :
                    maxDate = d
                    lastVaccine = self.covidVaccines[d]
                    
            return lastVaccine
        else :
            return None
            
    def getLastTest(self) :
        if len(self.covidTests) > 0 :
            maxDate = ""
            for d in self.covidTests :
                if d > maxDate :
                    maxDate = d
                    lastTest = self.covidTests[d]
                    
            return lastTest
        else :
            return None

    def getLastRecovery(self) :
        if len(self.covidRecoveries) > 0 :
            maxDate = ""
            for d in self.covidRecoveries :
                if d > maxDate :
                    maxDate = d
                    lastRecovery = self.covidRecoveries[d]
                    
            return lastRecovery
        else :
            return None
            	

forceDisplay = ""

testQRcode = "6BFOXN%TSMAHN-H6SKJPT.-7G2TZ978S80RBXEJW.TFJTXG41UQR$TTSJOF4R0WAN9I6T5XH-G2%E3EV4*2DYFPU*0CEBQ/GXQFY735LBJU0QHNRXGFAF+BB5-0G.8UG5EV40ATPHN7Y47%S7Y48YIZ73423ZQTZABDG35:43%2..P*PP:+P*.1D9R+Q6646G%63ZMZE9KZ56DE/.QC$Q3J62:6HT02R5LDCPF5RBQ746B46O1N646RM9AL5CBVW566LH 469/9-3AKI62R6R3R/FMSW6PK99Q9E$BDZIA9JQWTC.SPTI92KVB28PS.VS062POJC0JYB0ZY9P8Q/98V7J$%25I3KC3X83277U5S1DF3I8R39WZ8JG3OA5Y06C67 M1A0HBF144K0HPLWEU6UX0EI+NSQNK:C%QAWZ7F%NGCNOTN4IHX7SJ4P*P9X+P9.4AANBOO%+2D:3P.D"

app = Flask(__name__)

camera = cv2.VideoCapture(0)  # use 0 for web camera


font = cv2.FONT_HERSHEY_SIMPLEX
lastQRcode = "Veuillez scanner votre passe sanitaire"
mois_fr = ["janvier","février","mars","avril","mai","juin","juillet","aout","septembre","octobre","novembre","décembre"]
vaccine_products={ 
    "EU/1/20/1528": "Pfizer",
    "EU/1/20/1507": "Moderna",
    "EU/1/21/1529": "AstraZeneca",
    "EU/1/20/1525": "Janssen",
    "CVnCoV": "Curevac",
    "Sputnik-V": "Sputnik v",
    "Convidecia": "CanSino Biological",
    "EpiVacCorona": "institut Vector",
    "BBIBP-CorV": "Sinopharm",
    "Inactivated-SARS-CoV-2-Vero-Cell": "Sinovac Life Sciences",
    "CoronaVac": "Sinovac",
    "Covaxin": "Bharat Biotech",
    }

def decode(im) : 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    return decodedObjects

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

class passAnalyser (threading.Thread):
    def __init__(self, payload):
        threading.Thread.__init__(self)
        self.payload = payload 

    def run(self):
        global forceDisplay
        forceDisplay="encours.png"
        time.sleep(0.5)
        valid, texte = testCertif( self.payload )
        if valid:
            forceDisplay="passvalide.png"
        else:
            forceDisplay="passnonvalide.png"
        for t in texte:
            printAndSay(t)

        forceDisplay = ""





def gen_frames():  # generate frame by frame from camera global

    global forceDisplay
    lastQrCode=b'Nothing'

    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            print( "error reading frame")
            break
        else:
            #ret, buffer = cv2.imencode('.jpg', frame)
            im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decodedObjects = decode(im)
            
            #for decodedObject in decodedObjects: 
            if len(decodedObjects) > 0:
                decodedObject = decodedObjects[0]
                payload = decodedObject.data.decode("UTF-8")[4:]

                if decodedObject.type=="QRCODE" and payload != lastQrCode:
                    
                    try:
                        lastQrCode = payload
                        t = passAnalyser(payload)
                        t.start()

                    except Exception as e:
                        #printAndSay("Impossible de décoder ce qr code")
                        print("error decoding", e)

            if forceDisplay != "":
                frame = cv2.imread(forceDisplay)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result        


def printAndSay(sentence):
    print(sentence)
    if os=="LINUX":
        os.system("pico2wave -l fr-FR -w=1.wav  \""+sentence+"\"")
        time.sleep(1)
        os.system("aplay "+os.path.join(app.root_path, '1.wav'))
    if os=="WINDOWS":
        speaker.Speak(sentence)

    
texte=[]

#https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf
def testCertif(qrcode):
    global texte
    texte = []
    decode45 = base45.b45decode(qrcode)
    decompressed = zlib.decompress(decode45)
    cose = CoseMessage.decode(decompressed)
    jsons = cbor2.loads(cose.payload)
    root = jsons[-260][1]
    name = root["nam"]
    print(jsons)
    certif = CovidCertif(name["gn"], name["fn"], name["gnt"], name["fnt"], root["dob"]) 
    passValide = False
    
    try:
        vaccines = root["v"]
        if vaccines is not None:
            for v in vaccines:
                vacc = CovidVaccine(v["dt"],v["sd"], v["dn"], v["mp"])
                certif.addVaccine(vacc)
    except:
        print("Not a vaccine")
        
    try:
        tests = root["t"]
        print("test1")
        if tests is not None:
            print("test2")
            for t in tests:
                print("test3")
                test = CovidTest(t["sc"],t["tc"])
                certif.addTest(test)
    except:
        print("Not a Test")
        
    try:
        recoveries = root["r"]
        if recoveries is not None:
            for r in recoveries:
                recovery = CovidRecovery(r["df"], r["du"], r["fr"])
                certif.addRecovery(recovery)
    except:
        print("Not a Recovery")

    print("TYPE : ",certif.getType())
    texte.append("Bonjour "+certif.name)
    if certif.getType() == "vaccine":
        lastVaccine = certif.getLastVaccine()
        texte.append("Vous avez reçu "+str(lastVaccine.nbDose)+" doses d'un vaccin produit par : "+vaccine_products[lastVaccine.product])

        if lastVaccine.nbDoseFull<=lastVaccine.nbDose :
            texte.append("Votre schéma vaccinal est donc complet depuis le "+getDateReadable(lastVaccine.getDate()))
            certifValidity = getDatePlus(lastVaccine.getDate(), 7)
            texte.append("Selon la législation actuelle votre passe sanitaire est valide depuis le "+getDateReadable(certifValidity))
            passValide = True
        else :
            texte.append("Votre schéma vaccinal n'est donc pas encore complet et votre passe n'est donc pas valide")
        
    if certif.getType() == "test":
        lastTest = certif.getLastTest()
        texte.append("Votre test a été effectué le "+getDateReadable(lastTest.getDate())+" en "+lastTest.getPays())
        testValidTill = getDatePlus(lastTest.getDate(), 3)
        currDate = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")
        if currDate <= testValidTill :  #WARNING 72H et pas 3 jours
            texte.append("Votre test est valide depuis le "+getDateReadable(lastTest.getDate()))
            texte.append("Selon la législation actuelle votre passe sanitaire est valide jusqu'au "+getDateReadable(testValidTill))
            passValide = True
        else :
            texte.append("Votre test n'est plus valide depuis le "+getDateReadable(testValidTill))

    if certif.getType() == "recovery":
        lastTest = certif.getLastRecovery()
        texte.append("Votre certificat de rétablissement est valide du "+getDateReadable(lastTest.getValidFrom())+" au "+lastTest.getValidTo())
        testValidTill = getDatePlus(lastTest.getDate(), 3)
        currDate = datetime.strftime(datetime.now(), "%Y-%m-%dT00:00:00")
        if currDate <= testValidTill :  #WARNING 72H et pas 3 jours
            texte.append("Votre test est valide depuis le "+getDateReadable(lastTest.getDate()))
            texte.append("Selon la législation actuelle votre passe sanitaire est valide jusqu'au "+getDateReadable(testValidTill))
            passValide = True
        else :
            texte.append("Votre test n'est plus valide depuis le "+getDateReadable(testValidTill))
        
    return passValide, texte

@app.route('/get_image')
def get_image():
    if request.args.get('type') == 'success':
       filename = 'validpass.png'
    elif request.args.get('type') == 'notvalid':
       filename = 'invalidpass.png'
    else:
       filename = 'processing.png'
    return send_file(filename, mimetype='image/png')

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    #print("TEST : ",buildCertif(testQRcode))
    return render_template('index.html')

@app.route("/code")
def code():
    global texte
    message=""
    for t in texte:
        message=message+t+"<br/>"
    return '<img src="/get_image" width="640" height="360">'

if __name__ == '__main__':
    app.run(debug=True)

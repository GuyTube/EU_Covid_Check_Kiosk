

from flask import Flask, render_template, Response
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

# install flask https://linuxize.com/post/how-to-install-flask-on-ubuntu-18-04/
#pip install cryptography==2.8
#pip install cose
#pip install cbor2
#pip install base45
#pip3 install opencv-python
#pip3 install pyzbar
#pip3 install playsound
#pip install pygobject


class CovidTest:
    def __init__(self, date, nbDoseFull, nbDose, product) :
        self.date, self.nbDoseFull, self.nbDose, self.product = date, nbDoseFull, nbDose, product

    def getDate(self):
        return self.date

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
            	

detect_mode = True

testQRcode = "6BFOXN%TSMAHN-H6SKJPT.-7G2TZ978S80RBXEJW.TFJTXG41UQR$TTSJOF4R0WAN9I6T5XH-G2%E3EV4*2DYFPU*0CEBQ/GXQFY735LBJU0QHNRXGFAF+BB5-0G.8UG5EV40ATPHN7Y47%S7Y48YIZ73423ZQTZABDG35:43%2..P*PP:+P*.1D9R+Q6646G%63ZMZE9KZ56DE/.QC$Q3J62:6HT02R5LDCPF5RBQ746B46O1N646RM9AL5CBVW566LH 469/9-3AKI62R6R3R/FMSW6PK99Q9E$BDZIA9JQWTC.SPTI92KVB28PS.VS062POJC0JYB0ZY9P8Q/98V7J$%25I3KC3X83277U5S1DF3I8R39WZ8JG3OA5Y06C67 M1A0HBF144K0HPLWEU6UX0EI+NSQNK:C%QAWZ7F%NGCNOTN4IHX7SJ4P*P9X+P9.4AANBOO%+2D:3P.D"

app = Flask(__name__)

camera = cv2.VideoCapture(0)  # use 0 for web camera
camera.set(3, 800.0)
camera.set(4, 600.0)

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
    # Print results
    for obj in decodedObjects:
        print('Type : ', obj.type)
        print('Data : ', obj.data,'\n')     
    return decodedObjects

def getJour(date):
    print(date[8:])
    return date[8:]
   
def getMois(date):
    mois=date[5:7]
    print(mois)
    return mois_fr[int(mois)-1]
    
def getAnnee(date):
    print(date[0:4])
    return date[0:4]
    
def getDatePlus(d, n):
    date = datetime.strptime(d, "%Y-%m-%d")
    modified_date = date + timedelta(days=n)
    return datetime.strftime(modified_date, "%Y-%m-%d")

def getDateReadable(d):
    return getJour(d).lstrip("0")+" "+getMois(d)+" "+getAnnee(d)

def gen_frames():  # generate frame by frame from camera
    global lastQRcode
    global detect_mode
 
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
sudo reboot
philou
grizelda..Ph
sudo reboot
sudo reboot
            if detect_mode:
                #ret, buffer = cv2.imencode('.jpg', frame)
                im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                decodedObjects = decode(im)
                
                #for decodedObject in decodedObjects: 
                if len(decodedObjects) > 0:
                    print("Releasing camera")
                    camera.release()
                    decodedObject = decodedObjects[0]
                    detect_mode = False
                    points = decodedObject.polygon
                 
                    # If the points do not form a quad, find convex hull
                    if len(points) > 4 : 
                      hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                      hull = list(map(tuple, np.squeeze(hull)))
                    else : 
                      hull = points;
                     
                    # Number of points in the convex hull
                    n = len(hull)     
                    # Draw the convext hull
                    for j in range(0,n):
                      cv2.line(frame, hull[j], hull[ (j+1) % n], (255,0,0), 3)

                    x = decodedObject.rect.left
                    y = decodedObject.rect.top

                    print(x, y)

                    print('Type : ', decodedObject.type)
                    print('Data : ', decodedObject.data,'\n')
                    #lastQRcode = str(decodedObject.data)
                    #cv2.putText(frame, str(decodedObject.data), (x, y), font, 1, (0,255,255), 2, cv2.LINE_AA)
                    payload = decodedObject.data.decode("UTF-8")[4:]
                    buildCertif( payload )

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                        
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def printAndSay(sentence):
    os.system("pico2wave -l fr-FR -w=1.wav  \""+sentence+"\"")
    time.sleep(1)
    os.system("aplay "+os.path.join(app.root_path, '1.wav'))
    

#https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf
def buildCertif(qrcode):
    global detect_mode
    print("APPEL DE BUILDCERTIF ________________")
    decode45 = base45.b45decode(qrcode)
    decompressed = zlib.decompress(decode45)
    cose = CoseMessage.decode(decompressed)
    jsons = cbor2.loads(cose.payload)
    root = jsons[-260][1]
    name = root["nam"]
    
    certif = CovidCertif(name["gn"], name["fn"], name["gnt"], name["fnt"], root["dob"]) 
    
    vaccines = root["v"]
    if vaccines is not None:
        for v in vaccines:
            vacc = CovidVaccine(v["dt"],v["sd"], v["dn"], v["mp"])
            certif.addVaccine(vacc)
    try:
        tests = root["t"]
        if test is not None:
            for t in tests:
                test = CovidTest(t["sc"])
                certif.addTest(test)
    except:
        print("No Test")
        
    try:
        recoveries = root["r"]
        if recoveries is not None:
            for r in recoveries:
                recovery = CovidRecovery(r["df"], r["du"], r["fr"])
                certif.addRecovery(recovery)
    except:
        print("No Recovery")

    print("TYPE : ",certif.getType())
    printAndSay("Bonjour "+certif.name)
    if certif.getType() == "vaccine":
        lastVaccine = certif.getLastVaccine()
        printAndSay("Vous avez reçu "+str(lastVaccine.nbDose)+" doses d'un vaccin produit par : "+vaccine_products[lastVaccine.product])

        if lastVaccine.nbDoseFull<=lastVaccine.nbDose :
            printAndSay("Votre schéma vaccinal est donc complet depuis le "+getDateReadable(lastVaccine.getDate()))
            certifValidity = getDatePlus(lastVaccine.getDate(), 7)
            printAndSay("Selon la législation actuelle votre passe sanitaire est valide depuis le "+getDateReadable(certifValidity))
        else :
            printAndSay("Votre schéma vaccinal n'est donc pas encore complet et votre passe n'est donc pas valide")
        
    if certif.getType() == "test":
        lastTest = certif.getLastTest()
        printAndSay("Votre test a été effectué le "+getDateReadable(lastTest.getDate()))
        testValidTill = getDatePlus(lastTest.getDate(), 3)
        currDate = datetime.strftime(datetime.now(), "%Y-%m-%d")
        if currDate <= testValidTill :  #WARNING 72H et pas 3 jours
            printAndSay("Votre test est valide depuis le "+getDateReadable(lastTest.getDate()))
            printAndSay("Selon la législation actuelle votre passe sanitaire est valide jusqu'au "+getDateReadable(testValidTill)," à ","")
        else :
            printAndSay("Votre test n'est plus valide")
    
    detect_mode = True
    camera.open(0)

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
    return lastQRcode

if __name__ == '__main__':
    app.run(debug=True)

from flask import Blueprint, Flask, render_template, Response, send_file, request, jsonify
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import base45
import cbor2
import zlib
import subprocess
import os
import time
from datetime import datetime
from playsound import playsound
from cose.messages import CoseMessage
import threading
import pprint
import sqlite3
from checker.db import get_db
import pythoncom

bp = Blueprint('checker', __name__)

os="WINDOWS"

import win32com.client

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
#pip install pandas

from . import CovidCertif
from . import dateUtils
            	
class TestResult:
    def __init__(self, status, resultHTML, resultJSON, covidCertif, texte, qrCode):
        self.status, self.resultHTML, self.resultJSON, self.covidCertif = status, resultHTML, resultJSON, covidCertif
        self.texte, self.qrCode = texte, qrCode
        
    def setStatus( self, s ) :
        self.status = s
        
    def setResultHTML( self, r ) :
        self.resultHTML = r

    def setResultJSON( self, r ) :
        self.resultJSON = r

    def setCovidCertif( self, c ) :
        self.covidCertif = c

    def setTexte( self, t) :
        self.texte = t

    def setQrCode( self, q ) :
        self.qrCode = q
        
lastResult = TestResult("","","",None, None, None)

speaker = win32com.client.Dispatch("SAPI.SpVoice", pythoncom.CoInitialize())

testQRcode = "6BFOXN%TSMAHN-H6SKJPT.-7G2TZ978S80RBXEJW.TFJTXG41UQR$TTSJOF4R0WAN9I6T5XH-G2%E3EV4*2DYFPU*0CEBQ/GXQFY735LBJU0QHNRXGFAF+BB5-0G.8UG5EV40ATPHN7Y47%S7Y48YIZ73423ZQTZABDG35:43%2..P*PP:+P*.1D9R+Q6646G%63ZMZE9KZ56DE/.QC$Q3J62:6HT02R5LDCPF5RBQ746B46O1N646RM9AL5CBVW566LH 469/9-3AKI62R6R3R/FMSW6PK99Q9E$BDZIA9JQWTC.SPTI92KVB28PS.VS062POJC0JYB0ZY9P8Q/98V7J$%25I3KC3X83277U5S1DF3I8R39WZ8JG3OA5Y06C67 M1A0HBF144K0HPLWEU6UX0EI+NSQNK:C%QAWZ7F%NGCNOTN4IHX7SJ4P*P9X+P9.4AANBOO%+2D:3P.D"
status = ""
#app = Flask(__name__)
#db.init_app(app)
    
camera = cv2.VideoCapture(0)  # use 0 for web camera


font = cv2.FONT_HERSHEY_SIMPLEX


def decode(im) : 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    return decodedObjects

class passAnalyser (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global lastResult
        
        resultHTML = ""
        time.sleep(0.5)
        testCertif( lastResult.qrCode )
        for t in lastResult.texte :
            resultHTML=resultHTML+t+"<br/>"

        lastResult.setResultHTML( resultHTML )   

        for t in lastResult.texte :
            printAndSay(t)

        time.sleep(10)
        lastResult = TestResult("","","",None, None, "")




def gen_frames():  # generate frame by frame from camera global

    global lastResult
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

                if decodedObject.type=="QRCODE" and payload != lastResult.qrCode:
                    
                    try:
                        status = "processing"
                        lastResult.setQrCode( payload )
                        t = passAnalyser()
                        t.start()

                    except Exception as e:
                        #printAndSay("Impossible de décoder ce qr code")
                        print("error decoding", e)
        
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
        


#https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf
def testCertif(qrcode):
    global status
    global lastResult
    
    texte = []
    decode45 = base45.b45decode(qrcode)
    decompressed = zlib.decompress(decode45)
    cose = CoseMessage.decode(decompressed)
    jsons = cbor2.loads(cose.payload)
    root = jsons[-260][1]
    name = root["nam"]
    resultJSON = pprint.pformat(jsons)
    print ( resultJSON )
    resultJSON = resultJSON.replace("\n","<BR>").replace(" ","&nbsp;&nbsp;");
    lastResult.setResultJSON( resultJSON )
    certif = CovidCertif.CovidCertif(name["gn"], name["fn"], name["gnt"], name["fnt"], root["dob"]) 
    passValide = False
    
    try:
        vaccines = root["v"]
        if vaccines is not None:
            for v in vaccines:
                vacc = CovidCertif.CovidVaccine(v["dt"],v["sd"], v["dn"], v["mp"])
                certif.addVaccine(vacc)
    except:
        print("Not a vaccine")
        
    try:
        tests = root["t"]
        if tests is not None:
            for t in tests:
                test = CovidCertif.CovidTest(t["sc"],t["tc"])
                certif.addTest(test)
    except:
        print("Not a Test")
        
    try:
        recoveries = root["r"]
        if recoveries is not None:
            for r in recoveries:
                recovery = CovidCertif.CovidRecovery(r["df"], r["du"], r["fr"])
                certif.addRecovery(recovery)
    except:
        print("Not a Recovery")

    lastResult.setCovidCertif( certif )
    lastResult.setStatus("processing");
    
    currDate = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")


    texte.append("Bonjour "+certif.name)
    if certif.getType() == "vaccine":
        lastVaccine = certif.getLastVaccine()
        texte.append("Vous avez reçu "+str(lastVaccine.nbDose)+" doses d'un vaccin produit par : "+CovidCertif.vaccine_products[lastVaccine.product])

        if lastVaccine.nbDoseFull<=lastVaccine.nbDose :
            texte.append("Votre schéma vaccinal est donc complet depuis le "+dateUtils.getDateReadable(lastVaccine.getDate()))
            certifValidity = dateUtils.getDatePlus(lastVaccine.getDate(), 7)
            texte.append("Selon la législation actuelle votre passe sanitaire est valide depuis le "+dateUtils.getDateReadable(certifValidity))
            passValide = True
            lastResult.setStatus("valid")
        else :
            lastResult.setStatus("invalid")
            texte.append("Votre schéma vaccinal n'est donc pas encore complet et votre passe n'est donc pas valide")
        
    if certif.getType() == "test":
        lastTest = certif.getLastTest()
        texte.append("Votre test a été effectué le "+dateUtils.getDateReadable(lastTest.getDate())+" en "+lastTest.getPays())
        testValidTill = dateUtils.getDatePlus(lastTest.getDate(), 3)
        currDate = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")
        if currDate <= testValidTill :  #WARNING 72H et pas 3 jours
            texte.append("Votre test est valide depuis le "+dateUtils.getDateReadable(lastTest.getDate()))
            texte.append("Selon la législation actuelle votre passe sanitaire est valide jusqu'au "+dateUtils.getDateReadable(testValidTill))
            passValide = True
            lastResult.setStatus("valid")
        else :
            lastResult.setStatus("invalid")
            texte.append("Votre test n'est plus valide depuis le "+dateUtils.getDateReadable(testValidTill))

    if certif.getType() == "recovery":
        lastRecovery = certif.getLastRecovery()
        texte.append("Votre certificat de rétablissement est valide du "+dateUtils.getDateReadable(lastRecovery.getValidFrom())+" au "+lastRecovery.getValidTo())
        if currDate <= lastRecovery.getValidTo() : 
            texte.append("Votre certificat est valide depuis le "+dateUtils.getDateReadable(lastRecovery.getValidFrom()))
            texte.append("Selon la législation actuelle votre passe sanitaire est valide jusqu'au "+dateUtils.getDateReadable(lastRecovery.getValidTo()))
            passValide = True
            lastResult.setStatus("valid")
        else :
            lastResult.setStatus("invalid")
            texte.append("Votre certificat de rétablissement n'est plus valide depuis le "+dateUtils.getDateReadable(lastRecovery.getValidTo()))

    if lastResult.status == "invalid" :
        texte.append("La législation vous impose de quitter le bâtiment. Si vous choisissez de rester vous risquez une amende "+
                     "en cas de contrôle. L'association TechTicAndCo décline toute responsabilité")
    lastResult.setTexte( texte )  

@bp.route('/result_img')
def result_img():
    global lastResult
    if lastResult.status != "":
        print("status : "+lastResult.status )
        return '<img src="/get_image?type='+lastResult.status+'" width="640" height="360">'
    else:
        return '<br/>'
        

@bp.route('/get_image')
def get_image():
    imgtype = request.args.get('type')
    if imgtype == 'valid':
       filename = 'validpass.png'
    elif imgtype == 'invalid':
       filename = 'invalidpass.png'
    elif imgtype == 'processing':
        filename = 'processing.png'
    else:
       filename = ""
    return send_file(filename, mimetype='image/png')

@bp.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/')
def index():
    return render_template('index.html')

@bp.route("/result_txt")
def code():
    global lastResult
    if lastResult.resultHTML != "":
        return "<h3>Statut de votre certificat</h3><p>"+lastResult.resultHTML+"</p>"
    else:
        return ""
    
@bp.route("/result_json")
def json():
    global lastResult
    if lastResult.resultJSON != "":
        return "<h3>Ci-dessous le contenu de votre certificat</h3><p>"+lastResult.resultJSON+"</p>"
    else:
        return ""
    
@bp.route("/result_user_thilab")
def user_thilab():
    global lastResult

    certif = lastResult.covidCertif
    userTxt = ""
    if certif != None :
        try:
            print( "Looking at user : "+certif.surname +" "+certif.name)
            db = get_db()
            db.execute("insert into thilab_users (name, surname, dateOfBirth, isMember) values ('LAURENCE', 'MOREL', '1975-06-23', 0);")
            
            users = db.execute('SELECT id, name, surname, dateOfBirth, isMember '
                ' FROM thilab_users;').fetchall()
            print( "Found "+str(len(users))+" members")
            for user in users:
                print( user["name"] + " " + user["surname"])
            #'SELECT id, name, surname, dateOfBirth, isMember'
            user = db.execute(
                'SELECT id, name, surname, dateOfBirth, isMember '
                ' FROM thilab_users '
                ' WHERE upper(name)=upper(?) and upper(surname)=upper(?) and dateOfBirth=?',
                (certif.name, certif.surname, certif.dateOfBirth)
            ).fetchone()

            if user == None :
                userTxt =  "Vous n'êtes pas membre de l'association TechTic et ko. Vous pouvez adhérer à tout moment sur notre site internet."
            else :
                if user["isMember"] == 1 :
                    userTxt = "Votre cotisation est à jour";
                else:
                    userTxt = "Votre cotisation n'est pas à jour. Veuillez vous rapprocher d'un membre de l'association pour régulariser votre situation"
        except BaseException as e:
            print("cannot read db "+str(e))

    if userTxt != "":
        return "<h3>Etat de votre adhésion</h3><p>"+userTxt+"</p>"
    else:
        return ""
    
#if __name__ == '__main__':

#    app.run(debug=True)

import threading
import time
import base45
import cbor2
import zlib
import pprint
import os
from datetime import datetime
from cose.messages import CoseMessage
if os.name == 'nt':  # sys.platform == 'win32':
    import pythoncom
    import win32com.client
    speaker = win32com.client.Dispatch("SAPI.SpVoice", pythoncom.CoInitialize())

from . import CovidCertif
from . import TestResult
from . import dateUtils

class PassAnalyser (threading.Thread):
    def __init__(self, app, lastResult):
        threading.Thread.__init__(self)
        self.lastResult = lastResult
        self.app = app

    def run(self):
        
        resultHTML = ""
        time.sleep(0.5)
        self.testCertif( self.lastResult.qrCode )
        for t in self.lastResult.texte :
            resultHTML=resultHTML+t+"<br/>"

        self.lastResult.setResultHTML( resultHTML )   

        for t in self.lastResult.texte :
            self.printAndSay(t)

        time.sleep(10)
        self.lastResult.reset()

    #https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf
    def testCertif(self, qrcode):
     
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
        self.lastResult.setResultJSON( resultJSON )
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

        self.lastResult.setCovidCertif( certif )
        self.lastResult.setStatus("processing");
        
        currDate = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")
        texte.append("Bonjour "+certif.name)

        if certif.getType() == "vaccine":
            lastVaccine = certif.getLastVaccine()
            texte.append("Vous avez reçu "+str(lastVaccine.nbDose)+" doses d'un vaccin produit par : "+CovidCertif.vaccine_products[lastVaccine.product]+".")

            if lastVaccine.nbDoseFull<=lastVaccine.nbDose :
                texte.append("Votre schéma vaccinal est donc complet depuis le "+dateUtils.getDateReadable(lastVaccine.getDate())+".")
                certifValidity = dateUtils.getDatePlus(lastVaccine.getDate(), 7)
                texte.append("Selon la législation actuelle votre passe sanitaire est valide depuis le "+dateUtils.getDateReadable(certifValidity)+".")
                passValide = True
                self.lastResult.setStatus("valid")
            else :
                self.lastResult.setStatus("invalid")
                texte.append("Votre schéma vaccinal n'est donc pas encore complet et votre passe n'est donc pas valide.")
            
        if certif.getType() == "test":
            lastTest = certif.getLastTest()
            texte.append("Votre test a été effectué le "+dateUtils.getDateReadable(lastTest.getDate())+" en "+lastTest.getPays()+".")
            testValidTill = dateUtils.getDatePlus(lastTest.getDate(), 3)
            currDate = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")
            if currDate <= testValidTill :  #WARNING 72H et pas 3 jours
                texte.append("Votre test est valide depuis le "+dateUtils.getDateReadable(lastTest.getDate())+".")
                texte.append("Selon la législation actuelle votre passe sanitaire est valide jusqu'au "+dateUtils.getDateReadable(testValidTill)+".")
                passValide = True
                self.lastResult.setStatus("valid")
            else :
                self.lastResult.setStatus("invalid")
                texte.append("Votre test n'est plus valide depuis le "+dateUtils.getDateReadable(testValidTill)+".")

        if certif.getType() == "recovery":
            lastRecovery = certif.getLastRecovery()
            texte.append("Votre certificat de rétablissement est valide du "+dateUtils.getDateReadable(lastRecovery.getValidFrom())+" au "+lastRecovery.getValidTo()+".")
            if currDate <= lastRecovery.getValidTo() : 
                texte.append("Votre certificat est valide depuis le "+dateUtils.getDateReadable(lastRecovery.getValidFrom())+".")
                texte.append("Selon la législation actuelle votre passe sanitaire est valide jusqu'au "+dateUtils.getDateReadable(lastRecovery.getValidTo())+".")
                passValide = True
                self.lastResult.setStatus("valid")
            else :
                self.lastResult.setStatus("invalid")
                texte.append("Votre certificat de rétablissement n'est plus valide depuis le "+dateUtils.getDateReadable(lastRecovery.getValidTo())+".")

        if self.lastResult.status == "invalid" :
            texte.append("La législation vous impose de quitter le bâtiment. Si vous choisissez de rester vous risquez une amende "+
                         "en cas de contrôle. L'association TechTicAndCo décline toute responsabilité.")
        self.lastResult.setTexte( texte )  

    def printAndSay(self,sentence):
        print(sentence)
        if os.name == 'posix':
            filename = os.path.join(self.app.root_path, '1.wav')
            os.system("pico2wave -l fr-FR -w="+filename+"  \""+sentence+"\"")
            time.sleep(0.5)
            os.system("/usr/bin/aplay "+filename)
        if os.name == 'nt':
            speaker.Speak(sentence)



import requests
from datetime import datetime
import urllib.parse

class PadManager:
    def __init__(self, adr, secret, api_version, entete, padId):
        self.api_url = adr
        self.api_key =  secret
        self.api_version = api_version
        self.entete = entete
        self.getTextUrl = adr+"/api"+"/"+api_version+"/getText?apikey="+secret
        self.setTextUrl = adr+"/api"+"/"+api_version+"/setText"
        self.appendTextUrl = adr+"/api"+"/"+api_version+"/appendText?apikey="+secret
        self.createPadUrl = adr+"/api"+"/"+api_version+"/createPad?apikey="+secret
        
        self.padId=padId

        self.createPad()
        
    def getText(self):
        res = requests.get(url = self.getTextUrl)
        return res
    
    def append(self, t):
        urlGet = self.getTextUrl+"&padID="+self.padId
        resGet = requests.get(url = urlGet)
        fullText = resGet.json()['data']['text']+t+"\n"
        postParam={"apikey":self.api_key,"padID":self.padId,"text":fullText}
        resPost = requests.post(url = self.setTextUrl, data = postParam)


        return resPost.status_code
    
    def createPad(self):
        url = self.createPadUrl+"&padID="+self.padId+"&text="+self.entete
        res = requests.get(url = url)
        print(url)
        return res.status_code

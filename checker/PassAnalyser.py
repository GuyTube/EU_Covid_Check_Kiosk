import threading
import time
import base45
import cbor2
import zlib
import pprint
import os
import json
import base64
from datetime import datetime
from cose.messages import CoseMessage
from cose.headers import Algorithm, KID
from cose.keys import cosekey, ec2, keyops, curves
from typing import Dict, Tuple, Optional
from cryptography import x509
from cryptography import hazmat
from pyasn1.codec.ber import decoder as asn1_decoder
from cryptojwt import jwk as cjwtk
from cryptojwt import utils as cjwt_utils
import pygame

if os.name == 'nt':  # sys.platform == 'win32':
    import pythoncom
    import win32com.client
    speaker = win32com.client.Dispatch("SAPI.SpVoice", pythoncom.CoInitialize())

from . import CovidCertif
from . import TestResult
from . import dateUtils
from . import PadManager

DEFAULT_CERTIFICATE_DB_JSON = 'certs/Digital_Green_Certificate_Signing_Keys.json'


class PassAnalyser (threading.Thread):
    def __init__(self, app, lastResult):
        threading.Thread.__init__(self)
        self.lastResult = lastResult
        self.app = app
        pygame.init()


    def run(self):
        self.special_cases = json.loads(self.app.config.get("SPECIAL_CASES"))
            
        self.pm = None
        try:
            currDate = datetime.strftime(datetime.now(), "%Y-%m-%d")
            entete="Entrées du "+currDate
            padId="pass-log-"+currDate
            self.pm = PadManager.PadManager(self.app.config.get("PAD_HTTP_URL"),self.app.config.get("API_KEY"), self.app.config.get("API_VERSION"), entete, padId)
        except Exception as e:
            print("error creating pad", e)
            
        resultHTML = ""
        time.sleep(0.5)
        self.testCertif( self.lastResult.qrCode )
        for t in self.lastResult.texte :
            resultHTML=resultHTML+t+"<br/>"

        self.lastResult.setResultHTML( resultHTML )

        if self.pm != None :
            self.logToPad(self.lastResult.getPadLog())

        fullText = " ".join(self.lastResult.texte)
        self.printAndSay(fullText)

        time.sleep(10)
        pygame.mixer.music.fadeout(500)

        self.lastResult.reset()

    def logToPad(self, t) :
        self.pm.append(t)
        
    #https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf
    def testCertif(self, qrcode):

        checkSignature = self.app.config.get("CHECK_SIGNATURE"=="true")
        texte = []
        decode45 = base45.b45decode(qrcode)
        decompressed = zlib.decompress(decode45)
        cose = CoseMessage.decode(decompressed)
        key = self.find_key(cose.phdr[KID], DEFAULT_CERTIFICATE_DB_JSON)
        validSignature = False
        if key:
            validSignature = self.verify_signature(cose, key)
        else:
            print("Skip verify as no key found from database")
        jsons = cbor2.loads(cose.payload)
        root = jsons[-260][1]
        name = root["nam"]
        resultJSON = pprint.pformat(jsons)
        print ( resultJSON )
        resultJSON = resultJSON.replace("\n","<BR>").replace(" ","&nbsp;&nbsp;");
        self.lastResult.setResultJSON( resultJSON )
        certif = CovidCertif.CovidCertif(name["gn"], name["fn"], name["gnt"], name["fnt"], root["dob"])
        passValide = False

        self.is_special_case(certif.surname, certif.name, certif.dateOfBirth)

        if not validSignature and checkSignature:
            texte.append("Ce certificat est un faux. La loi ne vous autorise pas à rester dans ce bâtiment")
            self.lastResult.setCovidCertif( certif )
            self.lastResult.setStatus("invalid")
            self.lastResult.setTexte( texte )  
            return
        
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
            texte.append("Votre certificat de rétablissement est valide du "+dateUtils.getDateReadable(lastRecovery.getValidFrom())+" au "+dateUtils.getDateReadable(lastRecovery.getValidTo())+".")
            if currDate <= lastRecovery.getValidTo() : 
                passValide = True
                self.lastResult.setStatus("valid")
            else :
                self.lastResult.setStatus("invalid")
                texte.append("Votre certificat de rétablissement n'est plus valide depuis le "+dateUtils.getDateReadable(lastRecovery.getValidTo())+".")

        if self.lastResult.status == "invalid" :
            texte.append("La législation vous interdit de rester dans ce bâtiment. Si toutefois vous choisissez de rester les responsables de l'association,"
                         " qui ne peuvent vous contraindre physiquement à partir, décline toute responsabilité en cas de contrôle et ne cautionne pas votre attitude.")
        self.lastResult.setTexte( texte )  

    def printAndSay(self,sentence):
        print(sentence)
        if self.app.config.get("TALKACTIVE") :
            if os.name == 'posix':
                filename = os.path.join(self.app.root_path, '1.wav')
                os.system("pico2wave -l fr-FR -w="+filename+"  \""+sentence+"\"")
                time.sleep(1)
                self.playMusic(filename)
            if os.name == 'nt':
                speaker.Speak(sentence)

    def playMusic(self,filename,vol=1.0,wait=False):
        while wait and pygame.mixer.get_busy() :
            time.sleep(0.1)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.play(loops=0)
        
    def verify_signature(self, cose_msg: CoseMessage, key: cosekey.CoseKey) -> bool:
        cose_msg.key = key
        if not cose_msg.verify_signature():
            print("Signature does not verify with key ID {0}!".format(key.kid.decode()))
            return False

        print("Signature verified ok")

        return cose_msg.verify_signature()


    def find_key(self, key: Algorithm, keys_file: str) -> Optional[cosekey.CoseKey]:

        # Read the JSON-database of all known keys
        with open(keys_file, encoding='utf-8') as f:
            known_keys = json.load(f)

        jwt_key = None
        for key_id, key_data in known_keys.items():
            key_id_binary = base64.b64decode(key_id)
            if key_id_binary == key:
                print("Found the key from DB!")
                # pprint(key_data)
                # check if the point is uncompressed rather than compressed
                x, y = self.public_ec_key_points(base64.b64decode(key_data['publicKeyPem']))
                key_dict = {'crv': key_data['publicKeyAlgorithm']['namedCurve'],  # 'P-256'
                            'kid': key_id_binary.hex(),
                            'kty': key_data['publicKeyAlgorithm']['name'][:2],  # 'EC'
                            'x': x,  # 'eIBWXSaUgLcxfjhChSkV_TwNNIhddCs2Rlo3tdD671I'
                            'y': y,  # 'R1XB4U5j_IxRgIOTBUJ7exgz0bhen4adlbHkrktojjo'
                            }
                jwt_key = self.cosekey_from_jwk_dict(key_dict)
                break

        if not jwt_key:
            return None

        if jwt_key.kid.decode() != key.hex():
            raise RuntimeError("Internal: No key for {0}!".format(key.hex()))

        return jwt_key


    def public_ec_key_points(self, public_key: bytes) -> Tuple[str, str]:
        # This code adapted from: https://stackoverflow.com/a/59537764/1548275
        public_key_asn1, _remainder = asn1_decoder.decode(public_key)
        public_key_bytes = public_key_asn1[1].asOctets()

        off = 0
        if public_key_bytes[off] != 0x04:
            raise ValueError("EC public key is not an uncompressed point")
        off += 1

        size_bytes = (len(public_key_bytes) - 1) // 2

        x_bin = public_key_bytes[off:off + size_bytes]
        x = int.from_bytes(x_bin, 'big', signed=False)
        off += size_bytes

        y_bin = public_key_bytes[off:off + size_bytes]
        y = int.from_bytes(y_bin, 'big', signed=False)
        off += size_bytes

        bl = (x.bit_length() + 7) // 8
        bytes_val = x.to_bytes(bl, 'big')
        x_str = base64.b64encode(bytes_val, altchars='-_'.encode()).decode()

        bl = (y.bit_length() + 7) // 8
        bytes_val = y.to_bytes(bl, 'big')
        y_str = base64.b64encode(bytes_val, altchars='-_'.encode()).decode()

        return x_str, y_str


    # Create CoseKey from JWK
    def cosekey_from_jwk_dict(self, jwk_dict: Dict) -> cosekey.CoseKey:
        # Read key and return CoseKey
        if jwk_dict["kty"] != "EC":
            raise ValueError("Only EC keys supported")
        if jwk_dict["crv"] != "P-256":
            raise ValueError("Only P-256 supported")

        from pprint import pprint
        key = ec2.EC2(
            crv=curves.P256,
            x=cjwt_utils.b64d(jwk_dict["x"].encode()),
            y=cjwt_utils.b64d(jwk_dict["y"].encode()),
        )
        key.key_ops = [keyops.VerifyOp]
        if "kid" in jwk_dict:
            key.kid = bytes(jwk_dict["kid"], "UTF-8")

        return key


    # Create JWK and valculate KID from Public Signing Certificate
    def read_cosekey_from_pem_file(self, cert_file: str) -> cosekey.CoseKey:
        # Read certificate, calculate kid and return EC CoseKey
        if not cert_file.endswith(".pem"):
            raise ValueError("Unknown key format. Use .pem keyfile")

        with open(cert_file, 'rb') as f:
            cert_data = f.read()
            # Calculate Hash from the DER format of the Certificate
            cert = x509.load_pem_x509_certificate(cert_data, hazmat.backends.default_backend())
            keyidentifier = cert.fingerprint(hazmat.primitives.hashes.SHA256())
        f.close()
        key = cert.public_key()

        jwk = cjwtk.ec.ECKey()
        jwk.load_key(key)
        # Use first 8 bytes of the hash as Key Identifier (Hex as UTF-8)
        jwk.kid = keyidentifier[:8].hex()
        jwk_dict = jwk.serialize(private=False)

        return cosekey_from_jwk_dict(jwk_dict)

    def is_special_case(self, surname, name, dob) :
        for pers in self.special_cases:
            if pers['surname'].casefold() == surname.casefold() and pers['name'].casefold() == name.casefold() and pers['date-of-birth']==dob :
                self.playMusic(pers['music'],0.5)
        return False

from flask import Blueprint, Flask, render_template, Response, send_file, request
import cv2
import pyzbar.pyzbar as pyzbar
import time
from datetime import datetime   
import sqlite3
import os
from checker.db import get_db
from . import CovidCertif
from . import dateUtils
from . import TestResult
from . import PassAnalyser

# install flask https://linuxize.com/post/how-to-install-flask-on-ubuntu-18-04/
#pip install cryptography==2.8 sur windows pip install cryptography
#pip install cose
#pip install cbor2
#pip install base45
#pip3 install opencv-python
#pip3 install pyzbar
#pip install pywin32 // pour windows uniquement
#pip install pandas //csv
#pip install pythoncom // Windows uniquement
#pip install pyasn1
#pip install cryptojwt
#pip install playsound==1.2.2 // for python >3.8

app = Flask(__name__)

lastResult = TestResult.TestResult("","","",None, None, None, None)
camera = cv2.VideoCapture(0)  # use 0 for web camera
font = cv2.FONT_HERSHEY_SIMPLEX
bp = Blueprint('checker', __name__)
config = app.config.from_pyfile(os.path.join(".", "config/app.conf"), silent=False)

def decode(im) : 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    return decodedObjects

def gen_frames():  # generate frame by frame from camera global
    global lastResult

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
                        lastResult.date = datetime.now()
                        t = PassAnalyser.PassAnalyser(app, lastResult)
                        t.start()

                    except Exception as e:
                        print("error decoding", e)
            frame = cv2.flip(frame,1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result        

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
       filename = app.config.get("VALID_IMAGE")
    elif imgtype == 'invalid':
       filename = app.config.get("INVALID_IMAGE")
    elif imgtype == 'processing':
        filename = app.config.get("PROCESSING_IMAGE")
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

@bp.route('/testPad')
def testPad():
    from . import PadManager
    currDate = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")

    entete="Entr??es du "+currDate
    padId="pass-log-"+currDate
    
    pm = PadManager.PadManager(app.config.get("PAD_HTTP_URL"),app.config.get("API_KEY"), app.config.get("API_VERSION"), entete, padId)
    pm.append("2021-10-15T01:01:01 BOCKENFUSEAU MARCEL")
    return "Testing pad "+pm.padId

@bp.route('/test')
def test():
    return app.config.get("SPECIAL_CASES")

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
            db = get_db()
            user = db.execute(
                'SELECT id, name, surname, dateOfBirth, isMember '
                ' FROM thilab_users '
                ' WHERE upper(name)=upper(?) and upper(surname)=upper(?) ',
                (certif.name, certif.surname)
            ).fetchone()

            if user == None :
                userTxt =  "Vous n'??tes pas membre de l'association "+app.config.get("ASSOCIATION_NAME")+". Vous pouvez adh??rer ?? tout moment sur notre site internet."
            else :
                if user["isMember"] == 1 :
                    userTxt = "Votre cotisation est ?? jour";
                else:
                    userTxt = "Votre cotisation n'est pas ?? jour. Veuillez vous rapprocher d'un membre de l'association pour r??gulariser votre situation"
        except BaseException as e:
            print("cannot read db "+str(e))

    if userTxt != "":
        return "<h3>Etat de votre adh??sion</h3><p>"+userTxt+"</p>"
    else:
        return ""


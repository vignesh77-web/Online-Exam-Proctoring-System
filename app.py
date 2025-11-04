import math
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify, session,redirect,url_for,Response,flash,send_file
import os
import sqlite3
import json
import io
import warnings
import threading
import utils
import random
import time
import shutil

# Try to import optional packages
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not available")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not available")

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("Warning: keyboard not available")

#variables
studentInfo=None
camera=None
profileName=None

#Flak's Application Confguration
warnings.filterwarnings("ignore")
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'xyz'
# app.config["MONGO_URI"] = "mongodb://localhost:27017/"
os.path.dirname("../templates")

# Helpers
def current_user():
    return session.get('user')

def require_login():
    return current_user() is not None

def require_admin():
    u = current_user()
    return u is not None and u.get('Role') == 'ADMIN'

#Flask's Database Configuration
def get_db_connection():
    conn = sqlite3.connect('examproctordb.db')
    conn.row_factory = sqlite3.Row
    return conn

executor = ThreadPoolExecutor(max_workers=4)  # Adjust the number of workers as needed

#Function to show face detection's Rectangle in Face Input Page
def capture_by_frames():
    if not CV2_AVAILABLE:
        # Return a simple message frame when OpenCV is not available
        yield (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\n' + b'Camera not available - OpenCV not installed' + b'\r\n')
        return
    
    global camera
    utils.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        success, frame = utils.cap.read()  # read the camera frame
        detector=cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
        faces=detector.detectMultiScale(frame,1.2,6)
         #Draw the rectangle around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#Function to run Cheat Detection when we start run the Application
@app.before_request
def start_loop():
    task1 = executor.submit(utils.cheat_Detection2)
    task2 = executor.submit(utils.cheat_Detection1)
    task3 = executor.submit(utils.fr.run_recognition)
    task4 = executor.submit(utils.a.record)


#Login Related
@app.route('/')
def main():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    from werkzeug.security import check_password_hash
    global studentInfo
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ID, Name, Email, Password, Role FROM students WHERE Email=?", (username,))
        data = cur.fetchone()
        cur.close()
        conn.close()
        if data is None:
            flash('Your Email or Password is incorrect, try again.', category='error')
            return redirect(url_for('main'))
        else:
            id, name, email, hashed_password, role = data
            if not check_password_hash(hashed_password, password):
                flash('Your Email or Password is incorrect, try again.', category='error')
                return redirect(url_for('main'))
            studentInfo={ "Id": id, "Name": name, "Email": email, "Role": role }
            session['user'] = studentInfo
            if role == 'STUDENT':
                utils.Student_Name = name
                return redirect(url_for('rules'))
            else:
                return redirect(url_for('adminStudents'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('login.html')

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    from werkzeug.security import generate_password_hash
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        # Basic server validation
        if not name or not email or not password:
            flash('All fields are required', category='error')
            return redirect(url_for('signup'))
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO students (Name, Email, Password, Role) VALUES (?, ?, ?, ?)", (name, email, generate_password_hash(password), 'STUDENT'))
            conn.commit()
            flash('Account created. Please log in.', category='success')
            return redirect(url_for('main'))
        except Exception as e:
            flash('Email already exists', category='error')
            return redirect(url_for('signup'))
        finally:
            cur.close()
            conn.close()

# DB healthcheck
@app.route('/health/db')
def health_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        res = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"ok": True, "result": res[0] if res else None})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

#Student Related
@app.route('/rules')
def rules():
    if not require_login():
        return redirect(url_for('main'))
    return render_template('ExamRules.html')

@app.route('/faceInput')
def faceInput():
    if not require_login():
        return redirect(url_for('main'))
    return render_template('ExamFaceInput.html')

@app.route('/video_capture')
def video_capture():
    if not CV2_AVAILABLE:
        # Serve a static placeholder image when camera is unavailable
        return send_file('static/img/faceDetect.png', mimetype='image/png')
    return Response(capture_by_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/saveFaceInput', methods=['GET','POST'])
def saveFaceInput():
    global profileName
    user = session.get('user')
    if not user:
        return redirect(url_for('main'))
    # Browser capture via base64
    if request.method == 'POST':
        try:
            data = request.get_json(force=True)
            data_url = data.get('image','')
            if data_url.startswith('data:image'):
                header, b64 = data_url.split(',',1)
                import base64
                img_bytes = base64.b64decode(b64)
                profileName = f"{user['Name']}_{utils.get_resultId():03}" + "Profile.png"
                dst_dir = os.path.join('static','Profiles')
                os.makedirs(dst_dir, exist_ok=True)
                with open(os.path.join(dst_dir, profileName), 'wb') as f:
                    f.write(img_bytes)
                return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        return jsonify({"ok": False}), 400

    if not CV2_AVAILABLE:
        # Create a dummy profile when OpenCV is not available
        profileName = f"{user['Name']}_{utils.get_resultId():03}" + "Profile.png"
        src = os.path.join('static','img','faceDetect.png')
        dst_dir = os.path.join('static','Profiles')
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, profileName)
        try:
            shutil.copyfile(src, dst)
        except Exception:
            # Fallback: create a tiny placeholder file
            with open(dst, 'wb') as f:
                f.write(b'')
        return redirect(url_for('confirmFaceInput'))
    
    if utils.cap.isOpened():
        utils.cap.release()
    cam = cv2.VideoCapture(0)
    success, frame = cam.read()  # read the camera frame
    profileName=f"{user['Name']}_{utils.get_resultId():03}" + "Profile.jpg"
    cv2.imwrite(profileName,frame)
    utils.move_file_to_output_folder(profileName,'static/Profiles')
    cam.release()
    return redirect(url_for('confirmFaceInput'))

@app.route('/confirmFaceInput')
def confirmFaceInput():
    if not session.get('user'):
        return redirect(url_for('main'))
    profile = profileName if profileName else ''
    if profile == '':
        # ensure placeholder exists in static/Profiles
        placeholder = 'placeholder.png'
        dst_dir = os.path.join('static','Profiles')
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, placeholder)
        if not os.path.exists(dst):
            try:
                shutil.copyfile(os.path.join('static','img','faceDetect.png'), dst)
            except Exception:
                with open(dst, 'wb') as f:
                    f.write(b'')
        profile = placeholder
    utils.fr.encode_faces()
    return render_template('ExamConfirmFaceInput.html', profile = profile)

@app.route('/systemCheck')
def systemCheck():
    if not require_login():
        return redirect(url_for('main'))
    return render_template('ExamSystemCheck.html')

@app.route('/systemCheck', methods=["POST"])
def systemCheckRoute():
    if request.method == 'POST':
        examData = request.json
        output = 'exam'
        if 'Not available' in examData['input'].split(';'): output = 'systemCheckError'
    return jsonify({"output": output})

@app.route('/systemCheckError')
def systemCheckError():
    if not require_login():
        return redirect(url_for('main'))
    return render_template('ExamSystemCheckError.html')

@app.route('/exam')
def exam():
    if not session.get('user'):
        return redirect(url_for('main'))
    if CV2_AVAILABLE:
        utils.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if KEYBOARD_AVAILABLE:
        keyboard.hook(utils.shortcut_handler)
    return render_template('Exam.html')

@app.route('/exam', methods=["POST"])
def examAction():
    link = ''
    if request.method == 'POST':
        examData = request.json
        if(examData['input']!=''):
            utils.Globalflag= False
            try:
                if CV2_AVAILABLE and utils.cap is not None:
                    utils.cap.release()
            except Exception:
                pass
            utils.write_json({
                "Name": ('Prohibited Shorcuts (' + ','.join(list(dict.fromkeys(utils.shorcuts))) + ') are detected.'),
                "Time": (str(len(utils.shorcuts)) + " Counts"),
                "Duration": '',
                "Mark": (1.5 * len(utils.shorcuts)),
                "Link": '',
                "RId": utils.get_resultId()
            })
            utils.shorcuts=[]
            trustScore= utils.get_TrustScore(utils.get_resultId())
            totalMark=  math.floor(float(examData['input'])* 6.6667)
            if trustScore >=30:
                status="Fail(Cheating)"
                link = 'showResultFail'
            else:
                if totalMark < 50:
                    status="Fail"
                    link = 'showResultFail'
                else:
                    status="Pass"
                    link = 'showResultPass'
            utils.write_json({
                "Id": utils.get_resultId(),
                "Name": session.get('user',{}).get('Name','Student'),
                "TotalMark": totalMark,
                "TrustScore": max(100-trustScore, 0),
                "Status": status,
                "Date": time.strftime("%Y-%m-%d", time.localtime(time.time())),
                "StId": session.get('user',{}).get('Id',0),
                "Link" : profileName
            },"result.json")
            uname = session.get('user',{}).get('Name','Student')
            resultStatus= uname+';'+str(totalMark)+';'+status+';'+time.strftime("%Y-%m-%d", time.localtime(time.time()))
        else:
            utils.Globalflag = True
            print('sfdsfsdsfdsfdsfdsfdsfdsfdsfds')
            resultStatus=''
    return jsonify({"output": resultStatus, "link": link})

@app.route('/showResultPass/<result_status>')
def showResultPass(result_status):
    return render_template('ExamResultPass.html',result_status=result_status)

@app.route('/showResultFail/<result_status>')
def showResultFail(result_status):
    return render_template('ExamResultFail.html',result_status=result_status)

#Admin Related
@app.route('/adminResults')
def adminResults():
    if not require_admin():
        return redirect(url_for('main'))
    results = utils.getResults()
    return render_template('Results.html', results=results)

@app.route('/adminResultDetails/<resultId>')
def adminResultDetails(resultId):
    if not require_admin():
        return redirect(url_for('main'))
    # Load result summary and violations for this resultId
    violations = utils.getResultDetails(resultId)
    # Load the result summary from result.json
    results = utils.getResults()
    result_summary = None
    for r in results:
        if str(r.get('Id', '')) == str(resultId):
            result_summary = r
            break
    # Build the data structure the template expects
    result_Details = {
        'Result': [result_summary] if result_summary else [],
        'Violation': violations
    }
    return render_template('ResultDetails.html', resultDetials=result_Details)

@app.route('/adminResultDetailsVideo/<videoInfo>')
def adminResultDetailsVideo(videoInfo):
    if not require_admin():
        return redirect(url_for('main'))
    return render_template('ResultDetailsVideo.html', videoInfo= videoInfo)

@app.route('/adminStudents')
def adminStudents():
    if not require_admin():
        return redirect(url_for('main'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT ID, Name, Email, '' as Password, Role FROM students WHERE Role='STUDENT'")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('Students.html', students=data)

@app.route('/insertStudent', methods=['POST'])
def insertStudent():
    from werkzeug.security import generate_password_hash
    if request.method == "POST":
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO students (Name, Email, Password, Role) VALUES (?, ?, ?, ?)", (name, email, hashed,'STUDENT'))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('adminStudents'))

@app.route('/deleteStudent/<string:stdId>', methods=['GET'])
def deleteStudent(stdId):
    flash("Record Has Been Deleted Successfully")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE ID=?", (stdId,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('adminStudents'))

@app.route('/updateStudent', methods=['POST', 'GET'])
def updateStudent():
    from werkzeug.security import generate_password_hash
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        hashed = generate_password_hash(password)
        cur.execute("""
               UPDATE students
               SET Name=?, Email=?, Password=?
               WHERE ID=?
            """, (name, email, hashed, id_data))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('adminStudents'))

if __name__ == '__main__':
    app.run(debug=True)
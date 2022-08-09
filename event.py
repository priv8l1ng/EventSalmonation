from random import randint
from flask import Flask, render_template, request, jsonify
from flask_minify import minify
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import sys
import json
import time
import base64
from urllib.parse import parse_qs

production = True if int(sys.argv[1]) == 1 else False
app = Flask(__name__)

database = json.load(open("rensmtnet@event.salmonation.com.json", "r"))
if production == True:
    app.config['SECRET_KEY'] = 'RENSMT.NET Production'
    minify(app=app, html=True, js=True, cssless=True)
else:
    app.config['SECRET_KEY'] = 'RENSMT.NET Sandbox'
    app.env = "development"


@app.route("/")
def index():
    if production == True:
        return render_template("index.html")
    return render_template("maintenance.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/tes")
def tes():
    if production != True:
        return render_template("test.html")
    return "Website event.salmonation.com sudah aktif."


@app.route("/sandbox")
def sandbox():
    if production != True:
        return render_template("index.html")
    return "Website event.salmonation.com sudah aktif."


@app.route("/upload/<id>")
def upload(id):
    try:
        SECRET = base64.b64decode(id).decode()
        if "RENSMT.NET" in SECRET:
            id = SECRET.split("~")[1]
            return id
        return render_template("404.html")
    except:
        return render_template("404.html")


@app.route("/student-reg", methods=["POST", "GET"])
def student_reg():
    if request.method == "GET":
        ID = None
        while True:
            ID = f"ID-SUI{randint(100000, 999999)}"
            if ID in database["data"]:
                continue
            break
        UPLOADURL_SECRET = f"{round(time.time() * 1000)}-{request.headers['Cf-Ray']}@RENSMT.NET~{ID}"
        print("UPLOADURL_SECRET", UPLOADURL_SECRET)
        UPLOADURLB64 = base64.b64encode(UPLOADURL_SECRET.encode()).decode()
        print("UPLOADURLB64", UPLOADURLB64)
        UPLOADURL = f"/upload/{UPLOADURLB64}"
        print("UPLOADURL", UPLOADURL)
        return jsonify({"status": 200, "message": "endpoint is active.", "secure_by": database["security_db"]})
    elif request.method == "POST":
        try:
            result = {
                "status": 200
            }
            ID = None
            while True:
                ID = f"ID-SUI{randint(100000, 999999)}"
                if ID in database["data"]:
                    continue
                break
            UPLOADURL_SECRET = f"{round(time.time() * 1000)}-{request.headers['Cf-Ray']}@RENSMT.NET~{ID}"
            UPLOADURLB64 = base64.b64encode(UPLOADURL_SECRET.encode()).decode()
            UPLOADURL = f"/upload/{UPLOADURLB64}"
            dr = request.get_json()
            NAMA = dr["inputSiswa"]
            JK = dr["inputJK"]
            UMUR = dr["inputUmur"]
            ASALSCH = dr["inputASD"]
            ALMTSCH = dr["inputAlamatSekolah"]
            datareq = {"nama": NAMA, "jenis_kelamin": JK, "umur": int(
                UMUR), "asal_sekolah": ASALSCH, "alamat_sekolah": ALMTSCH, "upload_path": UPLOADURL, "upload_b64": UPLOADURLB64, "upload_url": f"https://event.salmonation.com{UPLOADURL}"}
            database["data"][ID] = datareq
            json.dump(database, open(
                "rensmtnet@event.salmonation.com.json", "w+"), indent=4)
            result["message"] = f"Berhasil mendaftar (ID Daftar: {ID})"
            result["id_siswa"] = ID
            result["data_siswa"] = datareq
            return jsonify(result)
        except:
            return jsonify({"status": 404, "message": "Wrong input on form."})


if __name__ == "__main__":
    port = 80
    debug = False
    if production == False:
        debug = True
    app.run(debug=debug, host="0.0.0.0", port=port)

import os.path

from flask import Flask, jsonify, request
from Utils import reverse_geocode, geocode, google_geocode, google_reverse_geocode
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]='mysql+pymysql://root:mysql@localhost/bd_demo_geo'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["UPLOAD_FOLDER"] = "uploads"
db = SQLAlchemy(app)
m = Marshmallow(app)


class Addresses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), unique=False)

    def __init__(self, address):
        self.address = address


class latlong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitud = db.Column(db.String(60))
    longitud = db.Column(db.String(60))

    def __init__(self, latitud, longitud):
        self.latitud = latitud
        self.longitud = longitud


with app.app_context():
    db.create_all()


class AddressSchema(m.Schema):
    class Meta:
        fields = ('id', 'address')


address_schema = AddressSchema()
addresses_schema = AddressSchema(many=True)


@app.route("/geoservice/google_geocode", methods=['POST'])
def direct_google_geocode():
    if int(request.json['flag']) == 2:
        location = google_geocode(request.json['address'])
        print(location.raw)
        new_latlong = latlong(location.latitude, location.longitude)
        db.session.add(new_latlong)
        db.session.commit()
        #result = address_schema.dump(new_latlong)
        return jsonify({"response": {"latitude": location.latitude, "longitude": location.longitude}})
    elif int(request.json['flag']) == 1:
        location = geocode(request.json['address'])
        return jsonify({"response": location})
    else:
        return jsonify({'ressponse': {'message': 'flag invalido'}})


@app.route("/geoservice/google_reverse_geocode", methods=['POST'])
def reverse_google_geocode():
    if int(request.json['flag']) == 2:
        location = google_reverse_geocode(request.json['latitude'], request.json['longitude'])
        print(location.raw)
        new_address = Addresses(location.address)
        db.session.add(new_address)
        db.session.commit()
        result = address_schema.dump(new_address)
        return jsonify({"response": result})
    elif int(request.json['flag']) == 1:
        location = reverse_geocode(request.json['latitude'], request.json['longitude'])
        new_address = Addresses(location.address)
        db.session.add(new_address)
        db.session.commit()
        result = address_schema.dump(new_address)
        return jsonify({"address": result})
    else:
        return jsonify({'response': {'message': 'flag invalido'}})


@app.route("/geoservice/file", methods=['POST'])
def upload_file():
    file = request.files['uploadFiles']
    file_name = secure_filename(file.filename)

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file_name))
    return "archivo cargado"


if __name__ == '__main__':
    app.run(debug=True, port=4000)

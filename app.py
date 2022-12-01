import os.path

from flask import Flask, jsonify, request,Blueprint, make_response
from Utils import reverse_geocode, geocode, google_geocode, google_reverse_geocode
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import flask_mysqldb
import secrets
import jwt
from jwt import decode,exceptions



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]='mysql+pymysql://root:mysql@localhost/bd_demo_geo'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["UPLOAD_FOLDER"] = "uploads"

#
app.config['SECRET_KEY'] = 'thisissecrectkey'

db = SQLAlchemy(app)
ma = Marshmallow(app)

#MySql 
#implementando sqlalchemy para registro en tablas

#nombre-direccion
class tb_address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), unique=False)

    def __init__(self, address):
        self.address = address

class direc_esquema(ma.Schema):
    class Meta:
        fields = ('id','address')

esquema_post= direc_esquema()
esquema_post=direc_esquema(many=True)

#latitud/longitud
class tb_latlong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitud = db.Column(db.String(60))
    longitud = db.Column(db.String(60))

    def __init__(self, latitud, longitud):
        self.latitud = latitud
        self.longitud = longitud

class esquema(ma.Schema):
    class Meta:
        fields = ('id','latitud','longitud')

esquema_post= esquema()
esquema_post=esquema(many=True)

#usuario
class tb_user(db.Model):
    idusuario= db.Column(db.Integer, primary_key=True)
    nombre= db.Column(db.String(200))
    apellido= db.Column(db.String(200))
    usuario= db.Column(db.String(200))
    contraseña= db.Column(db.String(200))
    
    def __init__(self,nombre,apellido,usuario,contraseña):
       
        self.nombre=nombre
        self.apellido=apellido
        self.usuario=usuario
        self.contraseña=contraseña


class esquema(ma.Schema):
    class Meta:
        fields = ('idusuario','nombre','apellido','usuario','contraseña')

esquema_post= esquema()
esquema_post=esquema(many=True)

#token
class tb_token(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    descripcion= db.Column(db.String(200))
    idusuario= db.Column(db.Integer, foreig_key=True)

    def __init__(self,descripcion,idusuario):
       
        self.descripcion=descripcion
        self.idusuario=idusuario


class esquema(ma.Schema):
    class Meta:
        fields = ('id','descripcion','idusuario')

esquema_post= esquema()
esquema_post=esquema(many=True)

with app.app_context():
    db.create_all()


#rutas

#crear usuario
@app.route("/registrar/usuario", methods=['POST'])
def create_user():
    
    nombre=request.json['nombre']
    apellido=request.json['apellido']
    user=request.json['usuario']
    contraseña= request.json['contraseña']

    variable= db.session.query(tb_user).filter(tb_user.usuario==user).first()

    if variable:
          return 'Ya existe el usuario'
          
    else:
            new_user = tb_user(nombre,apellido,user,contraseña)
            db.session.add(new_user)   

            db.session.commit()
            return 'Usuario Registrado Exitosamente!'

#login
#devuelve token

@app.route('/login', methods=['POST'])
def logear():
    
    user = request.json['usuario']
    
    nombre= db.session.query(tb_user).filter(tb_user.usuario==user).first()
    id= db.session.query(tb_user.idusuario).filter(tb_user.usuario==user)

    if nombre:
        token=write_token2(data=request.get_json())
        new_tbl=tb_token(token,id)
        db.session.add(new_tbl)   
        db.session.commit()
        
        return  token
       
    else:
        return 'Usuario no encontrado'
   


##
@app.route("/geoservice/google_geocode", methods=['POST'])
def direct_google_geocode():
    if int(request.json['flag']) == 2:
        location = google_geocode(request.json['address'])
        print(location.raw)
        new_latlong = tb_latlong(location.latitude, location.longitude)
        new_address = tb_address(location.address)

        db.session.add(new_latlong)
        db.session.add(new_address)

        db.session.commit()
        
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
        
        new_address = tb_address(location.address)
        new_latlong = tb_latlong(location.latitude, location.longitude)
        
        db.session.add(new_address)
        db.session.add(new_latlong)

        db.session.commit()
        
        return jsonify({"response": location.raw})
    elif int(request.json['flag']) == 1:
        location = reverse_geocode(request.json['latitude'], request.json['longitude'])
        new_address = tb_address(location.address)
        db.session.add(new_address)
        db.session.commit()
       
        return jsonify({"response": location.raw})
    else:
        return jsonify({'response': {'message': 'flag invalido'}})


@app.route("/geoservice/file", methods=['POST'])
def upload_file():
    file = request.files['uploadFiles']
    file_name = secure_filename(file.filename)

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file_name))
    return "archivo cargado"


#implementando token 

#primera forma
def write_token(data:dict):
    token = secrets.token_urlsafe(20)
    return token.encode('UTF-8')

#segunda forma
def write_token2(data:dict):
    token = jwt.encode(payload={**data, "exp":datetime.utcnow()+timedelta(seconds=60)},key=app.config['SECRET_KEY'], algorithm="HS256")
    return token.encode('UTF-8')

#validar token
def valida_token(token, output=False):

            try:
                if output:
               
                    return  decode(token, key=app.config['SECRET_KEY'], algorithms="HS256")
        
            except exceptions.DecodeError:
                response= jsonify({'message':'Token invalido'})
                response.status_code=401
                return response
            except exceptions.ExpiredSignatureError:
                response= jsonify({'message':'Token expirado'})
                response.status_code=401
                return response
        
    
@app.route('/verify/token')
def verify():
   location = google_reverse_geocode(request.json['lat'], request.json['long'])
   token = request.headers['Authorization'].split(" ")[1]
   return valida_token(token, output=True) 
 

#

if __name__ == '__main__':
    app.run(debug=True, port=4000)

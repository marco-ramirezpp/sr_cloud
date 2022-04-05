from flask import Flask, render_template, url_for, redirect, flash, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user,LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, DateTimeField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, Email, Length
import pandas as pd
import numpy as np
import pandas as pd
from surprise import Reader
from surprise import Dataset
from surprise.model_selection import train_test_split
from surprise import KNNBasic
from surprise import accuracy
from sqlalchemy import create_engine
import random
import surprise
import psycopg2

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:Server13m@172.24.41.225/sr'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'contraseña'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(UserMixin, db.Model):
    usuario = db.Column(db.String(512), primary_key=True, unique=True)
    password = db.Column(db.String(512), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def get_by_usuario(usuario):
        return Usuario.query.filter_by(usuario=usuario).first()


class actividad_usuarios(db.Model):
    index = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = db.Column(db.String(80), primary_key=True, nullable=False)
    artist_name = db.Column(db.String(20), nullable=False)
    track_name = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.String(20), nullable=False)


class recomendaciones(db.Model):
    index = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = db.Column(db.String(80), primary_key=True,nullable=False)
    artist_id = db.Column(db.String(20), nullable=False)
    estimation = db.Column(db.Integer, unique=False)



class registroform(FlaskForm):
    usuario = StringField(validators=[InputRequired()], render_kw={"placeholder": "nombre"})
    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "contraseña"})
    password2 = PasswordField('confirmar contraseña', validators=[DataRequired()], render_kw={"placeholder": "contraseña"})
    submit = SubmitField("Registro")\

    def validate_email(self, email):
        existing_user_email = usuario.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                "Este email se encuentra en uso")

class registroform_2(FlaskForm):
    usuario = StringField(validators=[InputRequired()], render_kw={"placeholder": "nombre"})
    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "contraseña"})
    password2 = PasswordField('confirmar contraseña', validators=[DataRequired()], render_kw={"placeholder": "contraseña"})
    radiohead = IntegerField(validators=[DataRequired()], render_kw={"placeholder": "Radiohead"})
    coldplay = IntegerField(validators=[DataRequired()], render_kw={"placeholder": "coldplay"})
    beatles = IntegerField(validators=[DataRequired()], render_kw={"placeholder": "The Beatles"})
    muse = IntegerField(validators=[DataRequired()], render_kw={"placeholder": "Muse"})
    dcab = IntegerField(validators=[DataRequired()], render_kw={"placeholder": "Death Cab For Cutie"})
    smith = IntegerField(validators=[DataRequired()], render_kw={"placeholder": "Ellio Smith"})
    placebo = IntegerField(validators=[DataRequired()], render_kw={"placeholder": "Placebo"})
    nails = IntegerField(validators=[DataRequired()], render_kw={"placeholder": "Nine Inch Nails"})
    pink = IntegerField(validators=[DataRequired()], render_kw={"placeholder": "Pink Floyd"})
    mode = IntegerField(validators=[DataRequired()], render_kw={"placeholder": "Depeche Mode"})


    submit = SubmitField("Registro")\

    def validate_email(self, email):
        existing_user_email = usuario.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                "Este email se encuentra en uso")

class loginform(FlaskForm):
    usuario = EmailField(validators=[InputRequired()], render_kw={"placeholder": "usuario"})
    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "contraseña"})
    submit = SubmitField("Inciciar sesión")\

class eliminarform(FlaskForm):
    id_evento = StringField(validators=[InputRequired()], render_kw={"placeholder": "Evento ID"})
    submit = SubmitField("Eliminar")

class editarform(FlaskForm):
    id_evento = StringField(validators=[InputRequired()], render_kw={"placeholder": "evento ID"})
    nombre_evento = StringField(validators=[InputRequired()], render_kw={"placeholder": "nombre_evento"})
    categoria = StringField(validators=[InputRequired()], render_kw={"placeholder": "categoria"})
    lugar = StringField(validators=[InputRequired()], render_kw={"placeholder": "lugar"})
    direccion = StringField(validators=[InputRequired()], render_kw={"placeholder": "direccion"})
    fecha_inicio = StringField(validators=[InputRequired()], render_kw={"placeholder": "fecha_incio"})
    fecha_fin = StringField(validators=[InputRequired()], render_kw={"placeholder": "fecha_fin"})
    tipo = StringField(validators=[InputRequired()], render_kw={"placeholder": "tipo"})
    submit = SubmitField("Editar")

@app.route('/')
def pagina_incio():
    return render_template("base_template.html")
'''
@app.route('/test', methods=['GET'])
def test():
    return "<html><head><title>Mi primera pagina web </title></head><body><h1 align=""center"">Mi Primera pagina web</h1><hr><p>Esto tan sencillo es una verdadera página web, aunque le falta el contenido,pero todo llegará.</p></body></html>"
'''



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('principal'))
    form = loginform()
    if form.validate_on_submit():
        user = Usuario.get_by_usuario(form.usuario.data)
        usuario = form.usuario.data
        if user is not None and user.check_password(form.password.data):
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('show_concurso', usuario=usuario)
            return redirect(next_page)
    return render_template('login.html', form=form)
    #else:
    #    flash('Contraseña incorrecta')


@app.route("/usuario", methods=['GET', 'POST'])
@app.route("/usuario/<string:usuario>", methods=['GET', 'POST'])
def show_concurso(usuario):
    # recomendaciones =
    playlist = actividad_usuarios.query.filter_by(user_id='{}'.format(usuario)).all()
    rec = recomendaciones.query.filter_by(user_id='{}'.format(usuario)).all()
    return render_template("usuario_view.html", usuario=usuario,playlist=playlist, recomendaciones=rec)

@app.route('/activacion',methods=['GET', 'POST'])
def registro():
    form = registroform()
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        nuevo_usuario = Usuario(usuario=form.usuario.data,
                                #apellido=hash,
                                #email=form.email.data,
                                password=hash)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("registro.html", form = form)


@app.route('/registro',methods=['GET', 'POST'])
def registro_2():
    form = registroform_2()
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        nuevo_usuario = Usuario(usuario=form.usuario.data,
                                password=hash)
        db.session.add(nuevo_usuario)
        db.session.commit()
        dataset = pd.read_csv('dataset.csv')
        dataset.drop('Unnamed: 0', axis=1, inplace=True)
        new_user_1 = {'userid': form.usuario.data, 'artist-id': 'a74b1b7f-71a5-4011-9441-d0b5e4122711', 'rating': form.radiohead.data}
        new_user_2 = {'userid': form.usuario.data, 'artist-id': 'cc197bad-dc9c-440d-a5b5-d52ba2e14234', 'rating': form.coldplay.data}
        new_user_3 = {'userid': form.usuario.data, 'artist-id': 'b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d', 'rating': form.beatles.data}
        new_user_4 = {'userid': form.usuario.data, 'artist-id': '9c9f1380-2516-4fc9-a3e6-f9f61941d090', 'rating': form.muse.data}
        new_user_5 = {'userid': form.usuario.data, 'artist-id': '0039c7ae-e1a7-4a7d-9b49-0cbc716821a6', 'rating': form.dcab.data}
        new_user_6 = {'userid': form.usuario.data, 'artist-id': '03ad1736-b7c9-412a-b442-82536d63a5c4', 'rating': form.smith.data}
        new_user_7 = {'userid': form.usuario.data, 'artist-id': '847e8284-8582-4b0e-9c26-b042a4f49e57', 'rating': form.placebo.data}
        new_user_8 = {'userid': form.usuario.data, 'artist-id': 'b7ffd2af-418f-4be2-bdd1-22f8b48613da', 'rating': form.nails.data}
        new_user_9 = {'userid': form.usuario.data, 'artist-id': '83d91898-7763-47d7-b03b-b92132375c47', 'rating': form.pink.data}
        new_user_10 = {'userid': form.usuario.data, 'artist-id': '8538e728-ca0b-4321-b7e5-cff6565dd4c0', 'rating': form.mode.data}
        dataset = dataset.append([new_user_1, new_user_2, new_user_3,
                                  new_user_4, new_user_5, new_user_6,
                                  new_user_7, new_user_8, new_user_9, new_user_10])
        reader = Reader(rating_scale=(0, 100))
        surprise_dataset = Dataset.load_from_df(dataset, reader)
        train_set, test_set = train_test_split(surprise_dataset, test_size=.2)
        sim_options = {'name': 'pearson',
                       'user_based': True
                       }
        algo = KNNBasic(k=30, min_k=2, sim_options=sim_options)
        algo.fit(trainset=train_set)
        test_predictions = algo.test(test_set)
        labels = ['userid', 'artist-id', 'estimation']
        user_predictions = pd.DataFrame.from_records(list(map(lambda x: (x.uid, x.iid, x.est), test_predictions)),columns=labels)
        artistas = pd.read_csv('artistas.csv')
        artistas.drop('Unnamed: 0', axis=1, inplace=True)
        user_predictions = user_predictions.merge(artistas, how='left', on='artist-id')[['userid', 'artist-name', 'estimation']]
        recomendaciones = user_predictions.sort_values(['estimation'], ascending=False).groupby('userid').head(3)
        recomendaciones.rename(columns={'userid': 'user_id', 'artist-name': 'artist_id'}, inplace=True)
        engine = create_engine('postgresql+psycopg2://postgres:Server13m@172.24.41.225/sr')
        conn = engine.connect()
        conn.execute("DROP TABLE IF EXISTS recomendaciones;")
        recomendaciones.to_sql('recomendaciones', con=conn)
        return redirect(url_for('login'))

    return render_template("registro_2.html", form = form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def cerrar_sesion():
    logout_user()
    return redirect(url_for('login'))

@app.route('/principal', methods=['GET', 'POST'])
@login_required
def principal():
    eventos = evento.query.filter_by(email_id='{}'.format(current_user.email)).all()  #.filter(evento.email_id=='{}'.format(current_user.email)).all()
    return render_template("principal.html", eventos=eventos)
        #return render_template('principal.html', nombre_evento=ids) #.nombre_evento,
                           #categoria=consulta.categoria,
                           #lugar=consulta.lugar,
                           #direccion=consulta.direccion,
                           #fecha_inicio=consulta.fecha_inicio,
                           #fecha_fin=consulta.fecha_fin,s
                           #tipo=consulta.tipo,
                               #id=1)
    #else:
    #    return render_template('no_hay_eventos.html')

@app.route('/nuevo_evento', methods=['GET', 'POST'])
@login_required
def añadir_evento():
    form = eventoform()
    if form.is_submitted():
        nuevo_evento = evento(email_id= current_user.email,
                              nombre_evento=form.nombre_evento.data,
                              categoria=form.categoria.data,
                              lugar=form.lugar.data,
                              direccion=form.direccion.data,
                              fecha_inicio=form.fecha_inicio.data,
                              fecha_fin=form.fecha_fin.data,
                              tipo=form.tipo.data)
        db.session.add(nuevo_evento)
        db.session.commit()
        return redirect(url_for('principal'))
    return render_template('nuevo_evento.html', form=form, usuario= current_user.email)

@app.route('/principal/eliminar_evento', methods=['GET', 'POST'])
@login_required
def eliminar_evento():
    form = eliminarform()
    if form.is_submitted():
        eliminar = evento.query.filter_by(id=form.id_evento.data).one()
        db.session.delete(eliminar)
        db.session.commit()
        return redirect(url_for('principal'))
    else:
       return render_template('eliminar_evento.html', form=form)


@app.route('/principal/editar_evento', methods=['GET', 'POST'])
@login_required
def editar_evento():
    form = editarform()
    if form.is_submitted():
        seleccionar_evento = evento.query.filter_by(id=form.id_evento.data).one()
        seleccionar_evento.nombre_evento = form.nombre_evento.data
        seleccionar_evento.categoria = form.categoria.data
        seleccionar_evento.lugar = form.lugar.data
        seleccionar_evento.direccion = form.direccion.data
        seleccionar_evento.fecha_inicio = form.fecha_inicio.data
        seleccionar_evento.fecha_fin = form.fecha_fin.data
        seleccionar_evento.tipo = form.tipo.data
        #db.session.commit()
        return redirect(url_for('editar', val = seleccionar_evento.id))
    else:
       return render_template('seleccion_evento.html', form=form)


@app.route('/principal/<val>/editar', methods=['GET', 'POST'])
@login_required
def editar(val):
    form = editarform()
    seleccionar_evento = evento.query.filter_by(id='{}'.format(val)).one()
    if form.is_submitted():
        seleccionar_evento.nombre_evento = form.nombre_evento.data
        seleccionar_evento.categoria = form.categoria.data
        seleccionar_evento.lugar = form.lugar.data
        seleccionar_evento.direccion = form.direccion.data
        seleccionar_evento.fecha_inicio = form.fecha_inicio.data
        seleccionar_evento.fecha_fin = form.fecha_fin.data
        seleccionar_evento.tipo = form.tipo.data
        db.session.commit()
        return redirect(url_for('principal'))
    return render_template('edicion.html', form=form,campos = seleccionar_evento)


if __name__ == '__main__':
    app.run(debug=True)

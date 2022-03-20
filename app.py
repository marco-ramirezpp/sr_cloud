from flask import Flask, render_template, url_for, redirect, flash, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user,LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, DateTimeField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, Email, Length
import psycopg2

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sistemas123@sr.cn9fz0pde5yd.us-west-2.rds.amazonaws.com:5432/postgres'
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

@app.route('/registro',methods=['GET', 'POST'])
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

from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Asistencia(db.Model):
    __tablename__ = 'asistencia'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    codigoclase = db.Column(db.Integer)
    asistio = db.Column(db.String(3))
    justificacion = db.Column(db.String(100))
    idestudiante = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=False)
    estudiante = db.relationship('Estudiante', backref='asistencias', primaryjoin='Asistencia.idestudiante == Estudiante.id')


class Curso(db.Model):
    __tablename__ = 'curso'
    id = db.Column(db.Integer, primary_key=True)
    anio = db.Column(db.String(80), nullable=False)
    division = db.Column(db.String(80), nullable=False)
    idpreceptor = db.Column(db.Integer, db.ForeignKey('preceptor.id'))

    preceptor = db.relationship('Preceptor', backref='curso', primaryjoin='Curso.idpreceptor == Preceptor.id')



class Estudiante(db.Model):
    __tablename__ = 'estudiante'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    dni = db.Column(db.String(10), nullable=False)
    idcurso = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    idpadre = db.Column(db.Integer, db.ForeignKey('padre.id'))

    curso = db.relationship('Curso', backref='estudiante', primaryjoin='Curso.id == Estudiante.idcurso')


class Padre(db.Model):
    __tablename__ = 'padre'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    clave = db.Column(db.String(120), nullable=False)


class Preceptor(db.Model):
    __tablename__ = 'preceptor'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    clave = db.Column(db.String(120), nullable=False)

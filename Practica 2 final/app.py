import hashlib
from datetime import datetime
from flask import Flask, request, render_template, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Padre, Preceptor, Curso, Estudiante

@app.route('/')
def inicio():
	return render_template('inicio.html')

@app.route('/registrarse', methods = ['GET','POST'])

def registrarse():
	if request.method == 'POST':
		if not request.form['nombre'] or not request.form['email'] or not request.form['password']:
			return render_template('error.html', error="Los datos ingresados no son correctos...")
		else:
			nuevo_usuario = Usuario(nombre=request.form['nombre'], correo = request.form['email'], clave=generate_password_hash(request.form['password']), lenguaje= request.form['lenguaje'])
			db.session.add(nuevo_usuario)
			db.session.commit()
			return render_template('aviso.html', mensaje="El usuario se registró exitosamente")
	return render_template('nuevo_usuario.html')

@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
	if request.method == 'POST':
		if not request.form['email'] or not request.form['password']:
			return render_template('error.html', error="Por favor ingrese los datos requeridos")
		else:
			usuario_actual = Preceptor.query.filter_by(correo=request.form['email']).first()
			mensaje = ""
			rol = ""
			if usuario_actual is None:
				usuario_actual = Padre.query.filter_by(correo=request.form['email']).first()
				rol    = "padre"
				mensaje = "Bienvenido, estimado profesor, a la plataforma de la Escuela. Aquí podrá gestionar las calificaciones de los estudiantes, enviar comunicaciones a los padres y acceder a recursos educativos."
			else:
				rol = "preceptor"
				mensaje = "Bienvenido, estimado padre, a la plataforma de la Escuela. Aquí podrá acceder a información sobre el progreso académico de su hijo/a y mantenerse informado sobre las novedades de la escuela."

			if usuario_actual is None:
				return render_template('error.html', error=Padre.query.first().nombre)
			else:
				# verificacion = check_password_hash(usuario_actual.clave, request.form['password'])
				verificacion = hashlib.md5(request.form['password'].encode()).hexdigest() == usuario_actual.clave

				if verificacion:
					usuario_actual = Preceptor.query.filter_by(correo=request.form['email']).first()
					cursos = Curso.query.filter_by(idpreceptor=usuario_actual.id).all()
					session['ids_curso'] = [curso.id for curso in cursos]
					session['id'] = usuario_actual.id

					return render_template('bienvenida.html', mensaje = mensaje, usuario = usuario_actual, rol = rol )
				else:
					return render_template('error.html', error="La contraseña no es válida")
	else:
		return render_template('ingresar.html')



@app.route('/registrarAsistencia', methods = ['GET', 'POST'])
def registrarAsistencia():
	idpreceptor = session['id']
	return render_template('registrar_asistencia.html', cursos=Curso.query.filter_by(idpreceptor = idpreceptor).all())

@app.route('/listarEstudiantesAsistencia', methods = ['GET', 'POST'])
def listarEstudiantesAsistencia():
	if  request.method == 'POST':
		ids_curso = session['ids_curso']
		print(ids_curso)
		fecha = request.form['fecha']
		clase = request.form['clase']
		return render_template('asistenciaEstudiante.html', estudiantes = Estudiante.query.filter(Estudiante.idcurso.in_(ids_curso)).all(), fecha = fecha, clase = clase )

@app.route('/agregarAsistencias', methods = ['POST'])
def agregarAsistencias():

	if request.method == 'POST':
		clase = request.form['clase']
		fecha = request.form['fecha']

		asistencias = []
		estudiantes = []
		justificaciones = []

		for key in request.form.keys():
			if key.startswith('asistio_'):
				asistencias.append(request.form.get(key))
			elif key.startswith('estudiante_'):
				estudiantes.append(request.form.get(key))
			elif key.startswith('justificacion_'):
				justificaciones.append(request.form.get(key))

		print(estudiantes)
		print(asistencias)
		print(justificaciones)
		print(clase)
		print(fecha)

		for i in range(0, len(asistencias)):
			db.session.add(Asistencia())
			db.session.commit()

		return redirect(url_for('inicio'))



@app.route('/bienvenida/<leng>')
def bienvenida(leng):
	if leng == 'es':
		return render_template('bienvenida.html', saludo='Hola!')
	else:
		return render_template('bienvenida.html', saludo='Hello')



if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug = True)
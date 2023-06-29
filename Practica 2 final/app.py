import hashlib
from datetime import datetime
from flask import Flask, request, render_template, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Padre, Preceptor, Curso, Estudiante, Asistencia

@app.route('/')
def inicio():
	return render_template('inicio.html')

@app.route('/registrarse', methods = ['GET','POST'])

def registrarse():
	if request.method == 'POST':
		if not request.form['nombre'] or not request.form['email'] or not request.form['password']:
			return render_template('error.html', error="Los datos ingresados no son correctos...")
		else:
			nuevo_usuario = None#Usuario(nombre=request.form['nombre'], correo = request.form['email'], clave=generate_password_hash(request.form['password']), lenguaje= request.form['lenguaje'])
			db.session.add(nuevo_usuario)
			db.session.commit()
			return render_template('aviso.html', mensaje="El usuario se registró exitosamente")
	return render_template('nuevo_usuario.html')

@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
	if request.method == 'POST':
		if not request.form['email'] or not request.form['password']: #si esta vacia cualquier casilla del formulario
			return render_template('error.html', error="Por favor ingrese los datos requeridos")
		else:

			mensaje = ""

			rol = request.form['rol'] #accede al valor del elemento del formulario de nombre rol
			if rol == 'padre':
				#obtengo el primer objeto Padre que coincide con el mail del elemento del formulario de nombre email
				usuario_actual = Padre.query.filter_by(correo=request.form['email']).first()
				mensaje = "Bienvenido, estimado padre, a la plataforma de la Escuela. Aquí podrá acceder a información sobre el progreso académico de su hijo/a y mantenerse informado sobre las novedades de la escuela."

			elif rol == "preceptor":
				#guarda objeto preceptor
				usuario_actual = Preceptor.query.filter_by(correo=request.form['email']).first()
				rol = "preceptor"
				mensaje = "Bienvenido, estimado preceptor, a la plataforma de la Escuela. Aquí podrá gestionar las asistencias de los estudiantes, enviar comunicaciones a los padres y acceder a recursos educativos."
				#cursos = Curso.query.filter_by(idpreceptor=usuario_actual.id).all()

				#cursos = usuario_actual.cursos

				#session['ids_curso'] = [curso.id for curso in cursos]

			session['rol'] = rol

			#si la variable usuario esta vacia, entonces retorna un error
			if usuario_actual is None:
				return render_template('error.html', error="Usuario no encontrado")
			else:
				# verificacion = check_password_hash(usuario_actual.clave, request.form['password'])
				#Cifra la contraseña ingresada por teclado en texto plano a md5 y luego la compara con la almacenada en la base de datos
				verificacion = hashlib.md5(request.form['password'].encode()).hexdigest() == usuario_actual.clave

				if verificacion:
					session['id'] = usuario_actual.id

					return render_template('bienvenida.html', mensaje = mensaje, usuario = usuario_actual, rol = rol )
				else:
					return render_template('error.html', error="La contraseña no es válida")
	else:
		return render_template('ingresar.html')



@app.route('/registrarAsistencia', methods = ['GET', 'POST'])
def registrarAsistencia():
	idpreceptor = session['id'] #la clave id almacenada en session se guarda en esta variable
	preceptor   = Preceptor.query.filter_by(id = idpreceptor).first()
	return render_template('registrar_asistencia.html', cursos=preceptor.cursos)

@app.route('/listarEstudiantesAsistencia', methods = [ 'POST'])
def listarEstudiantesAsistencia():

	if  request.method == 'POST':
		idcurso = request.form["curso"]
		estudiantes = Estudiante.query.filter_by(idcurso = idcurso).order_by(Estudiante.nombre, Estudiante.apellido).all() #Estudiante.query.filter(idcurso = 2).order_by(Estudiante.apellido, Estudiante.nombre).all()



		fecha = request.form['fecha']
		clase = request.form['clase']
		return render_template('asistenciaEstudiante.html', estudiantes = estudiantes, fecha = fecha, clase = clase )

@app.route('/agregarAsistencias', methods = ['POST'])
def agregarAsistencias():

	if request.method == 'POST':
		clase = request.form['clase']
		fecha = request.form['fecha']

		asistencias = []
		estudiantes = []
		justificaciones = []

		for key in request.form.keys(): #busco todos los atributos del formulario enviado
			if key.startswith('asistio_'): #si el nombre del atributo comienza con asistio_
				asistencias.append(request.form.get(key))
				#obtiene el valor de ese formulario y lo agrega a la lista asistencias
			elif key.startswith('estudiante_'):
				estudiantes.append(request.form.get(key))
			elif key.startswith('justificacion_'):
				#equivalente a request.form[key]
				justificaciones.append(request.form.get(key))



		for i in range(0, len(asistencias)):

			asistencia = Asistencia(codigoclase = clase, fecha = fecha, justificacion = justificaciones[i], asistio = asistencias[i], idestudiante = estudiantes[i] )

			db.session.add(asistencia)

			db.session.commit()

		return redirect(url_for('inicio'))

@app.route('/informeDetalles', methods = ['GET', 'POST'])
def informeDetalles():
	idpreceptor = session['id']
	preceptor = Preceptor.query.filter_by(id=idpreceptor).first()
	cursos = preceptor.cursos
	if request.method == 'GET':
		if session['rol'] is not None and  session['rol'] == 'preceptor' :

			return  render_template('informeDetalles.html', cursos = cursos)
	elif request.method == 'POST':
		curso = request.form['curso']
		estudiantes = Estudiante.query.filter_by(idcurso = curso).order_by(Estudiante.nombre, Estudiante.apellido)
		aux = []
		for estudiante in estudiantes:
			estudiantes_faltas = []

			asistencias_aula_presente = Asistencia.query.filter_by(idestudiante=estudiante.id, codigoclase=1,
																   asistio='s').count()

			asistencias_educacion_fisica_presente = Asistencia.query.filter_by(idestudiante=estudiante.id,
																			   codigoclase=2, asistio='s').count()

			asistencias_aula_ausente_justificadas = Asistencia.query.filter(Asistencia.justificacion != '').filter_by(idestudiante=estudiante.id,
																			   codigoclase=1, asistio='n').count()

			asistencias_aula_ausente_injustificadas = Asistencia.query.filter_by(idestudiante=estudiante.id,
																				 codigoclase=1, asistio='n',
																				 justificacion='').count()

			asistencias_educacion_fisica_ausente_justificadas = Asistencia.query.filter(Asistencia.justificacion != '').filter_by(idestudiante=estudiante.id,
																						   codigoclase=2, asistio='n').count()

			asistencias_educacion_fisica_ausente_injustificadas = Asistencia.query.filter_by(idestudiante=estudiante.id,
																							 codigoclase=2, asistio='n',
																							 justificacion = '').count()



			total_inasistencias = asistencias_aula_ausente_justificadas + asistencias_aula_ausente_injustificadas \
								  + (asistencias_educacion_fisica_ausente_justificadas + \
								  asistencias_educacion_fisica_ausente_injustificadas)/2

			estudiantes_faltas.append(asistencias_aula_presente)
			estudiantes_faltas.append(asistencias_educacion_fisica_presente)
			estudiantes_faltas.append(asistencias_aula_ausente_justificadas)
			estudiantes_faltas.append(asistencias_aula_ausente_injustificadas)
			estudiantes_faltas.append(asistencias_educacion_fisica_ausente_justificadas)
			estudiantes_faltas.append(asistencias_educacion_fisica_ausente_injustificadas)
			estudiantes_faltas.append(total_inasistencias)

			aux.append(estudiantes_faltas)

		return render_template('informeDetalles.html', estudiantes = estudiantes.all(), cantidades = aux, informar = True, cursos = cursos )


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
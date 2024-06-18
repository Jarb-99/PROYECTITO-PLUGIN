# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash 
from flask import session as sessionF
import sessionFlask as SM 
from connection import get_cassandra_session
from ScriptsCQL import createTables, deleteTables, insert
from uuid import uuid4
from datetime import datetime, date
import json

app = Flask(__name__)
app.secret_key = 'secret_key'
session = get_cassandra_session()

#############################################
# true/ false para activar la creacion de tablas en la base de datos
# true = puede tardar un 1 minuto la cracion de las tablas   
boolTables = False
if boolTables:
	deleteTables.deleteTables()
	createTables.createTables()
	insert.insertDatas()  

#############################################
# Views/Urls
@app.route('/')
def index():

  	return render_template('index.html', usuario=sessionF)

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		correo = request.form['email']
		contrasena = request.form['password']
		
		usuario = session.execute("""
		SELECT * FROM usuario 
		WHERE correo=%s AND contrasena=%s ALLOW FILTERING
		""", ( correo, contrasena )).one()

		if usuario:
			if usuario.contrasena == contrasena:
				SM.set_usuario_dict(sessionF, usuario._asdict())

				return redirect(url_for('index'))
			else:
				flash('Contraseña incorrecta', 'error')
				return redirect('/login')
		else:
			flash('Usuario no registrado', 'error')
			return redirect('/register')
		
	return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
	if request.method == 'POST':
		nombre = request.form['nombre']
		apellido = request.form['apellido']
		correo = request.form['email']
		contrasena = request.form['password']
		
		usuario = session.execute("""
		SELECT * FROM usuario 
		WHERE correo=%s AND contrasena=%s ALLOW FILTERING
		""", ( correo, contrasena )).one()

		if usuario:
			flash('Ya existe el usuario', 'error')
			return redirect('/login')
		
		else:
			usuario_id = uuid4()
			date = datetime.now().date()

			SM.set_usuario(sessionF, usuario_id, nombre, apellido, correo, contrasena, date.strftime("%Y-%m-%d"), '', '', '')

			session.execute("""
					INSERT INTO USUARIO (usuario_id, nombre, apellido, correo, contrasena, fecha_rgstro, foto, direccion, telefono)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
				""", 
				(usuario_id, nombre, apellido, correo, contrasena, date, '', '', ''))
			
			return redirect(url_for('index'))
	return render_template('register.html')

@app.route('/Home')
def home():
	return render_template('index.html')

@app.route('/Perfil')
def perfil():
  	return render_template('perfil.html')

@app.route('/Carrito')
def carrito():
  	return render_template('carrito.html')

@app.route('/Soporte')
def soporte():
  	return render_template('soporte.html')

@app.route('/Logout')
def logout():
  	return render_template('login.html')

@app.route('/PComprados')
def PComprados():
  	return render_template('productos-comprados.html')

@app.route('/LSoportes')
def LSoportes():
  	return render_template('lista-soportes.html')

@app.route('/LRecibos')
def LRecibos():
	return render_template('lista-recibos.html')

@app.route('/recibo')
def recibo():
	metodo_pago = request.args.get('metodoPago')
	# Aquí puedes procesar más información para el recibo si es necesario
	return render_template('recibo.html', metodoPago=metodo_pago)


@app.route('/Producto')
def todas_peliculas():
	peliculas = all_movies()
	return render_template('producto.html', peliculas=peliculas)


if __name__ == '__main__':
	app.run(host='localhost', port=8080, debug=True)

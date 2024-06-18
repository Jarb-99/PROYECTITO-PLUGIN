# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash 
from flask import session as sessionF
import sessionFlask as SM 
from connection import get_cassandra_session
from ScriptsCQL import createTables, deleteTables, insert
from uuid import uuid4, UUID
from datetime import datetime, date
from UDTs import *
import json

app = Flask(__name__)
app.secret_key = 'secret_key'
session = get_cassandra_session()

#############################################
# true/ false para activar la creacion de tablas en la base de datos
# true = puede tardar un 1 minuto la cracion de las tablas   
boolTables = True
if boolTables:
	deleteTables.deleteTables()
	createTables.createTables()
	insert.insertDatas()  

#############################################
# global de productos para ahorrar las consultas por usuarios
productos = session.execute("""
		SELECT * FROM producto
		""")
lista_productos = [producto._asdict() for producto in productos]

#############################################
# Views/Urls
@app.route('/')
def index():
	  
	return render_template('index.html', usuario=sessionF, productos=lista_productos)

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
			carrito_id = uuid4()
			date = datetime.now().date()

			SM.set_usuario(sessionF, usuario_id, carrito_id, nombre, apellido, correo, contrasena, date.strftime("%Y-%m-%d"), '', '', '')

			session.execute("""
					INSERT INTO USUARIO (usuario_id, carrito_id, nombre, apellido, correo, contrasena, fecha_rgstro, foto, direccion, telefono)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				""", 
				(usuario_id, carrito_id, nombre, apellido, correo, contrasena, date, '', '', ''))

			session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
			session.execute("""
				INSERT INTO CARRITO (usuario_id, carrito_id, fecha, monto, productos)
				VALUES (%s, %s, %s, %s, %s)
			""", (usuario_id, carrito_id, date, 0, {}))
			
			return redirect(url_for('index'))
	return render_template('register.html')


@app.route('/Perfil')
def perfil():
  	return render_template('perfil.html', usuario=sessionF)


@app.route('/Carrito', methods=['GET', 'POST'])
def carrito():
    carrito = session.execute("""
		SELECT * FROM carrito 
		WHERE carrito_id=%s ALLOW FILTERING
		""", (sessionF['carrito_id'],)).one()
    
    if request.method == 'POST':
        cantidad = int(request.form['cantidad'])
        producto_id = UUID(request.form['producto_id'])
        precio = float(request.form['precio'])
        nombre = request.form['nombre']
        monto = cantidad*precio
        
        session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
        
        session.execute("""
			UPDATE carrito 
			SET productos = productos + %s, monto = %s 
			WHERE carrito_id=%s AND usuario_id=%s AND fecha=%s 
			""", 
   			({Prdcto_anddo(producto_id, nombre, precio, monto, cantidad)}, float(carrito.monto) + monto, carrito.carrito_id, carrito.usuario_id, carrito.fecha))
        
        carrito = session.execute("""
			SELECT * FROM carrito 
			WHERE carrito_id=%s ALLOW FILTERING
			""", (sessionF['carrito_id'],)).one()
        
    return render_template('carrito.html', usuario=sessionF, carrito=carrito)

@app.route('/Carrito/edit', methods=['POST'])
def editar_producto_carrito():
    
    if request.method == 'POST':
        carrito = session.execute("""
			SELECT * FROM carrito 
			WHERE carrito_id=%s ALLOW FILTERING
			""", (sessionF['carrito_id'],)).one()
        
        producto_id = UUID(request.form['producto_id'])
        nueva_cantidad = int(request.form['nuevacantidad'])
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        nombre = request.form['nombre']
        actual_monto = float(request.form['monto'])
        monto = nueva_cantidad*precio
        old_monto = cantidad*precio
        
        session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
        
        session.execute("""
            UPDATE carrito 
            SET productos = productos -  %s, productos = productos  +  %s, monto = %s 
            WHERE carrito_id = %s AND usuario_id = %s AND fecha = %s
        """, (
            {Prdcto_anddo(producto_id, nombre, precio, old_monto, cantidad)},
            {Prdcto_anddo(producto_id, nombre, precio, monto, nueva_cantidad)},
            actual_monto - old_monto + monto,
            carrito.carrito_id,
            carrito.usuario_id,
            carrito.fecha
        ))
    
    return redirect(url_for('carrito'))

@app.route('/Carrito/del', methods=['POST'])
def eliminar_producto_carrito():
    if request.method == 'POST':
        carrito = session.execute("""
			SELECT * FROM carrito 
			WHERE carrito_id=%s ALLOW FILTERING
			""", (sessionF['carrito_id'],)).one()
        
        producto_id = UUID(request.form['producto_id'])	
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        nombre = request.form['nombre']
        actual_monto = float(request.form['monto'])
        old_monto = cantidad*precio
        
        session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
        
        session.execute("""
			UPDATE carrito 
			SET productos = productos - %s, monto = %s 
			WHERE carrito_id = %s AND usuario_id = %s AND fecha = %s
		""", (
		{Prdcto_anddo(producto_id, nombre, precio, old_monto, cantidad)},
		actual_monto -  old_monto,
		carrito.carrito_id,
		carrito.usuario_id,
		carrito.fecha
	))
    
    return redirect(url_for('carrito'))

@app.route('/Soporte')
def soporte():
  	return render_template('soporte.html', usuario=sessionF)

@app.route('/Logout')
def logout():
  	return render_template('login.html', usuario=sessionF)

@app.route('/PComprados')
def PComprados():
  	return render_template('productos-comprados.html', usuario=sessionF)

@app.route('/LSoportes')
def LSoportes():
  	return render_template('lista-soportes.html', usuario=sessionF)

@app.route('/LRecibos')
def LRecibos():
	return render_template('lista-recibos.html', usuario=sessionF)

@app.route('/recibo')
def recibo():
	metodo_pago = request.args.get('metodoPago')
	# Aquí puedes procesar más información para el recibo si es necesario
	return render_template('recibo.html', metodoPago=metodo_pago, usuario=sessionF)


@app.route('/producto/<uuid:producto_id>')
def producto(producto_id):
    
    producto = session.execute("""
        SELECT * FROM producto WHERE producto_id = %s
    """, (producto_id,)).one()
    
    comentario_producto = session.execute("""
        SELECT * FROM cmntrio_prdcto WHERE producto_id = %s
    """, (producto_id,))
    
    lista_comentarios = [comentario._asdict() for comentario in comentario_producto]
 
    if not producto:
        return redirect(url_for('index'))

    return render_template('producto.html', producto=producto, usuario=sessionF, lista_comentarios=lista_comentarios)


if __name__ == '__main__':
	app.run(host='localhost', port=8080, debug=True)

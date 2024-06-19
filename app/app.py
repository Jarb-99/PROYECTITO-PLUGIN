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
def start():
	return render_template('login.html')

@app.route('/index')
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
			datestamp = datetime.now()
			date = datestamp.date()

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
			""", (usuario_id, carrito_id, datestamp, 0, {}))
			
			return redirect(url_for('index'))
	return render_template('register.html')


@app.route('/Perfil')
def perfil():
    compras_realizadas = session.execute("""
		SELECT * FROM PRDCTO_CMPRDO 
		WHERE usuario_id=%s 
  		ORDER BY fecha DESC
		LIMIT 3
		""", (sessionF['usuario_id'],))
    
    return render_template('perfil.html', usuario=sessionF, compras=compras_realizadas)


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

@app.route('/Carrito/pag', methods=['POST'])
def pagar_carrito():
    if request.method == 'POST':
        metodo_pago = request.form.get('metodoPago')
        correo = request.form.get('correo')
        datestamp = datetime.now()
        
        pago_id = uuid4()
        recibo_id = uuid4()
        carrito_id = uuid4()
        print(carrito_id)
        
        carrito = session.execute("""
			SELECT * FROM carrito 
			WHERE carrito_id=%s ALLOW FILTERING
			""", (sessionF['carrito_id'],)).one()
        
        session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
        session.user_type_registered(keyspace, 'metodo_pago', Metodo_pago)
        
        session.execute("""
            INSERT INTO PAGO (usuario_id, pago_id, carrito_id, fecha, monto, metodo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, 
        (carrito.usuario_id, pago_id, carrito.carrito_id, datestamp, carrito.monto, Metodo_pago(metodo_pago,correo)))
        
        lista_productos = {Prdcto_anddo(producto.producto_id, producto.nombre, producto.precio, producto.monto, producto.cantidad) for producto in carrito.productos}
        
        session.execute("""
            INSERT INTO RECIBO (usuario_id, recibo_id, carrito_id, pago_id, fecha, monto, metodo, productos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (carrito.usuario_id, recibo_id, carrito.carrito_id, pago_id, datestamp, carrito.monto, Metodo_pago(metodo_pago,correo), lista_productos))
        
        session.execute("""
			INSERT INTO CARRITO (usuario_id, carrito_id, fecha, monto, productos)
			VALUES (%s, %s, %s, %s, %s)
			""", (carrito.usuario_id, carrito_id, datestamp, 0, {}))
        
        #inserta los produtos comprados       
        for product in carrito.productos:
            session.execute("""
				INSERT INTO PRDCTO_CMPRDO (usuario_id, producto_id, fecha, nombre, precio, cantidad)
				VALUES (%s, %s, %s, %s, %s, %s)
    		""", (carrito.usuario_id, product.producto_id, datestamp, product.nombre,product.precio, product.cantidad))
            
        SM.set(sessionF, 'carrito_id', carrito_id)
        session.execute("""
			UPDATE USUARIO
   			SET carrito_id=%s
			WHERE usuario_id=%s
			""", (carrito_id, carrito.usuario_id))
        
    return redirect(url_for('recibo'))

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
    recibos = session.execute("""
		SELECT * FROM recibo
		WHERE usuario_id=%s 
  		ORDER BY fecha DESC
		""", (sessionF['usuario_id'], ))
    
    lista_recibos = [recibo._asdict() for recibo in recibos]
    
    
    return render_template('lista-recibos.html', usuario=sessionF, recibos=lista_recibos)


@app.route('/recibo')
def recibo():
    recibo_reciente = session.execute("""
		SELECT * FROM recibo 
		WHERE usuario_id=%s 
		ORDER BY fecha DESC 
		LIMIT 1
	""", (sessionF['usuario_id'], )).one()
    print(recibo_reciente)
    return render_template('recibo.html', usuario=sessionF, recibo=recibo_reciente)


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

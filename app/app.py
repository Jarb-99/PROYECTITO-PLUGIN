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
from collections import OrderedDict

app = Flask(__name__)
app.secret_key = 'secret_key'
session = get_cassandra_session()

#############################################
# true/ false para activar la creacion de tablas en la base de datos
# true = puede tardar un 1 minuto la cracion de las tablas   
boolTables = False
if boolTables:
    d = 100 # cantidad de datos
    p = d # cantidad de productos
    deleteTables.deleteTables()
    createTables.createTables()
    insert.insertDatas(d,p)  

#############################################
# global de productos para ahorrar las consultas por usuarios

lista_productos = OrderedDict(sorted({producto.producto_id:producto._asdict() for producto in 
                   session.execute("""
						SELECT * FROM producto
						""")
                   }.items(), key=lambda x: x[1]['fecha'], reverse=True))

#############################################
# Views/Urls
@app.route('/')
def start():
	return render_template('login.html')

@app.route('/index')
def index():
        
    return render_template('index.html', usuario=sessionF, productos=lista_productos)

@app.route('/index/s', methods=['GET','POST'])
def buscar_producto():
    if request.method == 'POST':
        buscar = request.form['buscar'].lower()
        
        if buscar == '':
            return redirect(url_for('index'))
        
        lista_productos_buscados = {producto_id:producto 
                                    for producto_id,producto in lista_productos.items() 
                                    if buscar in producto['nombre'].lower()}
        
        return render_template('index.html', usuario=sessionF, productos=lista_productos_buscados)
    
    return redirect(url_for('index'))

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
    
                admin = session.execute("""
				SELECT nombre_usuario FROM propietario 
				WHERE usuario_id=%s ALLOW FILTERING
				""", ( sessionF['usuario_id'], )).one()
    
                if admin:
                    return redirect(url_for('index_admin'))
    
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
		SELECT correo FROM usuario 
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

@app.route('/Perfil/editar', methods=['POST'])
def editar_perfil():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    
    SM.set(sessionF, 'nombre', nombre)
    SM.set(sessionF, 'apellido', apellido)
    SM.set(sessionF, 'correo', correo)
    SM.set(sessionF, 'contrasena', contrasena)
    SM.set(sessionF, 'telefono', telefono)
    SM.set(sessionF, 'direccion', direccion)
    
    session.execute("""
		UPDATE USUARIO
		SET nombre=%s, apellido=%s, correo=%s, contrasena=%s, telefono=%s, direccion=%s
		WHERE usuario_id=%s
		""", (nombre, apellido, correo, contrasena, telefono, direccion, sessionF['usuario_id']))
    
    
    return redirect(url_for('perfil'))


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
        nueva_cantidad = int(request.form['nuevacantidad'])
        cantidad = int(request.form['cantidad'])
        
        if cantidad == 1 and nueva_cantidad == 1:
            return redirect(url_for('carrito'))
        
        producto_id = UUID(request.form['producto_id'])
        precio = float(request.form['precio'])
        nombre = request.form['nombre']
        actual_monto = float(request.form['monto'])
        monto = nueva_cantidad*precio
        old_monto = cantidad*precio
        
        carrito = session.execute("""
			SELECT * FROM carrito 
			WHERE carrito_id=%s ALLOW FILTERING
			""", (sessionF['carrito_id'],)).one()
        
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
        
        lista_productos_andddo = {Prdcto_anddo(producto.producto_id, producto.nombre, producto.precio, producto.monto, producto.cantidad) for producto in carrito.productos}
        
        session.execute("""
            INSERT INTO RECIBO (usuario_id, recibo_id, carrito_id, pago_id, fecha, monto, metodo, productos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (carrito.usuario_id, recibo_id, carrito.carrito_id, pago_id, datestamp, carrito.monto, Metodo_pago(metodo_pago,correo), lista_productos_andddo))
        
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
            
            num_compras = session.execute("""
				SELECT compras,fecha FROM PRODUCTO
				WHERE producto_id=%s 
				""", (product.producto_id, )).one()
            
            session.execute("""
				UPDATE PRODUCTO
				SET compras=%s
				WHERE producto_id=%s AND fecha=%s 
				""", (num_compras.compras + product.cantidad, product.producto_id, num_compras.fecha))
            
            lista_productos[product.producto_id]['compras'] =  num_compras.compras + product.cantidad
   
        SM.set(sessionF, 'carrito_id', carrito_id)
        session.execute("""
			UPDATE USUARIO
   			SET carrito_id=%s
			WHERE usuario_id=%s
			""", (carrito_id, carrito.usuario_id))
        
        
    return redirect(url_for('recibo'))

@app.route('/Soporte', methods=['GET', 'POST'])
def soporte():
    if request.method == 'POST':
        mensaje = request.form.get('mensaje')
        
        if mensaje == ' ':
            return redirect(url_for('index'))
        
        soporte_id = uuid4()
        datestamp = datetime.now()
        
        session.execute("""
            INSERT INTO SOPORTE (usuario_id, soporte_id, fecha, mensaje, respuestas)
            VALUES (%s, %s, %s, %s, {})
        """, (sessionF['usuario_id'], soporte_id, datestamp, mensaje))
        
        return redirect(url_for('LSoportes'))
	
    return render_template('soporte.html', usuario=sessionF)
     
@app.route('/Logout')
def logout():
    SM.clear(sessionF)
    return render_template('login.html', usuario=sessionF)

@app.route('/PComprados')
def PComprados():
    compras_realizadas = session.execute("""
		SELECT * FROM PRDCTO_CMPRDO 
		WHERE usuario_id=%s 
  		ORDER BY fecha DESC
		""", (sessionF['usuario_id'],))
    
    return render_template('productos-comprados.html', usuario=sessionF, compras=compras_realizadas)

@app.route('/LSoportes')
def LSoportes():
	lista_soportes = session.execute("""
		SELECT * FROM soporte 
		WHERE usuario_id=%s
  		ORDER BY fecha DESC
		""", (sessionF['usuario_id'],))
	
	return render_template('lista-soportes.html', usuario=sessionF,soportes=lista_soportes)

@app.route('/LSoportes/resp', methods=['POST'])
def responder_soporte():
    if request.method == 'POST':
        respuesta = request.form.get('respuesta')
        soporte_id = UUID(request.form.get('soporte_id'))
        fecha = request.form.get('fecha')
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
        datestamp = datetime.now()
        
        session.user_type_registered(keyspace, 'respuesta', Respuesta)
        
        session.execute("""
            UPDATE soporte 
            SET respuestas = respuestas +  %s 
            WHERE usuario_id = %s AND soporte_id = %s AND fecha = %s
        """, (
            {datestamp: Respuesta(sessionF['usuario_id'], respuesta, sessionF['nombre'])},
            sessionF['usuario_id'],
            soporte_id,
            fecha
            ))

    return redirect(url_for('LSoportes'))

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




##############################################################
##############################################################
##							ADMIN							##
##															##
##############################################################
##############################################################



@app.route('/index/admin')
def index_admin():
        
    return render_template('index_admin.html', usuario=sessionF, productos=lista_productos)

@app.route('/index/admin/s', methods=['GET','POST'])
def buscar_producto_admin():
    if request.method == 'POST':
        buscar = request.form['buscar'].lower()
        
        if buscar == '':
            return redirect(url_for('index_admin'))
        
        lista_productos_buscados = {producto_id:producto 
                                    for producto_id,producto in lista_productos.items() 
                                    if buscar in producto['nombre'].lower()}
        
        return render_template('index_admin.html', usuario=sessionF, productos=lista_productos_buscados)
    
    return redirect(url_for('index_admin'))

@app.route('/index/admin/add', methods=['POST'])
def agregar_producto_admin():
    if request.method == 'POST':
        global lista_productos
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        version_comptble = request.form['version_comptble']
        plugins = request.form.getlist('plugins[]')
        schematics = request.form.getlist('schematics[]')
        fecha = datetime.now()
        producto_id = uuid4()

        session.user_type_registered(keyspace, 'plugin', Plugin)
        session.user_type_registered(keyspace, 'schematic', Schematic)
    
        plugins_list = [Plugin(version) for version in plugins]
        schematics_list = [Schematic(int(dimensiones)) for dimensiones in schematics]
    
        session.execute("""
        	INSERT INTO producto (producto_id, nombre, descripcion, precio, fecha, valoracion, compras, version_comptble, plugins, schematics)
        	VALUES (%s, %s, %s, %s, %s, 0, 0, %s, %s, %s)
    	""", (producto_id, nombre, descripcion, precio, fecha, version_comptble, plugins_list, schematics_list))

        nuevo_producto = {
            'producto_id': producto_id,
            'nombre': nombre,
            'descripcion': descripcion,
            'precio': precio,
            'fecha': fecha,
            'valoracion': 0,
            'compras': 0,
            'version_comptble': version_comptble,
            'plugins': plugins_list,
            'schematics': schematics_list
        }
        lista_productos = OrderedDict([(producto_id, nuevo_producto)] + list(lista_productos.items()))
        
        
    return render_template('index_admin.html', usuario=sessionF, productos=lista_productos)


@app.route('/index/admin/edit', methods=['POST'])
def editar_producto_admin():
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        if 'confirmar' in accion:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            precio = float(request.form['precio'])
            version_comptble = request.form['version_comptble']
            
            fecha = request.form['fecha']
            fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
            producto_id = UUID(request.form['producto_id'])
        
            session.user_type_registered(keyspace, 'plugin', Plugin)
            session.user_type_registered(keyspace, 'schematic', Schematic)
        
            session.execute("""
				UPDATE PRODUCTO 
				SET nombre=%s, descripcion=%s, precio=%s, version_comptble=%s 
				WHERE producto_id = %s AND fecha = %s 
			""", (nombre, descripcion, precio, version_comptble, producto_id, fecha))
        
            lista_productos[producto_id]['nombre'] = nombre
            lista_productos[producto_id]['descripcion'] = descripcion
            lista_productos[producto_id]['precio'] = precio
            lista_productos[producto_id]['version_comptble'] = version_comptble
        
        elif 'eliminar' in accion:   
            producto_id = UUID(request.form['producto_id'])	
            fecha = request.form['fecha']
            fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
        
            session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
        
            session.execute("""
				DELETE FROM PRODUCTO  
				WHERE producto_id = %s AND fecha = %s
			""", (producto_id, fecha))
        
            del lista_productos[producto_id]         

    return redirect(url_for('index_admin'))

@app.route('/index/admin/del', methods=['POST'])
def eliminar_producto_admin():
    if request.method == 'POST':       
        producto_id = UUID(request.form['producto_id'])	
        fecha = request.form['fecha']
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
        
        session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
        
        session.execute("""
			DELETE FROM PRODUCTO  
			WHERE producto_id = %s AND fecha = %s
		""", (producto_id, fecha))
        
        del lista_productos[producto_id]
        

    return redirect(url_for('index_admin'))

@app.route('/Perfil/admin')
def perfil_admin():
    compras_realizadas = session.execute("""
		SELECT * FROM PRDCTO_CMPRDO 
		WHERE usuario_id=%s 
  		ORDER BY fecha DESC
		LIMIT 3
		""", (sessionF['usuario_id'],))
    
    return render_template('perfil_admin.html', usuario=sessionF, compras=compras_realizadas)

@app.route('/Perfil/admin/editar', methods=['POST'])
def editar_perfil_admin():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    
    SM.set(sessionF, 'nombre', nombre)
    SM.set(sessionF, 'apellido', apellido)
    SM.set(sessionF, 'correo', correo)
    SM.set(sessionF, 'contrasena', contrasena)
    SM.set(sessionF, 'telefono', telefono)
    SM.set(sessionF, 'direccion', direccion)
    
    session.execute("""
		UPDATE USUARIO
		SET nombre=%s, apellido=%s, correo=%s, contrasena=%s, telefono=%s, direccion=%s
		WHERE usuario_id=%s
		""", (nombre, apellido, correo, contrasena, telefono, direccion, sessionF['usuario_id']))
    
    
    return redirect(url_for('perfil_admin'))


@app.route('/LSoportes/admin')
def soporte_admin(): 
    lista_soportes = OrderedDict(sorted({soporte.usuario_id:soporte._asdict() for soporte in 
                   session.execute("""
						SELECT * FROM soporte 
						""")
                   }.items(), key=lambda x: x[1]['fecha'], reverse=True))
    	
    
    
    return render_template('soporte_admin.html', usuario=sessionF,soportes=lista_soportes)


@app.route('/LSoportes/admin/resp', methods=['POST'])
def responder_soporte_admin():
    if request.method == 'POST':
        respuesta = request.form.get('respuesta')
        soporte_id = UUID(request.form.get('soporte_id'))
        usuario_id = UUID(request.form.get('usuario_id'))
        fecha = request.form.get('fecha')
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
        datestamp = datetime.now()
        
        session.user_type_registered(keyspace, 'respuesta', Respuesta)
        
        session.execute("""
            UPDATE soporte 
            SET respuestas = respuestas +  %s 
            WHERE usuario_id = %s AND soporte_id = %s AND fecha = %s
        """, (
            {datestamp: Respuesta(sessionF['usuario_id'], respuesta, sessionF['nombre'])},
            usuario_id,
            soporte_id,
            fecha
            ))

    return redirect(url_for('soporte_admin'))


@app.route('/LSoportes/admin/del', methods=['POST'])
def eliminar_soporte_admin():
    if request.method == 'POST':       
        soporte_id = UUID(request.form.get('soporte_id'))	
        usuario_id = UUID(request.form.get('usuario_id'))	
        fecha = request.form.get('fecha')
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
        
        session.execute("""
			DELETE FROM SOPORTE  
			WHERE soporte_id = %s AND fecha = %s AND usuario_id=%s
		""", (soporte_id, fecha, usuario_id))
    
    return redirect(url_for('soporte_admin'))




if __name__ == '__main__':
	app.run(host='localhost', port=8080, debug=True)

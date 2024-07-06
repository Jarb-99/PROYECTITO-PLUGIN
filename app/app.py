# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash 
from flask import session as sessionF
import sessionFlask as SM 
from connection import get_cassandra_session
from ScriptsCQL import createTables, deleteTables, insert
from uuid import uuid4, UUID
from datetime import datetime, date
from UDTs import *
from collections import OrderedDict

app = Flask(__name__)
app.secret_key = 'secret_key'
session = get_cassandra_session()

#############################################
# true/ false para activar la creacion de tablas en la base de datos
# true = puede tardar un 1 minuto la cracion de las tablas   
boolTables = False
if boolTables:
    d = 20000 # cantidad de datos
    p = d # cantidad de productos
    h = 60
    deleteTables.deleteTables()
    createTables.createTables()
    insert.insertDatas(d,p,h)  

#############################################
# global de lista productos ordenados para ahorrar las consultas por usuarios
lista_productos = OrderedDict(sorted({producto.producto_id:producto._asdict() for producto in 
	session.execute("""
		SELECT * FROM producto
		LIMIT 100
		""")
	}.items(), key=lambda x: x[1]['fecha'], reverse=True))

#############################################
# Views/Urls
@app.route('/')
def start():
	return render_template('login.html')





##############################################################
##############################################################
##							LOGIN							##
##															##
##############################################################
##############################################################




@app.route('/Logout')
def logout():
    SM.clear(sessionF)
    return render_template('login.html', usuario=sessionF)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        correo = request.form['email']
        contrasena = request.form['password']
        #seleccionar el usuario si es que existe
        usuario = session.execute("""
		SELECT * FROM usuario 
		WHERE correo=%s AND contrasena=%s ALLOW FILTERING
		""", ( correo, contrasena )).one()
    
        if usuario:
            # validar el ingreso del usuario a su cuenta
            if usuario.contrasena == contrasena:
                # actualizar la sesion del usuario para su uso global
                SM.set_usuario_dict(sessionF, usuario._asdict())
                
				# ver si el usuario es propietario
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
		
		# verificar si el usuario ya existe, si no registrarlo
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
			
   			# actualizar la session del usuario y insertar a la BD
			SM.set_usuario(sessionF, usuario_id, carrito_id, nombre, apellido, correo, contrasena, date.strftime("%Y-%m-%d"), '', '', '')

			session.execute("""
					INSERT INTO USUARIO (usuario_id, carrito_id, nombre, apellido, correo, contrasena, fecha_rgstro, foto, direccion, telefono)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				""", 
				(usuario_id, carrito_id, nombre, apellido, correo, contrasena, date, '', '', ''))
   
			# Crear el nuevo carrito del usuario
			session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
			session.execute("""
				INSERT INTO CARRITO (usuario_id, carrito_id, fecha, monto, productos)
				VALUES (%s, %s, %s, %s, %s)
			""", (usuario_id, carrito_id, datestamp, 0, {}))
			
			return redirect(url_for('index'))
	return render_template('register.html')



##############################################################
##############################################################
##							INDEX							##
##															##
##############################################################
##############################################################



@app.route('/index')
def index():
        
    return render_template('index.html', usuario=sessionF, productos=lista_productos)

@app.route('/index/s', methods=['GET','POST'])
def buscar_producto():
    if request.method == 'POST':
        buscar = request.form['buscar'].lower()
        
        if buscar == '':
            return redirect(url_for('index'))
        
        productos = OrderedDict(sorted({producto.producto_id:producto._asdict() for producto in 
            session.execute("""
                SELECT * FROM producto
                """)
            }.items(), key=lambda x: x[1]['fecha'], reverse=True))
        
        #Buscador del producto con codigo de aplicacion
        lista_productos_buscados = {producto_id:producto 
                                    for producto_id,producto in productos.items() 
                                    if buscar == producto['nombre'].lower()}
        
        return render_template('index.html', usuario=sessionF, productos=lista_productos_buscados)
    
    return redirect(url_for('index'))




##############################################################
##############################################################
##							PRODUCTO						##
##															##
##############################################################
##############################################################


@app.route('/PComprados')
def PComprados():
    # Seleccionar los productos ya comprados por el usuario para mostrarlo
    compras_realizadas = session.execute("""
		SELECT * FROM PRDCTO_CMPRDO 
		WHERE usuario_id=%s 
  		ORDER BY fecha DESC
		""", (sessionF['usuario_id'],))
    
    return render_template('productos-comprados.html', usuario=sessionF, compras=compras_realizadas)

@app.route('/producto/<uuid:producto_id>')
def producto(producto_id):
    #para ver la informacion del producto
    # validar si existe el producto
    producto = session.execute("""
        SELECT * FROM producto WHERE producto_id = %s
    """, (producto_id,)).one()
    if not producto:
        return redirect(url_for('index'))
        
    comentario_producto = session.execute("""
        SELECT * FROM cmntrio_prdcto WHERE producto_id = %s
    """, (producto_id,))
    
    lista_comentarios = [comentario._asdict() for comentario in comentario_producto]
 

    return render_template('producto.html', producto=producto, usuario=sessionF, lista_comentarios=lista_comentarios)






##############################################################
##############################################################
##							PERFIL							##
##															##
##############################################################
##############################################################





@app.route('/Perfil')
def perfil():
    # para cargar los productos(3) ya comprados por usuario y mostrarlo en su perfil de informacion
    compras_realizadas = session.execute("""
		SELECT * FROM PRDCTO_CMPRDO 
		WHERE usuario_id=%s 
  		ORDER BY fecha DESC
		LIMIT 3
		""", (sessionF['usuario_id'],))
    
    return render_template('perfil.html', usuario=sessionF, compras=compras_realizadas)

@app.route('/Perfil/editar', methods=['POST'])
def editar_perfil():
    # para editar el perfil del usuario
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    
    # actualizar la informacion en la session y en la BD del usuario 
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





##############################################################
##############################################################
##							CARRITO							##
##															##
##############################################################
##############################################################





@app.route('/Carrito', methods=['GET', 'POST'])
def carrito():
    # seleccionar el carrito del usuario
    carrito = session.execute("""
		SELECT * FROM carrito 
		WHERE carrito_id=%s ALLOW FILTERING
		""", (sessionF['carrito_id'],)).one()
        
    return render_template('carrito.html', usuario=sessionF, carrito=carrito)


@app.route('/Carrito/add', methods=['GET', 'POST'])
def agregar_carrito():
    # seleccionar el carrito del usuario
    carrito = session.execute("""
		SELECT * FROM carrito 
		WHERE carrito_id=%s ALLOW FILTERING
		""", (sessionF['carrito_id'],)).one()
    
    # agregar un producto al carrito
    if request.method == 'POST':
        producto_id = UUID(request.form['producto_id'])
        
        # para saber si el producto aun existe
        producto = session.execute("""
            SELECT * FROM producto WHERE producto_id = %s
        """, (producto_id,)).one()
        if not producto:
            return redirect(url_for('index'))
    
        cantidad = int(request.form['cantidad'])        
        precio = float(request.form['precio'])
        nombre = request.form['nombre']
        monto = cantidad*precio
        edit_monto = 0
        edit_cantidad = 0
        
        session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
        
        # verificar si el producto ya existe en el carrito
        verify_product = None    
        if carrito.productos:
            verify_product = session.execute("""
				SELECT monto,cantidad FROM PRODUCTO_EN_CARRITO 
				WHERE usuario_id=%s and producto_id=%s and carrito_id=%s
				""", (sessionF['usuario_id'], producto_id, sessionF['carrito_id'])).one()
                
        if verify_product: 
            # de existir el producto actualizarlo de carrito
            # eliminar el pruducto de la lista para luego reinsertarlo
            session.execute("""
				UPDATE carrito 
				SET productos = productos - %s, monto = %s 
				WHERE carrito_id=%s AND usuario_id=%s AND fecha=%s 
				""", 
				({Prdcto_anddo(producto_id, nombre, precio, float(verify_product.monto), int(verify_product.cantidad))}, float(carrito.monto) - float(verify_product.monto), carrito.carrito_id, carrito.usuario_id, carrito.fecha))
            
            edit_monto = float(verify_product.monto)
            edit_cantidad = int(verify_product.cantidad)
            #actualizar producto_en_carrito para los nuevos valores
            session.execute("""
				UPDATE PRODUCTO_EN_CARRITO 
				SET monto=%s, cantidad=%s
				WHERE usuario_id=%s and producto_id=%s and carrito_id=%s
				""", (monto + edit_monto, cantidad + edit_cantidad, sessionF['usuario_id'], producto_id, sessionF['carrito_id']))
            
        else:
            # de no existir se inserta el producto a producto_en_carrito            
            session.execute("""
				INSERT INTO PRODUCTO_EN_CARRITO (carrito_id, producto_id, usuario_id, fecha_carrito, monto, cantidad)
				VALUES (%s, %s, %s, %s, %s, %s)
				""", (carrito.carrito_id, producto_id, sessionF['usuario_id'], carrito.fecha, monto, cantidad))
            
        # insertar el nuevo producto en el carrito
        session.execute("""
			UPDATE carrito 
			SET productos = productos + %s, monto = %s 
			WHERE carrito_id=%s AND usuario_id=%s AND fecha=%s 
			""", 
			({Prdcto_anddo(producto_id, nombre, precio, monto + edit_monto, cantidad + edit_cantidad)}, float(carrito.monto) + monto, carrito.carrito_id, carrito.usuario_id, carrito.fecha))
        
    return redirect(url_for('carrito'))

@app.route('/Carrito/edit', methods=['POST'])
def editar_producto_carrito():
    
    if request.method == 'POST':
        producto_id = UUID(request.form['producto_id'])
        
        # para saber si el producto aun existe
        producto = session.execute("""
            SELECT nombre FROM producto WHERE producto_id = %s
        """, (producto_id,)).one()
        if not producto:
            return redirect(url_for('carrito'))
        
        nueva_cantidad = int(request.form['nuevacantidad'])
        cantidad = int(request.form['cantidad'])
        
        # para evitar la sobre carga de productos
        if cantidad == 1 and nueva_cantidad == 1:
            return redirect(url_for('carrito'))
        
        precio = float(request.form['precio'])
        nombre = request.form['nombre']
        actual_monto_producto = float(request.form['producto_monto'])
        carrito_monto = float(request.form['carrito_monto'])
        nuevo_monto_producto = nueva_cantidad*precio
        
        # Seleccionar la informacion de nuestro carrito
        carrito = session.execute("""
			SELECT * FROM carrito 
			WHERE carrito_id=%s ALLOW FILTERING
			""", (sessionF['carrito_id'],)).one()
        
        session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
        
        #actualizamos el carrito con la nueva informacion del producto editado
        session.execute("""
            UPDATE carrito 
            SET productos = productos -  %s, productos = productos  +  %s, monto = %s 
            WHERE carrito_id = %s AND usuario_id = %s AND fecha = %s
        """, (
            {Prdcto_anddo(producto_id, nombre, precio, actual_monto_producto, cantidad)},
            {Prdcto_anddo(producto_id, nombre, precio, nuevo_monto_producto, nueva_cantidad)},
            carrito_monto - actual_monto_producto + nuevo_monto_producto,
            carrito.carrito_id,
            carrito.usuario_id,
            carrito.fecha
        ))
        #tambien actualizar el producto de producto_en_carrito 
        session.execute("""
			UPDATE PRODUCTO_EN_CARRITO 
			SET monto=%s, cantidad=%s, fecha_carrito=%s
			WHERE usuario_id=%s and producto_id=%s and carrito_id=%s
			""", (nuevo_monto_producto, nueva_cantidad, carrito.fecha, sessionF['usuario_id'], producto_id, sessionF['carrito_id']))
    
    return redirect(url_for('carrito'))

@app.route('/Carrito/del', methods=['POST'])
def eliminar_producto_carrito():
    if request.method == 'POST':
        producto_id = UUID(request.form['producto_id'])
        # para saber si el producto aun existe
        producto = session.execute("""
            SELECT nombre FROM producto WHERE producto_id = %s
        """, (producto_id,)).one()
        if not producto:
            return redirect(url_for('carrito'))
        
        #logica para eliminar el productos	
        carrito = session.execute("""
			SELECT * FROM carrito 
			WHERE carrito_id=%s ALLOW FILTERING
			""", (sessionF['carrito_id'],)).one()
        
        precio = float(request.form['precio'])
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        producto_monto = float(request.form['producto_monto'])
        carrito_monto = float(request.form['carrito_monto'])
        
        session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
        
        #eliminamos el producto del carrito
        session.execute("""
			UPDATE carrito 
			SET productos = productos - %s, monto = %s 
			WHERE carrito_id = %s AND usuario_id = %s AND fecha = %s
		""", (
		{Prdcto_anddo(producto_id, nombre, precio, producto_monto, cantidad)},
		carrito_monto -  producto_monto,
		carrito.carrito_id,
		carrito.usuario_id,
		carrito.fecha
		))
        
        #eliminamos el producto de producto_en_carrito
        session.execute("""
			DELETE FROM PRODUCTO_EN_CARRITO 
   			WHERE usuario_id=%s and carrito_id=%s and producto_id=%s
			""", (sessionF['usuario_id'], carrito.carrito_id, producto_id))
    
    return redirect(url_for('carrito'))

@app.route('/Carrito/pag', methods=['POST'])
def pagar_carrito():
    global lista_productos
    if request.method == 'POST':
        carrito = session.execute("""
			SELECT * FROM carrito 
			WHERE carrito_id=%s ALLOW FILTERING
			""", (sessionF['carrito_id'],)).one()
        #comprobar si la lista de productos existe
        if not carrito.productos:
            return redirect(url_for('carrito'))

        metodo_pago = request.form.get('metodoPago')
        correo = request.form.get('correo')
        datestamp = datetime.now()
        
        pago_id = uuid4()
        recibo_id = uuid4()
        carrito_id = uuid4()
        print(carrito_id)
        
        
        session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
        session.user_type_registered(keyspace, 'metodo_pago', Metodo_pago)
        
        #creamos un nuevo pago
        session.execute("""
            INSERT INTO PAGO (usuario_id, pago_id, carrito_id, fecha, monto, metodo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, 
        (carrito.usuario_id, pago_id, carrito.carrito_id, datestamp, carrito.monto, Metodo_pago(metodo_pago,correo)))
        
        #creamos y agregamos en el recibo los productos que fueron comprados desde el carrito
        lista_productos_andddo = {Prdcto_anddo(producto.producto_id, producto.nombre, producto.precio, producto.monto, producto.cantidad) for producto in carrito.productos}
        
        session.execute("""
            INSERT INTO RECIBO (usuario_id, recibo_id, carrito_id, pago_id, fecha, monto, metodo, productos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (carrito.usuario_id, recibo_id, carrito.carrito_id, pago_id, datestamp, carrito.monto, Metodo_pago(metodo_pago,correo), lista_productos_andddo))
        
        #creamos el nuevo carrito para el usario
        session.execute("""
			INSERT INTO CARRITO (usuario_id, carrito_id, fecha, monto, productos)
			VALUES (%s, %s, %s, %s, %s)
			""", (carrito.usuario_id, carrito_id, datestamp, 0, {}))
        
        #actualizamos los datos correspondiente al comprar un carrito       
        for product in carrito.productos:
            #insertamos el producto a producto_comprado
            session.execute("""
				INSERT INTO PRDCTO_CMPRDO (usuario_id, producto_id, fecha, nombre, precio, cantidad)
				VALUES (%s, %s, %s, %s, %s, %s)
    		""", (carrito.usuario_id, product.producto_id, datestamp, product.nombre,product.precio, product.cantidad))
            
            #actualizamos la informacion de nuemero de compras del producto
            num_compras = session.execute("""
				SELECT compras,fecha,producto_id FROM PRODUCTO
				WHERE producto_id=%s 
				""", (product.producto_id, )).one()
            
            session.execute("""
				UPDATE PRODUCTO
				SET compras=%s
				WHERE producto_id=%s AND fecha=%s 
				""", (num_compras.compras + product.cantidad, product.producto_id, num_compras.fecha))
            
            #lista_productos[num_compras.producto_id]['compras'] =  num_compras.compras + product.cantidad
            lista_productos = OrderedDict(sorted({producto.producto_id:producto._asdict() 
                for producto in 
                session.execute("""
                    SELECT * FROM producto
                    LIMIT 100
                    """)
                }.items(), key=lambda x: x[1]['fecha'], reverse=True))
		#eliminamos todos los productos del carrito de la tabla producto_en_carrito
        session.execute("""
			DELETE FROM PRODUCTO_EN_CARRITO 
   			WHERE usuario_id=%s AND carrito_id=%s
			""", (sessionF['usuario_id'], carrito.carrito_id))
  
		#actualizamos el nuevo carrito para el usuario
        SM.set(sessionF, 'carrito_id', carrito_id)
        session.execute("""
			UPDATE USUARIO
   			SET carrito_id=%s
			WHERE usuario_id=%s
			""", (carrito_id, carrito.usuario_id))
        
        
    return redirect(url_for('recibo'))






##############################################################
##############################################################
##							SOPORTE							##
##															##
##############################################################
##############################################################





@app.route('/Soporte', methods=['GET', 'POST'])
def soporte():
    if request.method == 'POST':
        # para crear un soporte
        
        mensaje = request.form.get('mensaje')
        # por si el mensaje esta vacio 
        if mensaje == ' ':
            return redirect(url_for('index'))
        
        soporte_id = uuid4()
        datestamp = datetime.now()
        
        # insertar el nuevo soporte
        session.execute("""
            INSERT INTO SOPORTE (usuario_id, soporte_id, fecha, mensaje, respuestas)
            VALUES (%s, %s, %s, %s, {})
        """, (sessionF['usuario_id'], soporte_id, datestamp, mensaje))
        
        return redirect(url_for('LSoportes'))
	
    return render_template('soporte.html', usuario=sessionF)
    

@app.route('/LSoportes')
def LSoportes():
    # para visualizar los soportes creados
	lista_soportes = session.execute("""
		SELECT * FROM soporte 
		WHERE usuario_id=%s
  		ORDER BY fecha DESC
		""", (sessionF['usuario_id'],))
	
	return render_template('lista-soportes.html', usuario=sessionF,soportes=lista_soportes)

@app.route('/LSoportes/resp', methods=['POST'])
def responder_soporte():
    # para responder los soportes creados
    if request.method == 'POST':
        #revisar si existe el soporte
        soporte_id = UUID(request.form.get('soporte_id'))
        soporte = session.execute("""
            SELECT soporte_id FROM soporte 
            WHERE soporte_id = %s ALLOW FILTERING
        """, (soporte_id, ))

        if not soporte:
            return redirect(url_for('LSoportes'))
        
        # agregar una respuesta a un soporte
        respuesta = request.form.get('respuesta')
        
        fecha = request.form.get('fecha')
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
        datestamp = datetime.now()
        
        session.user_type_registered(keyspace, 'respuesta', Respuesta)
        
        session.execute("""
            UPDATE soporte 
            SET respuestas = respuestas +  %s 
            WHERE usuario_id = %s  AND fecha = %s
        """, (
            {datestamp: Respuesta(sessionF['usuario_id'], respuesta, sessionF['nombre'])},
            sessionF['usuario_id'],
            fecha
            ))

    return redirect(url_for('LSoportes'))





##############################################################
##############################################################
##							RECIBO							##
##															##
##############################################################
##############################################################




@app.route('/LRecibos')
def LRecibos():
    # Visualizar la lista de lso recibos
    recibos = session.execute("""
		SELECT * FROM recibo
		WHERE usuario_id=%s 
  		ORDER BY fecha DESC
		""", (sessionF['usuario_id'], ))
    
    # Para usar la lista en el html en forma de diccionario
    lista_recibos = [recibo._asdict() for recibo in recibos]
    
    
    return render_template('lista-recibos.html', usuario=sessionF, recibos=lista_recibos)


@app.route('/recibo')
def recibo():
    # para ver la informacion del recibo creado en una solo pagina
    recibo_reciente = session.execute("""
		SELECT * FROM recibo 
		WHERE usuario_id=%s 
		ORDER BY fecha DESC 
		LIMIT 1
	""", (sessionF['usuario_id'], )).one()

    return render_template('recibo.html', usuario=sessionF, recibo=recibo_reciente)



##############################################################
##############################################################
##							ADMIN							##
##															##
##############################################################
##############################################################



@app.route('/index/admin')
def index_admin():
    # cargar los productos en el indice para su edicion
    return render_template('index_admin.html', usuario=sessionF, productos=lista_productos)

@app.route('/index/admin/s', methods=['GET','POST'])
def buscar_producto_admin():
    # para buscar productos por su nombre
    sessionF['sp_producto_id'] = None
    sessionF['sp_nombre'] = None
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        producto_id = request.form['producto_id']
        
        sessionF['sp_nombre'] = nombre
        sessionF['sp_producto_id'] = producto_id
    
    nombre = sessionF['sp_nombre']
    producto_id = sessionF['sp_producto_id']
    productos = None
    
    # evitar busqueda vacia
    if not nombre  and not producto_id:
        return redirect(url_for('index_admin'))
    
    elif producto_id == '':
        productos = OrderedDict(sorted({producto.producto_id:producto._asdict() for producto in 
            session.execute("""
                SELECT * FROM producto
                where nombre = %s ALLOW FILTERING
                """, (nombre, ))
            }.items(), key=lambda x: x[1]['fecha'], reverse=True))
        
    elif nombre == '':
        productos = OrderedDict(sorted({producto.producto_id:producto._asdict() for producto in 
            session.execute("""
                SELECT * FROM producto
                where producto_id = %s
                """, (UUID(producto_id), ))
            }.items(), key=lambda x: x[1]['fecha'], reverse=True))
    else:
        productos = OrderedDict(sorted({producto.producto_id:producto._asdict() for producto in 
            session.execute("""
                SELECT * FROM producto
                where producto_id = %s and nombre = %s ALLOW FILTERING
                """, (UUID(producto_id), nombre ))
            }.items(), key=lambda x: x[1]['fecha'], reverse=True))
    
    
    return render_template('index_admin.html', usuario=sessionF, productos=productos)
    

@app.route('/index/admin/add', methods=['POST'])
def agregar_producto_admin():
    # para agregar productos nuevos
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
        
		# insertar el nuevo producto con los datos ingresados
        session.execute("""
        	INSERT INTO producto (producto_id, nombre, descripcion, precio, fecha, valoracion, compras, version_comptble, plugins, schematics)
        	VALUES (%s, %s, %s, %s, %s, 0, 0, %s, %s, %s)
    	""", (producto_id, nombre, descripcion, precio, fecha, version_comptble, plugins_list, schematics_list))

		#Para actualizar nuestro diccionario global que ayuda a la eficiencia
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
    # para editar o eliminar un producto 
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        producto_id = None
        
        # para editar el producto
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
			
   			#Actualiza la informacion del producto en la BD y en global
            session.execute("""
				UPDATE PRODUCTO 
				SET nombre=%s, descripcion=%s, precio=%s, version_comptble=%s 
				WHERE producto_id = %s AND fecha = %s 
			""", (nombre, descripcion, precio, version_comptble, producto_id, fecha))

            if producto_id in lista_productos:
                lista_productos[producto_id]['nombre'] = nombre
                lista_productos[producto_id]['descripcion'] = descripcion
                lista_productos[producto_id]['precio'] = precio
                lista_productos[producto_id]['version_comptble'] = version_comptble
        
        # si se elimina el producto
        elif 'eliminar' in accion:   
            producto_id = UUID(request.form['producto_id'])	
            fecha = request.form['fecha']
            fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
        
            session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)

			#eliminar el producto de la BD y del global
            session.execute("""
				DELETE FROM PRODUCTO  
				WHERE producto_id = %s AND fecha = %s
			""", (producto_id, fecha))
            
            try: 
                del lista_productos[producto_id]
            except:
                pass
        # buscar en el producto editado en las tablas para vaciar todo los productos de los carritos y de producto_en_carrito que contengan el producto 
        # usamos la ayuda de la view prdcto_en_crrto_producto_id de PRODUCTO_EN_CARRITO
        carritosFind = session.execute("""
			SELECT carrito_id,producto_id,usuario_id,fecha_carrito 
   			FROM prdcto_en_crrto_producto_id  
			WHERE producto_id = %s ALLOW FILTERING
			""", (producto_id, ))
        
        # si se encontro el producto procedemos con la eliminacion
        if carritosFind:
            for carrito in carritosFind:
                session.execute("""
    			    UPDATE carrito 
    			    SET productos = {}, monto=0 
		    	    WHERE usuario_id = %s AND carrito_id = %s AND fecha=%s
    			    """, (carrito.usuario_id, carrito.carrito_id, carrito.fecha_carrito))         
                
                
                session.execute("""
				    DELETE FROM PRODUCTO_EN_CARRITO 
   				    WHERE usuario_id=%s and carrito_id=%s and producto_id=%s
				    """, (carrito.usuario_id, carrito.carrito_id, carrito.producto_id))
        
        
        
    return redirect(url_for('buscar_producto_admin'))

@app.route('/Perfil/admin')
def perfil_admin():
    # para mostrar la informacion del administrador con sus 3 primeras compras
    compras_realizadas = session.execute("""
		SELECT * FROM PRDCTO_CMPRDO 
		WHERE usuario_id=%s 
  		ORDER BY fecha DESC
		LIMIT 3
		""", (sessionF['usuario_id'],))
    
    return render_template('perfil_admin.html', usuario=sessionF, compras=compras_realizadas)

@app.route('/Perfil/admin/editar', methods=['POST'])
def editar_perfil_admin():
    # para editar la informacion del administrador de la bd y en global
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
    # para ver los soportes creados por los usuarios ordenados
    lista_soportes = OrderedDict(sorted({soporte.usuario_id:soporte._asdict() for soporte in 
		session.execute("""
			SELECT * FROM soporte 
			LIMIT 100
			""")
		}.items(), key=lambda x: x[1]['fecha'], reverse=True))
    	
    
    
    return render_template('soporte_admin.html', usuario=sessionF,soportes=lista_soportes)


@app.route('/LSoportes/admin/resp', methods=['POST'])
def responder_soporte_admin():
    # para responder un soporte de un usuario 
    if request.method == 'POST':
        respuesta = request.form.get('respuesta')
        usuario_id = UUID(request.form.get('usuario_id'))
        fecha = request.form.get('fecha')
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
        datestamp = datetime.now()
        
        session.user_type_registered(keyspace, 'respuesta', Respuesta)
        # ingresar la nueva respeusta al soporte del usuario
        session.execute("""
            UPDATE soporte
            SET respuestas = respuestas +  %s 
            WHERE usuario_id = %s AND fecha = %s
        """, (
            {datestamp: Respuesta(sessionF['usuario_id'], respuesta, sessionF['nombre'])},
            usuario_id,
            fecha
            ))

    return redirect(url_for('buscar_soporte_admin'))


@app.route('/LSoportes/admin/del', methods=['POST'])
def eliminar_soporte_admin():
    # para eliminar un soporte del usuario
    if request.method == 'POST':       
        soporte_id = UUID(request.form.get('soporte_id'))	
        usuario_id = UUID(request.form.get('usuario_id'))	
        fecha = request.form.get('fecha')
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
        
        session.execute("""
			DELETE FROM SOPORTE  
			WHERE fecha = %s AND usuario_id=%s
		""", (fecha, usuario_id))
    
    return redirect(url_for('buscar_soporte_admin'))

@app.route('/LSoportes/admin/s', methods=['GET','POST'])
def buscar_soporte_admin():
    if not 'ss_usuario_id' in sessionF: 
        sessionF['ss_usuario_id'] = None
        sessionF['ss_soporte_id'] = None
        sessionF['ss_fecha1'] = None
        sessionF['ss_fecha2'] = None
        sessionF['ss_fecha_condicion'] = "<="

    # para buscar un soporte por su id o/y por el id el usuario
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        soporte_id = request.form['soporte_id']
        fecha1 = request.form['fecha1']
        fecha2 = request.form['fecha2']
        fecha_condicion = "<="
        
        lista_soportes_buscados = {}
        sessionF['ss_usuario_id'] = usuario_id
        sessionF['ss_soporte_id'] = soporte_id
        sessionF['ss_fecha1'] = fecha1
        sessionF['ss_fecha2'] = fecha2
        sessionF['ss_fecha_condicion'] = fecha_condicion

    
    usuario_id = sessionF['ss_usuario_id']
    soporte_id = sessionF['ss_soporte_id'] 
    fecha_condicion = sessionF['ss_fecha_condicion']
    fecha1 = sessionF['ss_fecha1']
    fecha2 = sessionF['ss_fecha2']
    fecha_condicion = sessionF['ss_fecha_condicion']

    lista_soportes_buscados = None
    
    # inicio de la consulta
    query = "SELECT * FROM soporte WHERE "
    params = []
    query_conditions = []
    end_conditions = []
    
    # busqueda en blanco
    if not usuario_id  and not soporte_id and not fecha1 and not fecha2:
        return redirect(url_for('soporte_admin'))    
    
    # busqueda por id de usuario     
    if usuario_id:
        query_conditions.append("usuario_id = %s")
        params.append(UUID(usuario_id))
        end_conditions.append("ORDER BY fecha DESC")  

    # busqueda por id de soporte 
    if soporte_id:
        query_conditions.append("soporte_id = %s")
        params.append(UUID(soporte_id))

    # busqueda por una fecha o entre dos fechas 
    if fecha1:
        query_conditions.append("fecha " + fecha_condicion + " %s")
        params.append(datetime.strptime(fecha1 + " 00:00:00.000000" , '%Y-%m-%d %H:%M:%S.%f'))
        
    if fecha2 and fecha_condicion == '<=':
        query_conditions.append("fecha >= %s")
        params.append(datetime.strptime(fecha2 + " 00:00:00.000000", '%Y-%m-%d %H:%M:%S.%f'))
        
        
    end_conditions.append("LIMIT 100")  
    if soporte_id or fecha1 or fecha2:
        end_conditions.append("ALLOW FILTERING")  
        
        
    query = query + " AND ".join(query_conditions) + " " + " ".join(end_conditions) 
    print(query)
    print(params)
    
    lista_soportes_buscados = OrderedDict({soporte.soporte_id: soporte._asdict() for soporte in 
        session.execute(
            query, params)}.items())
        
    
    return render_template('soporte_admin.html', usuario=sessionF, soportes=lista_soportes_buscados)


if __name__ == '__main__':
	app.run(host='localhost', port=8080, debug=True)

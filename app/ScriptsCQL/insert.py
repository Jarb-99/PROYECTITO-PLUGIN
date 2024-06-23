from UDTs import *
from uuid import uuid4
from faker import Faker
from datetime import datetime, date
from connection import get_cassandra_session
import threading
import time
import math

lock = threading.RLock()

def uuids(n):
    time.sleep(0.1)
    with lock:
        list_uuid = []
        for i in range(n):
            list_uuid.append(uuid4())
    return list_uuid

def generateDatas(dh, produ, start_index, hilo):
    print(f"Empezando: Datos {hilo}")
    time.sleep(1)
    session = get_cassandra_session()
    fake = Faker()
    
    propietario1_id = uuid4()
    
    #Carga de UDTS
    session.user_type_registered(keyspace, 'respuesta', Respuesta)
    session.user_type_registered(keyspace, 'plugin', Plugin)
    session.user_type_registered(keyspace, 'schematic', Schematic)
    session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
    session.user_type_registered(keyspace, 'metodo_pago', Metodo_pago)
    
    #Generador de datos
    for i in range(dh):
        list_uuid = uuids(6)
        usuario_id = list_uuid[0]
        soporte_id = list_uuid[1]
        producto_id = list_uuid[2]
        carrito_id = list_uuid[3]
        pago_id = list_uuid[4]
        recibo_id = list_uuid[5]
        
        nombre_usuario = fake.first_name()
        
        fecha_soporte = fake.date_this_year()
        respuesta_soporte = {fake.date_this_year(): Respuesta(usuario_id, fake.sentence(), nombre_usuario)}
        
        precio_producto = round(fake.random_number(digits=2), 2)
        nombre_producto = f"Producto {start_index+i+1}"
        valoracion_producto = fake.random_int(min=1, max=5)
        compras_producto = fake.random_int(min=1, max=100)
        
        cantidad_producto_anddo = fake.random_int(min=1, max=10)
        monto_producto_anddo = cantidad_producto_anddo*precio_producto
        monto_carrito = monto_producto_anddo
        
        producto_anddo = {Prdcto_anddo(producto_id, nombre_producto, precio_producto, monto_producto_anddo, cantidad_producto_anddo)}
        
        fecha_pago = fake.date_this_year()
        metodo_pago = Metodo_pago(fake.random_element(elements=('Tarjeta de Crédito', 'PayPal', 'Efectivo')), fake.sentence())
        
        
        # Generar password fake
        password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)

        # Generar datos de usuarios
        session.execute("""
            INSERT INTO USUARIO (usuario_id, carrito_id, nombre, apellido, correo, contrasena, fecha_rgstro, foto, direccion, telefono)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (usuario_id, carrito_id, nombre_usuario, fake.last_name(), fake.email(), password, fake.date_this_year(), fake.image_url(), fake.street_address(), fake.phone_number()))
        
        # Generar datos de propietarios (Solo uno)
        if start_index == 0:
            session.execute("""
                INSERT INTO PROPIETARIO (administrador_id, usuario_id, nombre_usuario)
                VALUES (%s, %s, %s)
            """, (propietario1_id, usuario_id, nombre_usuario))
        
        # Generar datos de soporte
        session.execute("""
            INSERT INTO SOPORTE (usuario_id, soporte_id, fecha, mensaje, respuestas)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_id, soporte_id, fecha_soporte, fake.sentence(), respuesta_soporte))
        
        # Generar datos de productos (3 por ejemplo)
        if i < produ: 
            session.execute("""
                INSERT INTO PRODUCTO (producto_id, nombre, descripcion, precio, fecha, valoracion, compras, version_comptble, plugins, schematics)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (producto_id, nombre_producto, fake.sentence(), precio_producto, fake.date_this_year(), valoracion_producto, compras_producto, f'v{fake.random_digit()}', [Plugin(fake.random_element(elements=('1.0', '2.0', '3.0')))], [Schematic(fake.random_int(min=10, max=50))]))
        
        # Generar datos de carritos
        session.execute("""
            INSERT INTO CARRITO (usuario_id, carrito_id, fecha, monto, productos)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_id, carrito_id, fake.date_this_year(), monto_carrito, producto_anddo))
        
        # Generar datos de pagos
        session.execute("""
            INSERT INTO PAGO (usuario_id, pago_id, carrito_id, fecha, monto, metodo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario_id, pago_id, carrito_id, fecha_pago, monto_carrito, metodo_pago))
        
        # Generar datos de recibos
        session.execute("""
            INSERT INTO RECIBO (usuario_id, recibo_id, carrito_id, pago_id, fecha, monto, metodo, productos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (usuario_id, recibo_id, carrito_id, pago_id, fecha_pago, monto_carrito, metodo_pago, producto_anddo))
        
        # Generar datos de productos comprados
        session.execute("""
            INSERT INTO PRDCTO_CMPRDO (usuario_id, producto_id, fecha, nombre, precio, cantidad)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario_id, producto_id, fecha_pago, nombre_producto, precio_producto, cantidad_producto_anddo))
        
        # Generar datos de comentarios de productos
        session.execute("""
            INSERT INTO CMNTRIO_PRDCTO (producto_id, usuario_id, fecha, nombre_usuario, descripcion)
            VALUES (%s, %s, %s, %s, %s)
        """, (producto_id, usuario_id, fake.date_this_year(), nombre_usuario, fake.sentence()))
        
        # Generar datos de valoraciones de productos
        session.execute("""
            INSERT INTO VALORAR_PRODUCTO (producto_id, usuario_id, fecha, estrellas)
            VALUES (%s, %s, %s, %s)
        """, (producto_id, usuario_id, fake.date_this_year(), fake.random_int(min=1, max=5)))
    
    print(f" Datos {hilo} generados e insertados en la base de datos.")

    

def insertDatas():
    h = 120  #cantidad de hilos [cassandra thead limit max:128]
    d = 15000 #cantidad de datos
    dh = int(math.ceil(d/h)) #datos por hilo
    produ = dh #cantidad productos
    
    ##Generar Hilos
    threads = []
    for i in range(h):
        thread = threading.Thread(target=generateDatas, args=(dh,produ,dh*i, i))
        threads.append(thread)
        thread.start()
        
    for thread in threads:
        thread.join()
        
    print(f"terminado: {dh*h} Datos generados e insertados en la base de datos.")
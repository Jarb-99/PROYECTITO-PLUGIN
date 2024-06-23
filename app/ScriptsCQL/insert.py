from UDTs import *
from uuid import uuid4
from faker import Faker
from datetime import datetime, date
from connection import get_cassandra_session

def insertDatas():
    session = get_cassandra_session()
    fake = Faker()
    
    usuarios = []
    propietarios = []
    soportes = []
    productos = []
    carritos = []
    pagos = []
    recibos = []
    productos_comprados = []
    comentarios_productos = []
    valoraciones_productos = []
    
    propietario1_id = uuid4()

    for i in range(1000):
        usuario_id = uuid4()
        carrito_id = uuid4()
        producto_id = uuid4()
        soporte_id = uuid4()
        pago_id = uuid4()
        recibo_id = uuid4()
        
        # Generar password fake
        password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)

        # Generar datos de usuarios
        usuarios.append((usuario_id, carrito_id, fake.first_name(), fake.last_name(), fake.email(), password, fake.date_this_year(), fake.image_url(), fake.street_address(), fake.phone_number()))
        
        # Generar datos de propietarios (uno por cada 10 usuarios, por ejemplo)
        if i % 10 == 0:
            propietarios.append((propietario1_id, usuario_id, fake.user_name()))
        
        # Generar datos de soporte
        soportes.append((usuario_id, soporte_id, fake.date_this_year(), fake.sentence(), {fake.date_this_year(): Respuesta(propietario1_id, fake.sentence(), fake.user_name())}))
        
        # Generar datos de productos (3 por ejemplo)
        if i < 3: 
            productos.append((producto_id, fake.word(), fake.sentence(), round(fake.random_number(digits=2), 2), fake.date_this_year(), fake.random_int(min=1, max=5), fake.random_int(min=1, max=100), f'v{fake.random_digit()}', [Plugin(fake.random_element(elements=('1.0', '2.0', '3.0')))], [Schematic(fake.random_int(min=10, max=50))]))
        
        # Generar datos de carritos
        carritos.append((usuario_id, carrito_id, fake.date_this_year(), round(fake.random_number(digits=3), 2), {Prdcto_anddo(producto_id, fake.word(), round(fake.random_number(digits=2), 2), round(fake.random_number(digits=2), 2), fake.random_int(min=1, max=10))}))
        
        # Generar datos de pagos
        pagos.append((usuario_id, pago_id, carrito_id, fake.date_this_year(), round(fake.random_number(digits=3), 2), Metodo_pago(fake.random_element(elements=('Tarjeta de Crédito', 'PayPal', 'Efectivo')), fake.sentence())))
        
        # Generar datos de recibos
        recibos.append((usuario_id, recibo_id, carrito_id, pago_id, fake.date_this_year(), round(fake.random_number(digits=3), 2), Metodo_pago(fake.random_element(elements=('Tarjeta de Crédito', 'PayPal', 'Efectivo')), fake.sentence()), {Prdcto_anddo(producto_id, fake.word(), round(fake.random_number(digits=2), 2), round(fake.random_number(digits=2), 2), fake.random_int(min=1, max=10))}))
        
        # Generar datos de productos comprados
        productos_comprados.append((usuario_id, producto_id, fake.date_this_year(), fake.word(), round(fake.random_number(digits=2), 2), fake.random_int(min=1, max=10)))
        
        # Generar datos de comentarios de productos
        comentarios_productos.append((producto_id, usuario_id, fake.date_this_year(), fake.user_name(), fake.sentence()))
        
        # Generar datos de valoraciones de productos
        valoraciones_productos.append((producto_id, usuario_id, fake.date_this_year(), fake.random_int(min=1, max=5)))
    
    session.user_type_registered(keyspace, 'respuesta', Respuesta)
    session.user_type_registered(keyspace, 'plugin', Plugin)
    session.user_type_registered(keyspace, 'schematic', Schematic)
    session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
    session.user_type_registered(keyspace, 'metodo_pago', Metodo_pago)
    
    # Insertar datos en la tabla USUARIO
    for usuario in usuarios:
        session.execute("""
            INSERT INTO USUARIO (usuario_id, carrito_id, nombre, apellido, correo, contrasena, fecha_rgstro, foto, direccion, telefono)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, usuario)

    # Insertar datos en la tabla PROPIETARIO
    for propietario in propietarios:
        session.execute("""
            INSERT INTO PROPIETARIO (administrador_id, usuario_id, nombre_usuario)
            VALUES (%s, %s, %s)
        """, propietario)

    # Insertar datos en la tabla SOPORTE
    for soporte in soportes:
        session.execute("""
            INSERT INTO SOPORTE (usuario_id, soporte_id, fecha, mensaje, respuestas)
            VALUES (%s, %s, %s, %s, %s)
        """, soporte)

    # Insertar datos en la tabla PRODUCTO
    for producto in productos:
        session.execute("""
            INSERT INTO PRODUCTO (producto_id, nombre, descripcion, precio, fecha, valoracion, compras, version_comptble, plugins, schematics)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, producto)

    # Insertar datos en la tabla CARRITO
    for carrito in carritos:
        session.execute("""
            INSERT INTO CARRITO (usuario_id, carrito_id, fecha, monto, productos)
            VALUES (%s, %s, %s, %s, %s)
        """, carrito)

    # Insertar datos en la tabla PAGO
    for pago in pagos:
        session.execute("""
            INSERT INTO PAGO (usuario_id, pago_id, carrito_id, fecha, monto, metodo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, pago)

    # Insertar datos en la tabla RECIBO
    for recibo in recibos:
        session.execute("""
            INSERT INTO RECIBO (usuario_id, recibo_id, carrito_id, pago_id, fecha, monto, metodo, productos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, recibo)

    # Insertar datos en la tabla PRDCTO_CMPRDO
    for producto_comprado in productos_comprados:
        session.execute("""
            INSERT INTO PRDCTO_CMPRDO (usuario_id, producto_id, fecha, nombre, precio, cantidad)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, producto_comprado)

    # Insertar datos en la tabla CMNTRIO_PRDCTO
    for comentario_producto in comentarios_productos:
        session.execute("""
            INSERT INTO CMNTRIO_PRDCTO (producto_id, usuario_id, fecha, nombre_usuario, descripcion)
            VALUES (%s, %s, %s, %s, %s)
        """, comentario_producto)

    # Insertar datos en la tabla VALORAR_PRODUCTO
    for valoracion_producto in valoraciones_productos:
        session.execute("""
            INSERT INTO VALORAR_PRODUCTO (producto_id, usuario_id, fecha, estrellas)
            VALUES (%s, %s, %s, %s)
        """, valoracion_producto)
    
    print("Datos generados e insertados en la base de datos.")

insertDatas()

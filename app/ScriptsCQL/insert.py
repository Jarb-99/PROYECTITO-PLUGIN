from UDTs import *
from uuid import uuid4
from datetime import datetime, date
from connection import get_cassandra_session

def insertDatas():
    session = get_cassandra_session()
    # Definir UUIDs
    usuario1_id = uuid4()
    usuario2_id = uuid4()
    usuario3_id = uuid4()

    producto1_id = uuid4()
    producto2_id = uuid4()
    producto3_id = uuid4()

    soporte1_id = uuid4()
    soporte2_id = uuid4()
    soporte3_id = uuid4()

    carrito1_id = uuid4()
    carrito2_id = uuid4()
    carrito3_id = uuid4()

    pago1_id = uuid4()
    pago2_id = uuid4()
    pago3_id = uuid4()

    recibo1_id = uuid4()
    recibo2_id = uuid4()
    recibo3_id = uuid4()

    propietario1_id = uuid4()

    # Datos de prueba
    usuarios = [
        (usuario1_id, carrito1_id, 'Juan', 'Perez', 'juan.perez@example.com', 'password123', date(2023, 1, 1), 'foto1.jpg', 'Calle Falsa 123', '1234567890'),
        (usuario2_id, carrito2_id, 'Maria', 'Gomez', 'maria.gomez@example.com', 'password123', date(2023, 1, 2), 'foto2.jpg', 'Avenida Siempre Viva 456', '0987654321'),
        (usuario3_id, carrito3_id, 'Pedro', 'Lopez', 'pedro.lopez@example.com', 'password123', date(2023, 1, 3), 'foto3.jpg', 'Boulevard de los Sueños 789', '1122334455')
    ]

    propietarios = [
        (propietario1_id, usuario1_id, 'juan.perez')
    ]

    session.user_type_registered(keyspace, 'respuesta', Respuesta)
    soportes = [
        (usuario1_id, soporte1_id, datetime(2023, 1, 1), 'Mensaje de soporte 1', {datetime(2023, 1, 1): Respuesta(propietario1_id, 'Respuesta 1', 'juan.perez')}),
        (usuario2_id, soporte2_id, datetime(2023, 1, 2), 'Mensaje de soporte 2', {datetime(2023, 1, 2): Respuesta(propietario1_id, 'Respuesta 2', 'juan.perez')}),
        (usuario3_id, soporte3_id, datetime(2023, 1, 3), 'Mensaje de soporte 3', {datetime(2023, 1, 3): Respuesta(usuario3_id, 'Respuesta 3', 'pedro')})
    ]

    session.user_type_registered(keyspace, 'plugin', Plugin)
    session.user_type_registered(keyspace, 'schematic', Schematic)
    productos = [
        (producto1_id, 'Producto 1', 'Descripción del producto 1', 100.0, date(2023, 1, 1), 5, 10, 'v1', [Plugin('1.0')], []),
        (producto2_id, 'Producto 2', 'Descripción del producto 2', 200.0, date(2023, 1, 2), 4, 20, 'v1', [], [Schematic(20)]),
        (producto3_id, 'Producto 3', 'Descripción del producto 3', 300.0, date(2023, 1, 3), 3, 30, 'v3', [Plugin('3.0')], [Schematic(30)])
    ]

    session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
    carritos = [
        (usuario1_id, carrito1_id, date(2023, 1, 1), 400.0, {Prdcto_anddo(producto1_id, 'Producto 1', 100.0, 200.0, 2)}),
        (usuario2_id, carrito2_id, date(2023, 1, 2), 200.0, {Prdcto_anddo(producto2_id, 'Producto 2', 200.0, 200.0, 1)}),
        (usuario3_id, carrito3_id, date(2023, 1, 3), 300.0, {Prdcto_anddo(producto3_id, 'Producto 3', 300.0, 300.0, 1)})
    ]

    session.user_type_registered(keyspace, 'metodo_pago', Metodo_pago)
    pagos = [
        (usuario1_id, pago1_id, carrito1_id, date(2023, 1, 1), 400.0, Metodo_pago('Tarjeta de Crédito', 'Pago con tarjeta de crédito')),
        (usuario2_id, pago2_id, carrito2_id, date(2023, 1, 2), 200.0, Metodo_pago('PayPal', 'Pago con PayPal')),
        (usuario3_id, pago3_id, carrito3_id, date(2023, 1, 3), 300.0, Metodo_pago('Efectivo', 'Pago en efectivo'))
    ]


    recibos = [
        (usuario1_id, recibo1_id, carrito1_id, pago1_id, date(2023, 1, 1), 400.0, Metodo_pago('Tarjeta de Crédito', 'Pago con tarjeta de crédito'), {Prdcto_anddo(producto1_id, 'Producto 1', 100.0, 200.0, 2)}),
        (usuario2_id, recibo2_id, carrito2_id, pago2_id, date(2023, 1, 2), 200.0, Metodo_pago('PayPal', 'Pago con PayPal'), {Prdcto_anddo(producto2_id, 'Producto 2', 200.0, 200.0, 1)}),
        (usuario3_id, recibo3_id, carrito3_id, pago3_id, date(2023, 1, 3), 300.0, Metodo_pago('Paypal', 'Pago con PayPal'), {Prdcto_anddo(producto3_id, 'Producto 3', 300.0, 300.0, 1)})
    ]

    productos_comprados = [
        (usuario1_id, producto1_id, date(2023, 1, 1), 'Producto 1',100, 2),
        (usuario2_id, producto2_id, date(2023, 1, 2), 'Producto 2',200, 1),
        (usuario3_id, producto3_id, date(2023, 1, 3), 'Producto 3',300, 1)
    ]

    comentarios_productos = [
        (producto1_id, usuario1_id, date(2023, 1, 1), 'juan.perez', 'Buen producto'),
        (producto2_id, usuario2_id, date(2023, 1, 2), 'maria.gomez', 'Producto regular'),
        (producto3_id, usuario3_id, date(2023, 1, 3), 'pedro.lopez', 'Excelente producto')
    ]

    valoraciones_productos = [
        (producto1_id, usuario1_id, date(2023, 1, 1), 5),
        (producto2_id, usuario2_id, date(2023, 1, 2), 4),
        (producto3_id, usuario3_id, date(2023, 1, 3), 3)
    ]

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
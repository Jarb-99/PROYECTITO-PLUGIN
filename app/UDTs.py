from connection import get_cassandra_session
from connection import keyspace

session = get_cassandra_session()

# Definir las clases para insertar datos en las tablas tipo User-Defined Type (UDT)
class Respuesta:
    def __init__(self, id_creador, mensaje, nombre_creador):
        self.id_creador = id_creador
        self.mensaje = mensaje
        self.nombre_creador = nombre_creador

class Prdcto_anddo:
    def __init__(self, producto_id, monto, cantidad):
        self.producto_id = producto_id
        self.monto = monto
        self.cantidad = cantidad

class Metodo_pago:
    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

class Plugin:
    def __init__(self, version):
        self.version = version

class Schematic:
    def __init__(self, dimensiones):
        self.dimensiones = dimensiones

# Registrar el tipo User-Defined Type (UDT)

# session.user_type_registered(keyspace, 'respuesta', Respuesta)
# session.user_type_registered(keyspace, 'prdcto_anddo', Prdcto_anddo)
# session.user_type_registered(keyspace, 'metodo_pago', Metodo_pago)
# session.user_type_registered(keyspace, 'plugin', Plugin)
# session.user_type_registered(keyspace, 'schematic', Schematic)


from connection import get_cassandra_session

def deleteTables():
    session = get_cassandra_session()

    # Eliminar las tablas
    session.execute("DROP TABLE IF EXISTS USUARIO;")
    session.execute("DROP TABLE IF EXISTS PROPIETARIO;")
    session.execute("DROP TABLE IF EXISTS SOPORTE;")
    session.execute("DROP TABLE IF EXISTS PRODUCTO;")
    session.execute("DROP TABLE IF EXISTS CARRITO;")
    session.execute("DROP TABLE IF EXISTS PAGO;")
    session.execute("DROP TABLE IF EXISTS RECIBO;")
    session.execute("DROP TABLE IF EXISTS PRDCTO_CMPRDO;")
    session.execute("DROP TABLE IF EXISTS CMNTRIO_PRDCTO;")
    session.execute("DROP TABLE IF EXISTS VALORAR_PRODUCTO;")
    session.execute("DROP TABLE IF EXISTS PRODUCTO_EN_CARRITO;")

    # Eliminar los tipos de datos
    session.execute("DROP TYPE IF EXISTS PRDCTO_ANDDO;")
    session.execute("DROP TYPE IF EXISTS METODO_PAGO;")
    session.execute("DROP TYPE IF EXISTS PLUGIN;")
    session.execute("DROP TYPE IF EXISTS SCHEMATIC;")
    session.execute("DROP TYPE IF EXISTS RESPUESTA;")
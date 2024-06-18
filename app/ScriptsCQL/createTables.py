from connection import get_cassandra_session

def createTables():
    session = get_cassandra_session()

    # Crear tipos de datos
    session.execute("""
    CREATE TYPE IF NOT EXISTS PRDCTO_ANDDO (
        producto_id UUID,
        nombre TEXT,
        precio DECIMAL,
        monto DECIMAL,
        cantidad INT
    );
    """)

    session.execute("""
    CREATE TYPE IF NOT EXISTS METODO_PAGO (
        nombre TEXT,
        descripcion TEXT
    );
    """)

    session.execute("""
    CREATE TYPE IF NOT EXISTS PLUGIN (
        version TEXT
    );
    """)

    session.execute("""
    CREATE TYPE IF NOT EXISTS SCHEMATIC (
        dimensiones INT
    );
    """)

    session.execute("""
    CREATE TYPE IF NOT EXISTS RESPUESTA (
        id_creador UUID,
        mensaje TEXT,
        nombre_creador TEXT
    );
    """)

    # Crear tablas
    session.execute("""
    CREATE TABLE IF NOT EXISTS USUARIO (
        usuario_id UUID PRIMARY KEY,
        carrito_id UUID,
        nombre TEXT,
        apellido TEXT,
        correo TEXT,
        contrasena TEXT,
        fecha_rgstro DATE,
        foto TEXT,
        direccion TEXT,
        telefono TEXT
    );
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS PROPIETARIO (
        administrador_id UUID,
        usuario_id UUID,
        nombre_usuario TEXT,
        PRIMARY KEY (administrador_id, usuario_id)
    );
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS SOPORTE (
        usuario_id UUID,
        soporte_id UUID,
        fecha DATE,
        mensaje TEXT,
        respuestas MAP<DATE, FROZEN<RESPUESTA>>,
        PRIMARY KEY (usuario_id, soporte_id, fecha)
    );
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS PRODUCTO (
        producto_id UUID PRIMARY KEY,
        nombre TEXT,
        descripcion TEXT,
        precio DECIMAL,
        fecha TIMESTAMP,
        valoracion INT,
        compras INT,
        version_comptble TEXT,
        plugins LIST<FROZEN<PLUGIN>>,
        schematics LIST<FROZEN<SCHEMATIC>>
    );
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS CARRITO (
        usuario_id UUID,
        carrito_id UUID,
        fecha TIMESTAMP,
        monto DECIMAL,
        productos SET<FROZEN<PRDCTO_ANDDO>>,
        PRIMARY KEY (usuario_id, carrito_id, fecha)
    );
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS PAGO (
        usuario_id UUID,
        pago_id UUID,
        carrito_id UUID,
        fecha TIMESTAMP,
        monto DECIMAL,
        metodo FROZEN<METODO_PAGO>,
        PRIMARY KEY (usuario_id, pago_id, carrito_id, fecha)
    );
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS RECIBO (
        usuario_id UUID,
        recibo_id UUID,
        carrito_id UUID,
        pago_id UUID,
        fecha TIMESTAMP,
        monto DECIMAL,
        metodo FROZEN<METODO_PAGO>,
        PRIMARY KEY (usuario_id, recibo_id, carrito_id, pago_id, fecha)
    );
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS PRDCTO_CMPRDO (
        usuario_id UUID,
        producto_id UUID,
        fecha TIMESTAMP,
        cantidad INT,
        PRIMARY KEY (usuario_id, producto_id, fecha)
    );
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS CMNTRIO_PRDCTO (
        producto_id UUID,
        usuario_id UUID,
        fecha TIMESTAMP,
        nombre_usuario TEXT,
        descripcion TEXT,
        PRIMARY KEY (producto_id, usuario_id, fecha)
    );
    """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS VALORAR_PRODUCTO (
        producto_id UUID,
        usuario_id UUID,
        fecha TIMESTAMP,
        estrellas INT,
        PRIMARY KEY (producto_id, usuario_id, fecha)
    );
    """)
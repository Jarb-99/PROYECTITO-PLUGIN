from datetime import datetime, date

#############################################

   
def clear(session):
    session.clear()


def sPrint(session):
    for s in session :
        print(session[s])


def set(session, key, atribute):
    session[key] = atribute



#############################################
#   SETTERS

def set_usuario_dict(session, usuario):
    clear(session)
    session['usuario_id'] = usuario['usuario_id']
    session['carrito_id'] = usuario['carrito_id']
    session['nombre'] = usuario['nombre']
    session['apellido'] = usuario['apellido']
    session['correo'] = usuario['correo']
    session['contrasena'] = usuario['contrasena']
    session['fecha_rgstro'] = str(usuario['fecha_rgstro'])
    session['foto'] = usuario['foto']
    session['direccion'] = usuario['direccion']
    session['telefono'] = usuario['telefono']


def set_usuario(session, usuario_id, carrito_id, nombre='', apellido='', correo='', contrasena='', fecha_rgstro='', foto='', direccion='', telefono=''):
    clear(session)
    session['usuario_id'] = usuario_id
    session['carrito_id'] = carrito_id
    session['nombre'] = nombre
    session['apellido'] = apellido
    session['correo'] = correo
    session['contrasena'] = contrasena
    session['fecha_rgstro'] = fecha_rgstro
    session['foto'] = foto
    session['direccion'] = direccion
    session['telefono'] = telefono



#############################################
#   GETTERS

def get_usuario(session):
    return {
        'usuario_id': session.get('usuario_id'),
        'carrito_id': session.get('carrito_id'),
        'nombre': session.get('nombre'),
        'apellido': session.get('apellido'),
        'correo': session.get('correo'),
        'contrasena': session.get('contrasena'),
        'fecha_rgstro': session.get('fecha_rgstro'),
        'foto': session.get('foto'),
        'direccion': session.get('direccion'),
        'telefono': session.get('telefono'),
    }

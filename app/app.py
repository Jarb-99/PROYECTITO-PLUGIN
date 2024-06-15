from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)

"""
app.secret_key = 'clave_secreta'

@app.route('/')
def login():
  return render_template('login.html')
"""

@app.route('/')
def login():
  return render_template('index.html')

@app.route('/Home')
def home():
  return render_template('index.html')

@app.route('/Perfil')
def perfil():
  return render_template('perfil.html')

@app.route('/Carrito')
def carrito():
  return render_template('carrito.html')

@app.route('/Soporte')
def soporte():
  return render_template('soporte.html')

@app.route('/Logout')
def logout():
  return render_template('login.html')

@app.route('/PComprados')
def PComprados():
  return render_template('productos-comprados.html')

@app.route('/LSoportes')
def LSoportes():
  return render_template('lista-soportes.html')

@app.route('/LRecibos')
def LRecibos():
  return render_template('lista-recibos.html')

@app.route('/recibo')
def recibo():
    metodo_pago = request.args.get('metodoPago')
    # Aquí puedes procesar más información para el recibo si es necesario
    return render_template('recibo.html', metodoPago=metodo_pago)

"""
@app.route('/pagina_principal')
def pagina_principal():
  peliculas = twoten_movies()
  return render_template('index.html')
"""

"""
@app.route('/submit_register', methods=['POST'])
def submit_register():
  nombre = request.form['nombre']
  email = request.form['email']
  contraseña = request.form['password']
  insert_user(nombre, email, contraseña)
  return redirect(url_for('pagina_principal'))


@app.route('/submit_login', methods=['POST'])
def submit_login():
  email = request.form['email']
  contraseña = request.form['password']
  id_user = get_user_id(email)
  print(id_user)
  if id_user:
    if verify_password(id_user['id'], contraseña):
      session['logged'] = True
      session['id'] = id_user['id']
      session['usuario'] = id_user['usuario']
      session['email'] = email
      return redirect(url_for('pagina_principal'))
    else:
      flash('Contraseña incorrecta', 'error')
      return redirect('/')
  else:
    flash('Usuario no registrado', 'error')
    return redirect('/')
"""

@app.route('/Producto')
def todas_peliculas():
  peliculas = all_movies()
  return render_template('producto.html', peliculas=peliculas)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)

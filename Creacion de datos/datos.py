from neo4j import GraphDatabase
from faker import Faker
import random

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "porfavor")
driver = GraphDatabase.driver(URI, auth=AUTH)
fake = Faker()

usuarios = 100

def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        return result

# CREAR USUARIOS
lista_usuarios = []
for _ in range(usuarios):
    lista_usuarios.append(fake.name())

for i in range(usuarios):
    nombre = lista_usuarios[i]
    edad = fake.random_int(18, 50)
    direccion = fake.address()
    conectado = random.choice([True, False])
    query = f"CREATE (:Persona {{nombre: '{nombre}', contraseña: '1234', edad: {edad}, direccion: '{direccion}', conectado: '{conectado}'}})"
    run_query(query)

# CREAR LIBROS
def create_libro(nombre, genero, autor):
    query = f"CREATE (:Libro {{nombre: '{nombre}', genero: '{genero}', autor: '{autor}'}})"
    return run_query(query)

libros = [
    {"titulo": "1984", "genero": "Ciencia Ficción", "autor": "George Orwell"},
    {"titulo": "El Gran Gatsby", "genero": "Drama", "autor": "F. Scott Fitzgerald"},
    {"titulo": "Crónicas Marcianas", "genero": "Ciencia Ficción", "autor": "Ray Bradbury"},
    {"titulo": "Orgullo y Prejuicio", "genero": "Romance", "autor": "Jane Austen"},
    {"titulo": "El Hobbit", "genero": "Fantasía", "autor": "J.R.R. Tolkien"},
    {"titulo": "Harry Potter y la Piedra Filosofal", "genero": "Fantasía", "autor": "J.K. Rowling"},
    {"titulo": "Moby Dick", "genero": "Aventura", "autor": "Herman Melville"},
    {"titulo": "Don Quijote de la Mancha", "genero": "Clásico", "autor": "Miguel de Cervantes"},
    {"titulo": "Crimen y Castigo", "genero": "Ficción Psicológica", "autor": "Fyodor Dostoevsky"},
    {"titulo": "El Extranjero", "genero": "Filosofía", "autor": "Albert Camus"} ]

for libro in libros:
    create_libro(libro["titulo"], libro["genero"], libro["autor"])

lista_libros = [libro["titulo"] for libro in libros]

# CREAR JUEGOS
def create_juego(nombre, genero, cooperativo, plataforma):
    query = f"CREATE (:Juego {{nombre: '{nombre}', genero: '{genero}', cooperativo: '{cooperativo}', plataforma: '{plataforma}'}})"
    return run_query(query)

juegos = [
    {"nombre": "The Legend of Zelda: Breath of the Wild", "genero": "Aventura", "cooperativo": False, "plataforma": "Nintendo Switch"},
    {"nombre": "Overcooked 2", "genero": "Simulación", "cooperativo": True, "plataforma": "Multiplataforma"},
    {"nombre": "Borderlands 2", "genero": "Disparos en primera persona", "cooperativo": True, "plataforma": "Multiplataforma"},
    {"nombre": "Super Mario Party", "genero": "Fiesta", "cooperativo": True, "plataforma": "Nintendo Switch"},
    {"nombre": "Rocket League", "genero": "Deportes", "cooperativo": True, "plataforma": "Multiplataforma"},
    {"nombre": "Divinity: Original Sin 2", "genero": "RPG", "cooperativo": True, "plataforma": "Multiplataforma"},
    {"nombre": "Minecraft", "genero": "Sandbox", "cooperativo": True, "plataforma": "Multiplataforma"},
    {"nombre": "Among Us", "genero": "Misterio", "cooperativo": True, "plataforma": "Multiplataforma"},
    {"nombre": "Halo: The Master Chief Collection", "genero": "Disparos en primera persona", "cooperativo": True, "plataforma": "Xbox/PC"},
    {"nombre": "Splatoon 2", "genero": "Disparos", "cooperativo": True, "plataforma": "Nintendo Switch"} ]

for juego in juegos:
    create_juego(juego["nombre"],juego["genero"], juego["cooperativo"], juego["plataforma"])

lista_juegos = [juego["nombre"] for juego in juegos]

# CREAR PELICULAS
def create_pelicula(nombre, genero, idioma, director):
    query = f"CREATE (:Pelicula {{nombre: '{nombre}', genero: '{genero}', idioma: '{idioma}', director: '{director}'}})"
    return run_query(query)

peliculas = [
    {"nombre": "Inception", "genero": "Ciencia Ficción", "idioma": "Inglés", "director": "Christopher Nolan"},
    {"nombre": "Pulp Fiction", "genero": "Drama/Crimen", "idioma": "Inglés", "director": "Quentin Tarantino"},
    {"nombre": "The Shawshank Redemption", "genero": "Drama", "idioma": "Inglés", "director": "Frank Darabont"},
    {"nombre": "The Godfather", "genero": "Drama/Crimen", "idioma": "Inglés", "director": "Francis Ford Coppola"},
    {"nombre": "Interstellar", "genero": "Ciencia Ficción", "idioma": "Inglés", "director": "Christopher Nolan"},
    {"nombre": "Forrest Gump", "genero": "Drama/Romance", "idioma": "Inglés", "director": "Robert Zemeckis"},
    {"nombre": "The Matrix", "genero": "Ciencia Ficción/Acción", "idioma": "Inglés", "director": "The Wachowskis"},
    {"nombre": "The Dark Knight", "genero": "Acción/Crimen", "idioma": "Inglés", "director": "Christopher Nolan"},
    {"nombre": "Schindlers List", "genero": "Drama/Biografía", "idioma": "Inglés", "director": "Steven Spielberg"},
    {"nombre": "Fight Club", "genero": "Drama", "idioma": "Inglés", "director": "David Fincher"} ]

for pelicula in peliculas:
    create_pelicula(pelicula["nombre"], pelicula["genero"], pelicula["idioma"], pelicula["director"])

lista_peliculas = [pelicula["nombre"] for pelicula in peliculas]

# CREAR MUSICA
def create_musica(nombre, genero, autor):
    query = f"CREATE (:Musica {{nombre: '{nombre}', genero: '{genero}', autor: '{autor}'}})"
    return run_query(query)

musicas = [
    {"nombre": "Bohemian Rhapsody", "genero": "Rock", "autor": "Queen"},
    {"nombre": "Billie Jean", "genero": "Pop", "autor": "Michael Jackson"},
    {"nombre": "Hotel California", "genero": "Rock", "autor": "Eagles"},
    {"nombre": "Imagine", "genero": "Pop", "autor": "John Lennon"},
    {"nombre": "Stairway to Heaven", "genero": "Rock", "autor": "Led Zeppelin"},
    {"nombre": "Thriller", "genero": "Pop", "autor": "Michael Jackson"},
    {"nombre": "Smells Like Teen Spirit", "genero": "Grunge", "autor": "Nirvana"},
    {"nombre": "Yesterday", "genero": "Pop", "autor": "The Beatles"},
    {"nombre": "Sweet Child o Mine", "genero": "Rock", "autor": "Guns N Roses"},
    {"nombre": "Like a Rolling Stone", "genero": "Rock", "autor": "Bob Dylan"} ]

for musica in musicas:
    create_musica(musica["nombre"], musica["genero"],musica["autor"])

lista_musicas = [musica["nombre"] for musica in musicas]

# CREAR FRASE
def create_frase(frase, fecha):
    query = f"CREATE (:Frase {{cita: '{frase}', fecha: date('{fecha}')}})"
    return run_query(query)

frases = [
    {"cita": "No se puede vivir con el corazón vacío, pero hay que tener cuidado de no dejarse llevar demasiado por él."},
    {"cita": "El mundo era tan reciente que muchas cosas carecían de nombre, y para nombrarlas había que señalarías con el dedo."},
    {"cita": "Lo importante no es lo que nos hace el destino, sino lo que nosotros hacemos con él."},
    {"cita": "La única forma de lidiar con un mundo sin libertad es volviéndose tan absolutamente libre que tu mera existencia sea un acto de rebeldía."},
    {"cita": "Hay cosas que son verdad aunque no sucedan."},
    {"cita": "Sólo se ve bien con el corazón, lo esencial es invisible a los ojos."},
    {"cita": "La vida es lo que pasa mientras estás ocupado haciendo otros planes."},
    {"cita": "No importa lo que piensen de ti, lo importante es que tú sepas quién eres."},
    {"cita": "Todos somos prisioneros, pero algunos están en celdas con ventanas y otros sin ellas."},
    {"cita": "No es que haya estado siempre de acuerdo con él, pero me habría dejado cortar la mano derecha sin titubear si me lo hubiera pedido."}
]
for frase in frases:
    create_frase(frase["cita"], fake.date_between(start_date='-10y', end_date='today'))

lista_frases = [frase["cita"] for frase in frases]

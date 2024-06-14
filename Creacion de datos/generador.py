from neo4j import GraphDatabase
from faker import Faker
from datos import usuarios, lista_usuarios, lista_libros, lista_juegos, lista_peliculas, lista_musicas, lista_frases
import random

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "porfavor")
driver = GraphDatabase.driver(URI, auth=AUTH)
fake = Faker()

def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        return result

# CREAR RELACIONES DE AMISTAD
for i in range(usuarios):
    persona = lista_usuarios[i]
    aux = random.randint(1, 3)  # Cuantos amigos para cada usuario
    for _ in range(aux):
        amigo = random.choice(lista_usuarios)
        while amigo == persona:
            amigo = random.choice(lista_usuarios)
        query_relacion = f"MATCH (p1:Persona {{nombre: '{persona}'}}), (p2:Persona {{nombre: '{amigo}'}}) CREATE (p1)-[:ES_AMIGO_DE]->(p2)"
        run_query(query_relacion)

# CREAR RELACIONES PERSONA -> LIBRO
for i in range(usuarios):
    persona = lista_usuarios[i]
    aux = random.randint(0, 1)  # Cuantos le gustan a cada usuario
    libro = random.sample(lista_libros, aux)
    for i in range(aux):
        query_relacion = f"MATCH (p1:Persona {{nombre: '{persona}'}}), (l1:Libro {{nombre: '{libro[i]}'}}) CREATE (p1)-[:LE_GUSTA_LEER]->(l1)"
        run_query(query_relacion)

# CREAR RELACIONES PERSONA -> JUEGO
for i in range(usuarios):
    persona = lista_usuarios[i]
    aux = random.randint(0, 1)  # Cuantos le gustan a cada usuario
    juego = random.sample(lista_juegos, aux)
    for i in range(aux):
        query_relacion = f"MATCH (p1:Persona {{nombre: '{persona}'}}), (j1:Juego {{nombre: '{juego[i]}'}}) CREATE (p1)-[:LE_GUSTA_JUGAR]->(j1)"
        run_query(query_relacion)

# CREAR RELACIONES PERSONA -> PELICULA
for i in range(usuarios):
    persona = lista_usuarios[i]
    aux = random.randint(0, 1)  # Cuantos le gustan a cada usuario
    pelicula = random.sample(lista_peliculas, aux)
    for i in range(aux):
        query_relacion = f"MATCH (p1:Persona {{nombre: '{persona}'}}), (a1:Pelicula {{nombre: '{pelicula[i]}'}}) CREATE (p1)-[:LE_GUSTA_VER]->(a1)"
        run_query(query_relacion)

# CREAR RELACIONES PERSONA -> MUSICA
for i in range(usuarios):
    persona = lista_usuarios[i]
    aux = random.randint(0, 1)  # Cuantos le gustan a cada usuario
    musica = random.sample(lista_musicas, aux)
    for i in range(aux):
        query_relacion = f"MATCH (p1:Persona {{nombre: '{persona}'}}), (m1:Musica {{nombre: '{musica[i]}'}}) CREATE (p1)-[:LE_GUSTA_ESCUCHAR]->(m1)"
        run_query(query_relacion)




# CREAR RELACIONES PERSONA -> FRASE
for i in range(usuarios):
    persona = lista_usuarios[i]
    aux = random.randint(0, 2)  # Cuantos le gustan a cada usuario
    frase = random.sample(lista_frases, aux)
    for i in range(aux):
        query_relacion = f"MATCH (p1:Persona {{nombre: '{persona}'}}), (f1:Frase {{cita: '{frase[i]}'}}) CREATE (p1)-[:LE_GUSTA]->(f1)"
        run_query(query_relacion)
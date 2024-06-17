from cassandra.cluster import Cluster

# Conectar
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('bd_prueba')#nombre de la base de datos

try:
    # make query
    query = "SELECT nombre, edad, direccion FROM alumno"
    rows = session.execute(query)

    # print
    for row in rows:
        #print('Nombre: {}, Edad: {}, Direccion: {}'.format(row.nombre, row.edad, row.direccion))
        print(f'Nombre: {row.nombre}, Edad: {row.edad}, Direccion: {row.direccion}')

finally:
    cluster.shutdown()

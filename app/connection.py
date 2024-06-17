from cassandra.cluster import Cluster
keyspace = 'DataBaseProject'

# Conectar
def get_cassandra_session():
    # Conectar
    cluster = Cluster(['localhost'])
    session = cluster.connect(keyspace)  # nombre de la base de datos
    return session
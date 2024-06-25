from cassandra.cluster import Cluster

keyspace = 'DataBaseProject'

def get_cassandra_session():
    try:
        cluster = Cluster(['localhost'], port=9042)
        session = cluster.connect(keyspace)  # usa 'databaseproject' en minúsculas
        print("Conexión a Cassandra establecida correctamente.")
        return session
    except Exception as e:
        print(f"Error al conectar con Cassandra: {e}")
        return None
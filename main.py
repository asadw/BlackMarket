from flask import Flask, render_template
import sqlalchemy, firebase_admin
from os import getenv
from psycopg2 import OperationalError
from psycopg2.pool import SimpleConnectionPool
import datetime

# TODO(developer): specify SQL connection details
CONNECTION_NAME = getenv(
  'INSTANCE_CONNECTION_NAME',
  'fullcourt-1227c:us-east1:fullcourt')
DB_USER = getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = getenv('POSTGRES_PASSWORD', 'postgres')
DB_NAME = getenv('POSTGRES_DATABASE', 'postgres')

pg_config = {
  'user': DB_USER,
  'password': DB_PASSWORD,
  'dbname': DB_NAME
}

# Connection pools reuse connections between invocations,
# and handle dropped or expired connections automatically.
pg_pool = None

def __connect(host):
    """
    Helper function to connect to Postgres
    """
    global pg_pool
    pg_config['host'] = host
    pg_pool = SimpleConnectionPool(1, 1, **pg_config)


def postgres_demo(request):
    global pg_pool

    # Initialize the pool lazily, in case SQL access isn't needed for this
    # GCF instance. Doing so minimizes the number of active SQL connections,
    # which helps keep your GCF instances under SQL connection limits.
    if not pg_pool:
        try:
            __connect('/cloudsql/{CONNECTION_NAME}')
        except OperationalError:
            # If production settings fail, use local develpment ones
            __connect('127.0.0.1')

    # Remember to close SQL resources declared while running this function.
    # Keep any declared in global scope (e.g. pg_pool) for later reuse.

    conn = pg_pool.getconn()

    with conn.cursor() as cursor:
        cursor.execute('SELECT NOW();')
        results = cursor.fetchone()
        pg_pool.putconn(conn)
        print(type(results[0]))
        return results[0]


app = Flask(__name__)


"""
conn = psycopg2.connect(
	host="104.196.196.66", 
	dbname="fullcourt", 
	user="postgres", 
	password="watchdog",
	sslmode="require",
	sslcert="cert/client-cert.pem",
	sslkey="cert/client-key.pem")
"""

# eng = sqlalchemy.create_engine('postgresql:///fullcourt')
# con = eng.connect()


@app.route('/<name>', methods=['GET'])
def hello_world(name=None):
    time = postgres_demo(None)
    ms = time.strftime("%f")[:-3]
    time = time.strftime("%b %d %Y %I:%M:%S%p")
    return render_template('hello.html', name=name, t=time)


if __name__ == '__main__':
    app.run()

# test comment on 6/26/19
import sqlite3

def connect():
    conn = sqlite3.connect('flats_.db')
    return conn

def create_flat_table():
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS flat(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flat_id TEXT UNIQUE,
    title TEXT,
    price INTEGER,
    description TEXT,
    image TEXT,
    rooms TEXT,
    square TEXT,
    year TEXT,
    floor TEXT,
    type_house TEXT,
    region TEXT,
    city TEXT,
    street TEXT,
    district TEXT,
    coordinates TEXT
    )
    ''')


def insert_flat(flat: dict) -> None:
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO flat(
    flat_id,
    title,
    price,
    description,
    image,
    rooms,
    square,
    year,
    floor,
    type_house,
    region,
    city,
    street,
    district,
    coordinates
    ) VALUES (
    :flat_id,
    :title,
    :price,
    :description,
    :image,
    :rooms,
    :square,
    :year,
    :floor,
    :type_house,
    :region,
    :city,
    :street,
    :district,
    :coordinates
    ) ON CONFLICT (flat_id) DO UPDATE SET price = :price
    ''', flat)

    conn.commit()
    conn.close()

def get_all_flats():
    conn = connect()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM flat''')
    data = cur.fetchall()
    conn.close()
    return data

def get_flat_data(query: str, params=None):
    conn = connect()
    cur = conn.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    data = cur.fetchall()
    conn.close()

    return data


# q = '''SELECT title, price FROM flat WHERE price < ?'''

# print(get_flat_data(q, (1000000,)))
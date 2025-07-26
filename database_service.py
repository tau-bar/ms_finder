def init_database():
    import os
    import psycopg2
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print('DATABASE_URL not set')
        return
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print('Users table initialized successfully.')
    except Exception as e:
        print(f'Error initializing users table: {e}')

def log_user_to_postgres(user):
    import os
    from datetime import datetime
    import psycopg2
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print('DATABASE_URL not set')
        return
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        ''', (
            user.id,
            user.username or '',
            user.first_name or '',
            user.last_name or '',
            datetime.now()
        ))
        conn.commit()
        cur.close()
        conn.close()
        print(f'User {user.id} logged to Postgres successfully.')
    except Exception as e:
        print(f'Error logging user to Postgres: {e}')
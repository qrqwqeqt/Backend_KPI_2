import psycopg2

conn = psycopg2.connect(
    dbname="KPILAB3",
    user="postgres",
    password="aika1711",
    host="localhost"
)
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """)
conn.close()
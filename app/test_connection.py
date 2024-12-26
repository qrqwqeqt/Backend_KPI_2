import psycopg2

# Данные для подключения
connection = None
try:
    connection = psycopg2.connect(
        host="localhost",          # Ваш хост
        port="5432",               # Ваш порт
        database="postgres",       # Имя базы данных
        user="postgres",           # Имя пользователя
        password="aika1711"      # Пароль
    )
    print("Успешное подключение к базе данных!")
except Exception as e:
    print(f"Ошибка подключения: {e}")
finally:
    if connection:
        connection.close()
        print("Соединение закрыто.")

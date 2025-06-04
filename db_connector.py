from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import os

# Загрузка переменных окружения
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                auth_plugin='mysql_native_password'
            )
            print("Успешное подключение к базе данных!")
        except Error as e:
            print(f"Ошибка подключения к MySQL: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=False):
        """Выполнение SQL запроса"""
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result
            
            self.connection.commit()
            return True
            
        except Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        """Закрытие соединения"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Соединение с базой данных закрыто")

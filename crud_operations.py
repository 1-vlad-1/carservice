import mysql
from tabulate import tabulate
from db_connector import DatabaseManager

# CRUD операции для клиентов
class clientCRUD:
    def add_client(self, name, phone, email=None, address=None):
        query = """
        INSERT INTO clients (name, phone, email, address)
        VALUES (%s, %s, %s, %s)
        """
        return self.db.execute_query(query, (name, phone, email, address))
    
    def get_clients(self):
        query = "SELECT * FROM clients"
        return self.db.execute_query(query, fetch=True)
    
    def update_client(self, client_id, **kwargs):
        if not kwargs:
            return False
            
        query = "UPDATE clients SET "
        params = []
        updates = []
        
        for field, value in kwargs.items():
            updates.append(f"{field} = %s")
            params.append(value)
        
        query += ", ".join(updates) + " WHERE client_id = %s"
        params.append(client_id)
        
        return self.db.execute_query(query, params)
    
    def delete_client(self, client_id):
        query = "DELETE FROM clients WHERE client_id = %s"
        return self.db.execute_query(query, (client_id,))
    
# CRUD операции для заказов---------------------------------------------------------------------------------
class OrderCRUD:
    def __init__(self):
        self.db = DatabaseManager()

    def create_order(self, client_id, car_id, status='new'):
        """
        Создание нового заказа с валидацией
        :param client_id: ID клиента (int)
        :param car_id: ID автомобиля (int)
        :param status: Статус заказа (str)
        :return: ID нового заказа или None при ошибке
        """
        cursor = None
        try:
            # Валидация входных данных
            if not isinstance(client_id, int) or not isinstance(car_id, int):
                raise ValueError("ID клиента и автомобиля должны быть числами")

            if not self._validate_client_and_car(client_id, car_id):
                return None

            # Создание заказа
            query = """
            INSERT INTO orders (client_id, car_id, status)
            VALUES (%s, %s, %s)
            """
            cursor = self.db.connection.cursor()
            cursor.execute(query, (client_id, car_id, status))
            self.db.connection.commit()
            return cursor.lastrowid

        except mysql.connector.Error as e:
            print(f"Ошибка базы данных: {e}")
            self.db.connection.rollback()
            return None
        except Exception as e:
            print(f"Ошибка при создании заказа: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def read_order(self, order_id):
        """
        Получение информации о заказе с JOIN-данными
        :param order_id: ID заказа
        :return: Словарь с данными заказа или None если не найден
        """
        try:
            query = """
            SELECT o.order_id, o.creation_date, o.status, o.total_cost,
                   c.client_id, c.name as client_name, c.phone as client_phone,
                   car.car_id, car.brand, car.model, car.license_plate
            FROM orders o
            JOIN clients c ON o.client_id = c.client_id
            JOIN cars car ON o.car_id = car.car_id
            WHERE o.order_id = %s
            """
            result = self.db.execute_query(query, (order_id,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка при чтении заказа: {e}")
            return None

    def read_all_orders(self):
        """
        Получение списка всех заказов с JOIN-данными
        :return: Список словарей с заказами
        """
        try:
            query = """
            SELECT o.order_id, o.creation_date, o.status,
                   c.name as client_name, car.brand, car.model
            FROM orders o
            JOIN clients c ON o.client_id = c.client_id
            JOIN cars car ON o.car_id = car.car_id
            ORDER BY o.creation_date DESC
            """
            return self.db.execute_query(query, fetch=True)
        except Exception as e:
            print(f"Ошибка при получении списка заказов: {e}")
            return []

    def update_order_status(self, order_id, new_status):
        """
        Обновление статуса заказа
        :param order_id: ID заказа
        :param new_status: Новый статус
        :return: True при успехе, False при ошибке
        """
        valid_statuses = ['new', 'in_progress', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            print(f"Недопустимый статус. Допустимые значения: {', '.join(valid_statuses)}")
            return False

        try:
            query = """
            UPDATE orders 
            SET status = %s 
            WHERE order_id = %s
            """
            return self.db.execute_query(query, (new_status, order_id))
        except Exception as e:
            print(f"Ошибка при обновлении статуса заказа: {e}")
            return False

    def delete_order(self, order_id):
        """
        Безопасное удаление заказа с проверкой существования
        :param order_id: ID заказа для удаления
        :return: True если удаление успешно, False при ошибке
        """
        cursor = None
        try:
            # 1. Проверяем существование заказа
            check_query = "SELECT 1 FROM orders WHERE order_id = %s"
            cursor = self.db.connection.cursor()
            cursor.execute(check_query, (order_id,))
            if not cursor.fetchone():
                print(f"Ошибка: Заказ с ID {order_id} не найден")
                return False

            # 2. Удаляем связанные работы (если нужно каскадное удаление)
            # delete_works_query = "DELETE FROM works WHERE order_id = %s"
            # cursor.execute(delete_works_query, (order_id,))

            # 3. Удаляем сам заказ
            delete_query = "DELETE FROM orders WHERE order_id = %s"
            cursor.execute(delete_query, (order_id,))
            self.db.connection.commit()
            
            print(f"Заказ {order_id} успешно удален")
            return True

        except mysql.connector.Error as err:
            print(f"Ошибка базы данных: {err}")
            self.db.connection.rollback()
            return False
        except Exception as e:
            print(f"Неожиданная ошибка при удалении: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_orders_by_client(self, client_id):
        """
        Получение всех заказов клиента
        :param client_id: ID клиента
        :return: Список заказов клиента
        """
        try:
            query = """
            SELECT o.order_id, o.creation_date, o.status,
                   car.brand, car.model, car.license_plate
            FROM orders o
            JOIN cars car ON o.car_id = car.car_id
            WHERE o.client_id = %s
            ORDER BY o.creation_date DESC
            """
            return self.db.execute_query(query, (client_id,), fetch=True)
        except Exception as e:
            print(f"Ошибка при получении заказов клиента: {e}")
            return []

    def _validate_client_and_car(self, client_id, car_id):
        """Приватный метод валидации"""
        try:
            # Проверка клиента
            client_check = self.db.execute_query(
                "SELECT 1 FROM clients WHERE client_id = %s",
                (client_id,),
                fetch=True
            )
            if not client_check:
                print("Ошибка: Клиент не существует")
                return False

            # Проверка автомобиля и его принадлежности клиенту
            car_check = self.db.execute_query(
                "SELECT 1 FROM cars WHERE car_id = %s AND client_id = %s",
                (car_id, client_id),
                fetch=True
            )
            if not car_check:
                print("Ошибка: Автомобиль не существует или не принадлежит клиенту")
                return False

            return True
        except Exception as e:
            print(f"Ошибка валидации: {e}")
            return False

    def display_orders_table(self, orders):
        """
        Красивый вывод таблицы заказов
        :param orders: Список заказов
        """
        if not orders:
            print("Нет данных для отображения")
            return

        # Форматируем дату для лучшего отображения
        formatted_orders = []
        for order in orders:
            formatted_order = order.copy()
            if 'creation_date' in formatted_order:
                formatted_order['creation_date'] = formatted_order['creation_date'].strftime('%Y-%m-%d %H:%M')
            formatted_orders.append(formatted_order)

        print(tabulate(formatted_orders, headers="keys", tablefmt="grid"))




    # def add_order(self, client_id, car_id, status='new'):
    #     query = """
    #     INSERT INTO orders (client_id, car_id, status)
    #     VALUES (%s, %s, %s)
    #     """
    #     return self.db.execute_query(query, (client_id, car_id, status))
    
    # def get_orders_with_details(self):
    #     query = """
    #     SELECT o.order_id, o.creation_date, o.status, 
    #            c.name as client_name, c.phone as client_phone,
    #            car.brand, car.model, car.license_plate
    #     FROM orders o
    #     JOIN clients c ON o.client_id = c.client_id
    #     JOIN cars car ON o.car_id = car.car_id
    #     """
    #     return self.db.execute_query(query, fetch=True)
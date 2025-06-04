from tabulate import tabulate
from db_connector import DatabaseManager
from analytics import analytical_requests
from crud_operations import clientCRUD 
from crud_operations import OrderCRUD

class AutoServiceApp:
    def __init__(self):
        self.db = DatabaseManager()
        self.order_crud = OrderCRUD()
    
    def display_menu(self):
        """Отображение главного меню с новыми пунктами"""
        while True:
            print("\n=== Автосервис - Управление ===")
            print("1. Управление клиентами")
            print("2. Управление заказами")
            print("3. Аналитические запросы")
            print("0. Выход")
            
            choice = input("Выберите раздел: ")
            
            if choice == "1":
                self.client_management_menu()
            elif choice == "2":
                self.order_management_menu()
            elif choice == "3":
                self.analytics_menu()
            elif choice == "0":
                print("Выход из программы...")
                self.db.close()
                break
            else:
                print("Неверный ввод, попробуйте снова")

    def client_management_menu(self):
        """Подменю управления клиентами"""
        while True:
            print("\n--- Управление клиентами ---")
            print("1. Добавить клиента")
            print("2. Просмотреть всех клиентов")
            print("3. Обновить данные клиента")
            print("4. Удалить клиента")
            print("0. Назад")
            
            choice = input("Выберите действие: ")
            
            if choice == "1":
                self.add_client_menu()
            elif choice == "2":
                self.show_clients()
            elif choice == "3":
                self.update_client_menu()
            elif choice == "4":
                self.delete_client_menu()
            elif choice == "0":
                break
            else:
                print("Неверный ввод, попробуйте снова")

    def order_management_menu(self):
        """Подменю управления заказами"""
        while True:
            print("\n--- Управление заказами ---")
            print("1. Создать новый заказ")
            print("2. Просмотреть все заказы")
            print("3. Просмотреть детали заказа")
            print("4. Изменить статус заказа")
            print("5. Удалить заказ")
            print("0. Назад")
            
            choice = input("Выберите действие: ")
            
            if choice == "1":
                self.add_order_menu()
            elif choice == "2":
                self.show_orders()
            elif choice == "3":
                self.show_order_details()
            elif choice == "4":
                self.update_order_menu()
            elif choice == "5":
                self.delete_order_menu()
            elif choice == "0":
                break
            else:
                print("Неверный ввод, попробуйте снова")
    def analytics_menu(self):
        """Подменю управления аналитическими запросами"""
        while True:
            print("\n--- Аналитические запросы ---")
            print("1. Посмотреть заказы за период")
            print("2. Просмотреть статистику о сотруднике")
            print("0. Назад")
            
            choice = input("Выберите действие: ")
            
            if choice == "1":
                self.orders_by_period_menu()
            elif choice == "2":
                self.employee_stats_menu()
            elif choice == "0":
                break
            else:
                print("Неверный ввод, попробуйте снова")
    
    # МЕТОДЫ МЕНЮ ДЛЯ КИЕНТОВ-----------------------------------------------------------------------------------
    def add_client_menu(self):
        print("\nДобавление нового клиента")
        name = input("ФИО: ")
        phone = input("Телефон: ")
        email = input("Email (необязательно): ") or None
        address = input("Адрес (необязательно): ") or None
        
        if clientCRUD.add_client(self,name, phone, email, address):
            print("Клиент успешно добавлен!")
        else:
            print("Ошибка при добавлении клиента")
    
    def show_clients(self):
        clients = clientCRUD.get_clients(self)
        if clients:
            print("\nСписок клиентов:")
            print(tabulate(clients, headers="keys", tablefmt="grid"))
        else:
            print("Нет данных о клиентах")
    
    def update_client_menu(self):
        self.show_clients()
        client_id = input("Введите ID клиента для обновления: ")
        
        print("Введите новые данные (оставьте пустым, чтобы не изменять):")
        name = input("ФИО: ") or None
        phone = input("Телефон: ") or None
        email = input("Email: ") or None
        address = input("Адрес: ") or None
        
        updates = {}
        if name: updates['name'] = name
        if phone: updates['phone'] = phone
        if email: updates['email'] = email
        if address: updates['address'] = address
        
        if updates and clientCRUD.update_client(self, client_id, **updates):
            print("Данные клиента обновлены!")
        else:
            print("Ошибка при обновлении или не введены новые данные")
    
    def delete_client_menu(self):
        self.show_clients()
        client_id = input("Введите ID клиента для удаления: ")
        
        if clientCRUD.delete_client(self, client_id):
            print("Клиент удален!")
        else:
            print("Ошибка при удалении клиента")

    #МЕТОДЫ МЕНЮ ДЛЯ ЗАКАЗОВ----------------------------------------------------------------------------------------
    def add_order_menu(self):
        """Меню добавления нового заказа"""
        print("\nДобавление нового заказа")
        
        # Показываем список клиентов для выбора
        clients = self.db.execute_query("SELECT client_id, name FROM clients", fetch=True)
        print("\nСписок клиентов:")
        print(tabulate(clients, headers="keys", tablefmt="grid"))
        client_id = int(input("Введите ID клиента: "))
        
        # Показываем список автомобилей клиента
        cars = self.db.execute_query(
            "SELECT car_id, brand, model, license_plate FROM cars WHERE client_id = %s",
            (client_id,),
            fetch=True
        )
        if not cars:
            print("У клиента нет зарегистрированных автомобилей!")
            return
            
        print("\nАвтомобили клиента:")
        print(tabulate(cars, headers="keys", tablefmt="grid"))
        car_id = int(input("Введите ID автомобиля: "))
        
        # Выбор статуса заказа
        status = input("Статус заказа (new/in_progress/completed) [new]: ") or "new"
        
        new_order_id = self.order_crud.create_order(client_id, car_id, status)

        if new_order_id:
            print(f"Заказ успешно создан! ID: {new_order_id}")
        else:
            print("Ошибка при создании заказа")

    def show_orders(self):
        """Отображение списка всех заказов с детализацией"""
        try:
            # Создаем экземпляр OrderCRUD для работы с заказами
            order_crud = OrderCRUD()
            
            # Получаем все заказы с JOIN-данными
            orders = order_crud.read_all_orders()
            
            if not orders:
                print("\nНет доступных заказов")
                return
            
            print("\nСписок всех заказов:")
            
            # Форматируем данные для лучшего отображения
            formatted_orders = []
            for order in orders:
                formatted_order = {
                    'ID': order['order_id'],
                    'Дата создания': order['creation_date'].strftime('%Y-%m-%d %H:%M'),
                    'Статус': self._translate_status(order['status']),
                    'Клиент': order['client_name'],
                    'Автомобиль': f"{order['brand']} {order['model']}"
                }
                formatted_orders.append(formatted_order)
            
            # Выводим красиво оформленную таблицу
            print(tabulate(formatted_orders, headers="keys", tablefmt="grid"))
            
            # Дополнительная статистика
            self._show_orders_stats(orders)
            
        except Exception as e:
            print(f"\nОшибка при получении списка заказов: {e}")

    def _translate_status(self, status):
        """Перевод статусов на русский язык"""
        status_map = {
            'new': 'Новый',
            'in_progress': 'В работе',
            'completed': 'Завершен',
            'cancelled': 'Отменен'
        }
        return status_map.get(status, status)

    def _show_orders_stats(self, orders):
        """Вывод статистики по заказам"""
        stats = {
            'Всего заказов': len(orders),
            'Новых': sum(1 for o in orders if o['status'] == 'new'),
            'В работе': sum(1 for o in orders if o['status'] == 'in_progress'),
            'Завершенных': sum(1 for o in orders if o['status'] == 'completed')
        }
        
        print("\nСтатистика по заказам:")
        print(tabulate(stats.items(), headers=['Тип', 'Количество'], tablefmt="grid"))

    def update_order_menu(self):
        """Меню обновления заказа"""
        orders = OrderCRUD.read_all_orders(self)
        if not orders:
            print("Нет доступных заказов")
            return
        
        print("\nСписок заказов:")
        print(tabulate(orders, headers="keys", tablefmt="grid"))
        order_id = input("Введите ID заказа для обновления: ")
        
        # Получаем текущий статус
        current_status = self.db.execute_query(
            "SELECT status FROM orders WHERE order_id = %s",
            (order_id,),
            fetch=True
        )
        if not current_status:
            print("Заказ не найден!")
            return
        
        print(f"\nТекущий статус: {current_status[0]['status']}")
        print("Доступные статусы: new, in_progress, completed, cancelled")
        new_status = input("Новый статус: ")
        
        if OrderCRUD.update_order_status(self, order_id, new_status):
            print("Статус заказа обновлен!")
        else:
            print("Ошибка при обновлении заказа")

    def delete_order_menu(self):
        """Меню удаления заказа"""
        try:
            # Получаем список заказов для отображения
            orders = self.order_crud.read_all_orders()
            if not orders:
                print("Нет доступных заказов для удаления")
                return

            print("\nСписок заказов:")
            self.order_crud.display_orders_table(orders)

            # Запрос ID заказа для удаления
            order_id = int(input("\nВведите ID заказа для удаления: "))
            
            # Подтверждение
            confirm = input(f"Вы уверены, что хотите удалить заказ {order_id}? (y/n): ")
            if confirm.lower() != 'y':
                print("Удаление отменено")
                return

            # Вызов метода удаления
            if self.order_crud.delete_order(order_id):
                print("Заказ успешно удален")
            else:
                print("Не удалось удалить заказ")

        except ValueError:
            print("Ошибка: ID заказа должен быть числом")
        except Exception as e:
            print(f"Ошибка при удалении заказа: {e}")

    def show_order_details(self):
        """Просмотр деталей конкретного заказа"""
        orders = OrderCRUD.read_all_orders(self)
        if not orders:
            print("Нет доступных заказов")
            return
        
        print("\nСписок заказов:")
        print(tabulate(orders, headers="keys", tablefmt="grid"))
        order_id = input("Введите ID заказа для просмотра деталей: ")
        
        # Получаем полную информацию о заказе
        order_info = self.db.execute_query("""
            SELECT o.order_id, o.creation_date, o.status, o.total_cost,
                c.name as client_name, c.phone as client_phone,
                car.brand, car.model, car.year, car.license_plate
            FROM orders o
            JOIN clients c ON o.client_id = c.client_id
            JOIN cars car ON o.car_id = car.car_id
            WHERE o.order_id = %s
        """, (order_id,), fetch=True)
        
        if not order_info:
            print("Заказ не найден!")
            return
        
        print("\nДетали заказа:")
        print(tabulate(order_info, headers="keys", tablefmt="grid"))
        
        # Показываем связанные работы
        works = self.db.execute_query("""
            SELECT w.work_id, s.name as service, e.name as employee,
                w.start_date, w.end_date, w.status
            FROM works w
            JOIN services s ON w.service_id = s.service_id
            JOIN employees e ON w.employee_id = e.employee_id
            WHERE w.order_id = %s
        """, (order_id,), fetch=True)
        
        if works:
            print("\nРаботы по заказу:")
            print(tabulate(works, headers="keys", tablefmt="grid"))
        else:
            print("По этому заказу нет работ")

    #аналитические запросы
    def orders_by_period_menu(self):
        print("\nАналитика: заказы за период")
        start_date = input("Начальная дата (ГГГГ-ММ-ДД): ")
        end_date = input("Конечная дата (ГГГГ-ММ-ДД): ")
        
        orders = analytical_requests.get_orders_by_period(self,start_date, end_date)
        if orders:
            print(f"\nЗаказы с {start_date} по {end_date}:")
            print(tabulate(orders, headers="keys", tablefmt="grid"))
        else:
            print("Нет заказов за указанный период")
    
    def employee_stats_menu(self):
        print("\nАналитика: статистика по сотруднику")
        employee_id = input("Введите ID сотрудника: ")
        
        stats = analytical_requests.get_employee_stats(self,employee_id)
        if stats:
            print("\nСтатистика по сотруднику:")
            print(tabulate(stats, headers="keys", tablefmt="grid"))
        else:
            print("Нет данных по указанному сотруднику")

if __name__ == "__main__":
    try:
        app = AutoServiceApp()
        app.display_menu()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        if 'app' in locals():
            app.db.close()
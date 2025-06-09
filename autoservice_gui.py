import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                             QLineEdit, QComboBox, QDateEdit, QMessageBox, QLabel, QDialogButtonBox, QToolBar)
from PyQt6.QtCore import Qt, QDate
from db_connector import DatabaseManager
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseManagerGUI:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_clients(self):
        return self.db.execute_query("SELECT * FROM clients", fetch=True)
    
    def add_client(self, name, phone, email=None, address=None):
        query = "INSERT INTO clients (name, phone, email, address) VALUES (%s, %s, %s, %s)"
        return self.db.execute_query(query, (name, phone, email, address))
    
    def add_car(self, client_id, brand, model, license_plate, year=None):
        """Добавление автомобиля для клиента"""
        query = """
        INSERT INTO cars (client_id, brand, model, license_plate, year)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (client_id, brand, model, license_plate, year))
    
    def get_orders_with_details(self):
        query = """
        SELECT o.order_id, o.creation_date, o.status, 
               c.name as client_name, car.brand, car.model
        FROM orders o
        JOIN clients c ON o.client_id = c.client_id
        JOIN cars car ON o.car_id = car.car_id
        """
        return self.db.execute_query(query, fetch=True)
    
    def get_orders_by_date(self, start_date, end_date):
        query = """
        SELECT o.order_id, o.creation_date, o.status,
               c.name as client_name, car.brand
        FROM orders o
        JOIN clients c ON o.client_id = c.client_id
        JOIN cars car ON o.car_id = car.car_id
        WHERE o.creation_date BETWEEN %s AND %s
        """
        return self.db.execute_query(query, (start_date, end_date), fetch=True)
    
    def delete_client(self, client_id):
        query = "DELETE FROM clients WHERE client_id = %s"
        return self.db.execute_query(query, (client_id,))
    
    def delete_order(self, order_id):
        query = "DELETE FROM orders WHERE order_id = %s"
        return self.db.execute_query(query, (order_id,))
    
    def add_order(self, client_id, car_id, status='new'):
        """Добавление нового заказа в БД"""
        query = """
        INSERT INTO orders (client_id, car_id, status)
        VALUES (%s, %s, %s)
        """
        return self.db.execute_query(query, (client_id, car_id, status))
    
    def get_client_cars(self, client_id):
        """Получение автомобилей клиента"""
        query = """
        SELECT car_id, brand, model, license_plate 
        FROM cars 
        WHERE client_id = %s
        """
        return self.db.execute_query(query, (client_id,), fetch=True)

#класс MainWindow -------------------------------------------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManagerGUI()
        self.setWindowTitle("Автосервис - Управление")
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем панель инструментов
        self.toolbar = QToolBar("Панель инструментов")
        self.addToolBar(self.toolbar)
        
        # Кнопки добавления
        self.btn_add_client = QPushButton("Добавить клиента")
        self.btn_add_client.clicked.connect(self.add_client_dialog)
        self.toolbar.addWidget(self.btn_add_client)
        
        self.btn_add_order = QPushButton("Добавить заказ")
        self.btn_add_order.clicked.connect(self.add_order_dialog)
        self.toolbar.addWidget(self.btn_add_order)
        
        # Основная таблица
        self.table = QTableWidget()
        self.setCentralWidget(self.table)
        
        # Главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        self.btn_clients = QPushButton("Клиенты")
        self.btn_clients.clicked.connect(self.show_clients)
        btn_layout.addWidget(self.btn_clients)
        
        self.btn_orders = QPushButton("Заказы")
        self.btn_orders.clicked.connect(self.show_orders)
        btn_layout.addWidget(self.btn_orders)
        
        self.btn_analytics = QPushButton("Аналитика")
        self.btn_analytics.clicked.connect(self.show_analytics)
        btn_layout.addWidget(self.btn_analytics)
        
        layout.addLayout(btn_layout)
        
        # Таблица для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(0)
        layout.addWidget(self.table)
        
        # Статус бар
        self.statusBar().showMessage("Готово")

    def clear_table(self):
        """Очищает таблицу и сбрасывает заголовки"""
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def show_clients(self):
        self.clear_table()  # Очищаем перед загрузкой новых данных
        clients = self.db.get_clients()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон", "Email", "Действия"])
        self.table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            self.table.setItem(row, 0, QTableWidgetItem(str(client["client_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(client["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(client["phone"]))
            self.table.setItem(row, 3, QTableWidgetItem(client["email"] or ""))
            
            btn_delete = QPushButton("Удалить")
            btn_delete.clicked.connect(lambda _, id=client["client_id"]: self.delete_client(id))
            self.table.setCellWidget(row, 4, btn_delete)

    def delete_client(self, client_id):
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            f'Вы уверены, что хотите удалить клиента с ID {client_id}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_client(client_id):
                QMessageBox.information(self, "Успех", "Клиент удален!")
                self.show_clients()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить клиента")

    def show_orders(self):
        self.clear_table()  # Очищаем перед загрузкой новых данных
        orders = self.db.get_orders_with_details()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Дата", "Статус", "Клиент", "Автомобиль", "Действия"])
        self.table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            self.table.setItem(row, 0, QTableWidgetItem(str(order["order_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(order["creation_date"])))
            self.table.setItem(row, 2, QTableWidgetItem(order["status"]))
            self.table.setItem(row, 3, QTableWidgetItem(order["client_name"]))
            self.table.setItem(row, 4, QTableWidgetItem(f"{order['brand']} {order['model']}"))
            
            btn_delete = QPushButton("Удалить")
            btn_delete.clicked.connect(lambda _, id=order["order_id"]: self.delete_order(id))
            self.table.setCellWidget(row, 5, btn_delete)
    
    def delete_order(self, order_id):
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            f'Вы уверены, что хотите удалить заказ с ID {order_id}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_order(order_id):
                QMessageBox.information(self, "Успех", "Заказ удален!")
                self.show_orders()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить заказ")
    
    def add_client_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить клиента")
        dialog.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # Поля клиента
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        
        layout.addRow("ФИО:", self.name_input)
        layout.addRow("Телефон:", self.phone_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Адрес:", self.address_input)

        # Разделитель
        layout.addRow(QLabel("<b>Данные автомобиля</b>"))

        # Поля автомобиля
        self.car_brand_input = QLineEdit()
        self.car_model_input = QLineEdit()
        self.car_license_input = QLineEdit()
        self.car_year_input = QLineEdit()
        
        layout.addRow("Марка:", self.car_brand_input)
        layout.addRow("Модель:", self.car_model_input)
        layout.addRow("Гос. номер:", self.car_license_input)
        layout.addRow("Год выпуска:", self.car_year_input)
        
        #Кнопки
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(lambda: self.save_client(dialog))
        btn_box.rejected.connect(dialog.reject)
        layout.addRow(btn_box)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def save_client(self, dialog):
         # Получаем данные клиента
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text() or None
        address = self.address_input.text() or None

         # Получаем данные автомобиля
        brand = self.car_brand_input.text()
        model = self.car_model_input.text()
        license_plate = self.car_license_input.text()
        year = self.car_year_input.text()
        year = int(year) if year.isdigit() else None
        
        # Проверка обязательных полей
        if not name or not phone:
            QMessageBox.warning(self, "Ошибка", "ФИО и телефон обязательны!")
            return
            
        if not brand or not model or not license_plate:
            QMessageBox.warning(self, "Ошибка", "Марка, модель и гос. номер автомобиля обязательны!")
            return

       # Добавляем клиента
        if self.db.add_client(name, phone, email, address):
            # Получаем ID последнего добавленного клиента
            clients = self.db.get_clients()
            last_client = clients[-1] if clients else None
            
            if last_client:
                client_id = last_client["client_id"]
                # Добавляем автомобиль
                if self.db.add_car(client_id, brand, model, license_plate, year):
                    QMessageBox.information(self, "Успех", "Клиент и автомобиль добавлены!")
                    dialog.close()
                    self.show_clients()
                else:
                    QMessageBox.critical(self, "Ошибка", "Клиент добавлен, но не удалось добавить автомобиль")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось получить ID нового клиента")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить клиента")
            
    def add_order_dialog(self):
        """Диалоговое окно для добавления нового заказа"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить заказ")
        dialog.setMinimumWidth(400)
        
        layout = QFormLayout(dialog)
        
        # Выбор клиента
        self.client_combo = QComboBox()
        self.load_clients_to_combo()
        layout.addRow("Клиент:", self.client_combo)
        
        # Выбор автомобиля
        self.car_combo = QComboBox()
        layout.addRow("Автомобиль:", self.car_combo)
        
        # Статус заказа
        self.status_combo = QComboBox()
        self.status_combo.addItems(["new", "in_progress", "completed"])
        layout.addRow("Статус:", self.status_combo)
        
        # Кнопки
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(lambda: self.save_order(dialog))
        btn_box.rejected.connect(dialog.reject)
        layout.addRow(btn_box)
        
        # Обновляем список автомобилей при выборе клиента
        self.client_combo.currentIndexChanged.connect(self.update_car_combo)
        
        dialog.exec()
    
    def load_clients_to_combo(self):
        """Загрузка клиентов в выпадающий список"""
        clients = self.db.get_clients()
        self.client_combo.clear()
        for client in clients:
            self.client_combo.addItem(
                f"{client['name']} ({client['phone']})", 
                client['client_id']
            )
    
    def update_car_combo(self):
        """Обновление списка автомобилей при выборе клиента"""
        client_id = self.client_combo.currentData()
        if not client_id:
            return
            
        self.car_combo.clear()
        cars = self.db.get_client_cars(client_id)
        for car in cars:
            self.car_combo.addItem(
                f"{car['brand']} {car['model']} ({car['license_plate']})", 
                car['car_id']
            )
    
    def save_order(self, dialog):
        """Сохранение нового заказа"""
        client_id = self.client_combo.currentData()
        car_id = self.car_combo.currentData()
        status = self.status_combo.currentText()
        
        if not client_id or not car_id:
            QMessageBox.warning(self, "Ошибка", "Необходимо выбрать клиента и автомобиль!")
            return
            
        if self.db.add_order(client_id, car_id, status):
            QMessageBox.information(self, "Успех", "Заказ успешно добавлен!")
            dialog.accept()
            self.show_orders()  # Обновляем список заказов
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить заказ")

    def show_analytics(self):
        self.clear_table()  # Очищаем перед загрузкой новых данных
        dialog = QDialog(self)
        dialog.setWindowTitle("Аналитика заказов")
        
        layout = QVBoxLayout()
        
        # Выбор дат
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("С:"))
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("По:"))
        self.end_date = QDateEdit(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        
        layout.addLayout(date_layout)
        
        # Кнопка запроса
        btn_query = QPushButton("Получить отчет")
        btn_query.clicked.connect(self.show_orders_report)
        layout.addWidget(btn_query)
        
        # Таблица результатов
        self.report_table = QTableWidget()
        layout.addWidget(self.report_table)
        
        dialog.setLayout(layout)
        dialog.resize(600, 400)
        dialog.exec()
    
    def show_orders_report(self):
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        orders = self.db.get_orders_by_date(start_date, end_date)
        
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(["ID", "Дата", "Клиент", "Автомобиль"])
        self.report_table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            self.report_table.setItem(row, 0, QTableWidgetItem(str(order["order_id"])))
            self.report_table.setItem(row, 1, QTableWidgetItem(str(order["creation_date"])))
            self.report_table.setItem(row, 2, QTableWidgetItem(order["client_name"]))
            self.report_table.setItem(row, 3, QTableWidgetItem(order["brand"]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
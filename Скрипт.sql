-- Создание базы данных
CREATE DATABASE IF NOT EXISTS autoservice;
USE autoservice;

CREATE TABLE positions (
    position_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(50) NOT NULL UNIQUE,
    salary DECIMAL(10,2) NOT NULL,
    responsibilities TEXT
);

CREATE TABLE warehouses (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    address VARCHAR(200) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

CREATE TABLE clients (
    client_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(50) UNIQUE,
    address VARCHAR(200)
);

CREATE TABLE services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    warranty_days INT
);

CREATE TABLE parts (
    part_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    warehouse_id INT,
    quantity INT NOT NULL DEFAULT 0,
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    hire_date DATE NOT NULL,
    position_id INT,
    FOREIGN KEY (position_id) REFERENCES positions(position_id)
);

CREATE TABLE cars (
    car_id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT,
    license_plate VARCHAR(15) UNIQUE,
    vin VARCHAR(17) UNIQUE,
    client_id INT,
    FOREIGN KEY (client_id) REFERENCES Client(client_id)
);

CREATE TABLE `orders` (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    client_id INT,
    car_id INT,
    status ENUM('new','in_progress','completed','cancelled') DEFAULT 'new',
    total_cost DECIMAL(10,2),
    FOREIGN KEY (client_id) REFERENCES Client(client_id),
    FOREIGN KEY (car_id) REFERENCES Car(car_id)
);

CREATE TABLE works (
    work_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    service_id INT,
    employee_id INT,
    start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_date DATETIME,
    status ENUM('planned','in_progress','completed','cancelled'),
    notes TEXT,
    FOREIGN KEY (order_id) REFERENCES `Order`(order_id),
    FOREIGN KEY (service_id) REFERENCES Service(service_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    amount DECIMAL(10,2) NOT NULL,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    method ENUM('cash','card','transfer') NOT NULL,
    status ENUM('pending','paid','cancelled') DEFAULT 'pending',
    FOREIGN KEY (order_id) REFERENCES `Order`(order_id)
);

CREATE TABLE workparts (
    work_id INT,
    part_id INT,
    quantity INT NOT NULL DEFAULT 1,
    price_at_usage DECIMAL(10,2),
    PRIMARY KEY (work_id, part_id),
    FOREIGN KEY (work_id) REFERENCES Work(work_id),
    FOREIGN KEY (part_id) REFERENCES Part(part_id)
);


# Заполнение таблицы positions (Должности)
INSERT INTO positions (title, salary, responsibilities) VALUES
('Senior Mechanic', 65000, 'Complex engine repairs, team leadership'),
('Auto Electrician', 48000, 'Diagnostics and repair of electrical systems'),
('Service Manager', 70000, 'Customer service, workflow organization'),
('Tire Technician', 42000, 'Wheel replacement, balancing, alignment'),
('Painter', 58000, 'Bodywork painting and polishing'),
('Diagnostic Specialist', 55000, 'Computer diagnostics of all systems'),
('AC Technician', 45000, 'Air conditioning maintenance and repair'),
('Junior Mechanic', 40000, 'Assisting senior mechanics, basic repairs'),
('Detailer', 38000, 'Interior and exterior cleaning, polishing'),
('Parts Manager', 50000, 'Warehouse management, parts ordering');

# Заполнение таблицы warehouses (Склады)
INSERT INTO warehouses (name, address, phone) VALUES
('Central Warehouse', '123 Industrial Ave, Moscow', '+79161234567'),
('North Storage', '456 Parts St, Moscow', '+79162345678'),
('East Warehouse', '789 Components Blvd, Moscow', '+79163456789'),
('South Storage', '321 Spare Parts Rd, Moscow', '+79164567890'),
('West Warehouse', '654 Auto Parts Ln, Moscow', '+79165678901'),
('Main Distribution', '987 Supply Chain Way, Moscow', '+79166789012'),
('Express Parts', '159 Quick Delivery St, Moscow', '+79167890123'),
('Metro Storage', '753 Underground Ave, Moscow', '+79168901234'),
('City Warehouse', '951 Urban Center Rd, Moscow', '+79169012345'),
('Premium Parts', '357 High Quality Blvd, Moscow', '+79160123456');

#Заполнение таблицы clients (Клиенты)
INSERT INTO clients (name, phone, email, address) VALUES
('Иван Петров', '+79161112233', 'ivan.p@mail.com', 'ул. Ленина, 10, кв.5, Москва'),
('Мария Сидорова', '+79162223344', 'maria.s@mail.com', 'пр. Мира, 25, Москва'),
('Алексей Смирнов', '+79163334455', 'alex.s@mail.com', 'ул. Горького, 15-12, Москва'),
('Елена Волкова', '+79164445566', 'elena.v@gmail.com', 'ул. Пушкина, 7, Москва'),
('Дмитрий Федоров', '+79165556677', 'dmitry.f@yandex.ru', 'ул. Советская, 33-4, Москва'),
('Ольга Иванова', '+79166667788', 'olga.i@mail.com', 'ул. Кирова, 19, Москва'),
('Сергей Кузнецов', '+79167778899', 'sergey.k@mail.com', 'ул. Лесная, 8-3, Москва'),
('Анна Павлова', '+79168889900', 'anna.p@gmail.com', 'ул. Садовая, 12, Москва'),
('Павел Воронин', '+79169990011', 'pavel.v@yandex.ru', 'ул. Зеленая, 45-1, Москва'),
('Татьяна Морозова', '+79161001012', 'tatiana.m@mail.com', 'ул. Центральная, 5, Москва');

# Заполнение таблицы employees (Сотрудники)
INSERT INTO employees (name, phone, hire_date, position_id) VALUES
('Александр Борисов', '+79171112233', '2020-05-15', 1),
('Екатерина Васнецова', '+79172223344', '2021-03-10', 3),
('Михаил Громов', '+79173334455', '2019-11-22', 2),
('Наталья Дмитриева', '+79174445566', '2022-01-30', 4),
('Олег Егоров', '+79175556677', '2020-07-18', 5),
('Полина Жукова', '+79176667788', '2021-09-05', 6),
('Роман Зайцев', '+79177778899', '2022-02-14', 7),
('Светлана Ильина', '+79178889900', '2018-12-03', 8),
('Тимур Козлов', '+79179990011', '2023-04-25', 9),
('Юлия Лебедева', '+79171001012', '2021-06-11', 10);

# Заполнение таблицы cars (Автомобили)
INSERT INTO cars (brand, model, year, license_plate, vin, client_id) VALUES
('Toyota', 'Camry', 2018, 'А123БВ777', 'XTA210990G7895123', 1),
('Kia', 'Rio', 2020, 'О765ТК177', 'Z94CB41BBER543210', 2),
('BMW', 'X5', 2019, 'У321КХ777', 'WBAJF5C58EVG54321', 3),
('Lada', 'Vesta', 2021, 'Р456МУ177', 'XTA210990G7895678', 4),
('Hyundai', 'Creta', 2022, 'Т789АВ777', 'Z94CB41BBER567890', 5),
('Volkswagen', 'Tiguan', 2020, 'Е321ТТ177', 'WVGZZZ5NZKW123456', 6),
('Skoda', 'Octavia', 2021, 'К654ОС777', 'TMBJF65L4D6123456', 7),
('Renault', 'Duster', 2019, 'Н987РУ177', 'VF1LJ0B0A45876543', 8),
('Mazda', 'CX-5', 2022, 'М159АК777', 'JMZGAR1AZ60123456', 9),
('Lexus', 'RX', 2020, 'В357ТМ177', 'JTJHF10U200765432', 10);

# Заполнение таблицы services (Услуги)
INSERT INTO services (name, description, price, warranty_days) VALUES
('Замена масла', 'Полная замена моторного масла и фильтра', 2500, 30),
('Диагностика', 'Компьютерная диагностика всех систем', 2000, 0),
('Ремонт тормозов', 'Замена колодок, дисков, прокачка системы', 4500, 90),
('Замена шин', 'Сезонная замена шин с балансировкой', 3000, 0),
('Ремонт двигателя', 'Капитальный ремонт двигателя', 20000, 180),
('Ремонт электроники', 'Диагностика и ремонт электронных систем', 5000, 60),
('Покраска кузова', 'Локальная или полная покраска кузова', 15000, 365),
('Ремонт подвески', 'Замена амортизаторов, сайлентблоков', 6000, 90),
('Обслуживание кондиционера', 'Заправка, замена фильтров', 3500, 30),
('Химчистка салона', 'Полная химчистка салона автомобиля', 5000, 0);
# Заполнение таблицы parts (Запчасти)
INSERT INTO parts (name, code, description, price, warehouse_id, quantity) VALUES
('Масло моторное 5W-40', 'OIL-001', 'Синтетическое, 4л', 3500, 1, 25),
('Тормозные колодки передние', 'BRK-101', 'Комплект для Kia Rio', 4500, 2, 12),
('Воздушный фильтр', 'FIL-201', 'Оригинальный фильтр', 1500, 3, 30),
('Аккумулятор 60Ah', 'BAT-301', 'Необслуживаемый', 8000, 4, 8),
('Лампа головного света', 'LMP-401', 'H7, 55W', 1200, 5, 40),
('Свечи зажигания', 'SPK-501', 'Иридиевые, комплект 4шт', 2500, 1, 20),
('Ремень ГРМ', 'BLT-601', 'С комплектом роликов', 5000, 2, 10),
('Амортизатор передний', 'SUS-701', 'Левый, оригинал', 6500, 3, 6),
('Щетки стеклоочистителя', 'WIP-801', 'Комплект передних щеток', 1800, 4, 35),
('Фильтр салона', 'FIL-901', 'Угольный, с антиаллергенным покрытием', 2000, 5, 28);

#Заполнение таблицы orders (Заказы)
INSERT INTO orders (creation_date, client_id, car_id, status, total_cost) VALUES
('2024-01-10 09:30:00', 1, 1, 'completed', 7500),
('2024-01-12 11:15:00', 2, 2, 'completed', 6500),
('2024-01-15 14:20:00', 3, 3, 'in_progress', NULL),
('2024-01-18 10:00:00', 4, 4, 'completed', 8500),
('2024-01-20 13:45:00', 5, 5, 'completed', 5000),
('2024-01-22 16:30:00', 6, 6, 'new', NULL),
('2024-01-25 09:15:00', 7, 7, 'completed', 12000),
('2024-01-28 11:00:00', 8, 8, 'in_progress', NULL),
('2024-02-01 14:45:00', 9, 9, 'completed', 9500),
('2024-02-05 10:30:00', 10, 10, 'new', NULL);

# Заполнение таблицы works (Работы)
INSERT INTO works (order_id, service_id, employee_id, start_date, end_date, status, notes) VALUES
(1, 1, 1, '2024-01-10 10:00:00', '2024-01-10 11:30:00', 'completed', 'Замена масла и фильтра'),
(1, 3, 2, '2024-01-10 11:45:00', '2024-01-10 13:30:00', 'completed', 'Замена передних тормозных колодок'),
(2, 2, 3, '2024-01-12 12:00:00', '2024-01-12 13:15:00', 'completed', 'Полная диагностика'),
(2, 4, 4, '2024-01-12 13:30:00', '2024-01-12 15:00:00', 'completed', 'Замена зимних шин на летние'),
(3, 5, 1, '2024-01-15 15:00:00', NULL, 'in_progress', 'Капитальный ремонт двигателя'),
(4, 6, 5, '2024-01-18 11:00:00', '2024-01-18 13:00:00', 'completed', 'Ремонт электрооборудования'),
(5, 7, 6, '2024-01-20 14:30:00', '2024-01-20 17:00:00', 'completed', 'Локальная покраска бампера'),
(6, 8, 7, '2024-01-22 17:00:00', NULL, 'planned', 'Замена амортизаторов'),
(7, 9, 8, '2024-01-25 10:00:00', '2024-01-25 11:30:00', 'completed', 'Заправка кондиционера'),
(8, 10, 9, '2024-01-28 12:00:00', NULL, 'in_progress', 'Химчистка салона');

#Заполнение таблицы payments (Платежи)
INSERT INTO payments (order_id, amount, date, method, status) VALUES
(1, 7500, '2024-01-10 13:45:00', 'card', 'paid'),
(2, 6500, '2024-01-12 15:30:00', 'cash', 'paid'),
(4, 8500, '2024-01-18 13:15:00', 'transfer', 'paid'),
(5, 5000, '2024-01-20 17:30:00', 'card', 'paid'),
(7, 12000, '2024-01-25 11:45:00', 'card', 'paid'),
(3, 5000, '2024-01-16 10:00:00', 'cash', 'pending'),
(8, 5000, '2024-01-29 09:00:00', 'transfer', 'pending'),
(9, 9500, '2024-02-01 15:30:00', 'card', 'paid'),
(10, 3000, '2024-02-05 11:00:00', 'cash', 'pending'),
(6, 4000, '2024-01-23 09:30:00', 'transfer', 'pending');

#Заполнение таблицы workparts (Использованные запчасти)
INSERT INTO workparts (work_id, part_id, quantity, price_at_usage) VALUES
(1, 1, 1, 3500),
(1, 3, 1, 1500),
(2, 2, 1, 4500),
(4, 4, 1, 8000),
(5, 5, 2, 1200),
(6, 6, 1, 2500),
(7, 7, 1, 5000),
(8, 8, 2, 6500),
(9, 9, 1, 1800),
(10, 10, 1, 2000);

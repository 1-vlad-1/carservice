# Аналитические запросы
class analytical_requests:
    def get_orders_by_period(self, start_date, end_date):
        query = """
        SELECT o.order_id, o.creation_date, o.status, o.total_cost,
               c.name as client_name, car.brand, car.model
        FROM orders o
        JOIN clients c ON o.client_id = c.client_id
        JOIN cars car ON o.car_id = car.car_id
        WHERE o.creation_date BETWEEN %s AND %s
        ORDER BY o.creation_date
        """
        return self.db.execute_query(query, (start_date, end_date), fetch=True)
    
    def get_employee_stats(self, employee_id):
        query = """
        SELECT e.name, COUNT(w.work_id) as work_count, 
               SUM(s.price) as total_income
        FROM works w
        JOIN employees e ON w.employee_id = e.employee_id
        JOIN services s ON w.service_id = s.service_id
        WHERE w.employee_id = %s
        GROUP BY e.name
        """
        return self.db.execute_query(query, (employee_id,), fetch=True)
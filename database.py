import sqlite3

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            self.conn = None
            self.cursor = None

    def execute(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def execute_and_commit(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()

    def create_table(self, table_name, columns):
        columns_str = ', '.join(columns)
        sql = f"CREATE TABLE {table_name} ({columns_str})"
        self.execute_and_commit(sql)

    def select_data(self, columns, table_name):
        columns_str = ', '.join(columns)
        sql = f"SELECT {columns_str} FROM {table_name}"
        return self.execute(sql)

    def insert_data(self, table_name, data):
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.cursor.execute(sql, data)
        self.conn.commit()

    def table_exist(self, table_name):
        try:
           self.select_data('*', table_name)
           return True
        except Exception as e:
            check = str(e) == f'no such table: {table_name}'
            if check:
                if table_name == 'Highscores':
                    self.create_table("Highscores", [
                        "ID INT AUTO_INCREMENT PRIMARY KEY",
                        "FNAME VARCHAR(30) NOT NULL",
                        "SCORE INT NOT NULL"
                    ])
            else:
                raise e
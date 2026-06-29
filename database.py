import mysql.connector
import pandas as pd

class UserDBManager:
    def __init__(self):
        # Establish MySQL connection using provided credentials
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="JonMonir@3210b",
            database="credit_app_db"
        )
        self.cursor = self.mydb.cursor()
    
    def get_all_users(self) -> pd.DataFrame:
        """Fetches all data from Users_db and returns a pandas DataFrame."""
        self.cursor.execute("SELECT * FROM Users_db")
        data = self.cursor.fetchall()
        df = pd.DataFrame(data, columns=self.cursor.column_names)
        return df

    def insert_user(self, username, password, sessionStart, validity, deviceName, macAddress):
        """Inserts a new user record into Users_db."""
        sql = f"""
        INSERT INTO Users_db (username, password, sessionStart, validity, deviceName, macAddress)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        val = (username, password, sessionStart, validity, deviceName, macAddress)
        self.cursor.execute(sql, val)
        self.mydb.commit()  # Commit changes to the database

        
class ActivityTable():


    def __init__(self) -> None:
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="JonMonir@3210b",
            database="credit_app_db"
        )

        self.cursor = self.mydb.cursor()
    def create_user_activity_table(self):
        
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="JonMonir@3210b",
            database="credit_app_db"
        )

        self.cursor = self.mydb.cursor()
        """Creates a new table called 'user_activity' in the same database."""
        sql = """
        CREATE TABLE IF NOT EXISTS user_activity (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            password VARCHAR(255),
            is_login BOOL,
            mac_address CHAR(20),
            device_name VARCHAR(40),
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activity_description TEXT
        )
        """
        self.cursor.execute(sql)

        # Add index to the referenced column
        index_sql = """
        ALTER TABLE Users_db ADD INDEX username_index (username)
        """
        self.cursor.execute(index_sql)

        self.mydb.commit()  # Commit changes to the database

    def add_activity(self, username, password, is_login, mac_address, device_name, activity_description):
        """Inserts a new activity record into user_activity."""
        try:
            # Disable foreign key checks temporarily
            self.cursor.execute("SET FOREIGN_KEY_CHECKS=0")

            # Insert the activity record
            sql = """
            INSERT INTO user_activity (username, password, is_login, mac_address, device_name, activity_description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            val = (username, password, is_login, mac_address, device_name, activity_description)
            self.cursor.execute(sql, val)
            self.mydb.commit()  # Commit changes to the database

        finally:
            # Re-enable foreign key checks
            self.cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    
    def get_all_activities(self):
        """Fetches all data from user_activity and returns a pandas DataFrame."""
        sql = "SELECT * FROM user_activity"
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        df = pd.DataFrame(data, columns=[desc[0] for desc in self.cursor.description])
        return df

    # Example usage:
if __name__ == "__main__":
    at = ActivityTable()
    print(at.get_all_activities())

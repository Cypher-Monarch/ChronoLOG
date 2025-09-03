import mysql.connector
from mysql.connector import Error
import logging
import os
from datetime import datetime

# Create 'logs' directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Create log file with date stamp
log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
log_path = os.path.join(log_dir, log_filename)

# Configure logging
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

HOST = "localhost"
USER = "root"
PASSWORD = "root"
DATABASE = "chronolog"

def create_database():
    try:
        connection = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
        logging.info("[DB Creator] Created database or it already exists.")
    except Error as e:
        logging.error(f"[DB Creator] Error while creating database (Error code: `{e}`)")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_tables():
    try:
        connection = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_groups (
                group_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50)
            )
        """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                id INT PRIMARY KEY,
                theme VARCHAR(50) DEFAULT 'dark',
                font_size INT DEFAULT 12,
                FOREIGN KEY(id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INT AUTO_INCREMENT PRIMARY KEY,
                group_id INT,
                title VARCHAR(255) NOT NULL,
                is_completed BOOLEAN DEFAULT FALSE,
                due_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES task_groups(group_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                assignment_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                due_date DATE,
                is_done BOOLEAN DEFAULT FALSE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                start_time DATETIME,
                end_time DATETIME,
                duration INT,
                category VARCHAR(50),
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS streaks (
                user_id INT PRIMARY KEY,
                current_streak INT DEFAULT 0,
                last_active DATE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                user_id INT PRIMARY KEY,
                theme INT,
                gradient_index INT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        connection.commit()
        logging.info("[DB Creator] All tables created successfully.")

    except Error as e:
        logging.error(f"[DB Creator] Error while creating tables (Error code: `{e}`)")
        raise

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database()
    create_tables()

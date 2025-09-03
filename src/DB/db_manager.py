import mysql.connector as mc
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

class DBManager:
    def __init__(self):
        try:
            self.conn = mc.connect(
                host="localhost",
                user="root",
                password="root",
                database="chronolog"
            )
            self.cursor = self.conn.cursor(dictionary=True)
            logging.info("[DB] Connection to MySQL successful.")
        except Error as e:
            logging.error("[DB] Connection failed: %s", e)

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            logging.debug("[DB] Executed query: %s | Params: %s", query, params)
        except Error as e:
            logging.error("[DB] Query execution failed: %s | Query: %s", e, query)

    def fetch_all(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            result = self.cursor.fetchall()
            logging.debug("[DB] fetch_all successful for query: %s", query)
            return result
        except Error as e:
            logging.error("[DB] fetch_all failed: %s | Query: %s", e, query)
            return None

    def fetch_one(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            result = self.cursor.fetchone()
            logging.debug("[DB] fetch_one successful for query: %s", query)
            return result
        except Error as e:
            logging.error("[DB] fetch_one failed: %s | Query: %s", e, query)
            return None

    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
            logging.info("[DB] MySQL connection closed.")
        except Error as e:
            logging.error("[DB] Failed to close connection: %s", e)

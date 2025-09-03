from src.DB.db_manager import DBManager
from datetime import datetime
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

class ChronoCore:
    def __init__(self):
        self.db = DBManager()

    # Schedule management
    def create_schedule(self, user_id, category, notes):
        query = """
            INSERT INTO schedule (user_id, start_time, category, notes) 
            VALUES (%s, %s, %s, %s)
        """
        params = (user_id, datetime.now(), category, notes)
        self.db.execute_query(query, params)
        logging.info("[Schedule] Session created for user %s in category '%s'", user_id, category)

    def end_schedule(self, session_id, end_time, duration):
        query = """
            UPDATE schedule 
            SET end_time = %s, duration = %s 
            WHERE id = %s
        """
        params = (end_time, duration, session_id)
        self.db.execute_query(query, params)
        logging.info("[Schedule] Session %s ended successfully.", session_id)
    
    def get_user_schedule(self, user_id):
        query = "SELECT * FROM schedule WHERE user_id = %s"
        return self.db.fetch_all(query, (user_id,))

    def delete_schedule(self, schedule_id):
        query = "DELETE FROM schedule WHERE id = %s"
        self.db.execute_query(query, (schedule_id,))
        logging.info("[Schedule] Schedule %s deleted.", schedule_id)

    # Streak management
    def update_streak(self, user_id, last_active_date):
        query = "SELECT current_streak, last_active FROM streaks WHERE user_id = %s"
        streak_data = self.db.fetch_one(query, (user_id,))
        
        if streak_data:
            if streak_data['last_active'] == last_active_date:
                new_streak = streak_data['current_streak'] + 1
                update_query = "UPDATE streaks SET current_streak = %s WHERE user_id = %s"
                self.db.execute_query(update_query, (new_streak, user_id))
                logging.info("[Streak] Updated streak to %s for user %s", new_streak, user_id)
            else:
                logging.info("[Streak] Streak not updated: Dates don't match for user %s", user_id)
        else:
            logging.warning("[Streak] No streak found for user %s", user_id)
    
    def get_user_streak(self, user_id):
        query = "SELECT current_streak FROM streaks WHERE user_id = %s"
        streak_data = self.db.fetch_one(query, (user_id,))
        if streak_data:
            return streak_data['current_streak']
        return 0

    # Task management
    def create_task(self, group_id, title, due_date):
        query = """INSERT INTO tasks (group_id, title, due_date)
        VALUES (%s, %s, %s)"""
        params = (group_id, title, due_date)
        self.db.execute_query(query, params)
        logging.info("[Task] Task '%s' created successfully!", title)

    def get_all_tasks(self, group_id):
        query = "SELECT * FROM tasks WHERE group_id = %s"
        return self.db.fetch_all(query, (group_id,))

    def update_task_status(self, task_id, is_completed):
        query = "UPDATE tasks SET is_completed = %s WHERE task_id = %s"
        self.db.execute_query(query, (is_completed, task_id))
        logging.info("[Task] Task %s status updated to %s", task_id, is_completed)

    def edit_task(self, task_id, new_title, new_due_date, new_group_id=None):
        query = """
            UPDATE tasks
            SET title = %s, due_date = %s
            """ + (", group_id = %s" if new_group_id is not None else "") + """
            WHERE task_id = %s
        """
        params = (new_title, new_due_date, new_group_id, task_id) if new_group_id else (new_title, new_due_date, task_id)
        self.db.execute_query(query, params)
        logging.info("[Task] Task %s edited.", task_id)

    def add_task_to_schedule(self, user_id, start_time, end_time, duration, category, notes):
        self.db.execute_query("""
            INSERT INTO schedule (user_id, start_time, end_time, duration, category, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, start_time, end_time, duration, category, notes))
        logging.info("[Schedule] Task added to schedule for user %s.", user_id)

    def count_related_tasks(self, subject_name):
        query = """
            SELECT COUNT(*) 
            FROM tasks
            WHERE group_id IN (
                SELECT group_id FROM task_groups WHERE name = %s
            )
        """
        result = self.db.fetch_one(query, (subject_name,))
        if result and 'COUNT(*)' in result:
            return result['COUNT(*)']
        return 0

    def get_task(self, task_id):
        query = "SELECT * FROM tasks WHERE task_id = %s"
        return self.db.fetch_one(query, (task_id,))
    
    def get_task_completion_status(self, task_id):
        query = "SELECT is_completed FROM tasks WHERE task_id = %s"
        result = self.db.fetch_one(query, (task_id,))
        if result and 'is_completed' in result:
            return result['is_completed']
        return None

    def delete_task(self, task_id):
        query = "DELETE FROM tasks WHERE task_id = %s"
        self.db.execute_query(query, (task_id,))
        logging.info("[Task] Task %s deleted.", task_id)

    # Subject management
    def create_subject(self, subject, priority):
        query = "INSERT INTO task_groups (name, type) VALUES (%s, %s)"
        params = (subject, priority)
        self.db.execute_query(query, params)
        logging.info("[Subject] Subject '%s' created with priority '%s'", subject, priority)

    def get_all_subjects(self):
        query = "SELECT group_id, name, type FROM task_groups"
        return self.db.fetch_all(query)

    def edit_subject(self, group_id, new_name, new_priority):
        query = "UPDATE task_groups SET name = %s, type = %s WHERE group_id = %s"
        self.db.execute_query(query, (new_name, new_priority, group_id))
        logging.info("[Subject] Subject %s updated to '%s' with priority '%s'", group_id, new_name, new_priority)

    def delete_subject(self, group_id):
        query = "SELECT name FROM task_groups WHERE group_id = %s"
        subject_data = self.db.fetch_one(query, (group_id,))
        if subject_data:
            subject_name = subject_data['name']
            task_count = self.count_related_tasks(subject_name)
            logging.info("[Subject] %s has %s related tasks.", subject_name, task_count)
            if task_count > 0:
                logging.warning("[Subject] Cannot delete subject '%s'. Tasks still linked.", subject_name)
                return
            query = "DELETE FROM task_groups WHERE group_id = %s"
            self.db.execute_query(query, (group_id,))
            logging.info("[Subject] Subject %s deleted successfully.", subject_name)
        else:
            logging.warning("[Subject] Subject with ID %s not found.", group_id)

    def save_data(self):
        try:
            self.db.conn.commit()
            logging.info("[Core] Data saved successfully to database.")
        except Exception as e:
            logging.error("[Core] Error during save_data: %s", e)

    # Clean up
    def close_connection(self):
        self.db.close()
        logging.info("[Core] Database connection closed.")
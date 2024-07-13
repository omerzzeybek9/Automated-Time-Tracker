import sys
import os
import psutil
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
import threading
import sqlite3

class TimeTracker(QWidget):
    def __init__(self):
        super().__init__()  # Correct super call
        print("Initializing UI...")
        self.initUI()  # Initialize the user interface
        self.running = True  # Flag to control the tracking loop
        print("Connecting to database...")
        db_path = os.path.join(os.getcwd(), "time_tracker.db")
        print(f"Database will be created at: {db_path}")
        self.db_conn = sqlite3.connect(db_path)  # Connect to the database
        self.create_table()  # Ensure the table is created
        print("Starting tracker thread...")
        self.tracker_thread = threading.Thread(target=self.track_time)  # Create a thread for time tracking
        self.tracker_thread.start()  # Start the tracking thread

    def initUI(self):
        # Set up user interface
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('Time Tracker')
        layout = QVBoxLayout()
        self.status_label = QLabel('Tracking...', self)
        self.stop_button = QPushButton('Stop Tracking', self)
        self.stop_button.clicked.connect(self.stop_tracking)
        self.view_logs_button = QPushButton('View Logs', self)
        self.view_logs_button.clicked.connect(self.view_logs)
        self.logs_text = QTextEdit(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.view_logs_button)
        layout.addWidget(self.logs_text)
        self.setLayout(layout)
        self.show()

    def create_table(self):
        # Create the database table if it doesn't exist
        cursor = self.db_conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS time_log (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          application TEXT,
                          start_time TEXT,
                          end_time TEXT)''')
        self.db_conn.commit()
        print("Table created or already exists.")

    def track_time(self):
        # Track the active window and log time
        while self.running:
            active_window = self.get_active_window()
            if active_window:
                print(f"Active window: {active_window}")
                start_time = time.strftime('%Y-%m-%d %H:%M:%S')
                time.sleep(5)  # Check every 5 seconds
                end_time = time.strftime('%Y-%m-%d %H:%M:%S')
                self.log_time(active_window, start_time, end_time)

    def get_active_window(self):
        # Get the title of currently active window
        try:
            import ctypes
            user32 = ctypes.windll.user32
            window = user32.GetForegroundWindow()
            length = user32.GetWindowTextLengthW(window)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(window, buff, length + 1)
            return buff.value
        except Exception as e:
            print(f"Error: {e}")
            return None

    def log_time(self, application, start_time, end_time):
        # Log the time spent on the active application to the database
        try:
            with sqlite3.connect("time_tracker.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO time_log (application, start_time, end_time)
                                  VALUES (?, ?, ?)''', (application, start_time, end_time))
                conn.commit()
                print(f"Logged time for {application} from {start_time} to {end_time}")
        except Exception as e:
            print(f"Error logging time: {e}")

    def stop_tracking(self):
        # Stop time tracking
        self.running = False
        self.status_label.setText('Tracking Stopped')
        self.db_conn.close()

    def view_logs(self):
        # Display the logs in the text area
        self.logs_text.clear()
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM time_log")
        rows = cursor.fetchall()
        log_text = ""
        for row in rows:
            log_text += f"ID: {row[0]}, Application: {row[1]}, Start Time: {row[2]}, End Time: {row[3]}\n"
        self.logs_text.setPlainText(log_text)

if __name__ == "__main__":
    print("Starting application...")
    app = QApplication(sys.argv)
    ex = TimeTracker()
    sys.exit(app.exec_())

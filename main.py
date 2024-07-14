import sys
import os
import psutil
import time
import sqlite3
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QLabel, QPushButton, QTextEdit, QTabWidget, QWidget, QAction, QSystemTrayIcon, QMessageBox, QGridLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class TimeTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.running = False
        self.db_path = os.path.join(os.getcwd(), "time_tracker.db")
        self.db_conn = sqlite3.connect(self.db_path)
        self.create_table()
        self.tracker_thread = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_logs_and_graph)
        self.timer.start(5000)  # Update every 5 seconds

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('icon.png'))
        self.tray_icon.setVisible(True)
        
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.close_application)

    def initUI(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Time Tracker')
        self.setWindowIcon(QIcon('icon.png'))  # Set the window icon
        
        self.tabs = QTabWidget()
        
        self.tracking_tab = QWidget()
        self.logs_tab = QWidget()
        self.graph_tab = QWidget()
        
        self.tabs.addTab(self.tracking_tab, "Tracking")
        self.tabs.addTab(self.logs_tab, "Logs")
        self.tabs.addTab(self.graph_tab, "Graph")
        
        self.initTrackingTab()
        self.initLogsTab()
        self.initGraphTab()
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.createActions()
        self.createMenuBar()

        self.show()

    def initTrackingTab(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel('Tracking stopped', self)
        self.status_label.setStyleSheet("font-size: 16px; color: red;")
        
        self.start_button = QPushButton('Start Tracking', self)
        self.start_button.setStyleSheet("font-size: 14px; padding: 10px;")
        self.start_button.clicked.connect(self.start_tracking)
        
        self.stop_button = QPushButton('Stop Tracking', self)
        self.stop_button.setStyleSheet("font-size: 14px; padding: 10px;")
        self.stop_button.clicked.connect(self.stop_tracking)
        
        self.reset_button = QPushButton('Reset Database', self)
        self.reset_button.setStyleSheet("font-size: 14px; padding: 10px;")
        self.reset_button.clicked.connect(self.reset_database)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.reset_button)
        
        layout.addWidget(self.status_label)
        layout.addLayout(button_layout)
        
        self.tracking_tab.setLayout(layout)

    def initLogsTab(self):
        layout = QVBoxLayout()
        self.logs_text = QTextEdit(self)
        self.logs_text.setReadOnly(True)
        layout.addWidget(self.logs_text)
        self.logs_tab.setLayout(layout)

    def initGraphTab(self):
        layout = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(10, 6)))  # Adjust figure size if needed
        layout.addWidget(self.canvas)
        self.graph_tab.setLayout(layout)

    def create_table(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS time_log (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          application TEXT,
                          start_time TEXT,
                          end_time TEXT)''')
        self.db_conn.commit()

    def reset_database(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS time_log''')
        self.db_conn.commit()
        self.create_table()
        self.update_logs_and_graph()
        self.status_label.setText('Database reset')

    def track_time(self):
        while self.running:
            active_window = self.get_active_window()
            if active_window:
                start_time = time.strftime('%Y-%m-%d %H:%M:%S')
                time.sleep(5)
                end_time = time.strftime('%Y-%m-%d %H:%M:%S')
                self.log_time(active_window, start_time, end_time)

    def get_active_window(self):
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
        try:
            with sqlite3.connect("time_tracker.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO time_log (application, start_time, end_time)
                                  VALUES (?, ?, ?)''', (application, start_time, end_time))
                conn.commit()
        except Exception as e:
            print(f"Error logging time: {e}")

    def start_tracking(self):
        if not self.running:
            self.running = True
            self.status_label.setText('Tracking started')
            self.status_label.setStyleSheet("color: green;")
            if self.tracker_thread is None or not self.tracker_thread.is_alive():
                self.tracker_thread = threading.Thread(target=self.track_time)
                self.tracker_thread.start()

    def stop_tracking(self):
        self.running = False
        self.status_label.setText('Tracking stopped')
        self.status_label.setStyleSheet("color: red;")

    def update_logs_and_graph(self):
        self.update_logs()
        self.update_graph()

    def update_logs(self):
        self.logs_text.clear()
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM time_log")
        rows = cursor.fetchall()
        log_text = ""
        for row in rows:
            log_text += f"ID: {row[0]}, Application: {row[1]}, Start Time: {row[2]}, End Time: {row[3]}\n"
        self.logs_text.setPlainText(log_text)

    def seconds_to_minutes(self, seconds):
        minutes = seconds / 60
        return minutes

    def update_graph(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT application, start_time, end_time FROM time_log")
        rows = cursor.fetchall()
        
        app_times = {}
        
        for row in rows:
            app_name = row[0]
            start_time = time.mktime(time.strptime(row[1], '%Y-%m-%d %H:%M:%S'))
            end_time = time.mktime(time.strptime(row[2], '%Y-%m-%d %H:%M:%S'))
            duration_seconds = end_time - start_time
            
            if app_name in app_times:
                app_times[app_name] += duration_seconds
            else:
                app_times[app_name] = duration_seconds
    
        apps = list(app_times.keys())
        times_seconds = list(app_times.values())
        times_minutes = [self.seconds_to_minutes(seconds) for seconds in times_seconds]
        
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        
        colors = plt.cm.get_cmap('tab20')(range(len(apps)))
        bars = ax.bar(apps, times_minutes, align='center', color=colors)

        ax.set_xlabel('Applications')
        ax.set_ylabel('Time Spent (minutes)')
        ax.set_title('Time Spent on Applications')
        ax.grid(True)
        
        # Rotate x-axis labels for better readability
        ax.set_xticks(range(len(apps)))
        ax.set_xticklabels(apps, rotation=90, ha='right')
        
        # Adjust layout to prevent clipping of tick-labels
        self.canvas.figure.tight_layout()
        
        # Adjust subplots for more space
        self.canvas.figure.subplots_adjust(bottom=0.3)
        
        self.canvas.draw()

    def createActions(self):
        self.exitAct = QAction('Exit', self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.setStatusTip('Exit application')
        self.exitAct.triggered.connect(self.close_application)

    def createMenuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(self.exitAct)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db_conn.close()
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            event.accept()
        else:
            event.ignore()

    def close_application(self):
        self.db_conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = TimeTracker()
    sys.exit(app.exec_())
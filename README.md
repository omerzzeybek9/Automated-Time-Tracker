# Automated Time Tracker

## About the Project

**Automated Time Tracker** is a tool that tracks which applications you use on your computer and for how long, and visualises this information graphically. This application aims to help users manage their time more efficiently.

## Features

- Application Tracking:** Monitors the active window and records application usage times.
- Logging:** Saves usage information to the database and displays logs.
- Graphical Visualisation:** Shows usage times graphically.
- Database Management:** Ability to reset the database and clear logs.
- System Tray Icon:** The application is placed in the system tray and you can control basic operations from there.

## Installation

1. Clone or download this project:
   ```sh
   git clone https://github.com/omerzzeybek9/automated-time-tracker.git
   cd automated-time-tracker
2. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
3. Launch the application:
   ```sh
   python time_tracker.py

## Usage

1. Start: Tracking After running the application, you can start the tracking process by clicking the Start Tracking button.
2. Stop: You can stop the tracking process by clicking the Stop Tracking button.
3. Reset Database: You can delete all log records and reset the database by clicking the Reset Database button.
4. Logs and Graphics: You can see the logs of the tracked applications in the *Logs* tab and the usage times graphically in the *Graph* tab.

## Dependencies

- Python 3.x
- PyQt5
- Matplotlib
- Psutil

## Contact

Ömer Faruk Zeybek - [GitHub](https://github.com/omerzzeybek9)
   

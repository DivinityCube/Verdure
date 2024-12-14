import sys
import sqlite3
from datetime import date

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QTabWidget, QFrame, QHeaderView, QDateEdit
)
from PyQt6.QtGui import QFont, QPalette, QColor, QIntValidator
from PyQt6.QtCore import Qt, QDate

class CalorieTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Verdure 25 [INDEV BUILD]")
        self.resize(800, 600)
        
        # Set up dark theme
        self.setup_dark_theme()
        
        # Database setup
        self.conn = sqlite3.connect('calorie_tracker.db')
        self.create_tables()
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Calorie Tracker")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Tabs for different views
        tab_widget = QTabWidget()
        
        # Log Entry Tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        # Input Frame
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #2C2C2C;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        input_layout = QVBoxLayout(input_frame)
        
        # Date Picker Input
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        self.date_picker = QDateEdit(calendarPopup=True)
        self.date_picker.setDate(QDate.currentDate())
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_picker)
        input_layout.addLayout(date_layout)
        
        # Calories Consumed Input
        consumed_layout = QHBoxLayout()
        consumed_label = QLabel("Calories Consumed:")
        self.consumed_entry = QLineEdit()
        self.consumed_entry.setPlaceholderText("Enter calories consumed")
        self.consumed_entry.setValidator(QIntValidator(0, 10000))
        consumed_layout.addWidget(consumed_label)
        consumed_layout.addWidget(self.consumed_entry)
        input_layout.addLayout(consumed_layout)
        
        # Calories Burned Input
        burned_layout = QHBoxLayout()
        burned_label = QLabel("Calories Burned:")
        self.burned_entry = QLineEdit()
        self.burned_entry.setPlaceholderText("Enter calories burned")
        self.burned_entry.setValidator(QIntValidator(0, 10000))
        burned_layout.addWidget(burned_label)
        burned_layout.addWidget(self.burned_entry)
        input_layout.addLayout(burned_layout)
        
        # Save Button
        save_button = QPushButton("Save Daily Log")
        save_button.clicked.connect(self.save_daily_log)
        input_layout.addWidget(save_button)
        
        log_layout.addWidget(input_frame)
        
        # History Table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Calories Consumed", "Calories Burned", "Net Calories"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        log_layout.addWidget(self.history_table)
        
        # History Control Buttons
        button_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh History")
        refresh_button.clicked.connect(self.load_history)
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_log)
        delete_button.setStyleSheet("background-color: #8B0000; color: white;")
        
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(delete_button)
        
        log_layout.addLayout(button_layout)
        
        # Add tabs
        tab_widget.addTab(log_tab, "Daily Log")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        
        # Initial history load
        self.load_history()

    def setup_dark_theme(self):
        """Set up a dark theme for the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                color: white;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #2C2C2C;
                color: white;
                border: 1px solid #3C3C3C;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #4A4A4A;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QTableWidget {
                background-color: #2C2C2C;
                color: white;
                alternate-background-color: #3C3C3C;
            }
            QHeaderView::section {
                background-color: #4A4A4A;
                color: white;
                padding: 5px;
                border: none;
            }
        """)

    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calorie_logs (
                date TEXT PRIMARY KEY,
                calories_consumed INTEGER,
                calories_burned INTEGER
            )
        ''')
        self.conn.commit()

    def save_daily_log(self):
        """Save the daily calorie log to the database."""
        try:
            # Get selected date
            selected_date = self.date_picker.date().toString("yyyy-MM-dd")
            
            # Get consumed and burned calories
            consumed = int(self.consumed_entry.text())
            burned = int(self.burned_entry.text())

            # Insert or replace the log for the selected date
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO calorie_logs (date, calories_consumed, calories_burned)
                VALUES (?, ?, ?)
            ''', (selected_date, consumed, burned))
            
            self.conn.commit()
            
            # Clear entries
            self.consumed_entry.clear()
            self.burned_entry.clear()
            self.date_picker.setDate(QDate.currentDate())
            
            # Refresh history
            self.load_history()
            
            # Show success message
            QMessageBox.information(self, "Success", "Daily log saved successfully!")

        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numbers for calories.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def load_history(self):
        """Load and display calorie log history."""
        # Clear existing items
        self.history_table.setRowCount(0)
        
        # Fetch logs from database
        cursor = self.conn.cursor()
        cursor.execute('SELECT date, calories_consumed, calories_burned FROM calorie_logs ORDER BY date DESC')
        
        for row_data in cursor.fetchall():
            date, consumed, burned = row_data
            net_calories = consumed - burned
            
            # Insert row
            row_position = self.history_table.rowCount()
            self.history_table.insertRow(row_position)
            
            # Set row data
            self.history_table.setItem(row_position, 0, QTableWidgetItem(str(date)))
            self.history_table.setItem(row_position, 1, QTableWidgetItem(str(consumed)))
            self.history_table.setItem(row_position, 2, QTableWidgetItem(str(burned)))
            self.history_table.setItem(row_position, 3, QTableWidgetItem(str(net_calories)))

    def delete_log(self):
        """Delete the selected log from history."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.history_table.selectedIndexes())
        
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a log to delete.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 'Delete Logs', 
            "Are you sure you want to delete the selected log(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete selected logs
            for row in sorted(selected_rows, reverse=True):
                date_to_delete = self.history_table.item(row, 0).text()
                
                # Delete from database
                cursor = self.conn.cursor()
                cursor.execute('DELETE FROM calorie_logs WHERE date = ?', (date_to_delete,))
                self.conn.commit()
                
                # Remove from table
                self.history_table.removeRow(row)
            
            QMessageBox.information(self, "Success", "Selected log(s) deleted.")

    def closeEvent(self, event):
        """Ensure database connection is closed when app exits"""
        self.conn.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    main_window = CalorieTrackerApp()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
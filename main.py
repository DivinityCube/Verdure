import sys
import sqlite3
from datetime import date

import pyqtgraph as pg

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QFrame, QHeaderView, QDateEdit, QGridLayout,
    QDialog, QComboBox
)
from PyQt6.QtGui import QFont, QIntValidator, QIcon, QColor
from PyQt6.QtCore import Qt, QDate, QSize

class ExerciseCalculatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculate Exercise Calories")
        self.setFixedSize(300, 260)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: white;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 14px;
            }
            QComboBox, QLineEdit {
                background-color: #252525;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                background-color: #22C55E;
                color: white;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
            QPushButton#CancelButton {
                background-color: #333333;
                color: #E0E0E0;
            }
            QPushButton#CancelButton:hover {
                background-color: #444444;
            }
        """)

        # Scientific MET (Metabolic Equivalent of Task) values
        self.activities = {
            "Walking (Slow)": 2.5,
            "Walking (Brisk)": 4.3,
            "Running (Moderate)": 9.8,
            "Running (Fast)": 11.8,
            "Cycling (Moderate)": 8.0,
            "Cycling (Vigorous)": 10.0,
            "Swimming (Light)": 6.0,
            "Swimming (Vigorous)": 9.8,
            "Weightlifting": 3.5,
            "Yoga": 3.0,
            "HIIT": 8.0
        }

        layout = QVBoxLayout(self)

        # Action Selection
        layout.addWidget(QLabel("Action:"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(self.activities.keys())
        layout.addWidget(self.action_combo)

        # Weight Input
        layout.addWidget(QLabel("Body Weight (kg):"))
        self.weight_input = QLineEdit()
        self.weight_input.setValidator(QIntValidator(20, 300))
        self.weight_input.setText("70") # Default average weight
        layout.addWidget(self.weight_input)

        # Length Input
        layout.addWidget(QLabel("Length (Minutes):"))
        self.length_input = QLineEdit()
        self.length_input.setValidator(QIntValidator(1, 1440)) # Max 24 hours
        self.length_input.setPlaceholderText("e.g. 30")
        layout.addWidget(self.length_input)

        # Result Label
        self.result_label = QLabel("Calculated: 0 kcal")
        self.result_label.setStyleSheet("color: #4ADE80; font-weight: bold;")
        layout.addWidget(self.result_label)
        
        # Real-time calculation update
        self.weight_input.textChanged.connect(self.update_calculation)
        self.length_input.textChanged.connect(self.update_calculation)
        self.action_combo.currentIndexChanged.connect(self.update_calculation)

        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelButton")
        cancel_btn.clicked.connect(self.reject)
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(apply_btn)
        layout.addLayout(button_layout)
        
        self.calculated_calories = 0

    def update_calculation(self):
        try:
            minutes = int(self.length_input.text()) if self.length_input.text() else 0
            weight = float(self.weight_input.text()) if self.weight_input.text() else 0.0
            action = self.action_combo.currentText()
            met = self.activities[action]
            
            # Scientific MET Formula: Calories = Time * (MET * Weight in kg * 3.5) / 200
            self.calculated_calories = int(minutes * (met * weight * 3.5) / 200)
            
            self.result_label.setText(f"Calculated: {self.calculated_calories} kcal")
        except ValueError:
            self.result_label.setText("Calculated: 0 kcal")
            self.calculated_calories = 0

    def get_calories(self):
        return self.calculated_calories


class GoalPlannerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Goal Planner")
        self.setFixedSize(400, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: white;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 14px;
            }
            QLineEdit, QDateEdit, QComboBox {
                background-color: #252525;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QPushButton {
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                background-color: #22C55E;
                color: white;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
            QPushButton#CloseButton {
                background-color: #333333;
                color: #E0E0E0;
            }
            QPushButton#CloseButton:hover {
                background-color: #444444;
            }
        """)

        layout = QVBoxLayout(self)
        
        # BMR Parameters
        layout.addWidget(QLabel("Biological Sex:"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Male", "Female"])
        layout.addWidget(self.gender_combo)

        layout.addWidget(QLabel("Age (years):"))
        self.age_input = QLineEdit()
        self.age_input.setValidator(QIntValidator(10, 120))
        self.age_input.setText("30")
        layout.addWidget(self.age_input)

        layout.addWidget(QLabel("Height (cm):"))
        self.height_input = QLineEdit()
        self.height_input.setValidator(QIntValidator(100, 250))
        self.height_input.setText("170")
        layout.addWidget(self.height_input)
        
        layout.addWidget(QLabel("Activity Level:"))
        self.activity_combo = QComboBox()
        self.activity_combo.addItems([
            "Sedentary (little/no exercise)",
            "Lightly Active (1-3 days/week)",
            "Moderately Active (3-5 days/week)",
            "Very Active (6-7 days/week)",
            "Extra Active (physical job/2x day)"
        ])
        # Activity multipliers for TDEE
        self.activity_multipliers = [1.2, 1.375, 1.55, 1.725, 1.9]
        layout.addWidget(self.activity_combo)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep)

        layout.addWidget(QLabel("Current Weight (kg):"))
        self.current_weight_input = QLineEdit()
        self.current_weight_input.setValidator(QIntValidator(20, 300))
        layout.addWidget(self.current_weight_input)

        layout.addWidget(QLabel("Goal Weight (kg):"))
        self.goal_weight_input = QLineEdit()
        self.goal_weight_input.setValidator(QIntValidator(20, 300))
        layout.addWidget(self.goal_weight_input)

        layout.addWidget(QLabel("Target Date:"))
        self.target_date_picker = QDateEdit(calendarPopup=True)
        self.target_date_picker.setMinimumDate(QDate.currentDate().addDays(1)) # At least tomorrow
        self.target_date_picker.setDate(QDate.currentDate().addMonths(1))
        layout.addWidget(self.target_date_picker)

        # Result Label
        self.result_label = QLabel("Enter your details above.")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("color: #4ADE80; font-weight: bold; margin-top: 10px;")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.result_label)
        layout.addStretch()
        
        # Connections
        self.gender_combo.currentIndexChanged.connect(self.calculate_deficit)
        self.age_input.textChanged.connect(self.calculate_deficit)
        self.height_input.textChanged.connect(self.calculate_deficit)
        self.activity_combo.currentIndexChanged.connect(self.calculate_deficit)
        
        self.current_weight_input.textChanged.connect(self.calculate_deficit)
        self.goal_weight_input.textChanged.connect(self.calculate_deficit)
        self.target_date_picker.dateChanged.connect(self.calculate_deficit)

        # Buttons
        close_btn = QPushButton("Close")
        close_btn.setObjectName("CloseButton")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def calculate_deficit(self):
        try:
            current_wt = float(self.current_weight_input.text())
            goal_wt = float(self.goal_weight_input.text())
            age = int(self.age_input.text())
            height = int(self.height_input.text())
            
            # 1. Calculate BMR (Mifflin-St Jeor)
            if self.gender_combo.currentText() == "Male":
                bmr = (10 * current_wt) + (6.25 * height) - (5 * age) + 5
            else:
                bmr = (10 * current_wt) + (6.25 * height) - (5 * age) - 161
                
            # 2. Calculate TDEE
            multiplier = self.activity_multipliers[self.activity_combo.currentIndex()]
            tdee = bmr * multiplier
            
            # 3. Calculate Required Deficit
            days_diff = QDate.currentDate().daysTo(self.target_date_picker.date())
            
            if days_diff <= 0:
                self.result_label.setText("Target date must be in the future.")
                self.result_label.setStyleSheet("color: #EF4444;")
                return

            weight_diff = current_wt - goal_wt
            
            if weight_diff <= 0:
                self.result_label.setText(f"Maintenance Calories (TDEE): {int(tdee)} kcal/day\nSet a lower goal weight to calculate a deficit.")
                self.result_label.setStyleSheet("color: #FBBF24;")
                return

            # ~7700 kcal per kg of fat
            total_deficit = weight_diff * 7700
            daily_deficit = int(total_deficit / days_diff)
            target_intake = int(tdee - daily_deficit)
            
            # Warnings
            warning = ""
            if daily_deficit > 1000:
                warning += "<br><span style='color:#EF4444; font-size:12px;'>⚠️ Deficit over 1000 kcal/day is aggressive.</span>"
            if target_intake < 1200:
                warning += "<br><span style='color:#EF4444; font-size:12px;'>⚠️ Daily intake below 1200 kcal is medically unsafe without supervision.</span>"
                
            self.result_label.setStyleSheet("color: #4ADE80;")
            
            result_html = f"""
            <div style='line-height: 1.5;'>
                Target weight loss: {weight_diff:.1f} kg over {days_diff} days.<br>
                Base Burn (TDEE): <b>{int(tdee)} kcal/day</b><br>
                Required Deficit: <b>-{daily_deficit} kcal/day</b><br><br>
                Your Daily Calorie Target to hit this goal:<br>
                <span style='font-size: 28px; color: #E0E0E0;'>{target_intake} kcal &nbsp;🍎</span>{warning}
            </div>
            """
            
            self.result_label.setText(result_html)
            
        except ValueError:
            self.result_label.setText("Please fill out all numeric fields to calculate.")
            self.result_label.setStyleSheet("color: #A0A0A0;")
            
        except ValueError:
            self.result_label.setText("Please enter numerical values for weight.")
            self.result_label.setStyleSheet("color: #A0A0A0;")


class CalorieTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Verdure 26 - Health Dashboard")
        self.resize(1000, 700)
        
        # Database setup
        self.conn = sqlite3.connect('calorie_tracker.db')
        self.create_tables()

        # Apply global style
        self.apply_modern_theme()
        
        # Setup Menu Bar
        self.setup_menu()
        
        # Main widget & Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- Header Section ---
        self.header_frame = QFrame()
        self.header_frame.setObjectName("HeaderFrame")
        self.header_frame.setFixedHeight(80)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        title_label = QLabel("🌿 Verdure 26")
        title_label.setObjectName("MainTitle")
        header_layout.addWidget(title_label)
        
        self.status_label = QLabel("Stay healthy, track your progress!")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(self.status_label)
        
        self.main_layout.addWidget(self.header_frame)
        
        # --- Content Section ---
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)
        
        # Left Panel: Input & Dashboard Stats
        left_panel = QWidget()
        left_panel.setFixedWidth(350)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)
        
        # Dashboard Cards
        self.today_card = QFrame()
        self.today_card.setObjectName("Card")
        today_layout = QVBoxLayout(self.today_card)
        
        today_title = QLabel("Today's Summary")
        today_title.setObjectName("CardTitle")
        
        self.net_cal_label = QLabel("0 kcal")
        self.net_cal_label.setObjectName("BigStat")
        
        self.detail_label = QLabel("Consumed: 0 | Burned: 0")
        self.detail_label.setObjectName("SmallStat")
        
        self.water_label = QLabel("💧 Water: 0 glasses")
        self.water_label.setObjectName("SmallStat")
        self.water_label.setStyleSheet("color: #38BDF8; font-weight: bold; margin-top: 5px;")
        
        today_layout.addWidget(today_title)
        today_layout.addWidget(self.net_cal_label)
        today_layout.addWidget(self.detail_label)
        today_layout.addWidget(self.water_label)
        
        left_layout.addWidget(self.today_card)
        
        # Data Entry Form
        self.entry_frame = QFrame()
        self.entry_frame.setObjectName("Card")
        entry_layout = QVBoxLayout(self.entry_frame)
        entry_layout.setSpacing(15)
        
        entry_title = QLabel("Log Entry")
        entry_title.setObjectName("CardTitle")
        entry_layout.addWidget(entry_title)
        
        # Date
        self.date_picker = QDateEdit(calendarPopup=True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.dateChanged.connect(self.update_today_summary)
        entry_layout.addWidget(QLabel("Date:"))
        entry_layout.addWidget(self.date_picker)
        
        # Consumed
        self.consumed_entry = QLineEdit()
        self.consumed_entry.setPlaceholderText("Calories Consumed")
        self.consumed_entry.setValidator(QIntValidator(0, 10000))
        entry_layout.addWidget(QLabel("Food (kcal):"))
        entry_layout.addWidget(self.consumed_entry)
        
        # Burned
        self.burned_entry = QLineEdit()
        self.burned_entry.setPlaceholderText("Calories Burned")
        self.burned_entry.setValidator(QIntValidator(0, 10000))
        
        calc_button = QPushButton("🧮 Calc")
        calc_button.setObjectName("SecondaryButton")
        calc_button.setCursor(Qt.CursorShape.PointingHandCursor)
        calc_button.setFixedWidth(70)
        calc_button.clicked.connect(self.open_exercise_calculator)
        
        burned_layout = QHBoxLayout()
        burned_layout.addWidget(self.burned_entry)
        burned_layout.addWidget(calc_button)
        
        entry_layout.addWidget(QLabel("Exercise (kcal):"))
        entry_layout.addLayout(burned_layout)
        
        # Water
        self.water_entry = QLineEdit()
        self.water_entry.setPlaceholderText("Water (glasses)")
        self.water_entry.setValidator(QIntValidator(0, 100))
        
        quick_water_btn = QPushButton("+1 💧")
        quick_water_btn.setObjectName("SecondaryButton")
        quick_water_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        quick_water_btn.setFixedWidth(70)
        quick_water_btn.clicked.connect(self.add_one_glass)
        
        water_layout = QHBoxLayout()
        water_layout.addWidget(self.water_entry)
        water_layout.addWidget(quick_water_btn)
        
        entry_layout.addWidget(QLabel("Water (glasses):"))
        entry_layout.addLayout(water_layout)
        
        # Save Button
        save_button = QPushButton("Save Log")
        save_button.setObjectName("PrimaryButton")
        save_button.clicked.connect(self.save_daily_log)
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        entry_layout.addWidget(save_button)
        
        left_layout.addWidget(self.entry_frame)
        
        # --- Chart Section ---
        self.chart_frame = QFrame()
        self.chart_frame.setObjectName("Card")
        chart_layout = QVBoxLayout(self.chart_frame)
        
        chart_title = QLabel("Recent Trend")
        chart_title.setObjectName("CardTitle")
        chart_layout.addWidget(chart_title)
        
        # Setup Plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#1E1E1E')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Net Calories')
        self.plot_widget.getAxis('bottom').setTicks([]) # Simplify X axis for now
        
        self.plot_pen = pg.mkPen(color='#4ADE80', width=3)
        self.plot_curve = self.plot_widget.plot([], [], pen=self.plot_pen, symbol='o', symbolSize=6, symbolBrush='#4ADE80')
        chart_layout.addWidget(self.plot_widget)
        
        left_layout.addWidget(self.chart_frame)
        
        left_layout.addStretch()
        
        content_layout.addWidget(left_panel)
        
        # Right Panel: History Table
        right_panel = QFrame()
        right_panel.setObjectName("Card")
        right_layout = QVBoxLayout(right_panel)
        
        table_header_layout = QHBoxLayout()
        history_title = QLabel("Log History")
        history_title.setObjectName("CardTitle")
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("SecondaryButton")
        refresh_btn.clicked.connect(self.load_history)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        del_btn = QPushButton("Delete Selected")
        del_btn.setObjectName("DangerButton")
        del_btn.clicked.connect(self.delete_log)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        table_header_layout.addWidget(history_title)
        table_header_layout.addStretch()
        table_header_layout.addWidget(refresh_btn)
        table_header_layout.addWidget(del_btn)
        right_layout.addLayout(table_header_layout)
        
        # Table setup
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Date", "Consumed", "Burned", "Net (kcal)", "Water (glasses)"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setShowGrid(False)
        
        right_layout.addWidget(self.history_table)
        content_layout.addWidget(right_panel)
        
        self.main_layout.addWidget(content_widget)
        
        # Initialize Data
        self.load_history()
        self.update_today_summary()

    def apply_modern_theme(self):
        """Ultra-modern dark theme with green accents."""
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMainWindow {
                background-color: #121212;
            }
            #HeaderFrame {
                background-color: #1E1E1E;
                border-bottom: 1px solid #2C2C2C;
            }
            #MainTitle {
                color: #4ADE80;
                font-size: 24px;
                font-weight: bold;
            }
            #StatusLabel {
                color: #A0A0A0;
                font-size: 14px;
            }
            #Card {
                background-color: #1E1E1E;
                border-radius: 12px;
                border: 1px solid #2C2C2C;
                padding: 20px;
            }
            #CardTitle {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 10px;
            }
            #BigStat {
                color: #4ADE80;
                font-size: 36px;
                font-weight: bold;
            }
            #SmallStat {
                color: #A0A0A0;
                font-size: 14px;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 14px;
            }
            QLineEdit, QDateEdit {
                background-color: #252525;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 1px solid #4ADE80;
                background-color: #2A2A2A;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QPushButton {
                padding: 10px 15px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            #PrimaryButton {
                background-color: #22C55E;
                color: white;
            }
            #PrimaryButton:hover {
                background-color: #16A34A;
            }
            #SecondaryButton {
                background-color: #333333;
                color: #E0E0E0;
            }
            #SecondaryButton:hover {
                background-color: #444444;
            }
            #DangerButton {
                background-color: #EF4444;
                color: white;
            }
            #DangerButton:hover {
                background-color: #DC2626;
            }
            
            QTableWidget {
                background-color: transparent;
                color: #E0E0E0;
                border: none;
                gridline-color: #2C2C2C;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #2C2C2C;
            }
            QTableWidget::item:selected {
                background-color: rgba(74, 222, 128, 0.15);
                color: #4ADE80;
            }
            QHeaderView::section {
                background-color: #1E1E1E;
                color: #A0A0A0;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #2C2C2C;
                text-align: left;
            }
            QScrollBar:vertical {
                background: #121212;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #333333;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #444444;
            }
            QMenuBar {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-size: 14px;
            }
            QMenuBar::item {
                padding: 6px 12px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #333333;
                border-radius: 4px;
            }
            QMenu {
                background-color: #252525;
                color: #FFFFFF;
                border: 1px solid #333333;
                font-size: 14px;
            }
            QMenu::item {
                padding: 8px 24px 8px 24px;
            }
            QMenu::item:selected {
                background-color: #4ADE80;
                color: #121212;
            }
        """)

    def setup_menu(self):
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")
        
        goal_planner_action = help_menu.addAction("Goal Planner...")
        goal_planner_action.triggered.connect(self.show_goal_planner)
        
        weight_loss_info_action = help_menu.addAction("Weight Loss Information...")
        weight_loss_info_action.triggered.connect(self.show_weight_loss_info)
        
        about_action = help_menu.addAction("About Verdure...")
        about_action.triggered.connect(self.show_about_dialog)

    def show_goal_planner(self):
        dialog = GoalPlannerDialog(self)
        dialog.exec()

    def show_weight_loss_info(self):
        info_text = """
        <h3>Guidance for Weight Loss</h3>
        <ul>
            <li><b>Caloric Deficit:</b> Weight loss strictly requires burning more calories than you consume. A realistic goal is a 500 kcal deficit per day to safely lose about 1 lb (0.45 kg) per week.</li>
            <li><b>Nutrition First:</b> Focus on eating nutrient-dense foods (vegetables, lean proteins, whole grains) rather than simply eating fewer calories of heavily processed foods.</li>
            <li><b>Metabolism:</b> Remember that you also burn 'base' calories simply by living (your BMR/TDEE). The exercise calories calculated here are <i>additional</i> calories burned.</li>
            <li><b>Hydration:</b> Many times, thirst mimics hunger. Be sure to drink plenty of water daily!</li>
            <li><b>Consistency:</b> Focus on long-term trends rather than daily fluctuations. Weight can change daily based on water retention.</li>
        </ul>
        <br>
        <p><i>Note: Please consult with a healthcare professional before starting any restrictive diet or intensive exercise program.</i></p>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Weight Loss Information")
        msg_box.setText("<b>Healthy Weight Loss Principles</b>")
        msg_box.setInformativeText(info_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

    def show_about_dialog(self):
        about_text = """
        <img src="icon.png" width="48" height="48" style="float: left; margin-right: 15px;">
        <h2 style='color: #4ADE80; margin-bottom: 0px;'>Verdure 26</h2>
        <p style='color: #A0A0A0; margin-top: 0px;'><i>Your Personal Health & Fitness Dashboard</i></p>
        
        <p><b>Version:</b> 26.0<br>
        <b>Built with:</b> Python 3 & PyQt6<br>
        <b>Database:</b> SQLite3</p>
        
        <hr style='border: 0; border-top: 1px solid #333333;'>
        
        <p>Verdure is designed to help you track your daily caloric intake, monitor exercise output, and intelligently plan weight goals based on standard metabolic mathematics.</p>
        
        <p><i>"Stay healthy, track your progress."</i></p>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About Verdure")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        
        # Style the QMessageBox specifically
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1E1E1E;
                color: white;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 14px;
            }
            QPushButton {
                padding: 6px 20px;
                border-radius: 6px;
                background-color: #22C55E;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
        """)
        msg_box.exec()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calorie_logs (
                date TEXT PRIMARY KEY,
                calories_consumed INTEGER,
                calories_burned INTEGER
            )
        ''')
        
        # Add water_consumed column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE calorie_logs ADD COLUMN water_consumed INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass # Column already exists
            
        self.conn.commit()

    def add_one_glass(self):
        current_text = self.water_entry.text()
        current_val = int(current_text) if current_text else 0
        self.water_entry.setText(str(current_val + 1))

    def open_exercise_calculator(self):
        dialog = ExerciseCalculatorDialog(self)
        if dialog.exec():
            calculated_cal = dialog.get_calories()
            # If there's already a value, add to it, otherwise set it
            current_text = self.burned_entry.text()
            current_cal = int(current_text) if current_text else 0
            self.burned_entry.setText(str(current_cal + calculated_cal))

    def update_today_summary(self):
        """Update dashboard stats based on the selected date."""
        selected_date = self.date_picker.date().toString("yyyy-MM-dd")
        cursor = self.conn.cursor()
        
        # We catch an error gracefully if the column doesn't exist yet for some reason
        try:
            cursor.execute('SELECT calories_consumed, calories_burned, water_consumed FROM calorie_logs WHERE date = ?', (selected_date,))
            row = cursor.fetchone()
        except sqlite3.OperationalError:
            cursor.execute('SELECT calories_consumed, calories_burned FROM calorie_logs WHERE date = ?', (selected_date,))
            row = cursor.fetchone()
            if row:
                row = (*row, 0)
        
        if row:
            consumed, burned, water = row
            if water is None: water = 0
            
            net = consumed - burned
            self.net_cal_label.setText(f"{net} kcal")
            self.detail_label.setText(f"Consumed: {consumed}  |  Burned: {burned}")
            self.water_label.setText(f"💧 Water: {water} glasses")
            
            # Color coding for net calories
            if net > 2500: # Arbitrary high threshold for visual feedback
                self.net_cal_label.setStyleSheet("color: #EF4444;") # Red
            elif net < 1500:
                self.net_cal_label.setStyleSheet("color: #FBBF24;") # Yellow
            else:
                self.net_cal_label.setStyleSheet("color: #4ADE80;") # Green
        else:
            self.net_cal_label.setText("No Data")
            self.net_cal_label.setStyleSheet("color: #A0A0A0;")
            self.detail_label.setText("Enter your logs for the selected date.")
            self.water_label.setText("💧 Water: 0 glasses")

    def save_daily_log(self):
        try:
            selected_date = self.date_picker.date().toString("yyyy-MM-dd")
            consumed_text = self.consumed_entry.text()
            burned_text = self.burned_entry.text()
            water_text = self.water_entry.text()
            
            if not consumed_text or not burned_text:
                raise ValueError("Fields cannot be empty")

            consumed = int(consumed_text)
            burned = int(burned_text)
            water = int(water_text) if water_text else 0

            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO calorie_logs (date, calories_consumed, calories_burned, water_consumed)
                VALUES (?, ?, ?, ?)
            ''', (selected_date, consumed, burned, water))
            
            self.conn.commit()
            
            self.consumed_entry.clear()
            self.burned_entry.clear()
            self.water_entry.clear()
            self.load_history()
            self.update_today_summary()

        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values for calories.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save log: {str(e)}")

    def load_history(self):
        self.history_table.setRowCount(0)
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('SELECT date, calories_consumed, calories_burned, water_consumed FROM calorie_logs ORDER BY date DESC')
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            cursor.execute('SELECT date, calories_consumed, calories_burned FROM calorie_logs ORDER BY date DESC')
            rows = [(*r, 0) for r in cursor.fetchall()]
        
        for row_data in rows:
            date_str, consumed, burned, water = row_data
            if water is None: water = 0
            net_calories = consumed - burned
            
            row_position = self.history_table.rowCount()
            self.history_table.insertRow(row_position)
            
            # Display items
            item_date = QTableWidgetItem(str(date_str))
            item_cons = QTableWidgetItem(str(consumed))
            item_burn = QTableWidgetItem(str(burned))
            item_net = QTableWidgetItem(str(net_calories))
            item_water = QTableWidgetItem(str(water))
            
            # Center alignment for numeric columns
            item_cons.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_burn.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_net.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_water.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Color code net calories lightly in table
            if net_calories > 2500:
                item_net.setForeground(QColor("#EF4444"))
            elif net_calories < 1500:
                item_net.setForeground(QColor("#FBBF24"))
            else:
                item_net.setForeground(QColor("#4ADE80"))
                
            # Color code water
            item_water.setForeground(QColor("#38BDF8"))

            self.history_table.setItem(row_position, 0, item_date)
            self.history_table.setItem(row_position, 1, item_cons)
            self.history_table.setItem(row_position, 2, item_burn)
            self.history_table.setItem(row_position, 3, item_net)
            self.history_table.setItem(row_position, 4, item_water)
            
        self.update_chart()

    def update_chart(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT date, calories_consumed, calories_burned 
            FROM calorie_logs 
            ORDER BY date DESC LIMIT 14
        ''')
        rows = cursor.fetchall()
        
        # Chronological order
        rows.reverse()
        
        y_data = []
        x_labels = []
        
        for i, row in enumerate(rows):
            date_str, consumed, burned = row
            net = consumed - burned
            y_data.append(net)
            x_labels.append((i, date_str[-5:])) # Just MM-DD
            
        x_data = list(range(len(y_data)))
        
        self.plot_curve.setData(x_data, y_data)
        
        bottom_axis = self.plot_widget.getAxis('bottom')
        bottom_axis.setTicks([x_labels, []])

    def delete_log(self):
        selected_rows = set(item.row() for item in self.history_table.selectedIndexes())
        if not selected_rows:
            return
        
        reply = QMessageBox.question(
            self, 'Confirm Deletion', 
            "Are you sure you want to delete the selected log(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for row in sorted(selected_rows, reverse=True):
                date_to_delete = self.history_table.item(row, 0).text()
                cursor = self.conn.cursor()
                cursor.execute('DELETE FROM calorie_logs WHERE date = ?', (date_to_delete,))
                self.conn.commit()
                self.history_table.removeRow(row)
            
            self.update_today_summary()
            self.update_chart()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Optional: Set global font hinting and quality styles if needed via app
    app.setStyle("Fusion")
    
    main_window = CalorieTrackerApp()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
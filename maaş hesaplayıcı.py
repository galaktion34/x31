import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QGridLayout, QGroupBox, QVBoxLayout, QCheckBox, \
    QRadioButton, QLabel, QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy, QHBoxLayout, QTabWidget, QComboBox
from PyQt5.QtGui import QPalette, QColor

class EmployeeTab(QFrame):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def update_half_day_salary_input(self):
        half_day_selected = any(day_type.currentText() == "Yarım Gün" for day_type in self.day_type_var)
        self.half_day_salary_input.setEnabled(half_day_selected)    

    def get_employee_data(self):
        data = {
        "name": self.name_input.text(),  # Çalışan adını al
        "days": [day.isChecked() for day in self.days_var],
        "day_types": [day_type.currentIndex() for day_type in self.day_type_var],
        "salary": [salary.isChecked() for salary in self.salary_var],
        "custom_salary": self.custom_salary.text(),
        "tip": self.tip_input.text()
        }
        return data
    
    def set_employee_data(self, data):
        self.name_input.setText(data["name"])  # Çalışan adını ayarla
        # Diğer verileri ayarla
        for i, (day, day_type) in enumerate(zip(data["days"], data["day_types"])):
            self.days_var[i].setChecked(day)
            self.day_type_var[i].setCurrentIndex(day_type)
        for i, salary in enumerate(data["salary"]):
            self.salary_var[i].setChecked(salary)
        self.custom_salary.setText(data["custom_salary"])
        self.tip_input.setText(data["tip"])

        # Bahşiş tutarını ayarla
        if "tip" in data:
            self.tip_input.setText(data["tip"])
        else:
            self.tip_input.setText("0")

    def init_ui(self):
        layout = QGridLayout(self)

        # Çalışan adı için QLineEdit ekle
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Çalışan Adı")
        layout.addWidget(self.name_input, 0, 0, 1, 2)  # İlk satıra yerleştir

        # Diğer bileşenlerin yerleşimini bir satır aşağı kaydır
        days_frame = self.create_days_frame()
        layout.addWidget(days_frame, 1, 0, 1, 1)

        salary_frame = self.create_salary_frame()
        layout.addWidget(salary_frame, 1, 1, 1, 1)

        self.update_half_day_salary_input() 

        tip_frame = self.create_tip_frame()
        layout.addWidget(tip_frame, 2, 0, 1, 1)

        result_frame = self.create_result_frame()
        layout.addWidget(result_frame, 2, 1, 1, 1)

    def create_days_frame(self):
        frame = QGroupBox("Çalışılan Günler")
        layout = QVBoxLayout(frame)

        self.days_var = [QCheckBox(day) for day in
                         ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]]

        self.day_type_var = [QComboBox() for _ in range(7)]

        for day_type in self.day_type_var:
            day_type.addItem("Tam Gün")
            day_type.addItem("Yarım Gün")
            day_type.currentIndexChanged.connect(self.update_half_day_salary_input)

        for i, day in enumerate(self.days_var):
            day_layout = QHBoxLayout()
            day_layout.addWidget(day)
            day_layout.addWidget(self.day_type_var[i])
            layout.addLayout(day_layout)

        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return frame

    def create_salary_frame(self):
        frame = QGroupBox("Günlük Maaş")
        layout = QVBoxLayout(frame)

        self.salary_var = [QCheckBox(f"{salary} TL") for salary in [250, 300, 350, 400, 450, 500]]

        for salary in self.salary_var:
            layout.addWidget(salary)

        custom_salary_layout = QHBoxLayout()
        self.custom_salary = QLineEdit()
        self.custom_salary.setPlaceholderText("Özel maaş girin")
        custom_salary_layout.addWidget(QLabel("Özel:"))
        custom_salary_layout.addWidget(self.custom_salary)
        layout.addLayout(custom_salary_layout)
        
        self.half_day_salary_input = QLineEdit()
        self.half_day_salary_input.setPlaceholderText("Maaş")
        layout.addWidget(QLabel("Yarım Gün:"))
        layout.addWidget(self.half_day_salary_input)

        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return frame

    def on_salary_checked(self, state, salary):
        for i in range(len(self.salary_var)):
            if self.salary_var[i].text().startswith(str(salary)):
                self.salary_var[i].setChecked(state)

    def create_tip_frame(self):
        frame = QGroupBox("Bahşiş")
        layout = QVBoxLayout(frame)

        tip_label = QLabel("Bahşiş")
        self.tip_input = QLineEdit()

        layout.addWidget(tip_label)
        layout.addWidget(self.tip_input)
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        return frame

    def create_result_frame(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)

        self.calculate_button = QPushButton("Hesapla", clicked=self.calculate_salary)
        self.reset_button = QPushButton("Sıfırla", clicked=self.reset)
        self.result_label = QLabel("Maaş: 0 TL")
        self.result_label.setStyleSheet("color: red")

        layout.addWidget(self.calculate_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.result_label)
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        return frame

    def calculate_salary(self):
        days_worked = 0
        half_days_worked = 0

        for day_var, day_type in zip(self.days_var, self.day_type_var):
            if day_var.isChecked():
                if day_type.currentText() == "Tam Gün":
                    days_worked += 1
                elif day_type.currentText() == "Yarım Gün":
                    half_days_worked += 1

        salary_per_day = 0
        for index, salary in enumerate([250, 300, 350, 400, 450, 500]):
            if self.salary_var[index].isChecked():
                salary_per_day += salary

        custom_salary = self.custom_salary.text().strip()

        try:
            salary_per_day += int(custom_salary)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir özel maaş miktarı giriniz.")
            return
        try:
            tip_amount = int(self.tip_input.text())
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir bahşiş miktarı giriniz.")
            return

        half_day_salary = 0
        if half_days_worked > 0:  # Yarım gün sayısı sıfırdan büyükse  
            try:
                half_day_salary = int(self.half_day_salary_input.text())
            except ValueError:
                QMessageBox.warning(self, "Hata", "Lütfen geçerli bir yarım gün maaşı giriniz.")
                return

        salary = days_worked * salary_per_day + half_days_worked * half_day_salary + tip_amount
        self.result_label.setText(f"Toplam: {salary} TL")
        self.result_label.setStyleSheet("color: green")

    def reset(self):
        self.result_label.setText("Maaş: 0 TL")
        self.result_label.setStyleSheet("color: red")    

class SalaryCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # Set dark color palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Highlight, QColor(255, 102, 0))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

        self.setPalette(dark_palette)
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: #222222; border: 1px solid white; }")

    def init_ui(self):
        self.setWindowTitle("Maaş Hesaplayıcı")
        self.setGeometry(300, 300, 600, 450)
        self.center()

        main_frame = QFrame(self)
        main_layout = QVBoxLayout(main_frame)
        self.setCentralWidget(main_frame)

        self.employee_selector = QComboBox()
        main_layout.addWidget(self.employee_selector)

        self.employee_tabs = [EmployeeTab() for _ in range(20)]

        for index, employee_tab in enumerate(self.employee_tabs, start=1):
            self.employee_selector.addItem(f"Çalışan {index}")

        self.current_employee_tab = self.employee_tabs[0]
        main_layout.addWidget(self.current_employee_tab)

        self.employee_selector.currentIndexChanged.connect(self.change_employee_tab)

        self.load_employee_data()   

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def change_employee_tab(self, index):
        self.centralWidget().layout().removeWidget(self.current_employee_tab)
        self.current_employee_tab.hide()
        self.current_employee_tab = self.employee_tabs[index]
        self.centralWidget().layout().addWidget(self.current_employee_tab)
        self.current_employee_tab.show()  
    
    def closeEvent(self, event):
        self.save_employee_data()
        event.accept()

    def save_employee_data(self):
        employee_data = []
        for employee_tab in self.employee_tabs:
            employee_data.append(employee_tab.get_employee_data())
        
        with open("employee_data.json", "w") as outfile:
            json.dump(employee_data, outfile)

    def load_employee_data(self):
        if os.path.exists("employee_data.json"):
            with open("employee_data.json", "r") as infile:
                employee_data = json.load(infile)

            for employee_tab, data in zip(self.employee_tabs, employee_data):
                try:
                    employee_tab.set_employee_data(data)
                except Exception as e:
                    print(f"Error loading employee data: {e}")
            # Özel maaş ve bahşiş tutarını sıfırla
            for employee_tab in self.employee_tabs:
                employee_tab.custom_salary.setText("0")
                employee_tab.tip_input.setText("0")

            # Bahşiş tutarını sıfırla
            for employee_tab in self.employee_tabs:
                employee_tab.tip_input.setText("0")                          

if __name__ == "__main__":
    app = QApplication(sys.argv)
    salary_calculator = SalaryCalculator()
    salary_calculator.show()
    sys.exit(app.exec_())
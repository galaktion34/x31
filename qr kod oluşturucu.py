import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QFrame
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import qrcode
from io import BytesIO
from PIL import Image


class QRCodeGenerator(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('QR Kod Oluşturucu')

        layout = QVBoxLayout()

        self.website_edit = QLineEdit()
        layout.addWidget(QLabel('Web Sitesi:'))
        layout.addWidget(self.website_edit)

        generate_website_button = QPushButton('Web Sitesi QR Kodu Oluştur')
        generate_website_button.clicked.connect(self.generate_website_qrcode)
        layout.addWidget(generate_website_button)

        self.wifi_edit = QLineEdit()
        layout.addWidget(QLabel('WiFi SSID:'))
        layout.addWidget(self.wifi_edit)

        self.wifi_password_edit = QLineEdit()
        layout.addWidget(QLabel('WiFi Parola:'))
        layout.addWidget(self.wifi_password_edit)

        generate_wifi_button = QPushButton('WiFi QR Kodu Oluştur')
        generate_wifi_button.clicked.connect(self.generate_wifi_qrcode)
        layout.addWidget(generate_wifi_button)

        self.qrcode_label = QLabel()
        self.qrcode_label.setFixedSize(300, 300)  # QLabel boyutunu istediğiniz değere ayarlayın
        self.qrcode_label.setScaledContents(True)
        self.qrcode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.qrcode_label)

        save_button = QPushButton('QR Kodu Kaydet')
        save_button.clicked.connect(self.save_qrcode)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def generate_website_qrcode(self):
        website_text = self.website_edit.text()
        self.generate_qrcode(website_text)

    def generate_wifi_qrcode(self):
        wifi_ssid = self.wifi_edit.text()
        wifi_password = self.wifi_password_edit.text()
        wifi_text = f"WIFI:S:{wifi_ssid};T:WPA;P:{wifi_password};;"
        self.generate_qrcode(wifi_text)

    def generate_qrcode(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="transparent").convert("RGBA")
        img = img.resize((300, 300))  # QPixmap boyutunu istediğiniz değere ayarlayın
        qim = QImage(img.tobytes("raw", "RGBA"), img.size[0], img.size[1], QImage.Format.Format_RGBA8888)
        pix = QPixmap.fromImage(qim)
        self.qrcode_label.setPixmap(pix)

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        qrcode_image = QImage.fromData(buffer.read(), "PNG")
        pixmap = QPixmap.fromImage(qrcode_image)
        self.qrcode_label.setPixmap(pixmap)

    def save_qrcode(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save QR Code", "", "PNG Files (*.png);;All Files (*)")
        if file_name:
            pixmap = self.qrcode_label.pixmap()
            pixmap.save(file_name)

def main():
    app = QApplication(sys.argv)
    window = QRCodeGenerator()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

import sys
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from StatinoeryStore import StationeryStoreUI
import hashlib
class FadeLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 1px solid #6B5AE8;
                border-radius: 8px;
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6B5AE8;
            }
        """)
        self.setMinimumHeight(45)

class LoginApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Văn Phòng Mơ Ước ✨')
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon("image/store2.png"))
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1A1A;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #6B5AE8;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8677FF;
            }
            QPushButton:pressed {
                background-color: #5646CC;
            }
            #titleLabel {
                font-size: 38px;
                font-weight: bold;
                color: #FFFFFF;
            }
            #subtitleLabel {
                font-size: 16px;
                color: #888888;
                margin-top: 10px;
            }
            #switchButton {
                background-color: transparent;
                color: #6B5AE8;
                border: none;
                padding: 5px;
                font-size: 14px;
            }
            #switchButton:hover {
                color: #8677FF;
            }
        """)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left Panel
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #121212;") 
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(50, 50, 50, 50)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Store icon
        store_icon = QLabel()
        store_pixmap = QPixmap("image/store2.png")
        if not store_pixmap.isNull():
            store_pixmap = store_pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, 
                                             Qt.TransformationMode.SmoothTransformation)
        store_icon.setPixmap(store_pixmap)
        store_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Welcome text
        welcome_label = QLabel("Chào mừng đến với\nVăn Phòng Mơ Ước ✨")
        welcome_label.setObjectName("titleLabel")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setWordWrap(True)

        subtitle_label = QLabel("Gợi lên sự sáng tạo và chuyên nghiệp")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        left_layout.addStretch(1)
        left_layout.addWidget(store_icon)
        left_layout.addSpacing(30)
        left_layout.addWidget(welcome_label)
        left_layout.addWidget(subtitle_label)
        left_layout.addStretch(1)

        # Right Panel
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #1A1A1A;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(50, 50, 50, 50)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login Form
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # Login Title
        login_title = QLabel("Đăng Nhập")
        login_title.setObjectName("titleLabel")
        
        login_subtitle = QLabel("Đăng nhập vào tài khoản của bạn")
        login_subtitle.setObjectName("subtitleLabel")

        # Input fields
        self.username_input = FadeLineEdit("Tên đăng nhập")
        self.password_input = FadeLineEdit("Mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Login button container with center alignment
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login button
        login_button = QPushButton("Đăng Nhập")
        login_button.setFixedSize(200, 45)
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.clicked.connect(self.login)
        login_button.setStyleSheet("""
        QPushButton {
            background-color: #6B5AE8;
            color: white;
            border: 2px solid #8677FF;
            border-radius: 16px;
            padding: 9px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #8677FF;
            border: 2px solid #9989FF;
        }
        QPushButton:pressed {
            background-color: #5646CC;
            border: 2px solid #6B5AE8;
        }
        """)

        button_layout.addWidget(login_button)
        # Add widgets to form
        form_layout.addWidget(login_title)
        form_layout.addWidget(login_subtitle)
        form_layout.addSpacing(40)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(20)
        form_layout.addWidget(button_container)

        # Add form to right panel with stretches for vertical centering
        right_layout.addStretch(1)
        right_layout.addWidget(form_container)
        right_layout.addStretch(1)

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ thông tin đăng nhập")
            return
        
        user_data = self.db.validate_login(username, password)
        
        if user_data:
            user_role = user_data['role']  # Lấy role từ CSDL

            QMessageBox.information(
                self, 
                "Thành công", 
                f"Chào mừng {user_data['username']} đã đăng nhập thành công với vai trò {user_role}!"
            )
            
            # Mở giao diện chính với role
            self.main_window = StationeryStoreUI(user_role=user_role)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng")


class Database:
    def __init__(self, host="localhost", user="root", password="", database="quanlyvanphongpham"):
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.conn.cursor(dictionary=True)  # ✅ Sử dụng dictionary cursor
        except mysql.connector.Error as err:
            print(f"Database Error: {err}")

    
    def validate_login(self, username, password):
        """Kiểm tra đăng nhập với mật khẩu đã mã hóa SHA-256"""
        try:
            # Truy vấn lấy mật khẩu đã mã hóa từ database
            query = "SELECT username, password, role FROM users WHERE username = %s"
            self.cursor.execute(query, (username,))
            user = self.cursor.fetchone()

            if user:
                hashed_input_password = hashlib.sha256(password.encode()).hexdigest()  # Mã hóa mật khẩu nhập vào
                
                # So sánh mật khẩu đã mã hóa
                if hashed_input_password == user["password"]:
                    return {"username": user["username"], "role": user["role"]}
                else:
                    return None  # Mật khẩu không khớp
            else:
                return None  # Không tìm thấy tài khoản

        except mysql.connector.Error as err:
            print(f"Query Error: {err}")
            return None


    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())
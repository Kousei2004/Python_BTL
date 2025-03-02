from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                              QFormLayout, QComboBox, QMessageBox, QHeaderView, QCheckBox)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import QSize
import mysql.connector
import hashlib

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="quanlyvanphongpham"
    )

class UserManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title section
        title_layout = QHBoxLayout()
        title = QLabel("Quản Lý Phân Quyền")
        title.setFont(QFont("Arial", 14, QFont.Bold))

        clear_icon = QPushButton()
        clear_icon.setIcon(QIcon("image/broom.png"))
        clear_icon.setFixedSize(32, 32)
        clear_icon.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-radius: 5px;  
            }
        """)
        clear_icon.setToolTip("Làm mới danh sách")
        clear_icon.clicked.connect(self.clear_form)

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(clear_icon)
        layout.addLayout(title_layout)

        # Form section
        form_widget = QWidget()
        form_layout = QFormLayout()

        self.user_id = QLineEdit()
        self.user_id.setPlaceholderText("Tự động tạo mã mới")
        self.user_id.setReadOnly(True)

        self.username = QLineEdit()
        self.email = QLineEdit()
        
        # Password section with checkbox
        password_widget = QWidget()
        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.change_password_checkbox = QCheckBox("Đổi mật khẩu")
        self.change_password_checkbox.setChecked(True)  # Mặc định checked khi thêm mới
        self.change_password_checkbox.stateChanged.connect(self.toggle_password)
        
        password_layout.addWidget(self.password)
        password_layout.addWidget(self.change_password_checkbox)
        password_widget.setLayout(password_layout)
        
        self.role = QComboBox()
        self.role.addItems(["Admin", "Nhanvien"])

        form_layout.addRow("Mã người dùng:", self.user_id)
        form_layout.addRow("Tên đăng nhập:", self.username)
        form_layout.addRow("Email:", self.email)
        form_layout.addRow("Mật khẩu:", password_widget)
        form_layout.addRow("Quyền:", self.role)

        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)

        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm theo tên đăng nhập hoặc email...")
        
        search_button = QPushButton(" Tìm kiếm")
        search_button.setIcon(QIcon("search_icon.png"))
        search_button.setIconSize(QSize(24, 24))
        search_button.clicked.connect(self.search_users)
        search_button.setStyleSheet("""
            QPushButton {
                padding: 8px 50px;
                border-radius: 4px;
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Action buttons
        self.add_button = QPushButton("Thêm")
        self.edit_button = QPushButton("Sửa")
        self.delete_button = QPushButton("Xóa")
        self.clear_button = QPushButton("Làm mới")

        button_layout = QHBoxLayout()
        for button in [self.add_button, self.edit_button, self.delete_button, self.clear_button]:
            button.setStyleSheet("""
                QPushButton {
                    padding: 8px 15px;
                    border-radius: 4px;
                    background-color: #2196F3;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            button_layout.addWidget(button)

        layout.addLayout(button_layout)

        # Users table
        self.users_table = QTableWidget(0, 4)
        self.users_table.setHorizontalHeaderLabels([
            "Mã người dùng", "Tên đăng nhập", "Email", "Quyền"
        ])
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.cellClicked.connect(self.select_user)
        layout.addWidget(self.users_table)

        # Connect buttons to functions
        self.add_button.clicked.connect(self.add_user)
        self.edit_button.clicked.connect(self.edit_user)
        self.delete_button.clicked.connect(self.delete_user)
        self.clear_button.clicked.connect(self.load_data)

        self.setLayout(layout)
        self.load_data()

    def toggle_password(self, state):
        """Enable/disable password field based on checkbox state"""
        if not self.user_id.text():  # Nếu đang thêm mới
            self.password.setEnabled(True)
            self.change_password_checkbox.setChecked(True)
            return
            
        self.password.setEnabled(state)
        if state:
            self.password.clear()
        else:
            self.password.setText("********")  # Placeholder for unchanged password

    def hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def load_data(self):
        self.users_table.setRowCount(0)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT userID, username, email, role FROM users")
        for row_data in cursor.fetchall():
            row = self.users_table.rowCount()
            self.users_table.insertRow(row)
            for col, data in enumerate(row_data):
                self.users_table.setItem(row, col, QTableWidgetItem(str(data)))
        conn.close()

    def search_users(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.users_table.rowCount()):
            username = self.users_table.item(row, 1).text().lower()
            email = self.users_table.item(row, 2).text().lower()
            match = keyword in username or keyword in email
            self.users_table.setRowHidden(row, not match)

    def select_user(self, row, column):
        self.clear_form()
        self.user_id.setText(self.users_table.item(row, 0).text())
        self.username.setText(self.users_table.item(row, 1).text())
        self.email.setText(self.users_table.item(row, 2).text())
        self.password.setText("********")  # Placeholder for existing password
        self.password.setEnabled(False)
        self.change_password_checkbox.setChecked(False)
        
        role_text = self.users_table.item(row, 3).text()
        index = self.role.findText(role_text)
        if index >= 0:
            self.role.setCurrentIndex(index)

    def validate_input(self):
        if not self.username.text() or not self.email.text():
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return False
            
        # Kiểm tra mật khẩu chỉ khi thêm mới hoặc có chọn đổi mật khẩu
        if (not self.user_id.text() or self.change_password_checkbox.isChecked()) and not self.password.text():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu!")
            return False
            
        return True

    def add_user(self):
        if not self.validate_input():
            return

        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            hashed_password = self.hash_password(self.password.text())
            sql = "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)"
            values = (
                self.username.text(),
                self.email.text(),
                hashed_password,
                self.role.currentText()
            )
            cursor.execute(sql, values)
            conn.commit()
            QMessageBox.information(self, "Thành công", "Tài khoản đã được tạo!")
            self.clear_form()
            self.load_data()
        except mysql.connector.IntegrityError as e:
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập hoặc email đã tồn tại!")
        finally:
            conn.close()

    def edit_user(self):
        if not self.user_id.text():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn tài khoản để sửa!")
            return

        if not self.validate_input():
            return

        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            if self.change_password_checkbox.isChecked():  # Nếu có đổi mật khẩu
                hashed_password = self.hash_password(self.password.text())
                sql = "UPDATE users SET username=%s, email=%s, password=%s, role=%s WHERE userID=%s"
                values = (
                    self.username.text(),
                    self.email.text(),
                    hashed_password,
                    self.role.currentText(),
                    self.user_id.text()
                )
            else:  # Nếu không đổi mật khẩu
                sql = "UPDATE users SET username=%s, email=%s, role=%s WHERE userID=%s"
                values = (
                    self.username.text(),
                    self.email.text(),
                    self.role.currentText(),
                    self.user_id.text()
                )
            cursor.execute(sql, values)
            conn.commit()
            QMessageBox.information(self, "Thành công", "Thông tin tài khoản đã được cập nhật!")
            self.clear_form()
            self.load_data()
        except mysql.connector.IntegrityError as e:
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập hoặc email đã tồn tại!")
        finally:
            conn.close()

    def delete_user(self):
        if not self.user_id.text():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn tài khoản để xóa!")
            return

        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa tài khoản này?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE userID=%s", (self.user_id.text(),))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Thành công", "Tài khoản đã được xóa!")
            self.clear_form()
            self.load_data()

    def clear_form(self):
        self.user_id.clear()
        self.username.clear()
        self.email.clear()
        self.password.clear()
        self.password.setEnabled(True)
        self.change_password_checkbox.setChecked(True)
        self.role.setCurrentIndex(0)
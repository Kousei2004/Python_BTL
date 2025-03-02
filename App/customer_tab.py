import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                               QTableWidget, QTableWidgetItem, QFormLayout, QComboBox,QHeaderView, QTabWidget, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
import mysql.connector

from database import connect_db

class CustomerManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_customers()
    
    def init_ui(self):
        layout = QVBoxLayout()
    
        # Tạo layout ngang để chứa tiêu đề và nút chổi
        title_layout = QHBoxLayout()
        
        title = QLabel("Quản Lý Khách Hàng")
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
        title_layout.addStretch()  # Đẩy icon về góc phải
        title_layout.addWidget(clear_icon)

        layout.addLayout(title_layout)
        
        form_layout = QFormLayout()
        self.customer_id = QLineEdit()
        self.customer_id.setPlaceholderText("Tự động tạo mã mới")
        self.customer_id.setReadOnly(True)
        self.customer_name = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.address = QLineEdit()
        self.membership = QComboBox()
        self.membership.addItems(["Thường", "Bạc", "Vàng", "Kim Cương"])
        
        form_layout.addRow("Mã KH:", self.customer_id)
        form_layout.addRow("Tên KH:", self.customer_name)
        form_layout.addRow("Số ĐT:", self.phone)
        form_layout.addRow("Email:", self.email)
        form_layout.addRow("Địa chỉ:", self.address)
        form_layout.addRow("Hạng TV:", self.membership)
        layout.addLayout(form_layout)
        
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Lọc theo danh mục:")
        self.filter_category = QComboBox()
        self.filter_category.addItem("Tất cả")
        self.filter_category.addItems(["Thường", "Bạc", "Vàng", "Kim Cương"])
        self.filter_category.currentIndexChanged.connect(self.filter_customers)
        

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_category)
        layout.addLayout(filter_layout)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập tên sản phẩm...")
        search_button = QPushButton("Tìm kiếm")
        search_button.clicked.connect(self.search_customer)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Thêm")
        self.edit_button = QPushButton("Sửa")
        self.delete_button = QPushButton("Xóa")
        self.clear_button = QPushButton("Làm mới")
        
        for button in [self.add_button, self.edit_button, self.delete_button, self.clear_button]:
            button_layout.addWidget(button)
        layout.addLayout(button_layout)
        
        self.customer_table = QTableWidget(0, 6)
        self.customer_table.setHorizontalHeaderLabels([
            "Mã KH", "Tên KH", "Số ĐT", "Email", "Địa chỉ", "Hạng TV"
        ])
        header = self.customer_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.customer_table.cellClicked.connect(self.select_customer)
        layout.addWidget(self.customer_table)
        
        
        self.add_button.clicked.connect(self.add_customer)
        self.edit_button.clicked.connect(self.edit_customer)
        self.delete_button.clicked.connect(self.delete_customer)
        self.clear_button.clicked.connect(self.load_customers)
        
        self.load_customers()
        self.setLayout(layout)
    
    def search_customer(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.customer_table.rowCount()):
            name_item = self.customer_table.item(row, 1)  
            code_item = self.customer_table.item(row, 0)  

            if name_item and code_item:
                customer_name = name_item.text().strip().lower()
                customer_code = code_item.text().strip().lower()
                
                
                # Hiển thị hàng nếu từ khóa xuất hiện trong Mã SP hoặc Tên SP
                match = keyword in customer_name or keyword in customer_code
                self.customer_table.setRowHidden(row, not match)
    def select_customer(self, row, column):
        self.clear_form()  # Xóa dữ liệu cũ trên form
        
        # Lấy dữ liệu từ bảng và gán vào form
        self.customer_id.setText(self.customer_table.item(row, 0).text())
        self.customer_name.setText(self.customer_table.item(row, 1).text())
        self.phone.setText(self.customer_table.item(row, 2).text())
        self.email.setText(self.customer_table.item(row, 3).text())
        self.address.setText(self.customer_table.item(row, 4).text())
        
        membership_text = self.customer_table.item(row, 5).text()
        index = self.membership.findText(membership_text)
        if index >= 0:
            self.membership.setCurrentIndex(index)
            
    def load_customers(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM khachhang")
            customers = cursor.fetchall()
            
            self.customer_table.setRowCount(0)
            for row_idx, customer in enumerate(customers):
                self.customer_table.insertRow(row_idx)
                for col_idx, value in enumerate(customer):
                    self.customer_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi Database", f"Lỗi: {err}")
    
    def add_customer(self):
        if not self.validate():
            return 
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO khachhang (tenKH, sdt, email, diaChi, hangThanhVien, diemTichLuy)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                self.customer_name.text(),
                self.phone.text(),
                self.email.text(),
                self.address.text(),
                self.membership.currentText(),
                0
            )
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            QMessageBox.information(self, "Thông báo", "Thêm khách hàng thành công!")
            self.clear_form()
            self.load_customers()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi Database", f"Lỗi: {err}")
    
    def edit_customer(self):
        if not self.validate():
            return 
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            query = """
                UPDATE khachhang 
                SET tenKH = %s, sdt = %s, email = %s, diaChi = %s, hangThanhVien = %s
                WHERE maKH = %s
            """
            values = (
                self.customer_name.text(),
                self.phone.text(),
                self.email.text(),
                self.address.text(),
                self.membership.currentText(),
                self.customer_id.text()
            )
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            QMessageBox.information(self, "Thông báo", "Cập nhật khách hàng thành công!")
            self.clear_form()
            self.load_customers()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi Database", f"Lỗi: {err}")
    
    def delete_customer(self):
        if not self.customer_id.text():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn khách hàng cần xóa")
            return
        
        confirm = QMessageBox.question(self, "Xác nhận xóa", "Bạn có chắc chắn muốn xóa khách hàng này?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM khachhang WHERE maKH = %s", (self.customer_id.text(),))
                conn.commit()
                cursor.close()
                conn.close()
                
                QMessageBox.information(self, "Thông báo", "Xóa khách hàng thành công!")
                self.clear_form()
                self.load_customers()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Lỗi Database", f"Lỗi: {err}")
    
    def clear_form(self):
        self.customer_id.clear()
        self.customer_name.clear()
        self.phone.clear()
        self.email.clear()
        self.address.clear()
        self.membership.setCurrentIndex(0)
        
    
    def filter_customers(self):
        selected_category = self.filter_category.currentText()
        
        for row in range(self.customer_table.rowCount()):
            category_item = self.customer_table.item(row, 5 )
            if category_item:
                category_name = category_item.text().strip()
                is_match = (selected_category == "Tất cả") or (category_name == selected_category)
                self.customer_table.setRowHidden(row, not is_match)
    def validate(self):
        """Kiểm tra dữ liệu nhập có hợp lệ không"""
        ten_kh = self.customer_name.text().strip()
        sdt = self.phone.text().strip()
        email = self.email.text().strip()
        dia_chi = self.address.text().strip()

        # Kiểm tra tên khách hàng
        if not ten_kh:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên khách hàng!")
            return False

        # Kiểm tra số điện thoại (phải có ít nhất 10 số và chỉ chứa số)
        if not sdt.isdigit() or len(sdt) < 10:
            QMessageBox.warning(self, "Cảnh báo", "Số điện thoại phải có ít nhất 10 chữ số và chỉ chứa số!")
            return False

        # Kiểm tra email hợp lệ (chứa @ và .com)
        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Cảnh báo", "Email không hợp lệ! Vui lòng nhập đúng định dạng (ví dụ: example@gmail.com)")
            return False

        # Kiểm tra địa chỉ không để trống
        if not dia_chi:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập địa chỉ khách hàng!")
            return False

        return True  # ✅ Nếu tất cả hợp lệ




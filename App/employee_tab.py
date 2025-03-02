from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                              QFormLayout, QComboBox,QMessageBox,QHeaderView,QFileDialog, QDoubleSpinBox)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import QSize
import mysql.connector

import pandas as pd
from database import connect_db
class EmployeeManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
    
        # Tạo layout ngang để chứa tiêu đề và nút chổi
        title_layout = QHBoxLayout()
        
        title = QLabel("Quản Lý Nhân Viên")
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
        
        # Form thông tin nhân viên
        form_widget = QWidget()
        form_layout = QFormLayout()
        
        # Các trường nhập liệu
        self.employee_id = QLineEdit()
        self.employee_id.setPlaceholderText("Tự động tạo mã mới")
        self.employee_id.setReadOnly(True)  # Không cho sửa mã nhân viên
        
        self.employee_tenNV = QLineEdit()
        self.sdt = QLineEdit()
        self.email = QLineEdit()
        self.diaChi = QLineEdit()
        
        self.money = QDoubleSpinBox()
        self.money.setRange(0, 100000000)
        self.money.setDecimals(2)
        self.money.setSingleStep(1000)
        self.money.setSuffix(" VNĐ")
        
        self.membership = QComboBox()
        self.membership.addItems(["Nhân Viên", "Quản lí", "Bảo Vệ", "Lao Công"])

        # Thêm các trường vào form
        form_layout.addRow("Mã nhân viên:", self.employee_id)
        form_layout.addRow("Tên nhân viên:", self.employee_tenNV)
        form_layout.addRow("Số điện thoại:", self.sdt)
        form_layout.addRow("Email:", self.email)
        form_layout.addRow("Địa chỉ:", self.diaChi)
        form_layout.addRow("Chức vụ:", self.membership)
        form_layout.addRow("Lương:", self.money)
        
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)
        
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Lọc theo danh mục:")
        self.filter_category = QComboBox()
        self.filter_category.addItem("Tất cả")
        self.filter_category.addItems(["Nhân Viên", "Quản lí", "Bảo Vệ", "Lao Công"])
        self.filter_category.currentIndexChanged.connect(self.filter_employee)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_category)
        layout.addLayout(filter_layout)
        
        
        # Ô tìm kiếm
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa tìm kiếm...")
        
        # Nút tìm kiếm có icon
        search_button = QPushButton(" Tìm kiếm")
        search_button.setIcon(QIcon("search_icon.png"))  # Đường dẫn icon
        search_button.setIconSize(QSize(24, 24))  # Kích thước icon
        search_button.clicked.connect(self.search_employee)
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

        # Các nút chức năng
        self.add_button = QPushButton("Thêm")
        self.edit_button = QPushButton("Sửa")
        self.delete_button = QPushButton("Xóa")
        self.clear_button = QPushButton("Làm mới")
        self.export_button = QPushButton("Xuất Excel")

        button_layout = QHBoxLayout()
        for button in [self.add_button, self.edit_button, self.delete_button, self.clear_button, self.export_button]:
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

        
        # Bảng danh sách nhân viên
        self.employee_table = QTableWidget(0, 7)
        self.employee_table.setHorizontalHeaderLabels([
            "Mã NV", "Tên NV", "Chức Vụ", "SDT", "Lương", "Địa Chỉ", "Gmail"
        ])
        header = self.employee_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.employee_table.cellClicked.connect(self.select_employee)
        layout.addWidget(self.employee_table)
        
        self.add_button.clicked.connect(self.add_employee)
        self.edit_button.clicked.connect(self.edit_employee)
        self.delete_button.clicked.connect(self.delete_employee)
        self.clear_button.clicked.connect(self.load_data)
        self.export_button.clicked.connect(self.export_to_excel)
        
        self.setLayout(layout)
        self.load_data()
    
    def filter_employee(self):
        selected_category = self.filter_category.currentText()
        
        for row in range(self.employee_table.rowCount()):
            category_item = self.employee_table.item(row, 2)  # Cột 2 là danh mục
            if category_item:
                category_name = category_item.text().strip()
                is_match = (selected_category == "Tất cả") or (category_name == selected_category)
                self.employee_table.setRowHidden(row, not is_match)
    
    def search_employee(self):
        keyword = self.search_input.text().strip().lower()

        for row in range(self.employee_table.rowCount()):
            name_item = self.employee_table.item(row, 1)  # Cột "Tên NV"
            code_item = self.employee_table.item(row, 0)  # Cột "Mã NV"

            if name_item and code_item:
                employee_name = name_item.text().strip().lower()
                employee_code = code_item.text().strip().lower()

                match = keyword in employee_name or keyword in employee_code
                self.employee_table.setRowHidden(row, not match)

                
    def select_employee(self, row, column):
        self.clear_form()  # Xóa dữ liệu cũ trên form

        # Lấy dữ liệu từ bảng và gán vào form
        self.employee_id.setText(self.employee_table.item(row, 0).text())
        self.employee_tenNV.setText(self.employee_table.item(row, 1).text())
        self.sdt.setText(self.employee_table.item(row, 3).text())
        self.email.setText(self.employee_table.item(row, 6).text())
        self.diaChi.setText(self.employee_table.item(row, 5).text())

        # Đặt giá trị cho ComboBox (Chức vụ)
        chuc_vu_text = self.employee_table.item(row, 2).text()
        index = self.membership.findText(chuc_vu_text)
        if index >= 0:
            self.membership.setCurrentIndex(index)

        # Đặt giá trị cho QDoubleSpinBox (Lương)
        self.money.setValue(float(self.employee_table.item(row, 4).text()))


    def load_data(self):
        self.employee_table.setRowCount(0)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nhanvien")
        for row_data in cursor.fetchall():
            row = self.employee_table.rowCount()
            self.employee_table.insertRow(row)
            for col, data in enumerate(row_data):
                self.employee_table.setItem(row, col, QTableWidgetItem(str(data)))
        conn.close()

    def add_employee(self):
        if not self.validate_inputs():
            return
        conn = connect_db()
        cursor = conn.cursor()
        sql = "INSERT INTO nhanvien (tenNV, sdt, email, diaChi, chucVu, luong) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (
            self.employee_tenNV.text(), self.sdt.text(), self.email.text(), 
            self.diaChi.text(), self.membership.currentText(), 
            self.money.value()
        )
        cursor.execute(sql, values)
        conn.commit()
        conn.close()
        self.load_data()
        QMessageBox.information(self, "Thành công", "Nhân viên đã được thêm!")
        self.clear_form()


    def edit_employee(self):
        row = self.employee_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhân viên để sửa!")
            return
        
        if not self.validate_inputs():
            return
        
        conn = connect_db()
        cursor = conn.cursor()
        sql = "UPDATE nhanvien SET tenNV=%s, sdt=%s, email=%s, diaChi=%s, chucVu=%s, luong=%s WHERE maNV=%s"
        values = (
            self.employee_tenNV.text(), self.sdt.text(), self.email.text(), 
            self.diaChi.text(), self.membership.currentText(), 
            self.money.value(), self.employee_id.text()
        )
        cursor.execute(sql, values)
        conn.commit()
        conn.close()
        self.load_data()
        QMessageBox.information(self, "Thành công", "Thông tin nhân viên đã được cập nhật!")
        self.clear_form()

    def delete_employee(self):
        row = self.employee_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhân viên để xóa!")
            return
        employee_id = self.employee_table.item(row, 0).text()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM nhanvien WHERE maNV=%s", (employee_id,))
        conn.commit()
        conn.close()
        self.load_data()
        QMessageBox.information(self, "Thành công", "Nhân viên đã được xóa!")

    def clear_form(self):
        self.employee_id.clear()
        self.employee_tenNV.clear()
        self.sdt.clear()
        self.email.clear()
        self.diaChi.clear()
        self.money.setValue(0)
        self.membership.setCurrentIndex(0)
        
    def validate_inputs(self):
        """Kiểm tra dữ liệu nhập có hợp lệ không"""
        ten_nv = self.employee_tenNV.text().strip()
        sdt = self.sdt.text().strip()
        email = self.email.text().strip()
        dia_chi = self.diaChi.text().strip()
        chuc_vu = self.membership.currentText()
        luong = self.money.value()

        # Kiểm tra tên nhân viên
        if not ten_nv:
            QMessageBox.warning(self, "Lỗi", "Tên nhân viên không được để trống!")
            return False

        # Kiểm tra số điện thoại (phải có ít nhất 10 số, chỉ chứa số)
        if not sdt.isdigit() or len(sdt) < 10:
            QMessageBox.warning(self, "Lỗi", "Số điện thoại phải có ít nhất 10 chữ số và chỉ chứa số!")
            return False

        # Kiểm tra email hợp lệ
        if "@" not in email or ".com" not in email:
            QMessageBox.warning(self, "Lỗi", "Email không hợp lệ! Vui lòng nhập đúng định dạng (ví dụ: example@gmail.com)")
            return False

        # Kiểm tra địa chỉ
        if not dia_chi:
            QMessageBox.warning(self, "Lỗi", "Địa chỉ không được để trống!")
            return False

        # Kiểm tra lương hợp lệ
        if luong <= 0:
            QMessageBox.warning(self, "Lỗi", "Lương phải lớn hơn 0!")
            return False

        return True  # Nếu tất cả hợp lệ


    def export_to_excel(self):
        # Chọn vị trí lưu file
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu file Excel", "", "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not file_path:
            return  # Nếu không chọn file thì thoát

        # Lấy dữ liệu từ bảng sản phẩm
        data = []
        for row in range(self.product_table.rowCount()):
            row_data = []
            for col in range(self.product_table.columnCount()):
                item = self.product_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Tạo DataFrame từ dữ liệu
        df = pd.DataFrame(data, columns=["Mã NV", "Tên NV", "Số ĐT", "Email", "Địa chỉ", "Chức Vụ", "Lương"])

        try:
            # Xuất dữ liệu ra file Excel
            df.to_excel(file_path, index=False)

            QMessageBox.information(self, "Thành công", "Dữ liệu đã được xuất ra Excel thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất Excel: {e}")

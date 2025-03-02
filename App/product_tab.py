import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                           QTableWidget, QTableWidgetItem, QFormLayout, QComboBox, 
                           QSpinBox, QTabWidget, QFileDialog, QMessageBox,
                           QDoubleSpinBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import QHeaderView
import pandas as pd
import mysql.connector

import pandas as pd
from database import connect_db


class ProductManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
            
        # Tiêu đề
        layout = QVBoxLayout()
    
        # Tạo layout ngang để chứa tiêu đề và nút chổi
        title_layout = QHBoxLayout()
        
        title = QLabel("Quản Lý Sản Phẩm")
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
       
        # Layout chứa form nhập liệu và ảnh sản phẩm
        content_layout = QHBoxLayout()

        # Form nhập thông tin sản phẩm
        form_widget = QWidget()
        form_layout = QFormLayout()

        self.product_id = QLineEdit()
        self.product_id.setPlaceholderText("Tự động tạo mã mới")
        self.product_id.setReadOnly(True)
        self.product_name = QLineEdit()
        self.category = QComboBox()
        self.category.addItems(["Bút", "Sách", "Giấy & Sổ tay","Hồ sơ & Lưu trữ tài liệu", "Dụng cụ hỗ trợ học tập & văn phòng","Đồ dùng cá nhân & phụ kiện văn phòng","Quà tặng & Đồ chơi văn phòng" ,"Khác"])
        self.supplier = QComboBox()
        self.supplier.addItems(["Nhà cung cấp A", "Nhà cung cấp B", "Nhà cung cấp C"])
        self.import_price = QDoubleSpinBox()
        self.import_price.setRange(0, 10000000)
        self.import_price.setSingleStep(1000)
        self.import_price.setSuffix(" VNĐ")
        self.sale_price = QDoubleSpinBox()
        self.sale_price.setRange(0, 20000000)
        self.sale_price.setSingleStep(1000)
        self.sale_price.setSuffix(" VNĐ")
        self.inventory = QSpinBox()    
        self.inventory.setRange(0, 1000000)      
        self.inventory.setSingleStep(1)       
        self.inventory.setSuffix(" Sản phẩm")

        form_layout.addRow("Mã sản phẩm:", self.product_id)
        form_layout.addRow("Tên sản phẩm:", self.product_name)
        form_layout.addRow("Danh mục:", self.category)
        form_layout.addRow("Nhà cung cấp:", self.supplier)
        form_layout.addRow("Giá nhập:", self.import_price)
        form_layout.addRow("Giá bán:", self.sale_price)
        form_layout.addRow("Tồn kho:", self.inventory)

        form_widget.setLayout(form_layout)

        # Widget hiển thị ảnh sản phẩm
        image_widget = QWidget()
        image_layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
        """)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Ảnh sản phẩm")
        self.current_image_path = ""

        upload_button = QPushButton("Tải ảnh lên")
        upload_button.setStyleSheet("""
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
        upload_button.clicked.connect(self.open_image)

        image_layout.addWidget(self.image_label)
        image_layout.addWidget(upload_button)
        image_widget.setLayout(image_layout)

        content_layout.addWidget(form_widget)
        content_layout.addWidget(image_widget)
        layout.addLayout(content_layout)
    
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Lọc theo danh mục:")
        self.filter_category = QComboBox()
        self.filter_category.addItem("Tất cả") 
        self.filter_category.addItems(["Bút", "Sách", "Giấy & Sổ tay","Hồ sơ & Lưu trữ tài liệu", 
                                       "Dụng cụ hỗ trợ học tập & văn phòng","Đồ dùng cá nhân & phụ kiện văn phòng",
                                       "Quà tặng & Đồ chơi văn phòng", "Khác"])
        self.filter_category.currentIndexChanged.connect(self.filter_products)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_category)
        layout.addLayout(filter_layout)

        # Ô tìm kiếm sản phẩm
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập tên sản phẩm...")
        search_button = QPushButton("Tìm kiếm")
        search_button.clicked.connect(self.search_product)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Các nút chức năng
        button_layout = QHBoxLayout()
        add_button = QPushButton("Thêm")
        edit_button = QPushButton("Sửa")
        delete_button = QPushButton("Xóa")
        clear_button = QPushButton("Làm mới")
        export_button = QPushButton("Xuất Excel")
        
        
        add_button.clicked.connect(self.add_product)
        edit_button.clicked.connect(self.edit_product)
        delete_button.clicked.connect(self.delete_product)
        clear_button.clicked.connect(self.load_products)
        export_button.clicked.connect(self.export_to_excel)

        for button in [add_button, edit_button, delete_button, clear_button, export_button]:
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

        # Bảng danh sách sản phẩm
        self.product_table = QTableWidget(0, 8)
        self.product_table.setHorizontalHeaderLabels([
            "Mã SP", "Tên SP", "Danh Mục", "Nhà Cung Cấp",
            "Giá Nhập", "Giá Bán", "Tồn Kho", "Ảnh"
        ])
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.cellClicked.connect(self.select_product)
        layout.addWidget(self.product_table)

        # Load product data
        self.load_products()

        self.setLayout(layout)
    def filter_products(self):
        selected_category = self.filter_category.currentText()
        
        for row in range(self.product_table.rowCount()):
            category_item = self.product_table.item(row, 2)
            if category_item:
                category_name = category_item.text().strip()
                is_match = (selected_category == "Tất cả") or (category_name == selected_category)
                self.product_table.setRowHidden(row, not is_match)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn ảnh sản phẩm",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.current_image_path = file_name
            pixmap = QPixmap(file_name)
            pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

    def search_product(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.product_table.rowCount()):
            name_item = self.product_table.item(row, 1)  # Cột 1: "Tên SP"
            code_item = self.product_table.item(row, 0)  # Cột 0: "Mã SP"

            if name_item and code_item:
                product_name = name_item.text().strip().lower()
                product_code = code_item.text().strip().lower()
                
                # Hiển thị hàng nếu từ khóa xuất hiện trong Mã SP hoặc Tên SP
                match = keyword in product_name or keyword in product_code
                self.product_table.setRowHidden(row, not match)

    def load_products(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sanpham")
            products = cursor.fetchall()
            
            self.product_table.setRowCount(0)
            for row_idx, product in enumerate(products):
                self.product_table.insertRow(row_idx)
                for col_idx, value in enumerate(product):
                    if col_idx != 7:  # Not the image path
                        self.product_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
                    else:
                        image_cell = QTableWidgetItem("Có ảnh" if value else "Không có ảnh")
                        self.product_table.setItem(row_idx, col_idx, image_cell)
            
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi Database", f"Lỗi: {err}")

    def select_product(self, row, column):
        self.clear_form()
        
        # Get data from selected row
        product_id = self.product_table.item(row, 0).text()
        self.product_id.setText(product_id)
        self.product_name.setText(self.product_table.item(row, 1).text())
        
        category_idx = self.category.findText(self.product_table.item(row, 2).text())
        if category_idx >= 0:
            self.category.setCurrentIndex(category_idx)
            
        supplier_idx = self.supplier.findText(self.product_table.item(row, 3).text())
        if supplier_idx >= 0:
            self.supplier.setCurrentIndex(supplier_idx)
            
        self.import_price.setValue(float(self.product_table.item(row, 4).text()))
        self.sale_price.setValue(float(self.product_table.item(row, 5).text()))
        self.inventory.setValue(int(self.product_table.item(row, 6).text()))
    
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT hinhAnh FROM sanpham WHERE maSP = %s", (product_id,))
            image_path = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            if image_path and os.path.exists(image_path):
                self.current_image_path = image_path
                pixmap = QPixmap(image_path)
                pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
                self.image_label.setPixmap(pixmap)
            else:
                self.image_label.setText("Ảnh sản phẩm")
                self.current_image_path = ""
        except Exception as e:
            self.image_label.setText("Ảnh sản phẩm")
            self.current_image_path = ""
            
    def add_product(self):
        if not self.validate_inputs():
            return 
        if not self.product_name.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên sản phẩm")
            return
            
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Save image to a dedicated folder if exists
            image_path = ""
            if self.current_image_path:
                # Create images directory if not exists
                os.makedirs("images", exist_ok=True)
                
                # Get file extension and create new filename
                file_ext = os.path.splitext(self.current_image_path)[1]
                new_filename = f"images/product_{self.product_name.text().replace(' ', '_')}{file_ext}"
                
                # Copy image file
                import shutil
                shutil.copy2(self.current_image_path, new_filename)
                image_path = new_filename
            
            # Insert new product
            query = """
                INSERT INTO sanpham (tenSP, danhMuc, nhaCungCap, giaNhap, giaBan, tonKho, hinhAnh)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                self.product_name.text(),
                self.category.currentText(),
                self.supplier.currentText(),
                self.import_price.value(),
                self.sale_price.value(),
                self.inventory.value(),
                image_path
            )
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            QMessageBox.information(self, "Thông báo", "Thêm sản phẩm thành công!")
            self.clear_form()
            self.load_products()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi Database", f"Lỗi: {err}")
            
    def edit_product(self):
        if not self.product_id.text():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn sản phẩm cần sửa")
            return
            
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Handle image update if needed
            image_path_update = ""
            if self.current_image_path:
                # Check if this is a new image or existing one
                cursor.execute("SELECT hinhAnh FROM sanpham WHERE maSP = %s", (self.product_id.text(),))
                old_image_path = cursor.fetchone()[0]
                
                if self.current_image_path != old_image_path:
                    # Create images directory if not exists
                    os.makedirs("images", exist_ok=True)
                    
                    # Get file extension and create new filename
                    file_ext = os.path.splitext(self.current_image_path)[1]
                    new_filename = f"images/product_{self.product_name.text().replace(' ', '_')}{file_ext}"
                    
                    # Copy image file
                    import shutil
                    shutil.copy2(self.current_image_path, new_filename)
                    image_path_update = new_filename
                else:
                    image_path_update = old_image_path
            
            # Update product
            if image_path_update:
                query = """
                    UPDATE sanpham 
                    SET tenSP = %s, danhMuc = %s, nhaCungCap = %s, 
                        giaNhap = %s, giaBan = %s, tonKho = %s, hinhAnh = %s
                    WHERE maSP = %s
                """
                values = (
                    self.product_name.text(),
                    self.category.currentText(),
                    self.supplier.currentText(),
                    self.import_price.value(),
                    self.sale_price.value(),
                    self.inventory.value(),
                    image_path_update,
                    self.product_id.text()
                )
            else:
                query = """
                    UPDATE sanpham 
                    SET tenSP = %s, danhMuc = %s, nhaCungCap = %s, 
                        giaNhap = %s, giaBan = %s, tonKho = %s
                    WHERE maSP = %s
                """
                values = (
                    self.product_name.text(),
                    self.category.currentText(),
                    self.supplier.currentText(),
                    self.import_price.value(),
                    self.sale_price.value(),
                    self.inventory.value(),
                    self.product_id.text()
                )
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            QMessageBox.information(self, "Thông báo", "Cập nhật sản phẩm thành công!")
            self.clear_form()
            self.load_products()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi Database", f"Lỗi: {err}")
            
    def delete_product(self):
        if not self.product_id.text():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn sản phẩm cần xóa")
            return
            
        confirm = QMessageBox.question(self, "Xác nhận xóa", 
                                       "Bạn có chắc chắn muốn xóa sản phẩm này?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                conn = connect_db()
                cursor = conn.cursor()
                
                # Get image path to delete file
                cursor.execute("SELECT hinhAnh FROM sanpham WHERE maSP = %s", (self.product_id.text(),))
                image_path = cursor.fetchone()[0]
                
                # Delete from database
                cursor.execute("DELETE FROM sanpham WHERE maSP = %s", (self.product_id.text(),))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Delete image file if exists
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)
                
                QMessageBox.information(self, "Thông báo", "Xóa sản phẩm thành công!")
                self.clear_form()
                self.load_products()
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Lỗi Database", f"Lỗi: {err}")
                
    def clear_form(self):
        self.product_id.clear()
        self.product_name.clear()
        self.category.setCurrentIndex(0)
        self.supplier.setCurrentIndex(0)
        self.import_price.setValue(0)
        self.sale_price.setValue(0)
        self.inventory.setValue(0)
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("Ảnh sản phẩm")
        self.current_image_path = ""
        pass
    
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
        df = pd.DataFrame(data, columns=[
            "Mã SP", "Tên SP", "Danh Mục", "Nhà Cung Cấp",
            "Giá Nhập", "Giá Bán", "Tồn Kho", "Ảnh"
        ])

        try:
            # Xuất dữ liệu ra file Excel
            df.to_excel(file_path, index=False)

            QMessageBox.information(self, "Thành công", "Dữ liệu đã được xuất ra Excel thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất Excel: {e}")
            
    def validate_inputs(self):
        errors = []

        # Kiểm tra tên sản phẩm
        product_name = self.product_name.text().strip()
        if not product_name:
            errors.append("Tên sản phẩm không được để trống.\n")

        # Kiểm tra giá nhập
        if self.import_price.value() <= 0:
            errors.append("Giá nhập phải lớn hơn 0.")

        # Kiểm tra giá bán
        if self.sale_price.value() <= self.import_price.value():
            errors.append("Giá bán phải lớn hơn giá nhập.\n")

        # Kiểm tra tồn kho
        if self.inventory.value() < 0:
            errors.append("Tồn kho không thể là số âm.\n")

        # Nếu có lỗi, hiển thị thông báo và trả về False
        if errors:
            QMessageBox.warning(self, "Lỗi nhập liệu", "\n".join(errors))
            return False

        return True

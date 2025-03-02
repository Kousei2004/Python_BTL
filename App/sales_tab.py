from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit,QMessageBox, QTableWidget,QDialog, QSpinBox, QHeaderView, 
                              QTableWidgetItem, QInputDialog)
from PySide6.QtGui import QFont, QPixmap, Qt
from PySide6.QtWidgets import QFrame
import mysql.connector
import os
from database import connect_db

class SalesManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        title = QLabel("Danh Sách Sản Phẩm")
        title.setFont(QFont("Arial", 14, QFont.ExtraBold))
        left_layout.addWidget(title)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Tìm kiếm sản phẩm...")
        left_layout.addWidget(self.search_box)
        
        self.product_table = QTableWidget(0, 4)
        self.product_table.setHorizontalHeaderLabels(["Mã SP", "Tên SP", "Giá", "Tồn Kho"])
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        left_layout.addWidget(self.product_table)

        # Bắt sự kiện khi nhấn vào bảng sản phẩm
        self.product_table.cellDoubleClicked.connect(self.add_to_cart)
        
        left_panel.setLayout(left_layout)
        
        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        cart_title = QLabel("Giỏ Hàng")
        cart_title.setFont(QFont("Arial", 14, QFont.ExtraBold))
        right_layout.addWidget(cart_title)
        
        self.cart_table = QTableWidget(0, 5)
        self.cart_table.setHorizontalHeaderLabels(["Mã SP", "Tên SP", "Số Lượng", "Đơn Giá", "Thành Tiền"])
        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.cellDoubleClicked.connect(self.modify_cart_item)
        right_layout.addWidget(self.cart_table)
        
        # Payment info
        payment_layout = QVBoxLayout()
        self.total_label = QLabel("Tổng tiền: 0 VNĐ")
        self.total_label.setFont(QFont("Arial", 12, QFont.ExtraBold))
        payment_layout.addWidget(self.total_label)
        
        self.save_invoice_button = QPushButton("Lưu Hóa Đơn")  # Nút mới
        self.payment_button = QPushButton("Xuất Hóa Đơn")

        payment_layout.addWidget(self.save_invoice_button)
        payment_layout.addWidget(self.payment_button)

        # Gán sự kiện cho các nút
        self.save_invoice_button.clicked.connect(lambda: self.checkout("Chờ xử lý"))  # Lưu với trạng thái "Chờ xử lý"
        self.payment_button.clicked.connect(lambda: self.checkout("Đã thanh toán"))  # Lưu với trạng thái "Đã thanh toán"
        self.search_box.textChanged.connect(self.search_products)
        
        right_layout.addLayout(payment_layout)
        right_panel.setLayout(right_layout)
        
        # Thêm vào layout chính
        layout.addWidget(left_panel, 2)
        layout.addWidget(right_panel, 1)
          
        self.setLayout(layout)
        
    def search_products(self):
        """Lọc danh sách sản phẩm theo từ khóa tìm kiếm"""
        keyword = self.search_box.text().strip().lower()  # Lấy từ khóa và chuyển thành chữ thường
        for row in range(self.product_table.rowCount()):
            item = self.product_table.item(row, 1)  # Lấy tên sản phẩm từ cột thứ 2
            if item and keyword in item.text().lower():
                self.product_table.setRowHidden(row, False)  # Hiển thị dòng phù hợp
            else:
                self.product_table.setRowHidden(row, True)   # Ẩn dòng không khớp
    def modify_cart_item(self, row, column):
        """Hiển thị hộp thoại xác nhận xóa sản phẩm khỏi giỏ hàng"""
        ma_sp = self.cart_table.item(row, 0).text()
        ten_sp = self.cart_table.item(row, 1).text()

        confirm = QMessageBox.question(self, "Xóa sản phẩm", 
                                    f"Bạn có chắc muốn xóa {ten_sp} khỏi giỏ hàng?", 
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            self.cart_table.removeRow(row)  # Xóa sản phẩm khỏi giỏ hàng
            self.update_total()  # Cập nhật tổng tiền


    def load_products(self):
        """Nạp danh sách sản phẩm từ MySQL vào bảng product_table"""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT maSP, tenSP, giaBan, tonKho FROM sanpham")
            products = cursor.fetchall()
            conn.close()
            
            self.product_table.setRowCount(len(products))
            for row, (ma_sp, ten_sp, gia, ton_kho) in enumerate(products):
                self.product_table.setItem(row, 0, QTableWidgetItem(str(ma_sp)))
                self.product_table.setItem(row, 1, QTableWidgetItem(ten_sp))
                self.product_table.setItem(row, 2, QTableWidgetItem(f"{gia:,} VNĐ"))
                self.product_table.setItem(row, 3, QTableWidgetItem(str(ton_kho)))
                
        except mysql.connector.Error as e:
            print("Lỗi kết nối CSDL:", e)
            
    def update_cart_total(self, row, gia):
        """Cập nhật thành tiền khi số lượng thay đổi"""
        spin_box = self.cart_table.cellWidget(row, 2)
        so_luong = spin_box.value()
        thanh_tien = so_luong * gia
        self.cart_table.setItem(row, 4, QTableWidgetItem(f"{thanh_tien:,.2f} VNĐ"))
        self.update_total()


    from PySide6.QtWidgets import QSpinBox

    def add_to_cart(self, row, column):
        """Thêm sản phẩm vào giỏ hàng với QSpinBox để chỉnh số lượng"""
        ma_sp = self.product_table.item(row, 0).text()
        ten_sp = self.product_table.item(row, 1).text()
        gia = float(self.product_table.item(row, 2).text().replace(",", "").replace(" VNĐ", ""))
        ton_kho = int(self.product_table.item(row, 3).text())
        
        if ton_kho <= 0:
            QMessageBox.warning(self, "Hết hàng", f"Sản phẩm '{ten_sp}' đã hết hàng, không thể thêm vào giỏ!")
            return  # Dừng lại, không thêm vào giỏ

        # Kiểm tra sản phẩm đã có trong giỏ hàng chưa
        for i in range(self.cart_table.rowCount()):
            if self.cart_table.item(i, 0).text() == ma_sp:
                QMessageBox.warning(self, "Lỗi", "Sản phẩm đã có trong giỏ hàng. Vui lòng chỉnh sửa số lượng.")
                return

        row_count = self.cart_table.rowCount()
        self.cart_table.insertRow(row_count)

        self.cart_table.setItem(row_count, 0, QTableWidgetItem(ma_sp))
        self.cart_table.setItem(row_count, 1, QTableWidgetItem(ten_sp))

        spin_box = QSpinBox()
        spin_box.setMinimum(1)
        spin_box.setMaximum(ton_kho)
        spin_box.setValue(1)
        spin_box.valueChanged.connect(lambda: self.update_cart_total(row_count, gia))

        self.cart_table.setCellWidget(row_count, 2, spin_box)
        self.cart_table.setItem(row_count, 3, QTableWidgetItem(f"{gia:,.2f} VNĐ"))
        self.cart_table.setItem(row_count, 4, QTableWidgetItem(f"{gia:,.2f} VNĐ"))

        self.update_total()


    def update_total(self):
        """Cập nhật tổng tiền"""
        total = 0
        for row in range(self.cart_table.rowCount()):
            thanh_tien_text = self.cart_table.item(row, 4).text()
            thanh_tien = int(float(thanh_tien_text.replace(" VNĐ", "").replace(",", "")))

            total += thanh_tien
        self.total_label.setText(f"Tổng tiền: {total:,} VNĐ")
    
    
    def validate_ids(self):
        
        """Hiển thị dialog để nhập và kiểm tra mã nhân viên, mã khách hàng"""
        input_dialog = QDialog(self)
        input_dialog.setWindowTitle("Nhập thông tin đơn hàng")
        layout = QVBoxLayout()

        # Tạo các trường nhập liệu
        nv_layout = QHBoxLayout()
        nv_label = QLabel("Mã nhân viên:")
        nv_input = QLineEdit()
        nv_layout.addWidget(nv_label)
        nv_layout.addWidget(nv_input)
        layout.addLayout(nv_layout)

        kh_layout = QHBoxLayout()
        kh_label = QLabel("Mã khách hàng:")
        kh_input = QLineEdit()
        kh_layout.addWidget(kh_label)
        kh_layout.addWidget(kh_input)
        layout.addLayout(kh_layout)

        # Nút xác nhận và hủy
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Xác nhận")
        cancel_button = QPushButton("Hủy")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        input_dialog.setLayout(layout)

        # Biến lưu kết quả
        result = {"maNV": None, "maKH": None}

        def validate_and_accept():
            try:
                ma_nv = int(nv_input.text())
                ma_kh = int(kh_input.text())

                conn = connect_db()
                cursor = conn.cursor()

                # Kiểm tra mã nhân viên
                cursor.execute("SELECT maNV FROM nhanvien WHERE maNV = %s", (ma_nv,))
                if not cursor.fetchone():
                    QMessageBox.warning(input_dialog, "Lỗi", "Mã nhân viên không tồn tại!")
                    return

                # Kiểm tra mã khách hàng
                cursor.execute("SELECT maKH FROM khachhang WHERE maKH = %s", (ma_kh,))
                if not cursor.fetchone():
                    QMessageBox.warning(input_dialog, "Lỗi", "Mã khách hàng không tồn tại!")
                    return

                cursor.close()
                conn.close()

                result["maNV"] = ma_nv
                result["maKH"] = ma_kh
                input_dialog.accept()

            except ValueError:
                QMessageBox.warning(input_dialog, "Lỗi", "Vui lòng nhập số nguyên cho mã nhân viên và mã khách hàng!")
            except mysql.connector.Error as e:
                QMessageBox.critical(input_dialog, "Lỗi", f"Lỗi kết nối CSDL: {str(e)}")

        ok_button.clicked.connect(validate_and_accept)
        cancel_button.clicked.connect(input_dialog.reject)

        if input_dialog.exec_() == QDialog.Accepted:
            return result
        return None
   
    def show_qr_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Chuyển khoản qua QR")
        dialog.setFixedSize(350, 600)

        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 8px;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #212529;
                background-color: transparent;
            }
            QLabel#infoLabel {
                color: #6c757d;
                font-size: 12px;
            }
            QFrame#qrFrame {
                background-color: white;
                border: none;
            }
            QPushButton#payButton {
                background-color: #198754;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#payButton:hover {
                background-color: #157347;
            }
            QPushButton#cancelButton {
                background-color: transparent;
                color: #6c757d;
                border: none;
                font-size: 14px;
                text-decoration: underline;
            }
            QPushButton#cancelButton:hover {
                color: #343a40;
            }
        """)

        # Đường dẫn ảnh QR
        qr_path = "..\Py_BTL\image\qr.jpg"
        if not os.path.exists(qr_path):
            print(f"Lỗi: Không tìm thấy ảnh QR tại {qr_path}")
            return False

        # Tiêu đề
        title_label = QLabel("Quét mã QR để thanh toán", dialog)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Khung chứa QR (loại bỏ nền đen)
        qr_frame = QFrame(dialog)
        qr_frame.setObjectName("qrFrame")
        qr_frame_layout = QVBoxLayout(qr_frame)
        qr_frame_layout.setContentsMargins(0, 0, 0, 0)

        # Ảnh QR (full height)
        qr_label = QLabel()
        qr_pixmap = QPixmap(qr_path)

        if qr_pixmap.isNull():
            print("Lỗi: Không thể load ảnh QR.")
            return False

        qr_label.setPixmap(qr_pixmap)
        qr_label.setScaledContents(True)
        qr_label.setFixedSize(280, 380)  # Full height

        qr_frame_layout.addWidget(qr_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Nút thanh toán
        pay_button = QPushButton("Đã thanh toán xong", dialog)
        pay_button.setObjectName("payButton")
        pay_button.setFixedSize(220, 45)
        pay_button.clicked.connect(dialog.accept)

        # Nút hủy
        cancel_button = QPushButton("Hủy giao dịch", dialog)
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(dialog.reject)

        # Layout chính
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        main_layout.addWidget(title_label)
        main_layout.addWidget(qr_frame)  # Ảnh QR full height
        main_layout.addWidget(pay_button, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(cancel_button, 0, Qt.AlignmentFlag.AlignCenter)

        dialog.setLayout(main_layout)

        # Hiển thị hộp thoại
        return dialog.exec() == QDialog.DialogCode.Accepted

    def checkout(self, status):
        try:
            # Kiểm tra giỏ hàng trống
            if self.cart_table.rowCount() == 0:
                QMessageBox.warning(self, "Lỗi", "Giỏ hàng trống!")
                return

            # Xác nhận mã NV & KH
            ids = self.validate_ids()
            if not ids:
                return  # Người dùng hủy

            # Chọn phương thức thanh toán
            payment_methods = ["Tiền mặt", "Chuyển khoản", "Thẻ tín dụng"]
            selected_method, ok = QInputDialog.getItem(self, "Chọn phương thức thanh toán",
                                                    "Phương thức thanh toán:", payment_methods, 0, False)
            if not ok:
                return
            
            if selected_method == "Chuyển khoản":
                if not self.show_qr_dialog():  # Nếu người dùng bấm Hủy
                    return

            # Tính tổng tiền
            total_amount = float(self.total_label.text().replace("Tổng tiền: ", "").replace(",", "").replace(" VNĐ", ""))

            # Kết nối CSDL
            conn = connect_db()
            cursor = conn.cursor()

            try:
                # Bắt đầu giao dịch
                conn.start_transaction()

                # Thêm đơn hàng vào `donhang`
                cursor.execute("""
                    INSERT INTO donhang (maNV, maKH, ngayDat, tongTien, phuongThucThanhToan, trangThai)
                    VALUES (%s, %s, CURRENT_DATE, %s, %s, %s)
                """, (ids["maNV"], ids["maKH"], total_amount, selected_method, status))

                # Lấy mã đơn hàng vừa tạo
                ma_dh = cursor.lastrowid
                total_profit = 0  # Biến lưu tổng lợi nhuận

                # Thêm chi tiết hóa đơn + Cập nhật tồn kho
                for row in range(self.cart_table.rowCount()):
                    ma_sp = int(self.cart_table.item(row, 0).text())
                    so_luong = self.cart_table.cellWidget(row, 2).value()
                    don_gia = float(self.cart_table.item(row, 3).text().replace(",", "").replace(" VNĐ", ""))
                    thanh_tien = float(self.cart_table.item(row, 4).text().replace(",", "").replace(" VNĐ", ""))

                    # Lấy giá nhập từ bảng `sanpham`
                    cursor.execute("SELECT giaNhap, giaBan FROM sanpham WHERE maSP = %s", (ma_sp,))
                    result = cursor.fetchone()

                    if result:
                        gia_nhap = result[0]
                        gia_ban = result[1]
                        loi_nhuan = (float(gia_ban) - float(gia_nhap)) * so_luong
                        total_profit += loi_nhuan
                    else:
                        print("Sản phẩm không tồn tại!")

                    # Thêm vào `chitiethoadon`
                    cursor.execute("""
                        INSERT INTO chitiethoadon (maDH, maSP, soLuong, donGia, thanhTien, loiNhuan)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (ma_dh, ma_sp, so_luong, don_gia, thanh_tien, loi_nhuan))

                    # Nếu đơn hàng chưa thanh toán, không cập nhật tồn kho
                    if status == "Đã thanh toán":
                        cursor.execute("""
                            UPDATE sanpham 
                            SET tonKho = tonKho - %s 
                            WHERE maSP = %s
                        """, (so_luong, ma_sp))

                # Hoàn tất giao dịch
                conn.commit()

                # Xóa giỏ hàng sau khi thanh toán
                while self.cart_table.rowCount() > 0:
                    self.cart_table.removeRow(0)
                self.update_total()

                # Load lại sản phẩm để cập nhật tồn kho
                self.load_products()

                # Hiển thị thông báo thành công
                QMessageBox.information(self, "Thành công",
                                        f"Đã tạo đơn hàng thành công!\nMã đơn hàng: {ma_dh}\n"
                                        f"Phương thức thanh toán: {selected_method}\n"
                                        f"Trạng thái: {status}\n"
                                        f"Lợi nhuận đơn hàng: {total_profit:,.2f} VNĐ")

            except mysql.connector.Error as err:
                # Rollback nếu có lỗi
                conn.rollback()
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi tạo đơn hàng: {err}")

            finally:
                cursor.close()
                conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi hệ thống: {str(e)}")




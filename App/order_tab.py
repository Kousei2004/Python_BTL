import sys, os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                           QTableWidget, QTableWidgetItem, QFormLayout, QComboBox, 
                           QSpinBox, QTabWidget, QFileDialog, QMessageBox,
                           QDoubleSpinBox, QDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import QHeaderView
import mysql.connector
from datetime import datetime
from database import connect_db

class OrderDetailDialog(QDialog):
    def __init__(self, ma_dh, parent=None):
        super().__init__(parent)
        self.ma_dh = ma_dh
        self.setWindowTitle(f"Chi tiết đơn hàng #{ma_dh}")
        self.setMinimumSize(600, 400)
        self.init_ui()
        self.load_order_details()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Thông tin đơn hàng
        self.order_info = QLabel()
        layout.addWidget(self.order_info)
        
        # Bảng chi tiết
        self.detail_table = QTableWidget(0, 6)
        self.detail_table.setHorizontalHeaderLabels([
            "Mã SP", "Tên SP", "Số lượng", "Đơn giá", "Thành tiền", "Lợi nhuận"
        ])

        header = self.detail_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.detail_table)
        
        self.setLayout(layout)

    def load_order_details(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Lấy thông tin đơn hàng
            cursor.execute("""
                SELECT dh.maDH, dh.maKH, kh.tenKH, dh.ngayDat, dh.tongTien, 
                    dh.trangThai, dh.phuongThucThanhToan, nv.tenNV,
                    COALESCE(SUM(ct.loiNhuan), 0) AS loiNhuan
                FROM donhang dh 
                LEFT JOIN khachhang kh ON dh.maKH = kh.maKH
                LEFT JOIN nhanvien nv ON dh.maNV = nv.maNV
                LEFT JOIN chitiethoadon ct ON dh.maDH = ct.maDH
                WHERE dh.maDH = %s
                GROUP BY dh.maDH
            """, (self.ma_dh,))

            order_info = cursor.fetchone()
            if order_info:
                self.order_info.setText(
                    f"╔════════════════════════════════ THÔNG TIN ĐƠN HÀNG ═════════════════════════════════╗\n"
                    f"                            Mã đơn hàng: #{order_info[0]}\n"
                    f"                            Khách hàng:  {order_info[2]}\n"
                    f"                            Mã khách:    {order_info[1]}\n"
                    f"                            Ngày đặt:    {order_info[3]}\n"
                    f"                            Nhân viên:   {order_info[7]}\n"
                    f"                            Trạng thái:  {order_info[5]}\n"
                    f"                            Thanh toán:  {order_info[6]}\n"
                    f"╠═════════════════════════════════════════════════════════════════════════════════╣\n"
                    f"       TỔNG TIỀN:   {order_info[4]:,.0f} VNĐ\n"
                    f"       LỢI NHUẬN:   {order_info[8]:,.0f} VNĐ\n"
                    f"╚═════════════════════════════════════════════════════════════════════════════════╝"
                )

            # Lấy chi tiết đơn hàng
            cursor.execute("""
                SELECT ct.maSP, sp.tenSP, ct.soLuong, ct.donGia, ct.thanhTien, ct.loiNhuan
                FROM chitiethoadon ct
                JOIN sanpham sp ON ct.maSP = sp.maSP
                WHERE ct.maDH = %s
            """, (self.ma_dh,))

            details = cursor.fetchall()
            self.detail_table.setRowCount(len(details))
            for row, detail in enumerate(details):
                for col, value in enumerate(detail):
                    if col in [3, 4, 5]:  # Giá, thành tiền, lợi nhuận
                        item = QTableWidgetItem(f"{value:,.0f} VNĐ")
                    else:
                        item = QTableWidgetItem(str(value))
                    self.detail_table.setItem(row, col, item)

            cursor.close()
            conn.close()

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải chi tiết đơn hàng: {str(e)}")


class OrderManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_orders()
        
    def init_ui(self):
        layout = QVBoxLayout()

        # Tiêu đề
        title = QLabel("Quản Lý Đơn Hàng")
        title.setFont(QFont("Arial", 14, QFont.ExtraBold))
        layout.addWidget(title)

        # Ô tìm kiếm đơn hàng
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập mã đơn hàng hoặc tên khách hàng...")
        self.search_button = QPushButton("Tìm kiếm")
        self.search_button.clicked.connect(self.search_orders)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        # Các nút chức năng
        button_layout = QHBoxLayout()
        self.view_button = QPushButton("Xem chi tiết")
        self.update_button = QPushButton("Cập nhật trạng thái")
        self.cancel_button = QPushButton("Xóa đơn")
        self.export_button = QPushButton("Xuất hóa đơn")
        self.load_button = QPushButton("Làm mới")

        for button in [self.view_button, self.update_button, self.cancel_button, self.export_button, self.load_button]:
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

        # Bảng danh sách đơn hàng
        self.order_table = QTableWidget(0, 9)
        self.order_table.setHorizontalHeaderLabels([
            "Mã ĐH", "Mã NV", "Mã KH", "Tên KH", "Ngày đặt",
            "Tổng tiền", "Trạng thái", "PT Thanh toán", "Lợi nhuận"
        ])

        header = self.order_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.order_table)

        # Kết nối các nút với chức năng
        self.view_button.clicked.connect(self.view_order_details)
        self.update_button.clicked.connect(self.update_order_status)
        self.cancel_button.clicked.connect(self.cancel_order)
        self.export_button.clicked.connect(self.export_order)
        self.load_button.clicked.connect(self.load_orders)

        self.setLayout(layout)

    def load_orders(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT dh.maDH, dh.maNV, dh.maKH, kh.tenKH, dh.ngayDat, 
                    dh.tongTien, dh.trangThai, dh.phuongThucThanhToan,
                    COALESCE(SUM(ct.loiNhuan), 0) AS loiNhuan
                FROM donhang dh
                LEFT JOIN khachhang kh ON dh.maKH = kh.maKH
                LEFT JOIN chitiethoadon ct ON dh.maDH = ct.maDH
                GROUP BY dh.maDH
                ORDER BY dh.ngayDat DESC
            """)

            orders = cursor.fetchall()
            self.order_table.setRowCount(len(orders))

            for row, order in enumerate(orders):
                for col, value in enumerate(order):
                    if col == 4:  # Ngày đặt
                        value = value.strftime("%d/%m/%Y")
                    elif col == 5 or col == 8:  # Tổng tiền và lợi nhuận
                        value = f"{value:,.0f} VNĐ"
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Chỉ đọc
                    self.order_table.setItem(row, col, item)

            cursor.close()
            conn.close()

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách đơn hàng: {str(e)}")


    def search_orders(self):
        keyword = self.search_input.text().strip().lower()
        for row in range(self.order_table.rowCount()):
            order_id = self.order_table.item(row, 0).text().lower()
            customer_name = self.order_table.item(row, 3).text().lower()
            
            if keyword in order_id or keyword in customer_name:
                self.order_table.setRowHidden(row, False)
            else:
                self.order_table.setRowHidden(row, True)

    def view_order_details(self):
        current_row = self.order_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một đơn hàng!")
            return
            
        ma_dh = int(self.order_table.item(current_row, 0).text())
        dialog = OrderDetailDialog(ma_dh, self)
        dialog.exec_()

    def update_order_status(self):
        current_row = self.order_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một đơn hàng!")
            return
            
        ma_dh = int(self.order_table.item(current_row, 0).text())
        current_status = self.order_table.item(current_row, 6).text()
        
        status_dialog = QDialog(self)
        status_dialog.setWindowTitle("Cập nhật trạng thái")
        layout = QVBoxLayout()
        
        status_combo = QComboBox()
        status_combo.addItems(["Chờ xử lý", "Đang xử lý", "Đã giao hàng", "Đã hủy", "Đã thanh toán"])
        status_combo.setCurrentText(current_status)
        layout.addWidget(status_combo)
        
        button_box = QHBoxLayout()
        ok_button = QPushButton("Cập nhật")
        cancel_button = QPushButton("Hủy")
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)
        
        status_dialog.setLayout(layout)
        
        def update_status():
            try:
                conn = connect_db()
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE donhang 
                    SET trangThai = %s 
                    WHERE maDH = %s
                """, (status_combo.currentText(), ma_dh))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                self.order_table.item(current_row, 6).setText(status_combo.currentText())
                status_dialog.accept()
                QMessageBox.information(self, "Thành công", "Đã cập nhật trạng thái đơn hàng!")
                
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật trạng thái: {str(e)}")
        
        ok_button.clicked.connect(update_status)
        cancel_button.clicked.connect(status_dialog.reject)
        
        status_dialog.exec_()

    def cancel_order(self):
        current_row = self.order_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một đơn hàng!")
            return

        ma_dh = int(self.order_table.item(current_row, 0).text())
        current_status = self.order_table.item(current_row, 6).text()

        if current_status == "Đã giao hàng":
            QMessageBox.warning(self, "Cảnh báo", "Không thể xóa đơn hàng đã giao!")
            return

        reply = QMessageBox.question(self, "Xác nhận", 
                                "Bạn có chắc muốn **xóa** đơn hàng này khỏi hệ thống?",
                                QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                conn = connect_db()
                cursor = conn.cursor()

                # Hoàn lại số lượng tồn kho trước khi xóa đơn hàng
                cursor.execute("""
                    UPDATE sanpham sp
                    JOIN chitiethoadon ct ON sp.maSP = ct.maSP
                    SET sp.tonKho = sp.tonKho + ct.soLuong
                    WHERE ct.maDH = %s
                """, (ma_dh,))

                # Xóa chi tiết đơn hàng trước
                cursor.execute("""
                    DELETE FROM chitiethoadon 
                    WHERE maDH = %s
                """, (ma_dh,))

                # Xóa đơn hàng chính
                cursor.execute("""
                    DELETE FROM donhang 
                    WHERE maDH = %s
                """, (ma_dh,))

                conn.commit()
                cursor.close()
                conn.close()

                # Xóa dòng trong bảng hiển thị
                self.order_table.removeRow(current_row)

                QMessageBox.information(self, "Thành công", "Đã xóa đơn hàng thành công!")

            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa đơn hàng: {str(e)}")


    def export_order(self):
        current_row = self.order_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một đơn hàng!")
            return
            
        ma_dh = int(self.order_table.item(current_row, 0).text())
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Lấy thông tin đơn hàng
            cursor.execute("""
                SELECT dh.maDH, dh.ngayDat, dh.tongTien, dh.phuongThucThanhToan,
                       kh.tenKH, kh.sdt, kh.diaChi,
                       nv.tenNV
                FROM donhang dh
                LEFT JOIN khachhang kh ON dh.maKH = kh.maKH
                LEFT JOIN nhanvien nv ON dh.maNV = nv.maNV
                WHERE dh.maDH = %s
            """, (ma_dh,))
            
            order_info = cursor.fetchone()
            
            # Lấy chi tiết đơn hàng
            cursor.execute("""
                SELECT sp.tenSP, ct.soLuong, ct.donGia, ct.thanhTien
                FROM chitiethoadon ct
                JOIN sanpham sp ON ct.maSP = sp.maSP
                WHERE ct.maDH = %s
            """, (ma_dh,))
            
            order_details = cursor.fetchall()
            
            # Tạo nội dung hóa đơn
            invoice_content = f"""
                            HÓA ĐƠN BÁN HÀNG
-------------------------------------------------------------------------------
                            
Số hóa đơn: {order_info[0]}
Ngày: {order_info[1].strftime('%d/%m/%Y')}

THÔNG TIN KHÁCH HÀNG
Tên khách hàng: {order_info[4]}
Số điện thoại: {order_info[5]}
Địa chỉ: {order_info[6]}

Nhân viên bán hàng: {order_info[7]}

CHI TIẾT ĐƠN HÀNG
-------------------------------------------------------------------------------
{'Sản phẩm':<40} {'SL':>5} {'Đơn giá':>15} {'Thành tiền':>15}
"""
            
            for item in order_details:
                invoice_content += f"\n{item[0]:<40} {item[1]:>5} {item[2]:>15,.0f} {item[3]:>15,.0f}"
                
            invoice_content += f"""
\n
{'':->75}
Tổng tiền:{'':<52} {order_info[2]:>15,.0f} VNĐ
Phương thức thanh toán: {order_info[3]}

                        Cảm ơn quý khách!
"""
        

            # Tạo thư mục "hoadon" nếu chưa tồn tại
            save_dir = "hoadon"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # Đường dẫn mặc định khi lưu file
            default_path = os.path.join(save_dir, f"hoadon_{ma_dh}.txt")

            # Hiển thị hộp thoại lưu file
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Lưu hóa đơn",
                default_path,  # Đường dẫn mặc định
                "Text Files (*.txt)"
            )

            # Nếu người dùng chọn nơi lưu
            if file_name:
                try:
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.write(invoice_content)
                    QMessageBox.information(self, "Thành công", "Đã xuất hóa đơn thành công!")
                except Exception as e:
                    QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất hóa đơn: {str(e)}")

                
            cursor.close()
            conn.close()
            
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất hóa đơn: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất hóa đơn: {str(e)}")


import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                           QTableWidget, QTableWidgetItem, QFormLayout, QComboBox, 
                           QSpinBox, QTabWidget, QFileDialog, QMessageBox,
                           QDoubleSpinBox, QMenu, QFrame)
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QFont, QIcon, QPixmap
from sales_tab import SalesManagementTab
from employee_tab import EmployeeManagementTab
from product_tab import ProductManagementTab
from customer_tab import CustomerManagementTab
from order_tab import OrderManagementTab
from user_tab import UserManagementTab
from statistics_tab import StatisticsManagementTab
from styles import setup_styles


class StationeryStoreUI(QMainWindow):
    def __init__(self, user_role='Nhanvien'):  # Nhận role từ LoginApp
        super().__init__()
        self.user_role = user_role  # Lưu role của user
        self.setWindowTitle("Quản Lý Cửa Hàng Văn Phòng Phẩm")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QIcon("image/store2.png"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Tạo thanh TabWidget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Gọi hàm setup_tabs() để hiển thị các tab phù hợp
        self.setup_tabs()

        # Tạo nút logout
        self.setup_logout_button()
        setup_styles(self)

    def setup_tabs(self):
        """Hiển thị tab theo role của user"""
        # Tab chung cho tất cả các vai trò
        self.tab_widget.addTab(SalesManagementTab(), "🛒 Bán Hàng")
        self.tab_widget.addTab(CustomerManagementTab(), "🤝 Quản Lý Khách Hàng")
        self.tab_widget.addTab(OrderManagementTab(), "📜 Quản lí đơn hàng")

        # Nếu là Admin, hiển thị các tab quản lý khác
        if self.user_role == 'Admin':
            self.tab_widget.addTab(EmployeeManagementTab(), "👨‍💼 Quản lí Nhân Viên")
            self.tab_widget.addTab(ProductManagementTab(), "📦 Quản Lý Sản Phẩm")
            self.tab_widget.addTab(StatisticsManagementTab(), "📊 Thống Kê")
            self.tab_widget.addTab(UserManagementTab(), "🛡️ Quản lí phân quyền")

    def setup_logout_button(self):
        """Tạo nút logout ở góc phải tab"""
        self.logout_button = QPushButton()
        self.logout_button.setIcon(QIcon("image/logout1.png"))
        self.logout_button.setIconSize(QSize(16, 16))
        self.logout_button.setFixedSize(30, 30)
        self.logout_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: none;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.logout_button.clicked.connect(self.show_settings_menu)

        # Đặt widget nút logout vào góc phải TabBar
        logout_widget = QWidget()
        logout_layout = QHBoxLayout(logout_widget)
        logout_layout.setContentsMargins(0, 0, 0, 0)
        logout_layout.addStretch()
        logout_layout.addWidget(self.logout_button)

        self.tab_widget.setCornerWidget(logout_widget, Qt.TopRightCorner)

    def show_settings_menu(self):
        """Hiển thị menu khi nhấn nút logout."""
        menu = QMenu(self)
        
        logout_action = menu.addAction("Đăng xuất")
        logout_action.triggered.connect(self.logout)

        settings_action = menu.addAction("Cài đặt")
        settings_action.triggered.connect(self.open_settings)

        menu.exec(self.logout_button.mapToGlobal(QPoint(0, self.logout_button.height())))

    def logout(self):
        """Hàm xử lý đăng xuất."""
        confirm = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn đăng xuất?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            QMessageBox.information(self, "Đăng xuất", "Bạn đã đăng xuất khỏi hệ thống.")
            self.close()

    def open_settings(self):
        """Hàm mở cài đặt (hiện tại chỉ có thông báo)."""
        QMessageBox.information(self, "Cài đặt", "Chức năng cài đặt đang được phát triển!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StationeryStoreUI(user_role="Admin")  
    window.show()
    sys.exit(app.exec())


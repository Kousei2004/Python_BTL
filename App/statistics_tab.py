import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                           QTableWidget, QTableWidgetItem, QFormLayout, QComboBox, 
                           QSpinBox, QTabWidget, QFileDialog, QMessageBox,
                           QDoubleSpinBox, QStackedWidget)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QPieSeries, QBarSeries, QBarSet, QChart, QChartView
import datetime
import mysql.connector
import time
from database import connect_db

class StatisticsManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        title_layout = QHBoxLayout()
        title = QLabel("Thống kê")
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
        clear_icon.clicked.connect(self.update_chart)

        title_layout.addWidget(title)
        title_layout.addStretch()  # Đẩy icon về góc phải
        title_layout.addWidget(clear_icon)

        layout.addLayout(title_layout)
        
        # Tiêu đề
        title = QLabel("Thống Kê Doanh Thu")
        title.setFont(QFont("Arial", 14, QFont.ExtraBold))
        layout.addWidget(title)
        
        # Bộ lọc thời gian
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Thời gian:"))
        self.time_filter = QComboBox()
        self.time_filter.addItems(["Hôm nay", "Tuần này", "Tháng này", "Năm nay"])
        self.time_filter.currentIndexChanged.connect(self.update_chart)  # Kết nối sự kiện thay đổi bộ lọc
        filter_layout.addWidget(self.time_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Các widget thống kê
        stats_layout = QHBoxLayout()
        
        # Doanh thu
        font = QFont("Arial", 20, QFont.Bold) 
        revenue_widget = QWidget()
        revenue_layout = QVBoxLayout()
        revenue_label = QLabel("💵 Doanh Thu")
        revenue_label.setFont(font)
        self.revenue_amount = QLabel("0 VNĐ")
        self.revenue_amount.setFont(QFont("Arial", 16, QFont.ExtraBold))
        revenue_layout.addWidget(revenue_label)
        revenue_layout.addWidget(self.revenue_amount)
        revenue_widget.setLayout(revenue_layout)
        revenue_widget.setStyleSheet("background-color: #4F81BD; padding: 20px; border-radius: 10px;")
        
        # Lợi nhuận
        profit_widget = QWidget()
        profit_layout = QVBoxLayout()
        profit_label = QLabel("📈 Lợi Nhuận")
        profit_label.setFont(font)
        self.profit_amount = QLabel("0 VNĐ")
        self.profit_amount.setFont(QFont("Arial", 16, QFont.ExtraBold))
        profit_layout.addWidget(profit_label)
        profit_layout.addWidget(self.profit_amount)
        profit_widget.setLayout(profit_layout)
        profit_widget.setStyleSheet("background-color: #FF8C00; padding: 20px; border-radius: 10px;")
        
        # Đơn hàng
        orders_widget = QWidget()
        orders_layout = QVBoxLayout()
        orders_label = QLabel("📝 Số Đơn Hàng")
        orders_label.setFont(font)
        self.orders_amount = QLabel("0 Đơn")
        self.orders_amount.setFont(QFont("Arial", 16, QFont.ExtraBold))
        orders_layout.addWidget(orders_label)
        orders_layout.addWidget(self.orders_amount)
        orders_widget.setLayout(orders_layout)
        orders_widget.setStyleSheet("background-color: #FF4500; padding: 20px; border-radius: 10px;")
        
        stats_layout.addWidget(revenue_widget)
        stats_layout.addWidget(profit_widget)
        stats_layout.addWidget(orders_widget)
        
        layout.addLayout(stats_layout)
        
        # **Thêm Biểu Đồ Doanh Thu**
        self.chart = QChart()
        self.chart.setTitle("Biểu đồ doanh thu")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)  # Sửa lỗi Antialiasing
        layout.addWidget(self.chart_view)
        self.update_chart()

        self.setLayout(layout)
        self.update_chart()  # Gọi hàm cập nhật biểu đồ

    def fetch_statistics_data(self, filter_option):
        db = connect_db()
        cursor = db.cursor()

        today = datetime.date.today()
        month = today.month
        year = today.year

        revenue_data = []
        profit_data = []
        orders_data = []

        try:
            if filter_option == "Hôm nay":
                query_revenue = """
                SELECT ngayDat, SUM(tongTien) 
                FROM donhang 
                WHERE ngayDat = %s AND trangThai = 'Đã thanh toán'
                GROUP BY ngayDat
                """
                cursor.execute(query_revenue, (today,))
                revenue_data = cursor.fetchall()

                query_profit = """
                SELECT dh.ngayDat, SUM(ct.loiNhuan)
                FROM donhang dh
                JOIN chitiethoadon ct ON dh.maDH = ct.maDH
                WHERE dh.ngayDat = %s AND dh.trangThai = 'Đã thanh toán'
                GROUP BY dh.ngayDat
                """
                cursor.execute(query_profit, (today,))
                profit_data = cursor.fetchall()

                query_orders = """
                SELECT ngayDat, COUNT(maDH) 
                FROM donhang 
                WHERE ngayDat = %s AND trangThai = 'Đã thanh toán'
                GROUP BY ngayDat
                """
                cursor.execute(query_orders, (today,))
                orders_data = cursor.fetchall()

            elif filter_option == "Tuần này":
                start_week = today - datetime.timedelta(days=today.weekday())

                query_revenue = """
                SELECT ngayDat, SUM(tongTien) 
                FROM donhang 
                WHERE ngayDat BETWEEN %s AND %s AND trangThai = 'Đã thanh toán'
                GROUP BY ngayDat
                """
                cursor.execute(query_revenue, (start_week, today))
                revenue_data = cursor.fetchall()

                query_profit = """
                SELECT dh.ngayDat, SUM(ct.loiNhuan)
                FROM donhang dh
                JOIN chitiethoadon ct ON dh.maDH = ct.maDH
                WHERE dh.ngayDat BETWEEN %s AND %s AND dh.trangThai = 'Đã thanh toán'
                GROUP BY dh.ngayDat
                """
                cursor.execute(query_profit, (start_week, today))
                profit_data = cursor.fetchall()

                query_orders = """
                SELECT ngayDat, COUNT(maDH) 
                FROM donhang 
                WHERE ngayDat BETWEEN %s AND %s AND trangThai = 'Đã thanh toán'
                GROUP BY ngayDat
                """
                cursor.execute(query_orders, (start_week, today))
                orders_data = cursor.fetchall()

            elif filter_option == "Tháng này":
                query_revenue = """
                SELECT ngayDat, SUM(tongTien) 
                FROM donhang 
                WHERE MONTH(ngayDat) = %s AND YEAR(ngayDat) = %s AND trangThai = 'Đã thanh toán'
                GROUP BY ngayDat
                """
                cursor.execute(query_revenue, (month, year))
                revenue_data = cursor.fetchall()

                query_profit = """
                SELECT dh.ngayDat, SUM(ct.loiNhuan)
                FROM donhang dh
                JOIN chitiethoadon ct ON dh.maDH = ct.maDH
                WHERE MONTH(dh.ngayDat) = %s AND YEAR(dh.ngayDat) = %s AND dh.trangThai = 'Đã thanh toán'
                GROUP BY dh.ngayDat
                """
                cursor.execute(query_profit, (month, year))
                profit_data = cursor.fetchall()

                query_orders = """
                SELECT ngayDat, COUNT(maDH) 
                FROM donhang 
                WHERE MONTH(ngayDat) = %s AND YEAR(ngayDat) = %s AND trangThai = 'Đã thanh toán'
                GROUP BY ngayDat
                """
                cursor.execute(query_orders, (month, year))
                orders_data = cursor.fetchall()

            elif filter_option == "Năm nay":
                query_revenue = """
                SELECT ngayDat, SUM(tongTien) 
                FROM donhang 
                WHERE YEAR(ngayDat) = %s AND trangThai = 'Đã thanh toán'
                GROUP BY ngayDat
                """
                cursor.execute(query_revenue, (year,))
                revenue_data = cursor.fetchall()

                query_profit = """
                SELECT dh.ngayDat, SUM(ct.loiNhuan)
                FROM donhang dh
                JOIN chitiethoadon ct ON dh.maDH = ct.maDH
                WHERE YEAR(dh.ngayDat) = %s AND dh.trangThai = 'Đã thanh toán'
                GROUP BY dh.ngayDat
                """
                cursor.execute(query_profit, (year,))
                profit_data = cursor.fetchall()

                query_orders = """
                SELECT ngayDat, COUNT(maDH) 
                FROM donhang 
                WHERE YEAR(ngayDat) = %s AND trangThai = 'Đã thanh toán'
                GROUP BY ngayDat
                """
                cursor.execute(query_orders, (year,))
                orders_data = cursor.fetchall()

            # Debug kiểm tra dữ liệu
            print(f"📊 Dữ liệu doanh thu ({filter_option}): {revenue_data}")
            print(f"📈 Dữ liệu lợi nhuận ({filter_option}): {profit_data}")
            print(f"📝 Dữ liệu số đơn hàng ({filter_option}): {orders_data}")

        except Exception as e:
            print(f"⚠️ Lỗi truy vấn SQL: {e}")

        finally:
            db.close()

        return {
            "revenue": revenue_data if revenue_data else [(today, 0)],
            "profit": profit_data if profit_data else [(today, 0)],
            "orders": orders_data if orders_data else [(today, 0)]
        }

    def update_chart(self):
        filter_option = self.time_filter.currentText()
        data = self.fetch_statistics_data(filter_option)

        if not data:
            print("⚠️ Không có dữ liệu để hiển thị biểu đồ!")
            return

        # Xóa toàn bộ trục trước khi thêm mới
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        # Xóa series cũ
        self.chart.removeAllSeries()

        # Tính tổng doanh thu và lợi nhuận, đảm bảo chuyển đổi sang float
        total_revenue = float(sum(row[1] for row in data["revenue"])) if data["revenue"] else 0.0
        total_profit = float(sum(row[1] for row in data["profit"])) if data["profit"] else 0.0
        total_orders = sum(row[1] for row in data["orders"]) if data["orders"] else 0

        # Cập nhật giao diện
        self.revenue_amount.setText(f"{total_revenue:,.0f} VNĐ")
        self.profit_amount.setText(f"{total_profit:,.0f} VNĐ")
        self.orders_amount.setText(f"{total_orders} Đơn")

        print(f"📊 Cập nhật biểu đồ: {filter_option}, Doanh thu: {total_revenue}, Lợi nhuận: {total_profit}, Đơn hàng: {total_orders}")

        # **Hôm nay → Biểu đồ cột**
        if filter_option == "Hôm nay":
            bar_series = QBarSeries()
            revenue_set = QBarSet("Doanh thu")
            profit_set = QBarSet("Lợi nhuận")

            # Thêm dữ liệu vào cột
            revenue_set.append(total_revenue)
            profit_set.append(total_profit)

            bar_series.append(revenue_set)
            bar_series.append(profit_set)

            self.chart.addSeries(bar_series)
            self.chart.setTitle("Biểu đồ doanh thu hôm nay")

            # **Thêm trục X (Danh mục)**
            axis_x = QValueAxis()
            axis_x.setLabelFormat("%d")
            axis_x.setTitleText("Hôm nay")
            self.chart.addAxis(axis_x, Qt.AlignBottom)
            bar_series.attachAxis(axis_x)

            # **Thêm trục Y (Giá trị) và điều chỉnh tỷ lệ**
            axis_y = QValueAxis()
            axis_y.setLabelFormat("%.0f VNĐ")
            axis_y.setTitleText("Giá trị")
            axis_y.setRange(0, max(total_revenue, total_profit) * 1.2)  # Điều chỉnh tỉ lệ
            self.chart.addAxis(axis_y, Qt.AlignLeft)
            bar_series.attachAxis(axis_y)

        # **Tuần này, Tháng này & Năm nay → Biểu đồ đường**
        else:
            revenue_series = QLineSeries()
            revenue_series.setName("Doanh thu")
            profit_series = QLineSeries()
            profit_series.setName("Lợi nhuận")

            timestamps = set()

            # **Thêm dữ liệu doanh thu**
            for row in data["revenue"]:
                date_obj = row[0]
                if isinstance(date_obj, str):
                    date_obj = datetime.datetime.strptime(date_obj, "%Y-%m-%d").date()
                timestamp = int(time.mktime(date_obj.timetuple())) * 1000
                revenue_series.append(timestamp, float(row[1]))
                timestamps.add(timestamp)

            # **Thêm dữ liệu lợi nhuận**
            for row in data["profit"]:
                date_obj = row[0]
                if isinstance(date_obj, str):
                    date_obj = datetime.datetime.strptime(date_obj, "%Y-%m-%d").date()
                timestamp = int(time.mktime(date_obj.timetuple())) * 1000
                profit_series.append(timestamp, float(row[1]))
                timestamps.add(timestamp)

            # **Tránh lỗi nếu chỉ có một điểm dữ liệu**
            if len(timestamps) == 1:
                timestamps.add(list(timestamps)[0] + 86400000)
                revenue_series.append(list(timestamps)[1], float(data["revenue"][0][1]))
                profit_series.append(list(timestamps)[1], float(data["profit"][0][1]))

            # **Thêm tất cả series vào biểu đồ**
            self.chart.addSeries(revenue_series)
            self.chart.addSeries(profit_series)
            self.chart.setTitle(f"Biểu đồ doanh thu ({filter_option})")

            # **Thêm trục X (Ngày)**
            axis_x = QDateTimeAxis()
            axis_x.setFormat("dd-MM")
            axis_x.setTitleText("Ngày")
            self.chart.addAxis(axis_x, Qt.AlignBottom)
            revenue_series.attachAxis(axis_x)
            profit_series.attachAxis(axis_x)

            # **Thêm trục Y (Giá trị) và điều chỉnh tỷ lệ**
            max_y_value = max(
                max((float(row[1]) for row in data["revenue"] if row[1]), default=0),
                max((float(row[1]) for row in data["profit"] if row[1]), default=0)
            ) * 1.2
            axis_y = QValueAxis()
            axis_y.setLabelFormat("%.0f VNĐ")
            axis_y.setTitleText("Giá trị")
            axis_y.setRange(0, max_y_value)
            self.chart.addAxis(axis_y, Qt.AlignLeft)
            revenue_series.attachAxis(axis_y)
            profit_series.attachAxis(axis_y)

        # **Cập nhật giao diện biểu đồ**
        self.chart_view.update()












    
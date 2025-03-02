def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #1a1a1a;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3a3a3a;
            }
            QTableWidget {
                background-color: #2d2d2d;
                gridline-color: #404040;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #ffffff;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #404040;
                padding: 5px;
                border: 1px solid #505050;
                color: #ffffff;
                font-weight: bold;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid none;
                border-right: 5px solid none;
                border-top: 5px solid #ffffff;
                width: 0;
                height: 0;
                margin-right: 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QMessageBox, QFrame, QApplication,
                             QGraphicsDropShadowEffect, QTableWidget, QTableWidgetItem,
                             QHeaderView, QScrollArea)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QPalette
from opration import queryAll_picture
from NewDefectWindow import NewDefectWindow

class NewTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("检测历史记录")
        self.setFixedSize(1000, 600)
        self.setWindowFlags(Qt.Window)
        
        # 初始化变量
        self.search_buttons = []
        self.select_pic = 0
        self.defect_window = None
        
        # 初始化UI
        self.initUI()
        self.loadHistoryData()
        
    def initUI(self):
        """初始化用户界面"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("检测历史记录")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-family: 'Microsoft YaHei';
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 表格容器
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_frame.setStyleSheet("""
            #tableFrame {
                background: white;
                border-radius: 15px;
                border: 2px solid #e0e0e0;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 0)
        table_frame.setGraphicsEffect(shadow)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建表格
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                gridline-color: #ecf0f1;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #34495e, stop:1 #2c3e50);
                color: white;
                padding: 10px;
                border: none;
                font-family: 'Microsoft YaHei';
                font-size: 13px;
                font-weight: bold;
            }
        """)
        
        # 设置表格属性
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        
        table_layout.addWidget(self.table_widget)
        main_layout.addWidget(table_frame)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setObjectName("closeBtn")
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:1 #c0392b);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                padding: 10px 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c0392b, stop:1 #a93226);
            }
        """)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
    def loadHistoryData(self):
        """加载历史数据"""
        try:
            # 获取所有图片记录
            results = queryAll_picture()
            
            if not results:
                QMessageBox.information(self, "提示", "暂无检测历史记录")
                return
                
            # 设置表格行列数
            self.table_widget.setRowCount(len(results))
            self.table_widget.setColumnCount(5)
            
            # 设置表头
            headers = ["ID", "图片路径", "缺陷数量", "检测时间", "操作"]
            self.table_widget.setHorizontalHeaderLabels(headers)
            
            # 填充数据
            for index, value in enumerate(results):
                # 数据库返回5列：id, url, num, createtime, created_at
                # 我们只需要前4列
                id_val, url, num, createtime, created_at = value
                
                # ID列
                id_item = QTableWidgetItem(str(id_val))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(index, 0, id_item)
                
                # 图片路径列
                url_item = QTableWidgetItem(url)
                url_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(index, 1, url_item)
                
                # 缺陷数量列
                num_item = QTableWidgetItem(str(num))
                num_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(index, 2, num_item)
                
                # 检测时间列
                time_item = QTableWidgetItem(str(createtime))
                time_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(index, 3, time_item)
                
                # 操作按钮列
                detail_btn = QPushButton("查看详情")
                detail_btn.setObjectName(f"detailBtn_{index}")
                detail_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #3498db, stop:1 #2980b9);
                        border: none;
                        border-radius: 6px;
                        color: white;
                        font-size: 11px;
                        font-weight: bold;
                        font-family: 'Microsoft YaHei';
                        padding: 6px 12px;
                        margin: 2px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2980b9, stop:1 #21618c);
                    }
                """)
                
                # 连接按钮信号
                detail_btn.clicked.connect(lambda checked, row=index: self.showDefectDetail(row))
                
                self.table_widget.setCellWidget(index, 4, detail_btn)
                self.search_buttons.append(detail_btn)
                
            # 调整列宽
            header = self.table_widget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID列
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # 路径列
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 数量列
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 时间列
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 操作列
            
            # 调整行高
            self.table_widget.verticalHeader().setDefaultSectionSize(50)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载历史数据失败: {str(e)}")
            
    def showDefectDetail(self, row):
        """显示缺陷详情"""
        try:
            # 获取选中行的ID
            id_item = self.table_widget.item(row, 0)
            if id_item:
                pic_id = int(id_item.text())
                self.select_pic = pic_id
                
                # 创建缺陷详情窗口
                self.defect_window = NewDefectWindow(pic_id)
                self.defect_window.setWindowTitle("缺陷检测详情")
                self.defect_window.show()
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"显示缺陷详情失败: {str(e)}")
            
    def closeEvent(self, event):
        """关闭事件"""
        # 关闭缺陷详情窗口
        if self.defect_window:
            self.defect_window.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建并显示历史记录窗口
    history_window = NewTestWindow()
    history_window.show()
    
    sys.exit(app.exec_()) 
import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QScrollArea, QFrame, QApplication,
                             QGraphicsDropShadowEffect, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor

class ImageDisplayWindow(QMainWindow):
    """图像显示窗口 - 用于展示大图像"""
    
    def __init__(self, title="图像显示", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | 
                           Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            QLabel {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #007bff, stop:1 #0056b3);
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                padding: 8px 16px;
                margin: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0056b3, stop:1 #004085);
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.initUI()
        
    def initUI(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题标签
        self.title_label = QLabel("图像显示")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6c757d, stop:1 #495057);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                padding: 15px;
            }
        """)
        main_layout.addWidget(self.title_label)
        
        # 图像显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(600, 400)
        self.image_label.setStyleSheet("""
            QLabel {
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 缩放按钮
        self.zoom_in_btn = QPushButton("放大")
        self.zoom_in_btn.clicked.connect(self.zoomIn)
        button_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("缩小")
        self.zoom_out_btn.clicked.connect(self.zoomOut)
        button_layout.addWidget(self.zoom_out_btn)
        
        self.fit_btn = QPushButton("适应窗口")
        self.fit_btn.clicked.connect(self.fitToWindow)
        button_layout.addWidget(self.fit_btn)
        
        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button_layout.addWidget(spacer)
        
        # 关闭按钮
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dc3545, stop:1 #c82333);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c82333, stop:1 #bd2130);
            }
        """)
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
        
        # 初始化变量
        self.original_pixmap = None
        self.current_scale = 1.0
        self.min_scale = 0.1
        self.max_scale = 5.0
        
    def displayImage(self, image_path, title="图像显示"):
        """显示图像"""
        try:
            if not os.path.exists(image_path):
                QMessageBox.warning(self, "错误", f"图像文件不存在: {image_path}")
                return
                
            # 读取图像
            if image_path.lower().endswith(('.bmp', '.jpg', '.jpeg', '.png', '.tiff')):
                # 使用OpenCV读取
                image = cv2.imread(image_path)
                if image is None:
                    raise Exception("无法读取图像文件")
                    
                # 转换为Qt图像格式
                height, width, channel = image.shape
                bytes_per_line = 3 * width
                q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                q_image = q_image.rgbSwapped()
            else:
                # 使用Qt直接读取
                q_image = QImage(image_path)
                if q_image.isNull():
                    raise Exception("无法读取图像文件")
            
            # 创建QPixmap
            self.original_pixmap = QPixmap.fromImage(q_image)
            
            # 设置标题
            self.setWindowTitle(title)
            self.title_label.setText(title)
            
            # 适应窗口显示
            self.fitToWindow()
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载图像失败: {str(e)}")
            
    def displayBinaryImage(self, image_path):
        """显示二值化图像"""
        try:
            if not os.path.exists(image_path):
                QMessageBox.warning(self, "错误", f"二值化图像文件不存在: {image_path}")
                return
                
            # 读取二值化图像
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise Exception("无法读取二值化图像文件")
                
            # 转换为Qt图像格式
            height, width = image.shape
            bytes_per_line = width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            
            # 创建QPixmap
            self.original_pixmap = QPixmap.fromImage(q_image)
            
            # 设置标题
            self.setWindowTitle("二值化图像")
            self.title_label.setText("二值化图像")
            
            # 适应窗口显示
            self.fitToWindow()
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载二值化图像失败: {str(e)}")
            
    def displayDetectionResult(self, image_path):
        """显示检测结果图像"""
        self.displayImage(image_path, "缺陷检测结果")
        
    def displayLocationResult(self, image_path):
        """显示定位结果图像"""
        self.displayImage(image_path, "缺陷定位图")
        
    def zoomIn(self):
        """放大图像"""
        if self.original_pixmap:
            self.current_scale = min(self.current_scale * 1.2, self.max_scale)
            self.updateImage()
            
    def zoomOut(self):
        """缩小图像"""
        if self.original_pixmap:
            self.current_scale = max(self.current_scale / 1.2, self.min_scale)
            self.updateImage()
            
    def fitToWindow(self):
        """适应窗口大小"""
        if self.original_pixmap:
            # 获取图像标签的大小
            label_size = self.image_label.size()
            
            # 计算缩放比例
            scale_x = label_size.width() / self.original_pixmap.width()
            scale_y = label_size.height() / self.original_pixmap.height()
            
            # 使用较小的缩放比例以保持宽高比
            self.current_scale = min(scale_x, scale_y, 1.0)
            self.updateImage()
            
    def updateImage(self):
        """更新图像显示"""
        if self.original_pixmap:
            # 计算新的尺寸
            new_width = int(self.original_pixmap.width() * self.current_scale)
            new_height = int(self.original_pixmap.height() * self.current_scale)
            
            # 缩放图像
            scaled_pixmap = self.original_pixmap.scaled(
                new_width, new_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # 显示图像
            self.image_label.setPixmap(scaled_pixmap)
            
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 如果当前是适应窗口模式，重新适应
        if hasattr(self, 'current_scale') and self.current_scale <= 1.0:
            self.fitToWindow() 
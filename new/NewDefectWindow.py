import sys
import os
import cv2
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QMessageBox, QFrame, QApplication,
                             QGraphicsDropShadowEffect, QTableWidget, QTableWidgetItem,
                             QHeaderView, QScrollArea, QGroupBox, QSizePolicy)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QPalette, QImage
from opration import query_defect

class NewDefectWindow(QMainWindow):
    def __init__(self, pic_id):
        super().__init__()
        self.pic_id = pic_id
        self.setWindowTitle("缺陷检测详情")
        self.setFixedSize(1200, 700)
        self.setWindowFlags(Qt.Window)
        
        # 初始化UI
        self.initUI()
        self.loadDefectData()
        
    def initUI(self):
        """初始化用户界面"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel(f"缺陷检测详情 - 图片ID: {self.pic_id}")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-family: 'Microsoft YaHei';
                font-size: 22px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 创建左右分栏布局
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)
        
        # 左侧 - 缺陷列表
        left_panel = self.createLeftPanel()
        split_layout.addWidget(left_panel, 1)
        
        # 右侧 - 详细信息
        right_panel = self.createRightPanel()
        split_layout.addWidget(right_panel, 1)
        
        main_layout.addLayout(split_layout)
        
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
        
    def createLeftPanel(self):
        """创建左侧缺陷列表面板"""
        panel = QFrame()
        panel.setObjectName("leftPanel")
        panel.setStyleSheet("""
            #leftPanel {
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
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("缺陷列表")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title_label)
        
        # 创建表格
        self.defect_table = QTableWidget()
        self.defect_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                gridline-color: #ecf0f1;
                font-family: 'Microsoft YaHei';
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px;
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
                padding: 8px;
                border: none;
                font-family: 'Microsoft YaHei';
                font-size: 11px;
                font-weight: bold;
            }
        """)
        
        # 设置表格属性
        self.defect_table.setAlternatingRowColors(True)
        self.defect_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.defect_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.defect_table.itemSelectionChanged.connect(self.onDefectSelected)
        
        layout.addWidget(self.defect_table)
        
        return panel
        
    def createRightPanel(self):
        """创建右侧详细信息面板"""
        panel = QFrame()
        panel.setObjectName("rightPanel")
        panel.setStyleSheet("""
            #rightPanel {
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
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("缺陷详细信息")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title_label)
        
        # 详细信息组
        detail_group = QGroupBox("缺陷信息")
        detail_group.setStyleSheet("""
            QGroupBox {
                font-family: 'Microsoft YaHei';
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        detail_layout = QVBoxLayout(detail_group)
        
        # 详细信息标签 - 使用更清晰的布局
        self.detail_labels = {}
        detail_items = [
            ("缺陷ID", "defect_id", "#e74c3c"),
            ("图片ID", "pic_id", "#3498db"),
            ("缺陷类别", "defect_class", "#f39c12"),
            ("置信度", "confidence", "#27ae60"),
            ("位置坐标", "location", "#9b59b6"),
            ("检测时间", "detect_time", "#34495e")
        ]
        
        for text, name, color in detail_items:
            # 创建水平布局来显示标签和值
            item_layout = QHBoxLayout()
            
            # 标签
            label = QLabel(f"{text}:")
            label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-family: 'Microsoft YaHei';
                    font-size: 13px;
                    font-weight: bold;
                    min-width: 80px;
                }}
            """)
            
            # 值
            value_label = QLabel("暂无数据")
            value_label.setObjectName(name)
            value_label.setStyleSheet(f"""
                QLabel {{
                    color: #2c3e50;
                    font-family: 'Microsoft YaHei';
                    font-size: 13px;
                    padding: 4px 8px;
                    background: rgba(255, 255, 255, 0.8);
                    border-radius: 4px;
                    border-left: 3px solid {color};
                }}
            """)
            value_label.setWordWrap(True)  # 允许文字换行
            
            item_layout.addWidget(label)
            item_layout.addWidget(value_label, 1)  # 值标签占据剩余空间
            item_layout.addStretch()
            
            self.detail_labels[name] = value_label
            detail_layout.addLayout(item_layout)
            
        layout.addWidget(detail_group)
        
        # 图像显示区域
        image_group = QGroupBox("缺陷图像")
        image_group.setStyleSheet("""
            QGroupBox {
                font-family: 'Microsoft YaHei';
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        image_layout = QVBoxLayout(image_group)
        
        # 创建可滚动的图像显示区域
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setMinimumSize(300, 200)
        self.image_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background: #f8f9fa;
            }
        """)
        
        # 图像标签
        self.image_label = QLabel("暂无图像")
        self.image_label.setMinimumSize(280, 180)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background: #f8f9fa;
                color: #7f8c8d;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
        """)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_scroll.setWidget(self.image_label)
        
        image_layout.addWidget(self.image_scroll)
        
        layout.addWidget(image_group)
        
        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)
        
        return panel
        
    def loadDefectData(self):
        """加载缺陷数据"""
        try:
            # 获取缺陷数据
            results = query_defect(self.pic_id)
            
            if not results:
                QMessageBox.information(self, "提示", "该图片暂无缺陷记录")
                return
                
            # 设置表格行列数
            self.defect_table.setRowCount(len(results))
            self.defect_table.setColumnCount(4)
            
            # 设置表头
            headers = ["缺陷ID", "缺陷类别", "置信度", "位置坐标"]
            self.defect_table.setHorizontalHeaderLabels(headers)
            
            # 填充数据
            for index, value in enumerate(results):
                # 数据库返回8列：id, ficid, url, cla, prob, location, createtime, created_at
                # 我们只需要前7列，忽略created_at
                id_val, ficid, url, cla, prob, location, createtime, created_at = value
                
                # 缺陷ID列
                id_item = QTableWidgetItem(str(id_val))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.defect_table.setItem(index, 0, id_item)
                
                # 缺陷类别列
                class_item = QTableWidgetItem(cla)
                class_item.setTextAlignment(Qt.AlignCenter)
                self.defect_table.setItem(index, 1, class_item)
                
                # 置信度列
                prob_item = QTableWidgetItem(f"{float(prob):.4f}")
                prob_item.setTextAlignment(Qt.AlignCenter)
                self.defect_table.setItem(index, 2, prob_item)
                
                # 位置坐标列
                location_item = QTableWidgetItem(location)
                location_item.setTextAlignment(Qt.AlignCenter)
                self.defect_table.setItem(index, 3, location_item)
                
            # 调整列宽
            header = self.defect_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 缺陷ID列
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # 缺陷类别列
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 置信度列
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 位置坐标列
            
            # 调整行高
            self.defect_table.verticalHeader().setDefaultSectionSize(40)
            
            # 存储缺陷数据用于详情显示
            self.defect_data = results
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载缺陷数据失败: {str(e)}")
            
    def onDefectSelected(self):
        """缺陷选择变化事件"""
        current_row = self.defect_table.currentRow()
        if current_row >= 0 and hasattr(self, 'defect_data'):
            # 获取选中的缺陷数据
            defect_info = self.defect_data[current_row]
            self.updateDefectDetail(defect_info)
            
    def updateDefectDetail(self, defect_info):
        """更新缺陷详细信息"""
        try:
            # 数据库返回8列：id, ficid, url, cla, prob, location, createtime, created_at
            id_val, ficid, url, cla, prob, location, createtime, created_at = defect_info
            
            # 更新详细信息标签
            self.detail_labels["defect_id"].setText(str(id_val))
            self.detail_labels["pic_id"].setText(str(ficid))
            self.detail_labels["defect_class"].setText(cla)
            self.detail_labels["confidence"].setText(f"{float(prob):.4f}")
            self.detail_labels["location"].setText(location)
            self.detail_labels["detect_time"].setText(str(createtime))
            
            # 更新图像显示
            self.displayDefectImage(url, location)
                
        except Exception as e:
            print(f"更新缺陷详情失败: {e}")
            # 显示错误信息
            for label in self.detail_labels.values():
                label.setText("数据加载失败")
            self.image_label.setText("图像加载失败")
            
    def displayDefectImage(self, image_path, location_str):
        """显示缺陷图像"""
        try:
            # 检查图像路径是否存在
            if not image_path or not os.path.exists(image_path):
                self.image_label.setText("图像文件不存在")
                self.image_label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #e74c3c;
                        border-radius: 8px;
                        background: #f8f9fa;
                        color: #e74c3c;
                        font-family: 'Microsoft YaHei';
                        font-size: 12px;
                    }
                """)
                return
                
            # 读取原始图像
            original_image = cv2.imread(image_path)
            if original_image is None:
                self.image_label.setText("无法读取图像")
                return
                
            # 解析位置坐标
            try:
                # 位置格式通常是 "位置(x,y,w,h)" 或 "(x,y,w,h)"
                location_clean = location_str.replace("位置", "").replace("(", "").replace(")", "")
                coords = [int(x.strip()) for x in location_clean.split(",")]
                if len(coords) == 4:
                    x, y, w, h = coords
                    
                    # 确保坐标在图像范围内
                    height, width = original_image.shape[:2]
                    x = max(0, min(x, width - 1))
                    y = max(0, min(y, height - 1))
                    w = min(w, width - x)
                    h = min(h, height - y)
                    
                    # 提取缺陷区域
                    defect_region = original_image[y:y+h, x:x+w]
                    
                    # 在缺陷区域上绘制红色边框
                    cv2.rectangle(defect_region, (0, 0), (w-1, h-1), (0, 0, 255), 2)
                    
                    # 转换为Qt图像格式
                    defect_region_rgb = cv2.cvtColor(defect_region, cv2.COLOR_BGR2RGB)
                    height, width, channel = defect_region_rgb.shape
                    bytes_per_line = 3 * width
                    
                    q_image = QImage(defect_region_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    
                    # 创建QPixmap并缩放以适应显示区域
                    pixmap = QPixmap.fromImage(q_image)
                    
                    # 计算缩放比例，保持宽高比
                    label_size = self.image_label.size()
                    scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    # 显示图像
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_label.setStyleSheet("""
                        QLabel {
                            border: 2px solid #27ae60;
                            border-radius: 8px;
                            background: #f8f9fa;
                        }
                    """)
                    
                else:
                    # 如果无法解析坐标，显示整个图像
                    self.displayFullImage(original_image)
                    
            except Exception as e:
                print(f"解析位置坐标失败: {e}")
                # 如果解析失败，显示整个图像
                self.displayFullImage(original_image)
                
        except Exception as e:
            print(f"显示缺陷图像失败: {e}")
            self.image_label.setText("图像显示失败")
            self.image_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #e74c3c;
                    border-radius: 8px;
                    background: #f8f9fa;
                    color: #e74c3c;
                    font-family: 'Microsoft YaHei';
                    font-size: 12px;
                }
            """)
            
    def displayFullImage(self, image):
        """显示完整图像"""
        try:
            # 转换为Qt图像格式
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channel = image_rgb.shape
            bytes_per_line = 3 * width
            
            q_image = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # 创建QPixmap并缩放以适应显示区域
            pixmap = QPixmap.fromImage(q_image)
            
            # 计算缩放比例，保持宽高比
            label_size = self.image_label.size()
            scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # 显示图像
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #27ae60;
                    border-radius: 8px;
                    background: #f8f9fa;
                }
            """)
            
        except Exception as e:
            print(f"显示完整图像失败: {e}")
            self.image_label.setText("图像显示失败")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建并显示缺陷详情窗口
    defect_window = NewDefectWindow(1)  # 测试用ID
    defect_window.show()
    
    sys.exit(app.exec_()) 
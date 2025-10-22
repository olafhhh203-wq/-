import sys
import os
import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
import datetime
import json
import glob
from PIL import Image
from torchvision import transforms
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QMessageBox, QFrame, QApplication,
                             QGraphicsDropShadowEffect, QFileDialog, QProgressBar,
                             QTableWidget, QTableWidgetItem, QScrollArea, QGridLayout,
                             QSplitter, QGroupBox, QTextEdit, QComboBox, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor

# 导入自定义模块
from NewImageDisplayWindow import ImageDisplayWindow
from NewTestWindow import NewTestWindow
from NewDefectWindow import NewDefectWindow
import opration

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 全局变量
filepath = []
filepath1 = []

# 数据变换
data_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 加载模型
try:
    from model import model as ModelClass
    model = ModelClass()
    model.load_state_dict(torch.load(os.path.join(current_dir, "EfficientNet_self1.pth"), map_location='cpu'))
    model.eval()
except Exception as e:
    print(f"模型加载失败: {e}")
    model = None

# 加载类别索引
try:
    with open(os.path.join(current_dir, "class_indices.json"), 'r', encoding='utf-8') as f:
        class_indices = json.load(f)
except Exception as e:
    print(f"类别索引加载失败: {e}")
    class_indices = {"0": "正常", "1": "划痕", "2": "漏涂"}

# 加载图像文件列表
def load_image_files():
    """加载图像文件列表"""
    global filepath, filepath1
    
    # 尝试多个可能的路径
    possible_paths = [
        os.path.join(current_dir, "data/Img"),
        os.path.join(current_dir, "data/test"),
        os.path.join(current_dir, "data")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            # 查找图像文件
            image_extensions = ['*.bmp', '*.jpg', '*.jpeg', '*.png', '*.tiff']
            for ext in image_extensions:
                files = glob.glob(os.path.join(path, ext))
                files.extend(glob.glob(os.path.join(path, ext.upper())))
                if files:
                    filepath = sorted(files)
                    filepath1 = filepath.copy()
                    print(f"找到 {len(filepath)} 个图像文件在 {path}")
                    return
    
    print("警告: 未找到图像文件")

# 加载图像文件
load_image_files()

class DetectionThread(QThread):
    """检测线程"""
    finishSignal = pyqtSignal(list)
    progressSignal = pyqtSignal(int)
    
    def __init__(self, filepath, parent=None):
        super(DetectionThread, self).__init__(parent)
        self.filepath = filepath
        self.resultList = [0, 0, 0]  # [正常, 划痕, 漏涂]
        self.is_running = True
        
    def predict(self, file_path):
        """预测单张图片"""
        try:
            img = Image.open(file_path)
            img = data_transform(img)
            img = torch.unsqueeze(img, dim=0)
            
            with torch.no_grad():
                result = model(img)
                result = torch.squeeze(result)
                predict = torch.softmax(result, dim=0)
                predict_cla = torch.argmax(predict).numpy()
                
            return predict_cla, predict[predict_cla].item()
        except Exception as e:
            print(f"预测错误: {e}")
            return 0, 0.0
            
    def run(self):
        """运行检测"""
        # 重置结果
        self.resultList = [0, 0, 0]  # [正常, 划痕, 漏涂]
        
        print(f"开始检测 {len(self.filepath)} 张图像")
        
        for i, file_path in enumerate(self.filepath):
            if not self.is_running:
                break
                
            try:
                predict, prob = self.predict(file_path)
                
                # 根据类别映射统计结果
                # 正常类别: 0,1,2,3,5,7 (class1OK, class2OK, class3OK, class4OK, class6OK, class8OK)
                # 缺陷类别: 4=漏涂(class5NG), 6=划痕(class7NG)
                if predict in [0, 1, 2, 3, 5, 7]:  # 正常类别
                    self.resultList[0] += 1
                    print(f"图像 {i+1}: 类别 {predict} -> 正常")
                elif predict == 4:  # 漏涂
                    self.resultList[2] += 1
                    print(f"图像 {i+1}: 类别 {predict} -> 漏涂")
                elif predict == 6:  # 划痕
                    self.resultList[1] += 1
                    print(f"图像 {i+1}: 类别 {predict} -> 划痕")
                else:
                    # 未知类别，归类为正常
                    self.resultList[0] += 1
                    print(f"图像 {i+1}: 类别 {predict} -> 未知(归类为正常)")
                    
                self.progressSignal.emit(i + 1)
                
            except Exception as e:
                print(f"处理图片 {file_path} 时出错: {e}")
                continue
                
        print(f"检测完成，统计结果: 正常={self.resultList[0]}, 划痕={self.resultList[1]}, 漏涂={self.resultList[2]}")
        self.finishSignal.emit(self.resultList)

class DatabaseThread(QThread):
    """数据库操作线程"""
    finishSignal = pyqtSignal(bool)
    
    def __init__(self, picture_data, defect_data, parent=None):
        super(DatabaseThread, self).__init__(parent)
        self.picture_data = picture_data
        self.defect_data = defect_data
        
    def run(self):
        """运行数据库操作"""
        try:
            # 插入图片数据
            picid = opration.insert_picture(
                self.picture_data[0], 
                int(self.picture_data[1]), 
                self.picture_data[2]
            )
            
            # 插入缺陷数据
            for defect in self.defect_data:
                defect[0] = picid
                opration.insert_defect(*defect)
                
            self.finishSignal.emit(True)
        except Exception as e:
            print(f"数据库操作失败: {e}")
            self.finishSignal.emit(False) 

class NewMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("锂电池隔膜缺陷检测系统")
        self.setMinimumSize(1400, 900)
        # 设置初始尺寸，避免全屏
        self.resize(1600, 1000)
        # 确保窗口有正常的边框和按钮
        self.setWindowFlags(Qt.Window)
        
        # 初始化变量
        self.current_image = None
        self.resultList = [0, 0, 0]
        self.detection_thread = None
        self.database_thread = None
        self.isPause = False
        self.countPicture = 0
        self.rects = []
        self.db_picture = []
        self.db_defect = [[0 for i in range(6)] for i in range(116)]
        
        # 图像显示窗口
        self.image_display_window = None
        
        self.initUI()
        self.setupConnections()
        
        # 窗口居中
        self.centerWindow()
        
    def centerWindow(self):
        """窗口居中"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def ensureNormalWindow(self):
        """确保窗口正常显示，不是全屏或最大化"""
        # 确保窗口不是全屏
        if self.isFullScreen():
            self.showNormal()
        
        # 确保窗口不是最大化
        if self.isMaximized():
            self.showNormal()
            
        # 设置合适的尺寸
        self.resize(1600, 1000)
        
        # 再次居中
        self.centerWindow()
        
    def initUI(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板
        left_panel = self.createLeftPanel()
        splitter.addWidget(left_panel)
        
        # 右侧面板
        right_panel = self.createRightPanel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([800, 600])
        
    def createLeftPanel(self):
        """创建左侧图像显示面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # 图像显示区域
        image_group = QGroupBox("图像显示")
        image_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                border: 2px solid #dee2e6;
                border-radius: 10px;
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
        
        # 图像标签
        self.image_display = QLabel()
        self.image_display.setMinimumSize(600, 400)
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setStyleSheet("""
            QLabel {
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.image_display.setText("请选择图像文件")
        image_layout.addWidget(self.image_display)
        
        left_layout.addWidget(image_group)
        
        # 控制按钮区域
        control_group = QGroupBox("操作控制")
        control_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        control_layout = QHBoxLayout(control_group)
        
        # 选择文件按钮
        self.select_file_btn = QPushButton("选择文件")
        self.select_file_btn.setObjectName("selectFileBtn")
        self.select_file_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
        """)
        control_layout.addWidget(self.select_file_btn)
        
        # 开始检测按钮
        self.start_detect_btn = QPushButton("开始检测")
        self.start_detect_btn.setObjectName("startDetectBtn")
        self.start_detect_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #229954, stop:1 #27ae60);
            }
        """)
        control_layout.addWidget(self.start_detect_btn)
        
        # 暂停按钮
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setObjectName("pauseBtn")
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f39c12, stop:1 #e67e22);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e67e22, stop:1 #d35400);
            }
        """)
        control_layout.addWidget(self.pause_btn)
        
        # 下一张按钮
        self.next_btn = QPushButton("下一张")
        self.next_btn.setObjectName("nextBtn")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b59b6, stop:1 #8e44ad);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8e44ad, stop:1 #7d3c98);
            }
        """)
        control_layout.addWidget(self.next_btn)
        
        left_layout.addWidget(control_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                text-align: center;
                font-size: 12px;
                font-family: 'Microsoft YaHei';
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                border-radius: 6px;
            }
        """)
        left_layout.addWidget(self.progress_bar)
        
        return left_widget 
        
    def createRightPanel(self):
        """创建右侧信息面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # 结果显示区域
        result_group = QGroupBox("检测结果")
        result_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        result_layout = QGridLayout(result_group)
        
        # 结果标签
        self.result_labels = {}
        result_items = [
            ("normal_label", "正常:", "0"),
            ("defect_label", "缺陷:", "0"),
            ("total_label", "总计:", "0")
        ]
        
        for i, (name, text, value) in enumerate(result_items):
            label = QLabel(f"{text} {value}")
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    font-family: 'Microsoft YaHei';
                    padding: 8px;
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                }
            """)
            self.result_labels[name] = label
            result_layout.addWidget(label, i // 2, i % 2)
            
        right_layout.addWidget(result_group)
        
        # 操作按钮区域
        action_group = QGroupBox("图像处理")
        action_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        action_layout = QGridLayout(action_group)
        
        # 操作按钮
        action_buttons = [
            ("二值化图像", "binaryBtn", "#9b59b6"),
            ("缺陷检测结果", "detectResultBtn", "#e67e22"),
            ("缺陷定位图", "locationBtn", "#f39c12"),
            ("统计结果", "statisticsBtn", "#16a085"),
            ("保存到数据库", "saveDbBtn", "#8e44ad"),
            ("历史记录", "historyBtn", "#34495e")
        ]
        
        for i, (text, name, color) in enumerate(action_buttons):
            btn = QPushButton(text)
            btn.setObjectName(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color}, stop:1 {color}dd);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                    font-family: 'Microsoft YaHei';
                    padding: 12px;
                    margin: 3px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color}dd, stop:1 {color}bb);
                }}
            """)
            setattr(self, name, btn)
            action_layout.addWidget(btn, i // 2, i % 2)
            
        right_layout.addWidget(action_group)
        
        # 信息显示区域
        info_group = QGroupBox("检测信息")
        info_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        info_layout = QVBoxLayout(info_group)
        
        # 信息文本框
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(150)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                font-family: 'Microsoft YaHei';
            }
        """)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        right_layout.addWidget(info_group)
        
        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(spacer)
        
        return right_widget
        
    def setupConnections(self):
        """设置信号连接"""
        # 文件操作
        self.select_file_btn.clicked.connect(self.selectFile)
        self.next_btn.clicked.connect(self.nextPicture)
        
        # 检测控制
        self.start_detect_btn.clicked.connect(self.startDetection)
        self.pause_btn.clicked.connect(self.pauseDetection)
        
        # 图像处理 - 弹出新窗口显示
        self.binaryBtn.clicked.connect(self.showBinaryImage)
        self.detectResultBtn.clicked.connect(self.showDetectResult)
        self.locationBtn.clicked.connect(self.showLocationResult)
        
        # 结果操作
        self.statisticsBtn.clicked.connect(self.showStatistics)
        self.saveDbBtn.clicked.connect(self.saveToDatabase)
        self.historyBtn.clicked.connect(self.showHistory)
        
    def selectFile(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图像文件", "", 
            "图像文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        
        if file_path:
            self.loadImage(file_path)
            self.addInfo(f"已选择文件: {os.path.basename(file_path)}")
            
    def loadImage(self, file_path):
        """加载图像"""
        try:
            # 读取图像
            image = cv2.imread(file_path)
            if image is None:
                raise Exception("无法读取图像文件")
                
            # 转换为Qt图像格式
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            q_image = q_image.rgbSwapped()
            
            # 缩放图像以适应显示区域
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                self.image_display.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            # 显示图像
            self.image_display.setPixmap(scaled_pixmap)
            self.current_image = file_path
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载图像失败: {str(e)}")
            
    def startDetection(self):
        """开始检测"""
        if not self.current_image:
            QMessageBox.warning(self, "提示", "请先选择图像文件")
            return
            
        # 重置结果
        self.resultList = [0, 0, 0]
        self.updateResultDisplay()
        
        # 读取当前图像
        src = cv2.imread(self.current_image)
        if src is None:
            QMessageBox.warning(self, "错误", "无法读取当前图像")
            return
            
        try:
            # 1. 对大图进行二值化和轮廓检测
            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            ret, binary = cv2.threshold(gray, 39, 255, cv2.THRESH_BINARY_INV)
            se = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3), (-1, -1))
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, se)
            binary = cv2.erode(binary, se, iterations=2)
            binary = cv2.dilate(binary, se, iterations=3)
            binary = cv2.dilate(binary, se, iterations=1)
            binary = cv2.erode(binary, se, iterations=2)
            binary = cv2.dilate(binary, se, iterations=1)
            
            # 保存二值化图像
            binary_dir = os.path.join(current_dir, "data/binary")
            os.makedirs(binary_dir, exist_ok=True)
            current_filename = os.path.splitext(os.path.basename(self.current_image))[0]
            binary_path = os.path.join(binary_dir, f"{current_filename}_binary.bmp")
            cv2.imwrite(binary_path, binary)
            
            # 2. 查找轮廓并筛选
            contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            height, width = src.shape[:2]
            rects = []
            
            # 轮廓筛选 - 使用demo.py的参数
            index = 1
            for c in range(len(contours)):
                x, y, w, h = cv2.boundingRect(contours[c])
                area = cv2.contourArea(contours[c])
                if h > (height//2):
                    continue
                if area < 800:
                    continue
                if area > 150000:
                    continue
                if w/h > 3:
                    continue
                if h/w > 3:
                    continue
                rects.append([x, y, w, h])
                
                # 保存检测到的区域
                detect_dir = os.path.join(current_dir, "data/detect")
                os.makedirs(detect_dir, exist_ok=True)
                recimg = src[y:y + h, x:x + w]
                cv2.imwrite(os.path.join(detect_dir, f"region_{index}.png"), recimg)
                index += 1
            
            self.addInfo(f"检测到 {len(rects)} 个可能的缺陷区域")
            
            # 3. 对每个缺陷区域进行分类
            image_path = os.path.join(current_dir, "data/detect")
            filepath = glob.glob(os.path.join(image_path, "*.png"))
            filepath = sorted(filepath, key=os.path.getctime)
            
            defect_count = 0
            self.current_detection_results = []
            
            for i in range(len(filepath)):
                try:
                    # 对每个缺陷区域进行分类
                    img = Image.open(filepath[i])
                    img = data_transform(img)
                    img = torch.unsqueeze(img, dim=0)
                    
                    with torch.no_grad():
                        result = model(img)
                        result = torch.squeeze(result)
                        predict = torch.softmax(result, dim=0)
                        predict_cla = torch.argmax(predict).numpy()
                        confidence = predict[predict_cla].item()
                    
                    # 根据分类结果统计
                    if predict_cla in [0, 1, 2, 3, 5, 7]:  # 正常类别
                        self.resultList[0] += 1
                    elif predict_cla == 4:  # 漏涂
                        self.resultList[2] += 1
                        defect_count += 1
                        # 保存检测结果用于图像生成
                        if i < len(rects):
                            x, y, w, h = rects[i]
                            self.current_detection_results.append([x, y, w, h, 2, confidence])  # 2表示漏涂
                    elif predict_cla == 6:  # 划痕
                        self.resultList[1] += 1
                        defect_count += 1
                        # 保存检测结果用于图像生成
                        if i < len(rects):
                            x, y, w, h = rects[i]
                            self.current_detection_results.append([x, y, w, h, 1, confidence])  # 1表示划痕
                    else:
                        self.resultList[0] += 1
                        
                    class_name = class_indices.get(str(predict_cla), f"未知类别{predict_cla}")
                    self.addInfo(f"区域 {i+1}: {class_name} (置信度: {confidence:.4f})")
                    
                except Exception as e:
                    print(f"分类区域 {i+1} 时出错: {e}")
                    self.resultList[0] += 1  # 分类失败时归类为正常
            
            # 更新显示
            self.updateResultDisplay()
            self.addInfo(f"检测完成 - 检测到 {defect_count} 个缺陷，正常:{self.resultList[0]}, 划痕:{self.resultList[1]}, 漏涂:{self.resultList[2]}")
            
        except Exception as e:
            self.addInfo(f"检测失败: {str(e)}")
            QMessageBox.warning(self, "错误", f"检测失败: {str(e)}")
        
    def pauseDetection(self):
        """暂停/继续检测"""
        if self.detection_thread and self.detection_thread.isRunning():
            if self.isPause:
                # 继续检测
                self.isPause = False
                self.pause_btn.setText("暂停")
                self.addInfo("继续检测...")
            else:
                # 暂停检测
                self.isPause = True
                self.pause_btn.setText("继续")
                self.addInfo("检测已暂停")
                
    def onDetectionFinished(self, result_list):
        """检测完成回调"""
        self.resultList = result_list
        self.updateResultDisplay()
        self.progress_bar.setVisible(False)
        self.addInfo(f"检测完成 - 正常: {result_list[0]}, 缺陷: {result_list[1] + result_list[2]}")
        
    def updateProgress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def updateResultDisplay(self):
        """更新结果显示"""
        self.result_labels["normal_label"].setText(f"正常: {self.resultList[0]}")
        self.result_labels["defect_label"].setText(f"缺陷: {self.resultList[1] + self.resultList[2]}")
        self.result_labels["total_label"].setText(f"总计: {sum(self.resultList)}")
        
    def nextPicture(self):
        """下一张图片"""
        if not filepath1:
            QMessageBox.warning(self, "提示", "没有可用的图片文件")
            return
            
        if self.countPicture >= len(filepath1):
            self.countPicture = 0
            
        try:
            self.loadImage(filepath1[self.countPicture])
            self.countPicture += 1
            self.addInfo(f"切换到下一张图片: {os.path.basename(filepath1[self.countPicture-1])}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载下一张图片失败: {str(e)}")
            
    def showBinaryImage(self):
        """显示二值化图像 - 弹出新窗口"""
        if not self.current_image:
            QMessageBox.warning(self, "提示", "请先选择图像文件")
            return
            
        try:
            # 生成二值化图像文件路径 - 使用当前图像的文件名
            current_filename = os.path.splitext(os.path.basename(self.current_image))[0]
            binary_path = os.path.join(current_dir, "data/binary", f"{current_filename}_binary.bmp")
            
            # 每次都重新生成二值化图像
            self.generateBinaryImage()
            binary_path = os.path.join(current_dir, "data/binary", f"{current_filename}_binary.bmp")
                
            if os.path.exists(binary_path):
                # 创建图像显示窗口
                self.image_display_window = ImageDisplayWindow("二值化图像")
                self.image_display_window.displayBinaryImage(binary_path)
                self.image_display_window.show()
                self.addInfo("已打开二值化图像窗口")
            else:
                QMessageBox.warning(self, "错误", "无法生成二值化图像")
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"显示二值化图像失败: {str(e)}")
            
    def generateBinaryImage(self):
        """生成二值化图像 - 使用原始代码的参数和逻辑"""
        try:
            # 读取原始图像
            image = cv2.imread(self.current_image)
            if image is None:
                raise Exception("无法读取原始图像")
                
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 使用原始代码的二值化参数
            ret, binary = cv2.threshold(gray, 39, 255, cv2.THRESH_BINARY_INV)
            
            # 形态学处理 - 参考原始代码
            se = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3), (-1, -1))
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, se)
            binary = cv2.erode(binary, se, iterations=2)
            binary = cv2.dilate(binary, se, iterations=3)
            binary = cv2.dilate(binary, se, iterations=1)
            binary = cv2.erode(binary, se, iterations=2)
            binary = cv2.dilate(binary, se, iterations=1)
            
            # 保存二值化图像 - 使用当前图像的文件名
            binary_dir = os.path.join(current_dir, "data/binary")
            os.makedirs(binary_dir, exist_ok=True)
            
            # 使用当前图像的文件名作为基础
            current_filename = os.path.splitext(os.path.basename(self.current_image))[0]
            binary_path = os.path.join(binary_dir, f"{current_filename}_binary.bmp")
            cv2.imwrite(binary_path, binary)
            
            self.addInfo(f"已生成二值化图像: {os.path.basename(binary_path)}")
            
        except Exception as e:
            raise Exception(f"生成二值化图像失败: {str(e)}")
            
    def showDetectResult(self):
        """显示检测结果 - 弹出新窗口"""
        if not self.current_image:
            QMessageBox.warning(self, "提示", "请先选择图像文件")
            return
            
        try:
            # 生成检测结果图像文件路径 - 使用当前图像的文件名
            current_filename = os.path.splitext(os.path.basename(self.current_image))[0]
            result_path = os.path.join(current_dir, "data/binary", f"{current_filename}_detection_result.bmp")
            
            # 每次都重新生成检测结果图像
            self.generateDetectionResult()
            result_path = os.path.join(current_dir, "data/binary", f"{current_filename}_detection_result.bmp")
                
            if os.path.exists(result_path):
                # 创建图像显示窗口
                self.image_display_window = ImageDisplayWindow("缺陷检测结果")
                self.image_display_window.displayDetectionResult(result_path)
                self.image_display_window.show()
                self.addInfo("已打开缺陷检测结果窗口")
            else:
                QMessageBox.warning(self, "错误", "无法生成检测结果图像")
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"显示检测结果失败: {str(e)}")
            
    def generateDetectionResult(self):
        """生成检测结果图像"""
        try:
            # 读取原始图像
            src = cv2.imread(self.current_image)
            if src is None:
                raise Exception("无法读取原始图像")
                
            # 创建检测结果图像
            result_image = src.copy()
            
            # 根据检测结果在原图上标注缺陷区域
            if hasattr(self, 'current_detection_results') and self.current_detection_results:
                for defect_info in self.current_detection_results:
                    x, y, w, h, defect_type, confidence = defect_info
                    
                    if defect_type == 1:  # 划痕 - 绿色框
                        color = (0, 255, 0)  # BGR格式
                        label = "划痕(7NG)"
                    elif defect_type == 2:  # 漏涂 - 红色框
                        color = (0, 0, 255)  # BGR格式
                        label = "漏涂(5NG)"
                    else:
                        # 正常类型不显示框
                        continue
                        
                    # 绘制矩形框
                    cv2.rectangle(result_image, (x, y), (x + w, y + h), color, 2)
                    
                    # 添加标签
                    cv2.putText(result_image, label, (x, y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # 保存检测结果图像
            result_dir = os.path.join(current_dir, "data/binary")
            os.makedirs(result_dir, exist_ok=True)
            
            current_filename = os.path.splitext(os.path.basename(self.current_image))[0]
            result_path = os.path.join(result_dir, f"{current_filename}_detection_result.bmp")
            cv2.imwrite(result_path, result_image)
            
            self.addInfo(f"已生成检测结果图像: {os.path.basename(result_path)}")
            
        except Exception as e:
            raise Exception(f"生成检测结果图像失败: {str(e)}")
            
    def showLocationResult(self):
        """显示定位结果 - 弹出新窗口"""
        if not self.current_image:
            QMessageBox.warning(self, "提示", "请先选择图像文件")
            return
            
        try:
            # 生成定位结果图像文件路径 - 使用当前图像的文件名
            current_filename = os.path.splitext(os.path.basename(self.current_image))[0]
            location_path = os.path.join(current_dir, "data/binary", f"{current_filename}_location_result.bmp")
            
            # 每次都重新生成定位结果图像
            self.generateLocationResult()
            location_path = os.path.join(current_dir, "data/binary", f"{current_filename}_location_result.bmp")
                
            if os.path.exists(location_path):
                # 创建图像显示窗口
                self.image_display_window = ImageDisplayWindow("缺陷定位图")
                self.image_display_window.displayLocationResult(location_path)
                self.image_display_window.show()
                self.addInfo("已打开缺陷定位图窗口")
            else:
                QMessageBox.warning(self, "错误", "无法生成定位结果图像")
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"显示定位结果失败: {str(e)}")
            
    def generateLocationResult(self):
        """生成定位结果图像 - 显示所有检测到的缺陷区域"""
        try:
            # 读取原始图像
            src = cv2.imread(self.current_image)
            if src is None:
                raise Exception("无法读取原始图像")
                
            # 创建定位结果图像
            location_image = src.copy()
            
            # 显示所有检测到的缺陷区域（绿色框）
            if hasattr(self, 'current_detection_results') and self.current_detection_results:
                for defect_info in self.current_detection_results:
                    x, y, w, h, defect_type, confidence = defect_info
                    
                    # 所有检测到的区域都用绿色框标注
                    color = (0, 255, 0)  # 绿色
                    label = "缺陷区域"
                    
                    # 绘制矩形框
                    cv2.rectangle(location_image, (x, y), (x + w, y + h), color, 2)
                    
                    # 添加标签
                    cv2.putText(location_image, label, (x, y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # 保存定位结果图像
            result_dir = os.path.join(current_dir, "data/binary")
            os.makedirs(result_dir, exist_ok=True)
            
            current_filename = os.path.splitext(os.path.basename(self.current_image))[0]
            location_path = os.path.join(result_dir, f"{current_filename}_location_result.bmp")
            cv2.imwrite(location_path, location_image)
            
            defect_count = len(self.current_detection_results) if hasattr(self, 'current_detection_results') else 0
            self.addInfo(f"已生成定位结果图像: {os.path.basename(location_path)} (检测到 {defect_count} 个缺陷区域)")
            
        except Exception as e:
            raise Exception(f"生成定位结果图像失败: {str(e)}")
            
    def detectCurrentImage(self):
        """检测当前图像"""
        try:
            if not self.current_image:
                return
                
            # 使用模型预测当前图像
            img = Image.open(self.current_image)
            img = data_transform(img)
            img = torch.unsqueeze(img, dim=0)
            
            with torch.no_grad():
                result = model(img)
                result = torch.squeeze(result)
                predict = torch.softmax(result, dim=0)
                predict_cla = torch.argmax(predict).numpy()
                confidence = predict[predict_cla].item()
            
            # 模拟缺陷位置（实际应用中应该从模型输出中获取）
            # 这里使用图像中心作为示例
            image = cv2.imread(self.current_image)
            height, width = image.shape[:2]
            
            self.current_detection_results = []
            
            # 根据类别映射判断缺陷类型
            # 正常类别: 0,1,2,3,5,7 (class1OK, class2OK, class3OK, class4OK, class6OK, class8OK)
            # 缺陷类别: 4=漏涂(class5NG), 6=划痕(class7NG)
            if predict_cla == 4:  # 漏涂缺陷
                # 模拟缺陷位置
                x = width // 4
                y = height // 4
                w = width // 4
                h = height // 4
                self.current_detection_results.append([x, y, w, h, 2, confidence])  # 2表示漏涂
                
            elif predict_cla == 6:  # 划痕缺陷
                # 模拟缺陷位置
                x = width // 4
                y = height // 4
                w = width // 4
                h = height // 4
                self.current_detection_results.append([x, y, w, h, 1, confidence])  # 1表示划痕
            
            # 获取类别名称
            class_name = class_indices.get(str(predict_cla), f"未知类别{predict_cla}")
            self.addInfo(f"当前图像检测完成: {class_name} (置信度: {confidence:.4f})")
            
        except Exception as e:
            self.addInfo(f"检测当前图像失败: {str(e)}")
            
    def detectDefects(self, image):
        """缺陷检测 - 参考原始代码的detect方法"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 使用原始代码的二值化参数
            ret, binary = cv2.threshold(gray, 39, 255, cv2.THRESH_BINARY_INV)
            
            # 形态学处理 - 参考原始代码
            se = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3), (-1, -1))
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, se)
            binary = cv2.erode(binary, se, iterations=2)
            binary = cv2.dilate(binary, se, iterations=3)
            binary = cv2.dilate(binary, se, iterations=1)
            binary = cv2.erode(binary, se, iterations=2)
            binary = cv2.dilate(binary, se, iterations=1)
            
            # 查找轮廓
            contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            height, width = image.shape[:2]
            
            # 轮廓筛选 - 更严格的筛选条件
            rects = []
            for c in range(len(contours)):
                # 轮廓外接矩形
                x, y, w, h = cv2.boundingRect(contours[c])
                # 轮廓面积
                area = cv2.contourArea(contours[c])
                
                # 更严格的筛选条件
                if h > (height // 3):  # 高度不能超过图像高度的1/3
                    continue
                if area < 1000:  # 最小面积增加到1000
                    continue
                if area > 50000:  # 最大面积减少到50000
                    continue
                if w / h > 2:  # 宽高比不能超过2:1
                    continue
                if h / w > 2:  # 高宽比不能超过2:1
                    continue
                if w < 30 or h < 30:  # 最小尺寸限制
                    continue
                if w > width // 4 or h > height // 4:  # 最大尺寸限制
                    continue
                    
                rects.append([x, y, w, h])
            
            return rects, binary
            
        except Exception as e:
            self.addInfo(f"缺陷检测失败: {str(e)}")
            return [], None
            
    def showStatistics(self):
        """显示统计结果"""
        try:
            plt.rcParams['font.family'] = ['SimHei']
            plt.rcParams['axes.unicode_minus'] = False
            
            x = ['正常', '划痕', '漏涂']
            plt.figure(figsize=(8, 6))
            y = self.resultList
            plt.bar(x, y, align='center', color='b', edgecolor='r', 
                    tick_label=['正常', '划痕', '漏涂'],
                    alpha=0.6, ls='-', lw=2, width=0.7, hatch='', label='缺陷个数')
            plt.xlabel("缺陷类型")
            plt.ylabel("检测结果")
            plt.title("缺陷检测分布图")
            
            for a, b in zip(x, y):
                plt.text(a, b + 0.25, '%.0f' % b, ha='center', va='bottom', fontsize=12)
            plt.legend()
            plt.show()
            
            self.addInfo("已显示统计结果")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"显示统计结果失败: {str(e)}")
            
    def saveToDatabase(self):
        """保存到数据库"""
        try:
            if not self.current_image:
                QMessageBox.warning(self, "提示", "请先选择图像文件")
                return
                
            # 准备图片数据
            num = self.resultList[1] + self.resultList[2]  # 缺陷总数
            self.db_picture = [
                self.current_image,
                num,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            
            # 准备缺陷数据 - 根据实际检测结果
            self.db_defect = []
            
            # 检测当前图像
            if not hasattr(self, 'current_detection_results'):
                self.detectCurrentImage()
            
            # 根据检测结果生成缺陷数据
            if hasattr(self, 'current_detection_results'):
                for defect_info in self.current_detection_results:
                    x, y, w, h, defect_type, confidence = defect_info
                    
                    if defect_type == 1:  # 划痕缺陷
                        defect = [0, self.current_image, "划痕(class7NG)", confidence, f"位置({x},{y},{w},{h})", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                        self.db_defect.append(defect)
                        
                    elif defect_type == 2:  # 漏涂缺陷
                        defect = [0, self.current_image, "漏涂(class5NG)", confidence, f"位置({x},{y},{w},{h})", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                        self.db_defect.append(defect)
            
            # 创建数据库线程
            self.database_thread = DatabaseThread(self.db_picture, self.db_defect)
            self.database_thread.finishSignal.connect(self.onDatabaseFinished)
            self.database_thread.start()
            
            self.addInfo("正在保存到数据库...")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存到数据库失败: {str(e)}")
            
    def onDatabaseFinished(self, success):
        """数据库操作完成回调"""
        if success:
            QMessageBox.information(self, "提示", "数据已成功保存到数据库")
            self.addInfo("数据保存成功")
        else:
            QMessageBox.warning(self, "错误", "数据保存失败")
            self.addInfo("数据保存失败")
            
    def showHistory(self):
        """显示历史记录"""
        try:
            self.history_window = NewTestWindow()
            self.history_window.show()
            self.addInfo("已打开历史记录窗口")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开历史记录失败: {str(e)}")
            
    def addInfo(self, message):
        """添加信息到信息显示区域"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.info_text.append(f"[{current_time}] {message}")
        
        # 自动滚动到底部
        scrollbar = self.info_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum()) 
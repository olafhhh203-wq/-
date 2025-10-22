import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QFrame, QApplication, QGraphicsDropShadowEffect, QSizePolicy)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor

import opration
from NewMainWindow import NewMainWindow

class NewLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("锂电池隔膜缺陷检测系统 - 登录")
        self.setFixedSize(1000, 700)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始化变量
        self.main_window = None
        
        self.initUI()
        self.setupConnections()
        
        # 窗口居中
        self.centerWindow()
        
        # 添加淡入动画
        self.setWindowOpacity(0.0)
        self.fadeInAnimation()
        
    def centerWindow(self):
        """窗口居中"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def fadeInAnimation(self):
        """淡入动画"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
        
    def initUI(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建主框架
        main_frame = QFrame()
        main_frame.setObjectName("mainFrame")
        main_frame.setStyleSheet("""
            QFrame#mainFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        main_frame.setGraphicsEffect(shadow)
        
        main_layout.addWidget(main_frame)
        
        # 框架内部布局
        frame_layout = QHBoxLayout(main_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)
        
        # 左侧面板
        left_panel = self.createLeftPanel()
        frame_layout.addWidget(left_panel)
        
        # 右侧面板
        right_panel = self.createRightPanel()
        frame_layout.addWidget(right_panel)
        
    def createLeftPanel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(40, 40, 20, 40)
        left_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("锂电池隔膜缺陷检测系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                margin-bottom: 20px;
            }
        """)
        left_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("基于深度学习的智能检测平台")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                font-family: 'Microsoft YaHei';
                margin-bottom: 40px;
            }
        """)
        left_layout.addWidget(subtitle_label)
        
        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(spacer)
        
        # 系统信息
        info_label = QLabel("©锂电池隔膜缺陷检测系统")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
                font-family: 'Microsoft YaHei';
            }
        """)
        left_layout.addWidget(info_label)
        
        return left_widget
        
    def createRightPanel(self):
        """创建右侧面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(40, 60, 40, 60)
        right_layout.setSpacing(25)
        
        # 登录标题
        login_title = QLabel("用户登录")
        login_title.setAlignment(Qt.AlignCenter)
        login_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                margin-bottom: 10px;
            }
        """)
        right_layout.addWidget(login_title)
        
        # 用户名输入框
        username_label = QLabel("用户名:")
        username_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
            }
        """)
        right_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                background: white;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        right_layout.addWidget(self.username_input)
        
        # 密码输入框
        password_label = QLabel("密码:")
        password_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                margin-top: 15px;
            }
        """)
        right_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                background: white;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        right_layout.addWidget(self.password_input)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                padding: 12px 30px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a5fc8, stop:1 #5a3080);
            }
        """)
        button_layout.addWidget(self.login_btn)
        
        # 注册按钮
        self.register_btn = QPushButton("注册")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                padding: 12px 30px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #229954, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e8449, stop:1 #229954);
            }
        """)
        button_layout.addWidget(self.register_btn)
        
        right_layout.addLayout(button_layout)
        
        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(spacer)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        close_btn.clicked.connect(self.close)
        
        # 将关闭按钮添加到右上角
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        right_layout.addLayout(close_layout)
        
        return right_widget
        
    def setupConnections(self):
        """设置信号连接"""
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)
        
        # 回车键登录
        self.username_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)
        
    def login(self):
        """登录功能"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")
            return
            
        try:
            # 验证登录
            result = opration.query_login(username, password)
            
            if result:
                QMessageBox.information(self, "成功", "登录成功！")
                
                # 关闭登录窗口
                self.close()
                
                # 创建并显示主窗口
                self.main_window = NewMainWindow()
                self.main_window.setWindowTitle("锂电池隔膜缺陷检测系统")
                
                # 确保窗口正常显示
                self.main_window.ensureNormalWindow()
                self.main_window.show()
                
            else:
                QMessageBox.warning(self, "错误", "用户名或密码错误")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录失败: {str(e)}")
            
    def register(self):
        """注册功能"""
        from NewRegister import NewRegister
        
        try:
            self.register_window = NewRegister()
            self.register_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开注册窗口失败: {str(e)}")
            
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于窗口拖动"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 用于窗口拖动"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept() 
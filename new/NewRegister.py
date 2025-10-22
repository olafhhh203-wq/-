import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QFrame, QApplication, QGraphicsDropShadowEffect, QSizePolicy)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QPalette
from opration import query_username, insert_user

class NewRegister(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("锂电池隔膜缺陷检测系统 - 用户注册")
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框窗口
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        
        # 初始化UI
        self.initUI()
        self.setupAnimations()
        
    def initUI(self):
        # 主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧装饰面板
        left_panel = self.createLeftPanel()
        main_layout.addWidget(left_panel, 1)
        
        # 右侧注册面板
        right_panel = self.createRightPanel()
        main_layout.addWidget(right_panel, 1)
        
    def createLeftPanel(self):
        """创建左侧装饰面板"""
        panel = QFrame()
        panel.setObjectName("leftPanel")
        panel.setStyleSheet("""
            #leftPanel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 20px 0px 0px 20px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 60, 50, 60)
        
        # 标题
        title_label = QLabel("用户注册")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'Microsoft YaHei';
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        
        # 副标题
        subtitle_label = QLabel("创建您的账户\n开始使用智能检测系统")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                line-height: 1.5;
            }
        """)
        
        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 底部信息
        info_label = QLabel("注册即表示同意用户协议")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.6);
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(spacer)
        layout.addWidget(info_label)
        
        return panel
        
    def createRightPanel(self):
        """创建右侧注册面板"""
        panel = QFrame()
        panel.setObjectName("rightPanel")
        panel.setStyleSheet("""
            #rightPanel {
                background: white;
                border-radius: 0px 20px 20px 0px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 0)
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(60, 50, 60, 50)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            #closeBtn {
                background: transparent;
                border: none;
                color: #666;
                font-size: 20px;
                font-weight: bold;
            }
            #closeBtn:hover {
                color: #ff4757;
            }
        """)
        
        # 关闭按钮布局
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
        
        # 注册标题
        register_title = QLabel("创建新账户")
        register_title.setAlignment(Qt.AlignCenter)
        register_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-family: 'Microsoft YaHei';
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0px 30px 0px;
            }
        """)
        layout.addWidget(register_title)
        
        # 用户名输入框
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.setObjectName("usernameEdit")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                background: #f8f9fa;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background: white;
            }
        """)
        layout.addWidget(self.username_edit)
        
        # 密码输入框
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setObjectName("passwordEdit")
        self.password_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                background: #f8f9fa;
                margin-top: 15px;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background: white;
            }
        """)
        layout.addWidget(self.password_edit)
        
        # 确认密码输入框
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("请再次输入密码")
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setObjectName("confirmPasswordEdit")
        self.confirm_password_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                background: #f8f9fa;
                margin-top: 15px;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background: white;
            }
        """)
        layout.addWidget(self.confirm_password_edit)
        
        # 注册按钮
        self.register_btn = QPushButton("注册")
        self.register_btn.setObjectName("registerBtn")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                padding: 12px;
                margin-top: 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a5fc8, stop:1 #5a3180);
            }
        """)
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(self.register_btn)
        
        # 返回登录链接
        back_layout = QHBoxLayout()
        back_layout.addStretch()
        
        back_label = QLabel("已有账号？")
        back_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
            }
        """)
        
        self.back_btn = QPushButton("返回登录")
        self.back_btn.setObjectName("backBtn")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #667eea;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #5a6fd8;
            }
        """)
        self.back_btn.clicked.connect(self.close)
        
        back_layout.addWidget(back_label)
        back_layout.addWidget(self.back_btn)
        back_layout.addStretch()
        
        layout.addLayout(back_layout)
        
        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)
        
        return panel
        
    def setupAnimations(self):
        """设置动画效果"""
        # 窗口淡入动画
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
        
    def register(self):
        """用户注册"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()
        
        # 输入验证
        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "提示", "请填写完整信息")
            return
            
        if len(username) < 3:
            QMessageBox.warning(self, "提示", "用户名至少需要3个字符")
            return
            
        if len(password) < 6:
            QMessageBox.warning(self, "提示", "密码至少需要6个字符")
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, "提示", "两次输入的密码不一致")
            return
            
        # 检查用户名是否已存在
        result = query_username(username)
        if len(result) != 0:
            QMessageBox.warning(self, "注册失败", "用户名已存在")
            return
            
        # 注册用户
        try:
            insert_user(username, password)
            QMessageBox.information(self, "注册成功", "账户创建成功，请返回登录")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "注册失败", f"注册过程中出现错误：{str(e)}")
        
    def mousePressEvent(self, event):
        """鼠标按下事件，用于窗口拖动"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件，用于窗口拖动"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建并显示注册窗口
    register_window = NewRegister()
    register_window.show()
    
    sys.exit(app.exec_()) 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
锂电池隔膜缺陷检测系统 - 新版本主启动文件
基于深度学习的智能检测平台
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

# 导入新界面模块
from NewLogin import NewLogin
from NewMainWindow import NewMainWindow

class DefectDetectionApp:
    """锂电池隔膜缺陷检测系统主应用程序"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setupApplication()
        self.login_window = None
        self.main_window = None
        
    def setupApplication(self):
        """设置应用程序属性"""
        # 设置应用程序信息
        self.app.setApplicationName("锂电池隔膜缺陷检测系统")
        self.app.setApplicationVersion("2.0")
        self.app.setOrganizationName("大运队")
        
        # 设置应用程序样式
        self.app.setStyle('Fusion')
        
        # 设置全局字体
        font = QFont("Microsoft YaHei", 9)
        self.app.setFont(font)
        
    def showSplashScreen(self):
        """显示启动画面"""
        # 创建启动画面
        splash_pixmap = QPixmap(400, 300)
        splash_pixmap.fill(Qt.white)
        
        # 这里可以添加启动画面的设计
        # 暂时使用简单的文字显示
        splash = QSplashScreen(splash_pixmap)
        splash.setStyleSheet("""
            QSplashScreen {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        splash.showMessage("正在启动锂电池隔膜缺陷检测系统...", 
                         Qt.AlignCenter | Qt.AlignBottom, Qt.white)
        splash.show()
        
        # 处理应用程序事件
        self.app.processEvents()
        
        return splash
        
    def checkEnvironment(self):
        """检查运行环境"""
        try:
            # 检查必要的模块
            import torch
            import cv2
            import numpy as np
            from PIL import Image
            
            # 检查模型文件
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, "EfficientNet_self1.pth")
            
            if not os.path.exists(model_path):
                QMessageBox.warning(None, "警告", 
                                  "未找到模型文件 EfficientNet_self1.pth\n"
                                  "请确保模型文件存在于程序目录中")
                return False
                
            # 检查数据目录
            data_dir = os.path.join(current_dir, "data")
            if not os.path.exists(data_dir):
                QMessageBox.warning(None, "警告", 
                                  "未找到数据目录 data/\n"
                                  "请确保数据目录存在")
                return False
                
            return True
            
        except ImportError as e:
            QMessageBox.critical(None, "错误", 
                               f"缺少必要的依赖模块: {str(e)}\n"
                               "请安装所需的Python包")
            return False
        except Exception as e:
            QMessageBox.critical(None, "错误", 
                               f"环境检查失败: {str(e)}")
            return False
            
    def startApplication(self):
        """启动应用程序"""
        # 显示启动画面
        splash = self.showSplashScreen()
        
        # 检查环境
        if not self.checkEnvironment():
            splash.close()
            return False
            
        # 模拟加载过程
        QTimer.singleShot(2000, lambda: self.showLogin(splash))
        
        return True
        
    def showLogin(self, splash):
        """显示登录界面"""
        splash.close()
        
        # 创建登录窗口
        self.login_window = NewLogin()
        self.login_window.show()
        
    def showMainWindow(self):
        """显示主窗口"""
        if self.login_window:
            self.login_window.hide()
            
        # 创建主窗口
        self.main_window = NewMainWindow()
        self.main_window.show()
        
    def run(self):
        """运行应用程序"""
        if self.startApplication():
            return self.app.exec_()
        else:
            return 1

def main():
    """主函数"""
    try:
        # 创建应用程序实例
        app = DefectDetectionApp()
        
        # 运行应用程序
        return app.run()
        
    except Exception as e:
        QMessageBox.critical(None, "严重错误", 
                           f"应用程序启动失败: {str(e)}")
        return 1

if __name__ == "__main__":
    # 设置高DPI支持
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    # 运行应用程序
    sys.exit(main()) 
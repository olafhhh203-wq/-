-- 锂电池隔离膜缺陷检测系统数据库初始化脚本
-- 请根据您的MySQL密码修改下面的配置

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS lanmo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 使用数据库
USE lanmo;

-- 3. 创建用户表
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 创建图片表
CREATE TABLE IF NOT EXISTS picture (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(500) NOT NULL,
    num INT DEFAULT 0,
    createtime DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 创建缺陷表
CREATE TABLE IF NOT EXISTS defect (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ficid INT NOT NULL,
    url VARCHAR(500) NOT NULL,
    cla VARCHAR(100) NOT NULL,
    prob FLOAT NOT NULL,
    location VARCHAR(255) NOT NULL,
    createtime DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ficid) REFERENCES picture(id) ON DELETE CASCADE
);

-- 6. 插入默认管理员用户（可选）
INSERT INTO user (username, password) VALUES ('admin', 'admin123') ON DUPLICATE KEY UPDATE password = 'admin123';

-- 7. 显示表结构
SHOW TABLES;
DESCRIBE user;
DESCRIBE picture;
DESCRIBE defect; 
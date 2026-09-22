-- 商城初始化脚本，MySQL 首次启动时自动导入
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS mall DEFAULT CHARACTER SET utf8mb4;
USE mall;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS goods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    description VARCHAR(500) DEFAULT '',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_name (name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(32) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    goods_id INT NOT NULL,
    quantity INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status TINYINT DEFAULT 1 COMMENT '1待发货 2已发货 3已完成',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_user (user_id),
    KEY idx_goods (goods_id)
) ENGINE=InnoDB;

INSERT INTO users (username, password) VALUES ('admin', MD5('123456'));

INSERT INTO goods (name, price, stock, description) VALUES
('无线机械键盘', 299.00, 100, '87键 茶轴 蓝牙双模'),
('无线鼠标', 89.00, 200, '静音版 三档DPI'),
('27寸显示器', 1099.00, 50, '2K 165Hz IPS'),
('移动固态硬盘', 459.00, 80, '1TB USB3.2'),
('USB-C 扩展坞', 129.00, 150, '七合一 HDMI 千兆网口');
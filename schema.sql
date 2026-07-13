-- ============================================
-- Online Food Ordering System - MySQL Schema
-- Run this entire file in MySQL Workbench
-- ============================================

CREATE DATABASE IF NOT EXISTS food_ordering_db;
USE food_ordering_db;

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menu Categories
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(10) DEFAULT '🍽️'
);

-- Menu Items
CREATE TABLE IF NOT EXISTS menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255) DEFAULT '',
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled') DEFAULT 'pending',
    delivery_address TEXT NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'card',
    payment_status ENUM('paid', 'pending') DEFAULT 'paid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Order Items
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_item_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);

-- Admin Table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Seed Data
-- ============================================

INSERT INTO categories (name, icon) VALUES
('Burgers', '🍔'),
('Pizza', '🍕'),
('Chinese', '🥡'),
('Desi Food', '🍛'),
('Drinks', '🥤'),
('Desserts', '🍰');

INSERT INTO menu_items (category_id, name, description, price) VALUES
(1, 'Classic Beef Burger', 'Juicy beef patty with lettuce, tomato, cheese & special sauce', 350.00),
(1, 'Zinger Burger', 'Crispy fried chicken fillet with coleslaw and mayo', 320.00),
(1, 'Double Smash Burger', 'Two smashed patties, caramelized onions, pickles & cheddar', 480.00),
(2, 'Margherita Pizza', 'Classic tomato base, fresh mozzarella, basil leaves', 650.00),
(2, 'BBQ Chicken Pizza', 'Smoky BBQ sauce, grilled chicken, onions, peppers', 750.00),
(2, 'Pepperoni Feast', 'Loaded with spicy pepperoni and mozzarella', 800.00),
(3, 'Chicken Fried Rice', 'Wok-tossed rice with chicken, eggs & vegetables', 350.00),
(3, 'Beef Chow Mein', 'Stir-fried noodles with tender beef strips & veggies', 380.00),
(3, 'Sweet & Sour Chicken', 'Crispy chicken in tangy sweet & sour sauce with peppers', 400.00),
(4, 'Chicken Karahi', 'Slow-cooked chicken in spiced tomato gravy', 550.00),
(4, 'Mutton Biryani', 'Fragrant basmati rice with tender mutton & whole spices', 450.00),
(4, 'Seekh Kabab Platter', 'Six juicy seekh kababs with naan and chutney', 500.00),
(5, 'Fresh Mango Shake', 'Chilled fresh mango blended with cream', 180.00),
(5, 'Soft Drink (Can)', 'Pepsi / 7Up / Mirinda - your choice', 80.00),
(5, 'Fresh Lemonade', 'Freshly squeezed lemon with mint and ice', 150.00),
(6, 'Gulab Jamun (4pc)', 'Soft milk-solid dumplings in rose-flavored sugar syrup', 200.00),
(6, 'Brownie with Ice Cream', 'Warm chocolate brownie with a scoop of vanilla ice cream', 280.00),
(6, 'Kheer', 'Traditional rice pudding with cardamom and nuts', 180.00);

-- Default admin (password: admin123)
INSERT INTO admins (username, password) VALUES
('admin', 'admin123');

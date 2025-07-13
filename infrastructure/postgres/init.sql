-- Sample database for testing the tText-to-sql service
-- This file should be placed at: infrastructure/postgres/init.sql

-- Create customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    registration_date DATE DEFAULT CURRENT_DATE,
    city VARCHAR(50),
    country VARCHAR(50),
    phone VARCHAR(20)
);

-- Create categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

-- Create products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),
    brand VARCHAR(50),
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_address TEXT
);

-- Create order_items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

-- Create reviews table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    customer_id INTEGER REFERENCES customers(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample customers
INSERT INTO customers (name, email, city, country, phone) VALUES
('John Doe', 'john@example.com', 'New York', 'USA', '+1-555-0101'),
('Jane Smith', 'jane@example.com', 'Los Angeles', 'USA', '+1-555-0102'),
('Bob Johnson', 'bob@example.com', 'Chicago', 'USA', '+1-555-0103'),
('Alice Brown', 'alice@example.com', 'Houston', 'USA', '+1-555-0104'),
('Charlie Wilson', 'charlie@example.com', 'Phoenix', 'USA', '+1-555-0105'),
('Diana Prince', 'diana@example.com', 'Philadelphia', 'USA', '+1-555-0106'),
('Tom Anderson', 'tom@example.com', 'San Antonio', 'USA', '+1-555-0107'),
('Sarah Davis', 'sarah@example.com', 'San Diego', 'USA', '+1-555-0108'),
('Mike Miller', 'mike@example.com', 'Dallas', 'USA', '+1-555-0109'),
('Lisa Garcia', 'lisa@example.com', 'San Jose', 'USA', '+1-555-0110');

-- Insert sample categories
INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic devices and gadgets'),
('Clothing', 'Apparel and fashion items'),
('Books', 'Physical and digital books'),
('Home & Garden', 'Home improvement and garden supplies'),
('Sports', 'Sports equipment and gear'),
('Beauty', 'Beauty and personal care products');

-- Insert sample products
INSERT INTO products (name, category_id, price, cost, brand, stock_quantity) VALUES
('Laptop Pro', 1, 1299.99, 800.00, 'TechBrand', 25),
('Wireless Headphones', 1, 199.99, 120.00, 'AudioTech', 50),
('Smartphone X', 1, 899.99, 600.00, 'PhoneCorp', 30),
('4K Monitor', 1, 449.99, 280.00, 'DisplayTech', 15),
('Running Shoes', 2, 89.99, 45.00, 'SportWear', 100),
('Winter Jacket', 2, 149.99, 80.00, 'OutdoorGear', 30),
('Jeans', 2, 79.99, 35.00, 'DenimCo', 75),
('T-Shirt', 2, 24.99, 10.00, 'CasualWear', 200),
('Programming Book', 3, 49.99, 25.00, 'TechBooks', 75),
('Cookbook', 3, 29.99, 15.00, 'FoodPress', 40),
('Coffee Maker', 4, 79.99, 40.00, 'KitchenPro', 20),
('Garden Tools Set', 4, 159.99, 90.00, 'GardenPlus', 25),
('Tennis Racket', 5, 199.99, 120.00, 'SportsPro', 35),
('Yoga Mat', 5, 39.99, 20.00, 'FitLife', 60),
('Face Cream', 6, 59.99, 25.00, 'BeautyBrand', 80),
('Shampoo', 6, 19.99, 8.00, 'HairCare', 120);

-- Insert sample orders
INSERT INTO orders (customer_id, order_date, status, total_amount, shipping_address) VALUES
(1, '2024-01-15', 'completed', 1299.99, '123 Main St, New York, NY'),
(2, '2024-01-16', 'completed', 289.98, '456 Oak Ave, Los Angeles, CA'),
(3, '2024-01-17', 'shipped', 139.98, '789 Pine Rd, Chicago, IL'),
(4, '2024-01-18', 'shipped', 199.99, '321 Elm St, Houston, TX'),
(5, '2024-01-19', 'completed', 79.99, '654 Maple Dr, Phoenix, AZ'),
(1, '2024-01-20', 'pending', 549.98, '123 Main St, New York, NY'),
(2, '2024-01-21', 'completed', 169.97, '456 Oak Ave, Los Angeles, CA'),
(6, '2024-01-22', 'completed', 899.99, '987 First Ave, Philadelphia, PA'),
(7, '2024-01-23', 'shipped', 229.98, '147 Second St, San Antonio, TX'),
(8, '2024-01-24', 'completed', 159.99, '258 Third Blvd, San Diego, CA');

-- Insert sample order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1299.99),
(2, 2, 1, 199.99),
(2, 5, 1, 89.99),
(3, 6, 1, 149.99),
(4, 2, 1, 199.99),
(5, 11, 1, 79.99),
(6, 4, 1, 449.99),
(6, 9, 1, 49.99),
(6, 10, 1, 29.99),
(7, 7, 2, 79.99),
(7, 8, 1, 24.99),
(8, 3, 1, 899.99),
(9, 13, 1, 199.99),
(9, 14, 1, 39.99),
(10, 12, 1, 159.99);

-- Insert sample reviews
INSERT INTO reviews (product_id, customer_id, rating, comment) VALUES
(1, 1, 5, 'Excellent laptop, very fast and reliable! Perfect for work.'),
(2, 2, 4, 'Great sound quality, comfortable to wear. Battery could be better.'),
(5, 2, 5, 'Perfect fit, great for running. Highly recommend!'),
(2, 4, 4, 'Good headphones, but the price is a bit high.'),
(11, 5, 3, 'Coffee maker works fine but instructions were unclear.'),
(3, 6, 5, 'Amazing smartphone! Camera quality is outstanding.'),
(6, 3, 4, 'Warm and comfortable jacket. Good for winter weather.'),
(9, 1, 5, 'Very informative programming book. Well written.'),
(13, 7, 4, 'Good tennis racket, improved my game significantly.'),
(4, 1, 5, 'Crystal clear 4K display. Great for design work.');

-- Create indexes for better performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);

-- Create a view for order summaries (useful for complex queries)
CREATE VIEW order_summary AS
SELECT 
    o.id as order_id,
    o.order_date,
    o.status,
    c.name as customer_name,
    c.city as customer_city,
    o.total_amount,
    COUNT(oi.id) as items_count
FROM orders o
JOIN customers c ON o.customer_id = c.id
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, o.order_date, o.status, c.name, c.city, o.total_amount;
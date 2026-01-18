-- Database Schema for Microservice Demo - Phase 2
-- Separate databases for each service

-- Database for User Service
CREATE DATABASE IF NOT EXISTS user_db;
USE user_db;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);

-- Database for Order Service
CREATE DATABASE IF NOT EXISTS order_db;
USE order_db;

CREATE TABLE IF NOT EXISTS orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product VARCHAR(255) NOT NULL,
    amount INT NOT NULL
);

-- Note: No foreign key constraint in order_db
-- Order service will validate user_id by calling user-service API


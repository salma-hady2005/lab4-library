
-- =========================================
-- Lab 4 - Problem 2
-- Database DDL
-- =========================================

CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- 1. AUTHOR
CREATE TABLE IF NOT EXISTS AUTHOR (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    author_image VARCHAR(255)
);

-- 2. PUBLISHER
CREATE TABLE IF NOT EXISTS PUBLISHER (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100)
);

-- 3. CATEGORY
CREATE TABLE IF NOT EXISTS CATEGORY (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- 4. BOOK
CREATE TABLE IF NOT EXISTS BOOK (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    publish_year INT,
    author_id INT NOT NULL,
    publisher_id INT,
    category_id INT,
    cover_image VARCHAR(255),

    CONSTRAINT fk_book_author
        FOREIGN KEY (author_id)
        REFERENCES AUTHOR(author_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_book_publisher
        FOREIGN KEY (publisher_id)
        REFERENCES PUBLISHER(publisher_id),

    CONSTRAINT fk_book_category
        FOREIGN KEY (category_id)
        REFERENCES CATEGORY(category_id)
);

-- 5. MEMBER
CREATE TABLE IF NOT EXISTS MEMBER (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    join_date DATE
);

-- 6. LOAN
CREATE TABLE IF NOT EXISTS LOAN (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE NULL,

    CONSTRAINT fk_loan_book
        FOREIGN KEY (book_id)
        REFERENCES BOOK(book_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_loan_member
        FOREIGN KEY (member_id)
        REFERENCES MEMBER(member_id)
);

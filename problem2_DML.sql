USE library_db;

-- =====================================
-- 1. AUTHORS
-- =====================================
INSERT INTO AUTHOR (author_id, name, country, author_image)
VALUES
(2, 'William Shakespeare', 'England',
 'uploads/faed83206ac9496a8bbb72ccd81ea3b1.jpg'),
(3, 'Jane Austen', 'England',
 'uploads/f562fe3c76b040abbb3629f51c5803d2.jpg'),
(9, 'salma w lena', 'alexandria',
 'uploads/b2d93abe979949e5a1431b896dc48f44.webp'),
(10, 'salma w lena', 'alexandria',
 'uploads/fbeaccf8d6144b2c8bdcb047676e28e7.webp');

-- =====================================
-- 2. PUBLISHERS
-- =====================================
INSERT INTO PUBLISHER (publisher_id, name, country)
VALUES
(1, 'Penguin Books', 'England'),
(2, 'HarperCollins', 'USA'),
(3, 'Dar El Shorouk', 'Egypt');

-- =====================================
-- 3. CATEGORIES
-- =====================================
INSERT INTO CATEGORY (category_id, name)
VALUES
(1, 'Classic Literature'),
(2, 'Fantasy'),
(3, 'Drama');

-- =====================================
-- 4. BOOKS
-- =====================================
INSERT INTO BOOK
(book_id, title, price, author_id, cover_image,
 publish_year, publisher_id, category_id)
VALUES
(3, 'Hamlet', 200.00, 2,
 'uploads/e3ebe4f920914983b56ab6231b268038.jpg',
 NULL, NULL, NULL),

(4, 'Macbeth', 175.00, 2,
 'uploads/c17e3744c04546a39c7f8dbc22557923.jpg',
 NULL, NULL, NULL),

(5, 'Pride and Prejudice', 220.00, 3,
 'uploads/6dfc2d76fd724da7bfde83630feb8b80.jpg',
 NULL, NULL, NULL),

(6, 'Emma', 190.00, 3,
 'uploads/a57df54fe91244ca9aee2191d7ba5846.jpg',
 NULL, NULL, NULL),

(14, 'Harry potter and Travis Scott', 500.00, 9,
 'uploads/c3f3b96535834272b51be0b71aa8d143.webp',
 NULL, NULL, NULL),

(15, 'The Secret Garden', 18.50, 3,
 NULL, 1911, 1, 1),

(16, 'The Great Gatsby', 150.00, 2,
 NULL, 1925, 2, 1),

(17, 'The Hobbit', 180.00, 9,
 NULL, 1937, 3, 2),

(18, 'Romeo and Juliet', 120.00, 2,
 NULL, 1597, 1, 3),

(19, 'Sense and Sensibility', 135.00, 3,
 NULL, 1811, 2, 1);

-- =====================================
-- 5. MEMBERS
-- =====================================
INSERT INTO MEMBER (member_id, name, email, join_date)
VALUES
(1, 'Ahmed Ali', 'ahmed@example.com', '2026-01-10'),
(2, 'Mariam Hassan', 'mariam@example.com', '2026-02-15'),
(3, 'Omar Khaled', 'omar@example.com', '2026-03-20'),
(4, 'Nour Samir', 'nour@example.com', '2026-04-05'),
(5, 'Youssef Adel', 'youssef@example.com', '2026-05-12');

-- =====================================
-- 6. LOANS
-- =====================================
INSERT INTO LOAN
(loan_id, book_id, member_id, loan_date, return_date)
VALUES
(1, 3, 1, '2026-09-01', '2026-09-10'),
(2, 4, 2, '2026-09-03', '2026-09-12'),
(3, 5, 3, '2026-09-05', '2026-09-15'),
(4, 6, 4, '2026-09-07', '2026-09-17'),
(5, 14, 1, '2026-09-10', '2026-09-20'),
(6, 15, 2, '2026-09-12', '2026-09-22'),
(7, 16, 3, '2026-09-15', '2026-09-25'),
(8, 17, 4, '2026-09-18', NULL),
(9, 18, 1, '2026-09-20', '2026-09-30'),
(10, 3, 2, '2026-10-01', '2026-10-10'),
(11, 4, 3, '2026-10-05', NULL),
(12, 5, 4, '2026-10-08', '2026-10-18');
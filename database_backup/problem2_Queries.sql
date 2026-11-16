USE library_db;

-- =====================================
-- F2.1: SEARCH BOOKS
-- =====================================

SET @keyword = 'Hamlet';
SET @min_price = NULL;
SET @max_price = NULL;
SET @category_ids = NULL;

SELECT
    b.book_id,
    b.title,
    b.price,
    a.name AS author_name,
    c.name AS category_name
FROM BOOK b
JOIN AUTHOR a
    ON b.author_id = a.author_id
LEFT JOIN CATEGORY c
    ON b.category_id = c.category_id
WHERE
    (@keyword IS NULL OR @keyword = ''
        OR b.title LIKE CONCAT('%', @keyword, '%'))

    AND b.price BETWEEN
        COALESCE(@min_price, 0)
        AND COALESCE(@max_price, 99999999.99)

    AND (@category_ids IS NULL
        OR FIND_IN_SET(b.category_id, @category_ids) > 0)

ORDER BY b.price ASC;


-- =====================================
-- F2.2: BOOK CATALOGUE
-- =====================================

SELECT
    b.book_id,
    b.title,
    b.price,
    b.publish_year,
    a.name AS author_name,
    p.name AS publisher_name,
    c.name AS category_name
FROM BOOK b
JOIN AUTHOR a
    ON b.author_id = a.author_id
LEFT JOIN PUBLISHER p
    ON b.publisher_id = p.publisher_id
LEFT JOIN CATEGORY c
    ON b.category_id = c.category_id
ORDER BY b.title ASC;


-- =====================================
-- F2.3: REPORTS
-- =====================================

-- Report 1: Number of books and average price per category

SELECT
    c.category_id,
    c.name AS category_name,
    COUNT(b.book_id) AS number_of_books,
    AVG(b.price) AS average_price
FROM CATEGORY c
LEFT JOIN BOOK b
    ON c.category_id = b.category_id
GROUP BY c.category_id, c.name;


-- Report 2: Authors who have at least 2 books

SELECT
    a.author_id,
    a.name AS author_name,
    COUNT(b.book_id) AS number_of_books
FROM AUTHOR a
JOIN BOOK b
    ON a.author_id = b.author_id
GROUP BY a.author_id, a.name
HAVING COUNT(b.book_id) >= 2;


-- Report 3: Total, minimum, and maximum book prices

SELECT
    SUM(price) AS total_library_price,
    MIN(price) AS minimum_book_price,
    MAX(price) AS maximum_book_price
FROM BOOK;
-- =====================================
-- F2.4: LOANS
-- =====================================

-- (a) Loans that have not been returned
SELECT
    l.loan_id,
    b.title AS book_title,
    m.name AS member_name,
    l.loan_date
FROM LOAN l
JOIN BOOK b ON l.book_id = b.book_id
JOIN MEMBER m ON l.member_id = m.member_id
WHERE l.return_date IS NULL;


-- (b) Members who never borrowed a book
SELECT
    m.member_id,
    m.name,
    m.email
FROM MEMBER m
LEFT JOIN LOAN l ON m.member_id = l.member_id
WHERE l.loan_id IS NULL;


-- (c) Books that were never borrowed
SELECT
    b.book_id,
    b.title,
    b.price
FROM BOOK b
LEFT JOIN LOAN l ON b.book_id = l.book_id
WHERE l.loan_id IS NULL;
-- =====================================
-- F2.5: MOST BORROWED
-- =====================================

-- (a) Three most borrowed books
SELECT
    b.book_id,
    b.title,
    COUNT(l.loan_id) AS loan_count
FROM BOOK b
JOIN LOAN l ON b.book_id = l.book_id
GROUP BY b.book_id, b.title
ORDER BY loan_count DESC
LIMIT 3;


-- (b) Member with the most loans
SELECT
    m.member_id,
    m.name,
    COUNT(l.loan_id) AS loan_count
FROM MEMBER m
JOIN LOAN l ON m.member_id = l.member_id
GROUP BY m.member_id, m.name
ORDER BY loan_count DESC
LIMIT 1;
-- =====================================
-- F2.6: AUTHORS AND BOOKS
-- =====================================

-- (a) Every author with their book count, including authors with zero books
SELECT
    a.author_id,
    a.name,
    COUNT(b.book_id) AS book_count
FROM AUTHOR a
LEFT JOIN BOOK b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name
ORDER BY a.name;


-- (b) Books whose author and publisher are from the same country
SELECT
    b.book_id,
    b.title,
    a.name AS author_name,
    a.country AS author_country,
    p.name AS publisher_name,
    p.country AS publisher_country
FROM BOOK b
JOIN AUTHOR a ON b.author_id = a.author_id
JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
WHERE a.country = p.country
ORDER BY b.title;
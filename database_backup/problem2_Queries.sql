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
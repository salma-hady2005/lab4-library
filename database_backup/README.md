
# Library Management System

## Introduction

The Library Management System is a web-based application developed using Python Flask and MySQL. It allows users to manage a library database, search for books, view library information, and generate reports about books, authors, publishers, members, and loans.

The project was developed as part of the Database Systems Lab 4 assignment at Alexandria National University.

## Team Members

| Name | Student ID |
|---|---|
| Lena Tarek | 2304005 |
| Salma Hady | 2304046 |

## Technologies Used

- Python
- Flask
- MySQL
- MySQL Connector
- HTML
- CSS
- Jinja2
- Werkzeug
- python-dotenv

## Project Features

### 1. User Authentication

- User registration.
- User login using username or email.
- Password hashing for secure password storage.
- Input validation.
- Logout functionality.
- Session-based authentication.

### 2. Book and Author Management

- Display library books.
- Add new books.
- Edit existing books.
- Delete books.
- Add authors.
- Edit author information.
- Delete authors.
- Upload book cover images.
- Upload author images.

### 3. Database Requirements

The project uses a MySQL database containing the following main tables:

- **AUTHOR:** Stores author information, including name, country, and author image.
- **PUBLISHER:** Stores publisher information, including name and country.
- **CATEGORY:** Stores book categories.
- **BOOK:** Stores book information, including title, price, publication year, author, publisher, category, and cover image.
- **MEMBER:** Stores library member information.
- **LOAN:** Stores book borrowing records, including loan date and return date.

The database uses primary keys and foreign keys to maintain relationships between tables and enforce referential integrity.

## F2: SQL Requirements

### F2.1 – Search Books (WHERE)

The application allows users to search for books using:

- Book title.
- Minimum price.
- Maximum price.
- Selected book categories.

Search results are displayed in ascending order of price.

**Bonus:** Prepared statements with placeholders are used in the search form to safely pass user input to SQL queries instead of directly inserting user input into SQL statements.

### F2.2 – Book Catalogue (JOIN)

The application displays a complete book catalogue using JOIN operations to retrieve:

- Book information.
- Author names.
- Publisher names.
- Category names.

### F2.3 – Database Reports (GROUP BY and HAVING)

The application generates the following reports:

1. Number of books and average book price for each category.
2. Authors who have at least two books.
3. Overall book statistics, including:
   - Total number of books.
   - Total book price.
   - Minimum book price.
   - Maximum book price.

### F2.4 – Loan Reports (JOIN and LEFT JOIN)

The application provides three loan-related reports:

1. Loans that have not been returned yet, displaying the book title and member name.
2. Members who have never borrowed a book.
3. Books that have never been borrowed.

### F2.5 – Most Borrowed Books (GROUP BY, ORDER BY, LIMIT)

The application generates the following reports:

1. The three most borrowed books, ordered by loan count.
2. The member with the highest number of loans.

### F2.6 – Authors and Books (LEFT JOIN and JOIN)

The application provides two reports:

1. All authors with their book counts, including authors who have no books.
2. Books whose authors and publishers belong to the same country.

## Bonus Requirement

Prepared statements are implemented in the F2.1 search functionality.

SQL placeholders (`%s`) are used for user-provided search values, and the values are passed separately through `cursor.execute()`.

This helps prevent SQL injection and makes the search functionality safer.

## Project Structure

```text
lab4_library/
│
├── website/
│   ├── app.py
│   ├── templates/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── library.html
│   │   ├── loans.html
│   │   ├── most_borrowed.html
│   │   ├── authors_books.html
│   │   ├── add.html
│   │   ├── edit_book.html
│   │   └── base.html
│   │
│   └── static/
│       ├── style.css
│       └── uploads/
│
├── database_backup/
├── auth_DDL.sql
├── library_db.sql
├── problem2_DDL.sql
├── problem2_DML.sql
├── problem2_Queries.sql
├── .env
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <https://github.com/salma-hady2005/lab4-library.git>
```

Navigate to the project folder:

```bash
cd lab4_library
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install Flask mysql-connector-python python-dotenv
```

### 4. Set Up MySQL

1. Open MySQL Workbench.
2. Connect to your MySQL server.
3. Create/import the required databases and tables using the provided SQL files.
4. Execute the database creation scripts before inserting the sample data.
5. Execute the DML scripts to insert the required sample records.

The application uses two databases:

- `library_auth_db` for user authentication.
- `library_db` for library information and reports.

### 5. Configure Environment Variables

Create a `.env` file in the project's root directory.

Add your own MySQL connection details:

```env
SECRET_KEY=your_secret_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=library_auth_db
```

**Important:** The `.env` file contains private configuration information and should not be uploaded to GitHub.

### 6. Run the Application

From the project root directory, run:

```bash
python website/app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

Register a new account or log in to access the library application.

## Security Features

- Passwords are stored as hashes rather than plain text.
- SQL queries use parameterized statements.
- User input is validated.
- Login sessions are used to protect application pages.
- Environment variables are used for database configuration.
- Uploaded images are restricted to supported formats and a maximum file size of 5 MB.

## Testing

The application was tested to verify:

- User registration and login.
- Invalid input handling.
- Book and author management.
- Book search using different filters.
- Book catalogue display.
- Category and author reports.
- Loan reports.
- Most borrowed books and members.
- Authors and books reports.
- Prepared statements in the F2.1 search functionality.
- Image uploads and display.

## Conclusion

The Library Management System demonstrates the use of relational database concepts and SQL operations in a practical web application.

It combines Flask and MySQL to provide authentication, library management, book searching, database reports, and secure database interactions.

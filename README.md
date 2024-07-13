# Streamlit Bookstore App

This is a simple online bookstore application built with Streamlit. It allows users to browse books, add them to a shopping cart, and simulate a checkout process. The app also includes features like search functionality, sorting options, and email notifications for orders.

## Features

- Browse a catalog of books with cover images
- Search for books by title
- Sort books by title or stock quantity
- Add books to a shopping cart
- Remove books from the shopping cart
- Checkout process with email notification
- Responsive design for various screen sizes

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed Python 3.7 or later
- You have a Gmail account for sending email notifications (optional)

## Setup

To set up the Streamlit Bookstore App, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/your-username/streamlit-bookstore-app.git
   cd streamlit-bookstore-app
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv bookstore_env
   source bookstore_env/bin/activate  # On Windows, use: bookstore_env\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your EmailJS account:
   - Sign up for a free account at [EmailJS](https://www.emailjs.com/)
   - Create a new email service and email template
   - Update the EmailJS configuration variables in `book.py`:
     - `EMAILJS_PUBLIC_KEY`
     - `EMAILJS_SERVICE_ID`
     - `EMAILJS_TEMPLATE_ID`

5. Prepare your data:
   - Ensure you have a `books_counts.csv` file with your book data
   - Place your book cover images in a `book_images` directory

## Usage

To run the Streamlit Bookstore App:

1. Activate your virtual environment if you're using one:
   ```
   source bookstore_env/bin/activate  # On Windows, use: bookstore_env\Scripts\activate
   ```

2. Run the Streamlit app:
   ```
   streamlit run book.py
   ```

3. Open your web browser and go to `http://localhost:8501` to view the app.



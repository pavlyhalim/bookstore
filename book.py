import streamlit as st
import pandas as pd
from collections import defaultdict
import os
from PIL import Image
from fuzzywuzzy import fuzz
import base64
import io
import requests

# Set page config
st.set_page_config(layout="wide", page_title="Online Bookstore")

# Global variables
IMAGE_MAPPING = {}
df = None

# EmailJS configuration
EMAILJS_PUBLIC_KEY = ""
EMAILJS_SERVICE_ID = ""
EMAILJS_TEMPLATE_ID = ""

# Function to send email using EmailJS
def send_email(name, email, phone, address, order_summary):
    url = "https://api.emailjs.com/api/v1.0/email/send"
    message = f"""
New order details:
Name: {name}
Email: {email}
Phone: {phone}
Address: {address}

{order_summary}
    """
    data = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_PUBLIC_KEY,
        "template_params": {
            "from_name": name,
            "to_name": "Admin",
            "message": message,
            "reply_to": email
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=data, headers=headers)
    return response.status_code == 200

# Function to match book titles with image filenames
def match_books_with_images(book_names, image_dir):
    image_mapping = {}
    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpeg', '.jpg', '.png'))]
    
    for book in book_names:
        best_match = max(image_files, key=lambda x: fuzz.ratio(book.lower(), os.path.splitext(x)[0].lower()))
        image_mapping[book] = best_match
    
    return image_mapping

# Load and clean the data
@st.cache
def load_data():
    df = pd.read_csv('books_counts.csv')
    df['Book'] = df['Book'].astype(str).str.strip()
    df = df[df['Book'] != '']
    df['Count'] = pd.to_numeric(df['Count'], errors='coerce')
    df = df.dropna()
    df['Price'] = 0  # Set all prices to 0
    return df

# Function to get image for a book
def get_image(book_name):
    if book_name in IMAGE_MAPPING:
        image_path = os.path.join('book_images', IMAGE_MAPPING[book_name])
        if os.path.exists(image_path):
            return Image.open(image_path)
    return Image.new('RGB', (200, 300), color='gray')

# Function to convert image to base64
def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = defaultdict(int)

def add_to_cart(book, price):
    st.session_state.cart[book] = st.session_state.cart.get(book, 0) + 1
    st.success(f"Added {book} to cart!")

def remove_from_cart(book):
    if st.session_state.cart.get(book, 0) > 0:
        st.session_state.cart[book] -= 1
        if st.session_state.cart[book] == 0:
            del st.session_state.cart[book]
        st.success(f"Removed {book} from cart!")

def browse_books():
    st.title('Online Bookstore')

    # Search and sort functionality
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input('Search for a book:')
    with col2:
        sort_option = st.selectbox('Sort by:', ['Book Title', 'In Stock'])

    if search_term:
        results = df[df['Book'].str.contains(search_term, case=False)]
    else:
        results = df

    if sort_option == 'Book Title':
        results = results.sort_values('Book')
    elif sort_option == 'In Stock':
        results = results.sort_values('Count', ascending=False)

    # Display books
    for _, row in results.iterrows():
        img = get_image(row['Book'])
        img_base64 = image_to_base64(img.resize((150, 200)))
        st.markdown(f"""
        <div class="book-container">
            <div style="display: flex; align-items: center;">
                <div style="flex: 1;">
                    <img src="data:image/png;base64,{img_base64}" width="150">
                </div>
                <div style="flex: 2; padding-left: 1rem;">
                    <h3>{row['Book']}</h3>
                    <p>Price: ${row['Price']:.2f}</p>
                    <p>In stock: {row['Count']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button('Add to Cart', key=f"add_{row['Book']}"):
            add_to_cart(row['Book'], row['Price'])

def shopping_cart():
    st.title('Shopping Cart')
    if not st.session_state.cart:
        st.write("Your cart is empty.")
    else:
        total = 0
        for book, quantity in st.session_state.cart.items():
            book_row = df[df['Book'] == book].iloc[0]
            img = get_image(book)
            img_base64 = image_to_base64(img.resize((100, 133)))
            st.markdown(f"""
            <div class="cart-item">
                <div style="display: flex; align-items: center;">
                    <div style="flex: 1;">
                        <img src="data:image/png;base64,{img_base64}" width="100">
                    </div>
                    <div style="flex: 3; padding-left: 1rem;">
                        <h4>{book}</h4>
                        <p>Quantity: {quantity} - ${book_row['Price']:.2f} each</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button('Remove', key=f"remove_{book}"):
                remove_from_cart(book)
            total += quantity * book_row['Price']
        st.write(f"**Total: ${total:.2f}**")

def checkout():
    st.title('Checkout')
    if not st.session_state.cart:
        st.write("Your cart is empty. Add some books before checking out!")
    else:
        st.write("Enter your details to complete the purchase:")
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Mobile Phone")
        address = st.text_area("Shipping Address")
        if st.button("Place Order"):
            if name and email and phone and address:
                # Prepare order summary
                order_summary = "Order Summary:\n\n"
                total = 0
                for book, quantity in st.session_state.cart.items():
                    book_row = df[df['Book'] == book].iloc[0]
                    price = book_row['Price']
                    order_summary += f"{book} - Quantity: {quantity} - ${price:.2f} each\n"
                    total += quantity * price
                order_summary += f"\nTotal: ${total:.2f}"

                # Send email
                if send_email(name, email, phone, address, order_summary):
                    st.success("Order placed successfully!")
                    st.session_state.cart.clear()
                else:
                    st.error("Failed to process the order. Please try again later.")
            else:
                st.error("Please fill in all fields.")

def main():
    global df, IMAGE_MAPPING
    
    # Load data
    df = load_data()

    # Match books with images
    IMAGE_MAPPING = match_books_with_images(df['Book'].tolist(), 'book_images')

    # Custom CSS
    st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .book-container {
        background-color: #0f1116;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .cart-item {
        background-color: #1a1c23;
        border-radius: 5px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Browse Books", "Shopping Cart", "Checkout"])

    # Display cart summary in sidebar
    st.sidebar.write("---")
    st.sidebar.write("Cart Summary")
    cart_total = sum(df[df['Book'] == book]['Price'].values[0] * quantity 
                     for book, quantity in st.session_state.cart.items())
    st.sidebar.write(f"Total Items: {sum(st.session_state.cart.values())}")
    st.sidebar.write(f"Total Price: ${cart_total:.2f}")

    # Main content
    if page == "Browse Books":
        browse_books()
    elif page == "Shopping Cart":
        shopping_cart()
    elif page == "Checkout":
        checkout()

if __name__ == '__main__':
    main()
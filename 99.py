
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import matplotlib.pyplot as plt
from collections import Counter
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

class Library:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.borrowed_books = {}

    def add_book(self, title, author, isbn):
        if isbn in self.books:
            raise ValueError(f"Book with ISBN {isbn} already exists.")
        self.books[isbn] = {"title": title, "author": author, "available": True}

    def add_member(self, name, member_id):
        if member_id in self.members:
            raise ValueError(f"Member with ID {member_id} already exists.")
        self.members[member_id] = {"name": name, "borrowed_books": []}

    def borrow_book(self, isbn, member_id):
        if isbn not in self.books:
            raise ValueError(f"Book with ISBN {isbn} does not exist.")
        if not self.books[isbn]["available"]:
            raise ValueError(f"Book with ISBN {isbn} is not available.")
        if member_id not in self.members:
            raise ValueError(f"Member with ID {member_id} does not exist.")
        self.books[isbn]["available"] = False
        self.borrowed_books[isbn] = member_id
        self.members[member_id]["borrowed_books"].append(isbn)

    def return_book(self, isbn):
        if isbn not in self.borrowed_books:
            raise ValueError(f"Book with ISBN {isbn} is not borrowed.")
        member_id = self.borrowed_books[isbn]
        self.books[isbn]["available"] = True
        self.members[member_id]["borrowed_books"].remove(isbn)
        del self.borrowed_books[isbn]

library = Library()

@app.route('/')
def home():
    return render_template('index.html', 
                         books=library.books, 
                         members=library.members,
                         borrowed_books=library.borrowed_books)

@app.route('/add_book', methods=['POST'])
def add_book():
    try:
        library.add_book(request.form['title'], 
                        request.form['author'], 
                        request.form['isbn'])
        flash('Book added successfully!')
    except ValueError as e:
        flash(str(e))
    return redirect(url_for('home'))

@app.route('/add_member', methods=['POST'])
def add_member():
    try:
        library.add_member(request.form['name'], 
                          request.form['member_id'])
        flash('Member added successfully!')
    except ValueError as e:
        flash(str(e))
    return redirect(url_for('home'))

@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    try:
        library.borrow_book(request.form['isbn'], 
                          request.form['member_id'])
        flash('Book borrowed successfully!')
    except ValueError as e:
        flash(str(e))
    return redirect(url_for('home'))

@app.route('/return_book', methods=['POST'])
def return_book():
    try:
        library.return_book(request.form['isbn'])
        flash('Book returned successfully!')
    except ValueError as e:
        flash(str(e))
    return redirect(url_for('home'))

@app.route('/borrowed_books_chart')
def borrowed_books_chart():
    book_counts = {}
    for isbn in library.borrowed_books:
        title = library.books[isbn]['title']
        book_counts[title] = book_counts.get(title, 0) + 1
    
    if not book_counts:
        return "No books borrowed yet"

    plt.figure(figsize=(8, 8))
    plt.pie(book_counts.values(), labels=book_counts.keys(), autopct='%1.1f%%')
    plt.title('Most Borrowed Books')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    library.add_book("Python Basics", "J.S", "99")
    library.add_book("Data Science", "J.W", "88")
    library.add_book("Web Development","K.Q", "77")
    library.add_book("Machine Learning", "K.W", "66")
    
    library.add_member("Qam", "M001")
    library.add_member("Pam", "M002")
    library.borrow_book("99", "M001")  
    library.borrow_book("88", "M002") 
    
    app.run(host='0.0.0.0', port=5000)

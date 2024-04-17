from tkinter import *
from tkinter import ttk
import tkinter.messagebox as mb
import sqlite3

# Specify the new database file path
new_db_path = 'new_library.db'

# Connect to SQLite database (create a new file if it doesn't exist)
conn = sqlite3.connect(new_db_path)
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS books
             (id INTEGER PRIMARY KEY, title TEXT, author TEXT, status TEXT)''')

# Initialize GUI
root = Tk()
root.title('Library Management System')

# Color constants
bg_color = 'lightblue'
btn_hlb_bg = 'SteelBlue'  # Background color for Head Labels and Buttons

# Set background color
root.configure(bg=bg_color)

# Function to display books in the treeview
def display_books():
    for row in tree.get_children():
        tree.delete(row)
    c.execute("SELECT * FROM books")
    rows = c.fetchall()
    for row in rows:
        tree.insert('', 'end', values=row)

# Function to update the counts of available and issued books for each unique book
def update_counts():
    c.execute("SELECT title, author, status, COUNT(*) FROM books GROUP BY title, author, status")
    counts = c.fetchall()
    update_counts_tree.delete(*update_counts_tree.get_children())  # Clear existing data
    book_counts = {}
    total_available = 0
    total_issued = 0
    for count in counts:
        title, author, status, count_val = count
        if (title, author) not in book_counts:
            book_counts[(title, author)] = {'available': 0, 'issued': 0}
        if status == 'Available':
            book_counts[(title, author)]['available'] += count_val
            total_available += count_val
        elif status == 'Issued':
            book_counts[(title, author)]['issued'] += count_val
            total_issued += count_val
    for book, counts in book_counts.items():
        title, author = book    
        available_count = counts['available']
        issued_count = counts['issued']
        update_counts_tree.insert('', 'end', values=(title, author, available_count, issued_count))
    # Add a row for total available and issued books
    update_counts_tree.insert('', 'end', values=('Total:', '', total_available, total_issued))
    # Update total counts label
    total_counts_label.config(text=f'Total Available: {total_available}, Total Issued: {total_issued}')

# Function to verify login credentials
def verify_login():
    global username_entry, password_entry
    if username_entry.get() == 'admin' and password_entry.get() == 'admin':
        login_window.destroy()
        open_main_window()
    else:
        mb.showerror('Login Failed', 'Invalid username or password')

# Function to open the main window (Library Management System)
def open_main_window():
    global title_var, author_var, status_var, tree, update_counts_tree, total_counts_label

    # Variables for entry fields
    title_var = StringVar()
    author_var = StringVar()
    status_var = StringVar(value='Available')

    # Labels and entry fields
    Label(root, text='Title:', bg=bg_color).grid(row=0, column=0, padx=5, pady=5)
    Entry(root, textvariable=title_var).grid(row=0, column=1, padx=5, pady=5)
    Label(root, text='Author:', bg=bg_color).grid(row=1, column=0, padx=5, pady=5)
    Entry(root, textvariable=author_var).grid(row=1, column=1, padx=5, pady=5)
    Label(root, text='Status:', bg=bg_color).grid(row=2, column=0, padx=5, pady=5)
    ttk.Combobox(root, textvariable=status_var, values=['Available', 'Issued']).grid(row=2, column=1, padx=5, pady=5)

    # Buttons
    Button(root, text='Add Book', command=add_book, bg=btn_hlb_bg).grid(row=3, column=0, padx=5, pady=5)
    Button(root, text='Update Book', command=update_book, bg=btn_hlb_bg).grid(row=3, column=1, padx=5, pady=5)
    Button(root, text='Delete Book', command=delete_book, bg=btn_hlb_bg).grid(row=3, column=2, padx=5, pady=5)

    # Treeview to display books
    tree = ttk.Treeview(root, columns=('ID', 'Title', 'Author', 'Status'), show='headings')
    tree.heading('ID', text='ID')
    tree.heading('Title', text='Title')
    tree.heading('Author', text='Author')
    tree.heading('Status', text='Status')
    tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    # Treeview to display updated counts
    update_counts_tree = ttk.Treeview(root, columns=('Title', 'Author', 'Available', 'Issued'), show='headings')
    update_counts_tree.heading('Title', text='Title')
    update_counts_tree.heading('Author', text='Author')
    update_counts_tree.heading('Available', text='Available')
    update_counts_tree.heading('Issued', text='Issued')
    update_counts_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    # Label for total counts
    total_counts_label = Label(root, text='Total Available: 0, Total Issued: 0', bg=bg_color, font=('Helvetica', 14, 'bold'))
    total_counts_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    # Display initial books and counts
    display_books()
    update_counts()

# Function to add a new book
def add_book():
    title = title_var.get()
    author = author_var.get()
    status = status_var.get()
    if title and author:
        c.execute("INSERT INTO books (title, author, status) VALUES (?, ?, ?)", (title, author, status))
        conn.commit()
        display_books()
        update_counts()
    else:
        mb.showerror('Error', 'Please enter both title and author.')

# Function to update book information
def update_book():
    selected_item = tree.selection()
    if selected_item:
        book_id = tree.item(selected_item)['values'][0]
        title = title_var.get()
        author = author_var.get()
        status = status_var.get()
        if title and author:
            c.execute("UPDATE books SET title=?, author=?, status=? WHERE id=?", (title, author, status, book_id))
            conn.commit()
            clear_entries()
            display_books()
            update_counts()
        else:
            mb.showerror('Error', 'Please enter both title and author.')
    else:
        mb.showerror('Error', 'Please select a book to update.')

# Function to delete a book
def delete_book():
    selected_item = tree.selection()
    if selected_item:
        book_id = tree.item(selected_item)['values'][0]
        c.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        display_books()
        update_counts()
    else:
        mb.showerror('Error', 'Please select a book to delete.')

# Function to clear entry fields
def clear_entries():
    title_var.set('')
    author_var.set('')
    status_var.set('Available')

# Function to open the login window
def open_login_window():
    global login_window, username_entry, password_entry
    login_window = Tk()
    login_window.title('Login')

    # Labels and entry fields for username and password
    Label(login_window, text='Username:').grid(row=0, column=0, padx=5, pady=5)
    username_entry = Entry(login_window)
    username_entry.grid(row=0, column=1, padx=5, pady=5)
    Label(login_window, text='Password:').grid(row=1, column=0, padx=5, pady=5)
    password_entry = Entry(login_window, show='*')
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    # Button to login
    login_button = Button(login_window, text='Login', command=verify_login)
    login_button.grid(row=2, columnspan=2, padx=5, pady=5)

    # Centering the login window
    login_window.update_idletasks()
    login_window_width = login_window.winfo_reqwidth()
    login_window_height = login_window.winfo_reqheight()
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x_coordinate = (screen_width - login_window_width) // 2
    y_coordinate = (screen_height - login_window_height) // 2
    login_window.geometry(f"{login_window_width}x{login_window_height}+{x_coordinate}+{y_coordinate}")

    # Run the login window
    login_window.mainloop()

# Open the login window
open_login_window()

# Close database connection
conn.close()
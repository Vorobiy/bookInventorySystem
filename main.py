import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import backend
import csv
import json
from datetime import datetime

backend.connect()

# Create the main window
window = tk.Tk()
window.title("Book Shop")
window.geometry("900x600")  # Set a default size for the window
window.configure(bg="#eaf6f6")  # Light teal background for the window (default theme)

# Global Variables
selected_tuple = None
current_theme = "light"  # Default theme

# Apply ttk style
style = ttk.Style()
style.theme_use("clam")  # Use a modern theme

# Define themes
light_theme = {
    "frame_bg": "#eaf6f6",
    "label_bg": "#eaf6f6",
    "label_fg": "#333",
    "button_bg": "#0078D7",
    "button_fg": "white",
    "button_hover": "#0056A0",
    "tree_bg": "white",
    "tree_fg": "#333",
    "tree_heading_bg": "#0078D7",
    "tree_heading_fg": "white"
}

dark_theme = {
    "frame_bg": "#1e1e1e",
    "label_bg": "#1e1e1e",
    "label_fg": "#e6e6e6",
    "button_bg": "#3a9ad9",
    "button_fg": "white",
    "button_hover": "#2d7cb3",
    "tree_bg": "#2b2b2b",
    "tree_fg": "#e6e6e6",
    "tree_heading_bg": "#3a9ad9",
    "tree_heading_fg": "white"
}

# Apply theme settings
def apply_theme(theme):
    style.configure("TFrame", background=theme["frame_bg"])
    style.configure("TLabel", background=theme["label_bg"], foreground=theme["label_fg"], font=("Helvetica", 11))
    style.configure(
        "TButton",
        background=theme["button_bg"],
        foreground=theme["button_fg"],
        font=("Helvetica", 10, "bold"),
        padding=5
    )
    style.map("TButton", background=[("active", theme["button_hover"])])
    style.configure("Treeview", background=theme["tree_bg"], foreground=theme["tree_fg"], rowheight=25, font=("Helvetica", 10))
    style.configure("Treeview.Heading", background=theme["tree_heading_bg"], foreground=theme["tree_heading_fg"], font=("Helvetica", 12, "bold"))
    window.configure(bg=theme["frame_bg"])

    # Invert Treeview colors
    if theme == dark_theme:
        tree.tag_configure("dark_mode", background="#1e1e1e", foreground="#e6e6e6")
    else:
        tree.tag_configure("light_mode", background="white", foreground="#333")

    # Update all rows with the inverted theme
    for item in tree.get_children():
        tree.item(item, tags=("dark_mode" if theme == dark_theme else "light_mode"))

# Toggle dark mode
def toggle_theme():
    global current_theme
    if current_theme == "light":
        apply_theme(dark_theme)
        current_theme = "dark"
    else:
        apply_theme(light_theme)
        current_theme = "light"

# Input Validation Functions
def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_isbn(isbn_text):
    return isbn_text.isdigit()

# CRUD Functions
def add_command():
    if not title_text.get() or not author_text.get() or not isbn_text.get():
        messagebox.showerror("Error", "Please fill in all required fields!")
        return
    if not validate_date(pub_date_text.get()):
        messagebox.showerror("Error", "Invalid publication date! Use format YYYY-MM-DD.")
        return
    if not validate_isbn(isbn_text.get()):
        messagebox.showerror("Error", "ISBN must contain only numeric characters.")
        return
    backend.insert(title_text.get(), author_text.get(), genre_text.get(), pub_date_text.get(), isbn_text.get())
    view_command()

def view_command():
    sorted_data = backend.fetch_sorted_data("id")  # Default sort by ID
    for item in tree.get_children():
        tree.delete(item)  # Clear the Treeview
    for row in sorted_data:
        tree.insert("", "end", values=row)  # Insert sorted data

def search_command():
    for item in tree.get_children():
        tree.delete(item)
    results = backend.search(
        title_text.get(), author_text.get(), genre_text.get(), pub_date_text.get(), isbn_text.get()
    )
    if not results:
        messagebox.showinfo("Search", "No matching records found.")
    for row in results:
        tree.insert("", "end", values=row)

def delete_command():
    global selected_tuple
    if selected_tuple:
        backend.delete(selected_tuple[0])
        backend.reset_ids()
        view_command()
        selected_tuple = None  # Reset the selected tuple
        messagebox.showinfo("Success", "Book deleted and IDs updated!")
    else:
        messagebox.showerror("Error", "No book selected to delete!")

def sort_command(column):
    """
    Sort the data by the specified column and update the Treeview.
    :param column: The column to sort by (e.g., 'title', 'author', 'publication_date').
    """
    sorted_data = backend.fetch_sorted_data(column)
    # Clear existing data in the Treeview
    for item in tree.get_children():
        tree.delete(item)
    # Insert sorted data into the Treeview
    for row in sorted_data:
        tree.insert("", "end", values=row)

def get_selected_row(event):
    global selected_tuple
    try:
        selected_item = tree.selection()[0]
        selected_tuple = tree.item(selected_item)["values"]

        ent1.delete(0, tk.END)
        ent1.insert(tk.END, selected_tuple[1])

        ent2.delete(0, tk.END)
        ent2.insert(tk.END, selected_tuple[2])

        ent3.delete(0, tk.END)
        ent3.insert(tk.END, selected_tuple[3])

        ent4.delete(0, tk.END)
        ent4.insert(tk.END, selected_tuple[4])

        ent5.delete(0, tk.END)
        ent5.insert(tk.END, selected_tuple[5])
    except IndexError:
        pass

def update_command():
    if selected_tuple:
        if not validate_date(pub_date_text.get()):
            messagebox.showerror("Error", "Invalid publication date! Use format YYYY-MM-DD.")
            return
        if not validate_isbn(isbn_text.get()):
            messagebox.showerror("Error", "ISBN must contain only numeric characters.")
            return
        backend.update(selected_tuple[0], title_text.get(), author_text.get(), genre_text.get(), pub_date_text.get(), isbn_text.get())
        view_command()

# Export Functions
def export_csv():
    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file:
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Author", "Genre", "Publication Date", "ISBN"])
            for row in backend.view():
                pub_date = f"'{row[4]}" if row[4] else "'Invalid Date"
                isbn = f"'{row[5]}" if row[5] else ""
                writer.writerow([row[0], row[1], row[2], row[3], pub_date, isbn])
        messagebox.showinfo("Export", "Data exported successfully!")

def export_json():
    file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file:
        with open(file, "w") as f:
            json.dump(backend.view(), f, indent=4)
        messagebox.showinfo("Export", "Data exported successfully!")

# UI Layout
frame = ttk.Frame(window, padding=10)
frame.grid(row=0, column=0, sticky="ew")

# Input Fields
ttk.Label(frame, text="Title:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
title_text = tk.StringVar()
ent1 = ttk.Entry(frame, textvariable=title_text, width=30)
ent1.grid(row=0, column=1, sticky="w", padx=5, pady=5)

ttk.Label(frame, text="Author:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
author_text = tk.StringVar()
ent2 = ttk.Entry(frame, textvariable=author_text, width=30)
ent2.grid(row=1, column=1, sticky="w", padx=5, pady=5)

ttk.Label(frame, text="Genre:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
genre_text = tk.StringVar()
ent3 = ttk.Entry(frame, textvariable=genre_text, width=30)
ent3.grid(row=0, column=3, sticky="w", padx=5, pady=5)

ttk.Label(frame, text="Publication Date:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
pub_date_text = tk.StringVar()
ent4 = ttk.Entry(frame, textvariable=pub_date_text, width=30)
ent4.grid(row=1, column=3, sticky="w", padx=5, pady=5)

ttk.Label(frame, text="ISBN:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
isbn_text = tk.StringVar()
ent5 = ttk.Entry(frame, textvariable=isbn_text, width=30)
ent5.grid(row=2, column=1, sticky="w", padx=5, pady=5)

# Treeview Frame with Sorting Buttons
tree_frame = ttk.Frame(window, padding=10)
tree_frame.grid(row=1, column=0, sticky="nsew")

# Sorting Header
header_frame = ttk.Frame(tree_frame)
header_frame.grid(row=0, column=0, sticky="ew")

# ID Header and Sorting Button
ttk.Label(header_frame, text="ID", font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Button(header_frame, text="Sort", command=lambda: sort_command("id")).grid(row=0, column=1, padx=5, pady=5)

# Title Header and Sorting Button
ttk.Label(header_frame, text="Title", font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
ttk.Button(header_frame, text="Sort", command=lambda: sort_command("title")).grid(row=0, column=3, padx=5, pady=5)

# Author Header and Sorting Button
ttk.Label(header_frame, text="Author", font=("Helvetica", 10, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")
ttk.Button(header_frame, text="Sort", command=lambda: sort_command("author")).grid(row=0, column=5, padx=5, pady=5)

# Publication Date Header and Sorting Button
ttk.Label(header_frame, text="Publication Date", font=("Helvetica", 10, "bold")).grid(row=0, column=6, padx=5, pady=5, sticky="w")
ttk.Button(header_frame, text="Sort", command=lambda: sort_command("publication_date")).grid(row=0, column=7, padx=5, pady=5)

# Treeview (below the header frame)
tree = ttk.Treeview(tree_frame, columns=("ID", "Title", "Author", "Genre", "Publication Date", "ISBN"), show="headings")
tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
tree.bind("<ButtonRelease-1>", get_selected_row)

# Configure Treeview Columns
tree.heading("ID", text="ID")
tree.heading("Title", text="Title")
tree.heading("Author", text="Author")
tree.heading("Genre", text="Genre")
tree.heading("Publication Date", text="Publication Date")
tree.heading("ISBN", text="ISBN")

for col in tree["columns"]:
    tree.column(col, width=150)

# Make the Treeview and Header Responsive
tree_frame.grid_rowconfigure(1, weight=1)
tree_frame.grid_columnconfigure(0, weight=1)

# Configure Treeview Columns
tree.heading("ID", text="ID")
tree.heading("Title", text="Title")
tree.heading("Author", text="Author")
tree.heading("Genre", text="Genre")
tree.heading("Publication Date", text="Publication Date")
tree.heading("ISBN", text="ISBN")

for col in tree["columns"]:
    tree.column(col, width=150)

# Ensure the window layout is responsive
window.grid_rowconfigure(1, weight=1)
window.grid_columnconfigure(0, weight=1)

# Button Panel
btn_frame = ttk.Frame(window, padding=10)
btn_frame.grid(row=2, column=0, sticky="ew")

ttk.Button(btn_frame, text="View All", command=view_command).grid(row=0, column=0, padx=5, pady=5)
ttk.Button(btn_frame, text="Search", command=search_command).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(btn_frame, text="Add", command=add_command).grid(row=0, column=2, padx=5, pady=5)
ttk.Button(btn_frame, text="Update", command=update_command).grid(row=0, column=3, padx=5, pady=5)
ttk.Button(btn_frame, text="Delete", command=delete_command).grid(row=0, column=4, padx=5, pady=5)
ttk.Button(btn_frame, text="Export CSV", command=export_csv).grid(row=0, column=5, padx=5, pady=5)
ttk.Button(btn_frame, text="Export JSON", command=export_json).grid(row=0, column=6, padx=5, pady=5)
ttk.Button(btn_frame, text="Toggle Dark Mode", command=toggle_theme).grid(row=0, column=7, padx=5, pady=5)


# Enable resizing
window.grid_rowconfigure(1, weight=1)
window.grid_columnconfigure(0, weight=1)

# Apply default theme
apply_theme(light_theme)

view_command()
window.mainloop()

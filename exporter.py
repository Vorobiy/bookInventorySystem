import csv
from datetime import datetime
from tkinter import filedialog, messagebox
import backend

def export_csv():
    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file:
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Author", "Genre", "Publication Date", "ISBN"])  # Header row

            for row in backend.view():
                # Format publication date as text
                try:
                    formatted_date = datetime.strptime(row[4], "%Y-%m-%d").strftime("%Y-%m-%d")
                    formatted_date = f"'{formatted_date}"  # Force text in Excel
                except (ValueError, TypeError):
                    formatted_date = "'Invalid Date"  # Prefix invalid dates as text

                # Format ISBN as text
                isbn = f"'{row[5]}" if row[5] else ""  # Prefix ISBN with a single quote

                # Write the row
                writer.writerow([row[0], row[1], row[2], row[3], formatted_date, isbn])

        messagebox.showinfo("Export", "Data exported successfully!")
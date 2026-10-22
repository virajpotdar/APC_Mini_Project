import tkinter as tk
from tkinter import ttk, messagebox
import os

from models.trip import Trip
from services.file_manager import load_trip, save_trip, archive_trip, BudgetExceededError, JSON_FILE, CSV_FILE, TXT_FILE
from services.settlement import settle_expenses, calculate_balances
from services.report import generate_report
from services.validation import valid_amount, valid_mobile


class TripSplitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trip Expense Manager")
        self.root.geometry("980x720")
        self.trip = load_trip() or Trip("My Trip", 0)
        self.build()
        self.refresh()

    def build(self):
        root = self.root
        header = ttk.Frame(root, padding=10)
        header.pack(fill="x")
        ttk.Label(header, text="Trip Expense Manger", font=("Segoe UI", 22, "bold")).pack(side="left")
        ttk.Button(header, text="New Trip", command=self.new_trip).pack(side="right", padx=5)
        ttk.Button(header, text="Save", command=self.save).pack(side="right", padx=5)
        ttk.Button(header, text="Report", command=self.report).pack(side="right", padx=5)
        ttk.Button(header, text="Delete Entire Trip", command=self.delete_trip).pack(side="right", padx=5)

        trip_frame = ttk.LabelFrame(root, text="Trip", padding=10)
        trip_frame.pack(fill="x", padx=10, pady=5)
        self.trip_name = tk.StringVar(value=self.trip.name)
        self.budget = tk.StringVar(value=str(self.trip.budget))
        ttk.Label(trip_frame, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Entry(trip_frame, textvariable=self.trip_name, width=30).grid(row=0, column=1, padx=5)
        ttk.Label(trip_frame, text="Budget").grid(row=0, column=2, sticky="w")
        ttk.Entry(trip_frame, textvariable=self.budget, width=18).grid(row=0, column=3, padx=5)

        member_frame = ttk.LabelFrame(root, text="Add Member", padding=10)
        member_frame.pack(fill="x", padx=10, pady=5)
        self.member_name = tk.StringVar()
        self.mobile = tk.StringVar()
        for i, (label, var) in enumerate((("Name", self.member_name), ("Mobile", self.mobile))):
            ttk.Label(member_frame, text=label).grid(row=0, column=i * 2, sticky="w")
            ttk.Entry(member_frame, textvariable=var, width=22).grid(row=0, column=i * 2 + 1, padx=5)
        ttk.Button(member_frame, text="Add Member", command=self.add_member).grid(row=0, column=4, padx=8)

        expense_frame = ttk.LabelFrame(root, text="Add Expense", padding=10)
        expense_frame.pack(fill="x", padx=10, pady=5)
        self.expense_name = tk.StringVar()
        self.amount = tk.StringVar()
        self.category = tk.StringVar(value="Other")
        self.payer = tk.StringVar()
        self.description = tk.StringVar()
        labels = ["Expense", "Amount", "Category", "Paid By", "Description"]
        vars_ = [self.expense_name, self.amount, self.category, self.payer, self.description]
        widths = [18, 12, 14, 16, 28]
        for i, (label, var, width) in enumerate(zip(labels, vars_, widths)):
            ttk.Label(expense_frame, text=label).grid(row=0, column=i, sticky="w", padx=2)
            if label == "Category":
                widget = ttk.Combobox(expense_frame, textvariable=var, values=["Food", "Stay", "Travel", "Tickets", "Shopping", "Entertainment", "Other"], width=width - 1, state="readonly")
            elif label == "Paid By":
                widget = ttk.Combobox(expense_frame, textvariable=var, width=width - 1, state="readonly")
                self.payer_combo = widget
            else:
                widget = ttk.Entry(expense_frame, textvariable=var, width=width)
            widget.grid(row=1, column=i, padx=2, pady=4)
        ttk.Button(expense_frame, text="Add Expense", command=self.add_expense).grid(row=1, column=5, padx=5)

        content = ttk.Panedwindow(root, orient="horizontal")
        content.pack(fill="both", expand=True, padx=10, pady=5)
        left = ttk.Frame(content, padding=5)
        right = ttk.Frame(content, padding=5)
        content.add(left, weight=1)
        content.add(right, weight=2)

        ttk.Label(left, text="Members", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.member_list = tk.Listbox(left, height=14)
        self.member_list.pack(fill="both", expand=True, pady=5)
        ttk.Button(left, text="Balance", command=self.show_balance).pack(fill="x", pady=2)
        ttk.Button(left, text="Settle", command=self.show_settlement).pack(fill="x", pady=2)

        ttk.Label(right, text="Expenses", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        cols = ("id", "date", "name", "amount", "payer", "category")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", selectmode="browse")
        headings = {"id": "ID", "date": "Date", "name": "Expense", "amount": "Amount", "payer": "Paid By", "category": "Category"}
        for col in cols:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=90)
        self.tree.pack(fill="both", expand=True)
        ttk.Button(right, text="Delete Selected Expense", command=self.delete_expense).pack(anchor="e", pady=5)

        self.status = tk.StringVar()
        ttk.Label(root, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    def refresh(self):
        self.trip.name = self.trip_name.get().strip() or self.trip.name
        try:
            self.trip.budget = float(self.budget.get())
        except ValueError:
            pass
        calculate_balances(self.trip)
        self.member_list.delete(0, "end")
        for member in self.trip.members.values():
            self.member_list.insert("end", f"{member.name} | Paid ₹{member.paid:.2f} | Balance ₹{member.balance:.2f}")
        names = list(self.trip.members.keys())
        self.payer_combo["values"] = names
        if names and self.payer.get() not in names:
            self.payer.set(names[0])
        for row in self.tree.get_children():
            self.tree.delete(row)
        for expense in self.trip.expenses:
            self.tree.insert("", "end", values=(expense.expense_id, expense.date, expense.name, f"₹{expense.amount:.2f}", expense.paid_by, expense.category))
        self.status.set(f"Total ₹{self.trip.total_expense():.2f} | Remaining Budget ₹{self.trip.remaining_budget():.2f}")

    def save(self):
        try:
            self.trip.name = self.trip_name.get().strip() or "My Trip"
            self.trip.budget = float(self.budget.get())
            save_trip(self.trip)
            self.refresh()
            messagebox.showinfo("Saved", "Trip saved successfully.")
        except (ValueError, BudgetExceededError) as error:
            messagebox.showerror("Error", str(error))

    def add_member(self):
        name = self.member_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter member name.")
            return
        if self.mobile.get() and not valid_mobile(self.mobile.get()):
            messagebox.showerror("Error", "Enter a valid 10-digit Indian mobile number.")
            return
        try:
            self.trip.add_member(name, self.mobile.get())
            save_trip(self.trip)
            self.member_name.set("")
            self.mobile.set("")
            self.refresh()
        except (ValueError, OSError, BudgetExceededError) as error:
            messagebox.showerror("Error", str(error))

    def add_expense(self):
        if not self.trip.members:
            messagebox.showerror("Error", "Add at least one member first.")
            return
        if not self.expense_name.get().strip():
            messagebox.showerror("Error", "Enter an expense name.")
            return
        if not valid_amount(self.amount.get()):
            messagebox.showerror("Error", "Enter a valid amount greater than zero.")
            return
        try:
            self.trip.add_expense(self.expense_name.get(), float(self.amount.get()), self.payer.get(), self.category.get(), "equal", list(self.trip.members.keys()), description=self.description.get())
            save_trip(self.trip)
            self.expense_name.set("")
            self.amount.set("")
            self.description.set("")
            self.refresh()
        except (ValueError, KeyError, OSError, BudgetExceededError) as error:
            messagebox.showerror("Error", str(error))

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select expense", "Select an expense from the table first.")
            return
        values = self.tree.item(selected[0], "values")
        expense_id = int(values[0])
        if not messagebox.askyesno("Confirm delete", "Delete this expense? This cannot be undone."):
            return
        self.trip.expenses = [expense for expense in self.trip.expenses if expense.expense_id != expense_id]
        # Recalculate the amount paid by every member after deletion.
        for member in self.trip.members.values():
            member.paid = 0.0
        for expense in self.trip.expenses:
            if expense.paid_by in self.trip.members:
                self.trip.members[expense.paid_by].paid += expense.amount
        try:
            save_trip(self.trip)
            self.refresh()
        except (OSError, ValueError, BudgetExceededError) as error:
            messagebox.showerror("Error", str(error))

    def reset_trip_fields(self):
        self.trip_name.set("My Trip")
        self.budget.set("0")
        self.member_name.set("")
        self.mobile.set("")
        self.expense_name.set("")
        self.amount.set("")
        self.description.set("")
        self.payer.set("")

    def new_trip(self):
        has_data = bool(self.trip.members or self.trip.expenses or self.trip.name.strip() != "My Trip" or self.trip.budget != 0)
        if not has_data:
            self.trip = Trip("My Trip", 0)
            self.reset_trip_fields()
            self.refresh()
            return
        if not messagebox.askyesno("Start new trip", "Save the current trip and begin a fresh one?"):
            return
        try:
            backup_path = archive_trip(self.trip)
            self.trip = Trip("My Trip", 0)
            save_trip(self.trip)
            self.reset_trip_fields()
            self.refresh()
            messagebox.showinfo("New trip started", f"Previous trip saved to:\n{backup_path}")
        except (OSError, ValueError, BudgetExceededError) as error:
            messagebox.showerror("Error", str(error))

    def delete_trip(self):
        if not messagebox.askyesno("Delete entire trip", "Delete this trip, all members and all expenses? This cannot be undone."):
            return
        for path in (JSON_FILE, CSV_FILE, TXT_FILE):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError as error:
                messagebox.showerror("Delete error", str(error))
                return
        self.trip = Trip("My Trip", 0)
        self.reset_trip_fields()
        self.refresh()
        messagebox.showinfo("Trip deleted", "The trip and its saved data have been deleted.")

    def show_balance(self):
        balances = calculate_balances(self.trip)
        text = "\n".join(f"{name}: ₹{value:.2f}" for name, value in balances.items()) or "No members yet."
        messagebox.showinfo("Balances", text)
        self.refresh()

    def show_settlement(self):
        settlements = settle_expenses(self.trip)
        save_trip(self.trip)
        if not settlements:
            text = "All settled."
        else:
            text = "\n".join(f"{item['from']} pays {item['to']}: ₹{item['amount']:.2f}" for item in settlements)
        messagebox.showinfo("Settlement", text)
        self.refresh()

    def report(self):
        settlements = settle_expenses(self.trip)
        path = generate_report(self.trip, settlements)
        messagebox.showinfo("Report created", f"Saved report to:\n{path}")


def run():
    root = tk.Tk()
    TripSplitGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run()

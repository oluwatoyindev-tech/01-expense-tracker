"""
Expense Tracker — Python + SQLite
A CLI app to record, categorize, and report personal expenses.

Run:  python expense_tracker.py
Data: stored in expenses.db (auto-created next to this file)
"""
import sqlite3
import os
from datetime import datetime

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")


def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                note        TEXT,
                spent_on    TEXT NOT NULL
            )
            """
        )


def add_expense(amount, category, note, spent_on):
    with connect() as conn:
        conn.execute(
            "INSERT INTO expenses (amount, category, note, spent_on) VALUES (?, ?, ?, ?)",
            (amount, category, note, spent_on),
        )
    print(f"✓ Added {amount:.2f} to '{category}'.")


def list_expenses():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM expenses ORDER BY spent_on DESC, id DESC").fetchall()
    if not rows:
        print("No expenses yet.")
        return
    print(f"\n{'ID':<4}{'Date':<12}{'Category':<15}{'Amount':>10}  Note")
    print("-" * 60)
    for r in rows:
        print(f"{r['id']:<4}{r['spent_on']:<12}{r['category']:<15}{r['amount']:>10.2f}  {r['note'] or ''}")


def delete_expense(exp_id):
    with connect() as conn:
        cur = conn.execute("DELETE FROM expenses WHERE id = ?", (exp_id,))
    print("✓ Deleted." if cur.rowcount else "No expense with that id.")


def summary():
    with connect() as conn:
        total = conn.execute("SELECT COALESCE(SUM(amount), 0) t FROM expenses").fetchone()["t"]
        by_cat = conn.execute(
            "SELECT category, SUM(amount) s FROM expenses GROUP BY category ORDER BY s DESC"
        ).fetchall()
    print(f"\n=== Summary ===\nTotal spent: {total:.2f}")
    if by_cat:
        print("\nBy category:")
        for r in by_cat:
            pct = (r["s"] / total * 100) if total else 0
            bar = "█" * int(pct / 4)
            print(f"  {r['category']:<15}{r['s']:>10.2f}  {pct:5.1f}%  {bar}")


def prompt_float(msg):
    while True:
        try:
            return float(input(msg).strip())
        except ValueError:
            print("Please enter a number.")


def menu():
    init_db()
    actions = {
        "1": "Add expense",
        "2": "List expenses",
        "3": "Summary / report",
        "4": "Delete expense",
        "5": "Quit",
    }
    while True:
        print("\n=== Expense Tracker ===")
        for k, v in actions.items():
            print(f"  {k}. {v}")
        choice = input("Choose: ").strip()
        if choice == "1":
            amount = prompt_float("Amount: ")
            category = input("Category: ").strip() or "Uncategorized"
            note = input("Note (optional): ").strip()
            spent_on = input(f"Date [YYYY-MM-DD, blank=today]: ").strip() or datetime.now().strftime("%Y-%m-%d")
            add_expense(amount, category, note, spent_on)
        elif choice == "2":
            list_expenses()
        elif choice == "3":
            summary()
        elif choice == "4":
            list_expenses()
            try:
                delete_expense(int(input("ID to delete: ").strip()))
            except ValueError:
                print("Invalid id.")
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    try:
        menu()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")

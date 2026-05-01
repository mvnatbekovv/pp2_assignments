import psycopg2
import csv
from config8 import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

# --- Connection ---

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# --- Table setup ---

def create_table():
    command = """CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20) NOT NULL
            )"""
    with conn.cursor() as cur:
        cur.execute(command)
        conn.commit()

# --- Old Practice 7 feature kept: CSV import ---

def insert_from_csv(csv_file):
    command = "INSERT INTO contacts(name, phone) VALUES(%s, %s) ON CONFLICT (name) DO UPDATE SET phone = EXCLUDED.phone"
    with conn.cursor() as cur:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                name, phone = row
                cur.execute(command, (name, phone))
        conn.commit()
    print(f"Imported contacts from {csv_file}")

# --- Practice 8: functions and procedures ---

def search_contacts_by_pattern(pattern):
    command = "SELECT * FROM search_contacts_by_pattern(%s)"
    with conn.cursor() as cur:
        cur.execute(command, (pattern,))
        return cur.fetchall()

def get_contacts_paginated(limit, offset):
    command = "SELECT * FROM get_contacts_paginated(%s, %s)"
    with conn.cursor() as cur:
        cur.execute(command, (limit, offset))
        return cur.fetchall()

def upsert_contact(name, phone):
    command = "CALL upsert_contact(%s, %s)"
    with conn.cursor() as cur:
        cur.execute(command, (name, phone))
        conn.commit()
    print(f"Inserted/Updated: {name} - {phone}")

def insert_many_contacts():
    n = int(input("How many contacts do you want to add? "))
    names = []
    phones = []

    for i in range(n):
        print(f"\nContact {i + 1}")
        name = input("Enter name: ")
        phone = input("Enter phone: ")
        names.append(name)
        phones.append(phone)

    command = "CALL insert_many_contacts(%s, %s)"
    with conn.cursor() as cur:
        conn.notices.clear()
        cur.execute(command, (names, phones))
        conn.commit()

    if conn.notices:
        print("\nServer notices:")
        for notice in conn.notices:
            print(notice.strip())
    else:
        print("All contacts inserted successfully.")

def delete_contact(value):
    command = "CALL delete_contact(%s)"
    with conn.cursor() as cur:
        cur.execute(command, (value,))
        conn.commit()
    print(f"Deleted rows by value: {value}")

# --- Utility ---

def print_contacts(contacts):
    if not contacts:
        print("  (no contacts)")
        return
    for c in contacts:
        print(f"  [{c[0]}] {c[1]} - {c[2]}")

# --- Main menu ---

def main():ff
    create_table()

    while True:
        print("\n--- Practice 8: PhoneBook ---")
        print("1. Import from CSV")
        print("2. Search contacts by pattern")
        print("3. Show contacts with pagination")
        print("4. Insert or update one contact")
        print("5. Insert many contacts")
        print("6. Delete contact by name or phone")
        print("0. Exit")

        choice = input("\nChoice: ")

        if choice == "1":
            filename = input("CSV file path: ")
            insert_from_csv(filename)

        elif choice == "2":
            pattern = input("Enter pattern: ")
            print_contacts(search_contacts_by_pattern(pattern))

        elif choice == "3":
            limit = int(input("Enter LIMIT: "))
            offset = int(input("Enter OFFSET: "))
            print_contacts(get_contacts_paginated(limit, offset))

        elif choice == "4":
            name = input("Enter name: ")
            phone = input("Enter phone: ")
            upsert_contact(name, phone)

        elif choice == "5":
            insert_many_contacts()

        elif choice == "6":
            value = input("Enter username or phone: ")
            delete_contact(value)

        elif choice == "0":
            break

        else:
            print("Invalid choice")

    conn.close()
    print("Goodbye!")

if __name__ == "__main__":
    main()

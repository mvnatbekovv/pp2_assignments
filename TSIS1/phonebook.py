import csv
from pathlib import Path
import json
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from connect import get_connection


VALID_PHONE_TYPES = {"home", "work", "mobile"}
VALID_SORT_FIELDS = {"name", "birthday", "date_added"}


BASE_DIR = Path(__file__).resolve().parent

def run_sql_file(conn, path: str) -> None:
    sql_path = BASE_DIR / path
    with open(sql_path, "r", encoding="utf-8") as file:
        sql = file.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def setup_database(conn) -> None:
    run_sql_file(conn, "schema.sql")
    run_sql_file(conn, "procedures.sql")
    print("Database schema and procedures are ready.")


def normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def normalize_phone_type(value: Optional[str]) -> str:
    value = (value or "mobile").strip().lower()
    if value not in VALID_PHONE_TYPES:
        return "mobile"
    return value


def get_group_id(conn, group_name: Optional[str]) -> int:
    group_name = normalize_text(group_name) or "Other"
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO groups(name) VALUES(%s) ON CONFLICT(name) DO NOTHING",
            (group_name,),
        )
        cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
        group_id = cur.fetchone()[0]
    return group_id


def upsert_contact(conn, name: str, email: Optional[str], birthday: Optional[str], group_name: Optional[str]) -> int:
    group_id = get_group_id(conn, group_name)
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT(name) DO UPDATE
            SET email = EXCLUDED.email,
                birthday = EXCLUDED.birthday,
                group_id = EXCLUDED.group_id
            RETURNING id
            """,
            (name, email, birthday or None, group_id),
        )
        return cur.fetchone()[0]


def add_phone(conn, contact_name: str, phone: str, phone_type: str = "mobile") -> None:
    with conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, normalize_phone_type(phone_type)))
    conn.commit()


def add_contact_console(conn) -> None:
    name = input("Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    email = normalize_text(input("Email: "))
    birthday = normalize_text(input("Birthday (YYYY-MM-DD, empty if none): "))
    group_name = normalize_text(input("Group (Family/Work/Friend/Other): ")) or "Other"
    phone = normalize_text(input("Phone: "))
    phone_type = normalize_phone_type(input("Phone type (home/work/mobile): "))

    upsert_contact(conn, name, email, birthday, group_name)
    if phone:
        add_phone(conn, name, phone, phone_type)
    else:
        conn.commit()
    print(f"Saved contact: {name}")


def print_contacts(rows) -> None:
    if not rows:
        print("  (no contacts)")
        return

    print("-" * 110)
    print(f"{'ID':<4} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<12} Phones")
    print("-" * 110)
    for row in rows:
        if not isinstance(row, dict):
            row = {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "birthday": row[3],
                "group_name": row[4],
                "phones": row[5],
            }
        print(
            f"{row.get('id', ''):<4} "
            f"{str(row.get('name') or ''):<20} "
            f"{str(row.get('email') or ''):<25} "
            f"{str(row.get('birthday') or ''):<12} "
            f"{str(row.get('group_name') or ''):<12} "
            f"{row.get('phones') or ''}"
        )


def list_contacts(conn, group_name: Optional[str] = None, sort_by: str = "name", limit: int = 100, offset: int = 0):
    if sort_by not in VALID_SORT_FIELDS:
        sort_by = "name"
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM get_contacts_paginated_extended(%s, %s, %s, %s)",
            (limit, offset, sort_by, group_name),
        )
        return cur.fetchall()


def show_all_contacts(conn) -> None:
    sort_by = input("Sort by name/birthday/date_added [name]: ").strip() or "name"
    if sort_by not in VALID_SORT_FIELDS:
        print("Invalid sort field, using name.")
        sort_by = "name"
    print_contacts(list_contacts(conn, sort_by=sort_by))


def filter_by_group(conn) -> None:
    group_name = input("Group name: ").strip()
    sort_by = input("Sort by name/birthday/date_added [name]: ").strip() or "name"
    print_contacts(list_contacts(conn, group_name=group_name, sort_by=sort_by))


def search_contacts(conn) -> None:
    query = input("Search text (name/email/group/phone): ").strip()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
    print_contacts(rows)


def search_by_email(conn) -> None:
    query = input("Email search: ").strip()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT * FROM search_contacts(%s)
            WHERE email ILIKE %s
            ORDER BY name
            """,
            (query, f"%{query}%"),
        )
        rows = cur.fetchall()
    print_contacts(rows)


def paginated_navigation(conn) -> None:
    limit_text = input("Page size [5]: ").strip() or "5"
    try:
        limit = max(1, int(limit_text))
    except ValueError:
        limit = 5

    sort_by = input("Sort by name/birthday/date_added [name]: ").strip() or "name"
    if sort_by not in VALID_SORT_FIELDS:
        sort_by = "name"

    group_name = normalize_text(input("Filter group (empty for all): "))
    offset = 0

    while True:
        rows = list_contacts(conn, group_name=group_name, sort_by=sort_by, limit=limit, offset=offset)
        print(f"\nPage {offset // limit + 1}")
        print_contacts(rows)
        command = input("next / prev / quit: ").strip().lower()
        if command == "next":
            if len(rows) < limit:
                print("No next page.")
            else:
                offset += limit
        elif command == "prev":
            offset = max(0, offset - limit)
        elif command == "quit":
            break
        else:
            print("Unknown command.")


def import_from_csv(conn) -> None:
    path = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv"
    count = 0
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = normalize_text(row.get("name"))
            if not name:
                continue
            email = normalize_text(row.get("email"))
            birthday = normalize_text(row.get("birthday"))
            group_name = normalize_text(row.get("group")) or "Other"
            phone = normalize_text(row.get("phone"))
            phone_type = normalize_phone_type(row.get("type"))

            upsert_contact(conn, name, email, birthday, group_name)
            if phone:
                add_phone(conn, name, phone, phone_type)
            count += 1
    conn.commit()
    print(f"Imported {count} contact(s) from {path}.")


def export_to_json(conn) -> None:
    filename = input("Output JSON file [contacts_export.json]: ").strip() or "contacts_export.json"
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT
                c.id,
                c.name,
                c.email,
                c.birthday,
                g.name AS group_name,
                c.date_added
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY c.name
            """
        )
        contacts = cur.fetchall()

        for contact in contacts:
            cur.execute(
                "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY type, phone",
                (contact["id"],),
            )
            contact["phones"] = cur.fetchall()
            if contact["birthday"] is not None:
                contact["birthday"] = contact["birthday"].isoformat()
            if contact["date_added"] is not None:
                contact["date_added"] = contact["date_added"].isoformat(sep=" ", timespec="seconds")

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(contacts, file, ensure_ascii=False, indent=4)
    print(f"Exported {len(contacts)} contact(s) to {filename}.")


def contact_exists(conn, name: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT EXISTS(SELECT 1 FROM contacts WHERE name = %s)", (name,))
        return cur.fetchone()[0]


def delete_contact_by_name(conn, name: str) -> None:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
    conn.commit()


def import_from_json(conn) -> None:
    filename = input("JSON file path [contacts_export.json]: ").strip() or "contacts_export.json"
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    imported = 0
    skipped = 0
    for item in data:
        name = normalize_text(item.get("name"))
        if not name:
            skipped += 1
            continue

        if contact_exists(conn, name):
            action = input(f"Duplicate '{name}'. skip or overwrite? [skip]: ").strip().lower() or "skip"
            if action != "overwrite":
                skipped += 1
                continue
            delete_contact_by_name(conn, name)

        birthday = normalize_text(item.get("birthday"))
        email = normalize_text(item.get("email"))
        group_name = normalize_text(item.get("group_name") or item.get("group")) or "Other"
        upsert_contact(conn, name, email, birthday, group_name)

        for phone_item in item.get("phones", []):
            phone = normalize_text(phone_item.get("phone"))
            phone_type = normalize_phone_type(phone_item.get("type"))
            if phone:
                add_phone(conn, name, phone, phone_type)
        imported += 1

    conn.commit()
    print(f"Imported {imported} contact(s), skipped {skipped}.")


def move_contact_to_group(conn) -> None:
    name = input("Contact name: ").strip()
    group_name = input("New group: ").strip()
    with conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
    conn.commit()
    print(f"Moved {name} to {group_name}.")


def add_phone_console(conn) -> None:
    name = input("Contact name: ").strip()
    phone = input("New phone: ").strip()
    phone_type = normalize_phone_type(input("Type (home/work/mobile): "))
    add_phone(conn, name, phone, phone_type)
    print("Phone added.")


def delete_contact_console(conn) -> None:
    name = input("Name to delete: ").strip()
    delete_contact_by_name(conn, name)
    print("Deleted if contact existed.")


def print_menu() -> None:
    print("\n--- TSIS1 PhoneBook ---")
    print("1. Setup database tables and procedures")
    print("2. Show all contacts")
    print("3. Add or update contact")
    print("4. Add phone to existing contact")
    print("5. Search contacts (name/email/group/phone)")
    print("6. Search by email")
    print("7. Filter by group")
    print("8. Paginated navigation")
    print("9. Import from CSV")
    print("10. Export to JSON")
    print("11. Import from JSON")
    print("12. Move contact to group")
    print("13. Delete contact by name")
    print("0. Exit")


def main() -> None:
    try:
        conn = get_connection()
    except psycopg2.Error as error:
        print("Could not connect to PostgreSQL.")
        print(error)
        return

    actions = {
        "1": setup_database,
        "2": show_all_contacts,
        "3": add_contact_console,
        "4": add_phone_console,
        "5": search_contacts,
        "6": search_by_email,
        "7": filter_by_group,
        "8": paginated_navigation,
        "9": import_from_csv,
        "10": export_to_json,
        "11": import_from_json,
        "12": move_contact_to_group,
        "13": delete_contact_console,
    }

    try:
        while True:
            print_menu()
            choice = input("Choice: ").strip()
            if choice == "0":
                break
            action = actions.get(choice)
            if action is None:
                print("Invalid choice.")
                continue
            try:
                action(conn)
            except Exception as error:
                conn.rollback()
                print(f"Error: {error}")
    finally:
        conn.close()
        print("Goodbye!")


if __name__ == "__main__":
    main()

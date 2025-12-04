import os
import sqlite3
import pandas as pd

# Resolve paths relative to this script's directory so running from
# a different cwd still finds the data files.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_DIR = os.path.join(BASE_DIR, "abc_books")
DB_PATH = os.path.join(BASE_DIR, "tunes.db")


def setup_database():
    """
    Creates the tunes table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tunes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            title TEXT,
            tune_type TEXT,
            meter TEXT,
            key_sig TEXT,
            content TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized.")


def save_tune_to_db(tune_data):
    """Helper function to insert a dictionary of tune data into SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO tunes (book_id, title, tune_type, meter, key_sig, content)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        tune_data.get('book_id'),
        tune_data.get('title', 'Unknown'),
        tune_data.get('type', 'Unknown'),
        tune_data.get('meter', ''),
        tune_data.get('key', ''),
        tune_data.get('content', '')
    ))

    conn.commit()
    conn.close()


def process_file(file_path, book_id):
    """
    Reads an ABC file, parses multiple tunes, and saves them to DB.
    """
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    # Clean lines (preserve internal spacing; remove trailing newlines)
    lines = [line.rstrip('\n') for line in lines]

    current_tune = {}
    in_tune = False

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # X: indicates the start of a new tune
        if line.startswith('X:'):
            # If we were already building a tune, save the previous one
            if in_tune and current_tune:
                save_tune_to_db(current_tune)

            # Reset for the new tune
            current_tune = {'book_id': book_id, 'content': ''}
            in_tune = True

        if in_tune:
            current_tune['content'] += line + "\n"

            # Extract Metadata
            if line.startswith('T:') and 'title' not in current_tune:
                current_tune['title'] = line[2:].strip()
            elif line.startswith('R:'):
                current_tune['type'] = line[2:].strip()
            elif line.startswith('M:'):
                current_tune['meter'] = line[2:].strip()
            elif line.startswith('K:'):
                current_tune['key'] = line[2:].strip()

    # Save the very last tune in the file
    if in_tune and current_tune:
        save_tune_to_db(current_tune)


def ingest_data():
    print("--- Starting Data Ingestion ---")
    setup_database()  # Ensure table exists

    # Iterate over directories in abc_books
    if not os.path.exists(BOOKS_DIR):
        print(f"Error: Folder '{BOOKS_DIR}' not found.")
        return

    for item in os.listdir(BOOKS_DIR):
        item_path = os.path.join(BOOKS_DIR, item)

        # Check if it's a directory and has a numeric name (Book ID)
        if os.path.isdir(item_path) and item.isdigit():
            book_id = int(item)
            print(f"Processing Book {book_id}...")

            # Iterate over files in the numbered directory
            for file in os.listdir(item_path):
                if file.endswith('.abc'):
                    file_path = os.path.join(item_path, file)
                    process_file(file_path, book_id)

    print("--- Ingestion Complete ---")


def get_dataframe():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM tunes", conn)
    conn.close()
    return df


def search_tunes(search_term):
    df = get_dataframe()
    if df.empty:
        return "Database is empty."

    # Case insensitive search on Title
    results = df[df['title'].str.contains(search_term, case=False, na=False)]
    return results[['book_id', 'title', 'tune_type']]


def get_stats():
    df = get_dataframe()
    if df.empty:
        print("Database is empty.")
        return

    print(f"Total Tunes: {len(df)}")
    print("Tunes per Book:")
    print(df['book_id'].value_counts())


def main_menu():
    while True:
        print("\n=== ABC TUNE MANAGER 2025 ===")
        print("1. Ingest/Reload Data (Parse Files)")
        print("2. Show Statistics")
        print("3. Search for a Tune")
        print("4. Exit")

        choice = input("Choice: ")

        if choice == '1':
            ingest_data()
        elif choice == '2':
            get_stats()
        elif choice == '3':
            term = input("Enter search term: ")
            print(search_tunes(term))
        elif choice == '4':
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    # This runs the menu when you press play
    main_menu()
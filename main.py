import os
import sqlite3
import sys
import pandas as pd
import analysis  # Importing your analysis.py

# Resolve paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_DIR = os.path.join(BASE_DIR, "abc_books")
DB_PATH = os.path.join(BASE_DIR, "tunes.db")

# --- INGESTION LOGIC ---

def setup_database() -> None:
    """Creates the database table with the new reference_number column."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tunes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            reference_number TEXT,
            title TEXT,
            tune_type TEXT,
            meter TEXT,
            key_sig TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_tune_to_db(tune_data: dict) -> None:
    """Inserts a single tune dictionary into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tunes (book_id, reference_number, title, tune_type, meter, key_sig, content)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        tune_data.get('book_id'),
        tune_data.get('reference_number', '0'), # New field
        tune_data.get('title', 'Unknown'),
        tune_data.get('type', 'Unknown'),
        tune_data.get('meter', ''),
        tune_data.get('key', ''),
        tune_data.get('content', '')
    ))
    conn.commit()
    conn.close()

def process_file(file_path: str, book_id: int) -> None:
    """Parses a specific ABC file and extracts X-reference numbers."""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]

    current_tune = {}
    in_tune = False

    for raw in lines:
        line = raw.strip()
        if not line: continue

        if line.startswith('X:'):
            if in_tune and current_tune:
                save_tune_to_db(current_tune)
            
            # Start new tune and capture the Reference Number (X: value)
            ref_num = line[2:].strip()
            current_tune = {
                'book_id': book_id, 
                'reference_number': ref_num, 
                'content': ''
            }
            in_tune = True

        if in_tune:
            current_tune['content'] += line + "\n"
            if line.startswith('T:') and 'title' not in current_tune:
                current_tune['title'] = line[2:].strip()
            elif line.startswith('R:'):
                current_tune['type'] = line[2:].strip()
            elif line.startswith('M:'):
                current_tune['meter'] = line[2:].strip()
            elif line.startswith('K:'):
                current_tune['key'] = line[2:].strip()

    if in_tune and current_tune:
        save_tune_to_db(current_tune)

def ingest_data() -> None:
    """Main logic to traverse directories and process all files."""
    print("\n--- Starting Data Ingestion ---")
    setup_database()
    if not os.path.exists(BOOKS_DIR):
        print(f"Error: Folder '{BOOKS_DIR}' not found.")
        return

    count = 0
    for item in os.listdir(BOOKS_DIR):
        item_path = os.path.join(BOOKS_DIR, item)
        if os.path.isdir(item_path) and item.isdigit():
            book_id = int(item)
            print(f"Processing Book {book_id}...")
            for file in os.listdir(item_path):
                if file.endswith('.abc'):
                    process_file(os.path.join(item_path, file), book_id)
                    count += 1
    print(f"--- Ingestion Complete ({count} files) ---")

# --- UI HELPER ---

def print_results(df_results: pd.DataFrame) -> None:
    """Formats and prints search results."""
    if df_results.empty:
        print("\nNo results found.")
    else:
        print("\n--- Results ---")
        # Show reference number in the output now
        print(df_results[['book_id', 'reference_number', 'title', 'tune_type']].to_string(index=False))
        print(f"({len(df_results)} tunes found)")

# --- MAIN MENU ---

def main_menu() -> None:
    """Displays the interactive CLI menu."""
    df = analysis.load_data()
    
    while True:
        print("\n=== ABC TUNE MANAGER 2025 ===")
        print("1. Ingest/Reload Data")
        print("2. Show Statistics")
        print("3. Search by Title")
        print("4. Search by Book Number")
        print("5. Search by Book AND Reference Number (X:)")
        print("6. Search by Global DB ID")
        print("7. Exit")

        choice = input("Choice: ")

        if choice == '1':
            ingest_data()
            df = analysis.load_data()
            
        elif choice == '2':
            print(analysis.get_stats(df))
            
        elif choice == '3':
            if df.empty: df = analysis.load_data()
            term = input("Enter title search term: ")
            results = analysis.search_tunes(df, term)
            print_results(results)
            
        elif choice == '4':
            if df.empty: df = analysis.load_data()
            bk = input("Enter Book Number: ")
            results = analysis.get_tunes_by_book(df, bk)
            print_results(results)

        elif choice == '5':
            # NEW OPTION
            if df.empty: df = analysis.load_data()
            bk = input("Enter Book Number: ")
            ref = input("Enter Reference Number (X value): ")
            
            results = analysis.get_tune_by_book_and_ref(df, bk, ref)
            
            if not results.empty:
                row = results.iloc[0]
                print("\n" + "="*40)
                print(f"Book: {row['book_id']} | Ref (X): {row['reference_number']}")
                print(f"Title: {row['title']}")
                print(f"Type: {row['tune_type']} | Key: {row['key_sig']}")
                print("="*40)
                print(row['content'])
                print("="*40)
            else:
                print("Tune not found in that book.")
            
        elif choice == '6':
            if df.empty: df = analysis.load_data()
            tid = input("Enter Global Tune ID: ")
            results = analysis.get_tune_by_id(df, tid)
            
            if not results.empty:
                row = results.iloc[0]
                print("\n" + "="*40)
                print(f"Global ID: {row['id']} | Title: {row['title']}")
                print("="*40)
                print(row['content'])
                print("="*40)
            else:
                print("ID not found.")
                
        elif choice == '7':
            print("Goodbye.")
            sys.exit()
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main_menu()
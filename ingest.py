# ingest.py
import os
from parser import parse_abc_file
from database_manager import create_database, insert_tune

# Resolve the root dir relative to this script so it works regardless
# of the current working directory when the script is run.
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "abc_books")

def main():
    # 1. Setup DB
    create_database()
    
    # 2. Walk through directories
    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".abc"):
                full_path = os.path.join(root, file)
                
                # Extract book number from folder name (e.g., abc_books/1 -> 1)
                # Assuming structure is abc_books/{book_num}/{file}
                try:
                    book_id = int(os.path.basename(root))
                except ValueError:
                    book_id = 0 # Default if folder isn't a number
                
                print(f"Processing {file} for Book {book_id}...")
                
                # 3. Parse File
                tunes = parse_abc_file(full_path)
                
                # 4. Insert into DB
                for tune in tunes:
                    insert_tune(book_id, tune)
                    count += 1
                    
    print(f"Ingestion complete. {count} tunes stored.")

if __name__ == "__main__":
    main()
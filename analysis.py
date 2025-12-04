import pandas as pd
import sqlite3
from database_manager import DB_NAME

def load_data() -> pd.DataFrame:
    """Loads all data from SQL into a Pandas DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM tunes"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_tunes_by_book(df: pd.DataFrame, book_number: int) -> pd.DataFrame:
    """Returns a DataFrame containing only tunes from a specific book."""
    return df[df['book_id'] == book_number]

def get_tunes_by_type(df: pd.DataFrame, tune_type: str) -> pd.DataFrame:
    """Returns a DataFrame containing tunes of a specific type (e.g., Reel)."""
    # handling case sensitivity and whitespace
    return df[df['tune_type'].str.contains(tune_type, case=False, na=False)]

def search_tunes(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """Search tunes by title (case insensitive)."""
    return df[df['title'].str.contains(search_term, case=False, na=False)]

def get_stats(df: pd.DataFrame):
    """Prints basic statistics about the collection."""
    print("\n--- Collection Stats ---")
    print(f"Total Tunes: {len(df)}")
    print("Tunes per Book:")
    print(df['book_id'].value_counts().sort_index())
    print("\nMost Common Tune Types:")
    print(df['tune_type'].value_counts().head())
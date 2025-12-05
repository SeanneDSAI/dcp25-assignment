import pandas as pd
import sqlite3
import os

# Robust path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tunes.db")

def load_data() -> pd.DataFrame:
    """
    Loads all data from SQL into a Pandas DataFrame.
    Returns an empty DataFrame if the DB doesn't exist.
    """
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM tunes"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading database: {e}")
        return pd.DataFrame()

def get_tunes_by_book(df: pd.DataFrame, book_number: str) -> pd.DataFrame:
    """Returns a DataFrame containing only tunes from a specific book."""
    if df.empty: return df
    try:
        bid = int(book_number)
        return df[df['book_id'] == bid]
    except ValueError:
        return pd.DataFrame()

def get_tune_by_id(df: pd.DataFrame, tune_id: str) -> pd.DataFrame:
    """Returns a single row DataFrame for a specific tune ID."""
    if df.empty: return df
    try:
        tid = int(tune_id)
        return df[df['id'] == tid]
    except ValueError:
        return pd.DataFrame()

def search_tunes(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """Search tunes by title (case insensitive)."""
    if df.empty: return df
    return df[df['title'].str.contains(search_term, case=False, na=False)]

def get_stats(df: pd.DataFrame):
    """Returns a string of basic statistics about the collection."""
    if df.empty:
        return "No data available."
        
    stats = []
    stats.append(f"Total Tunes: {len(df)}")
    stats.append("\nTunes per Book:")
    stats.append(df['book_id'].value_counts().sort_index().to_string())
    stats.append("\nTop 5 Tune Types:")
    stats.append(df['tune_type'].value_counts().head(5).to_string())
    return "\n".join(stats)
import pandas as pd
import analysis # We import analysis because that is where your logic lives

print("----------------------------------------------------------------")
print("MANUAL TESTING SCRIPT")
print("----------------------------------------------------------------")

# 1. Load the Database
print("\n[TEST 1] Loading Database...")
df = analysis.load_data()

if df.empty:
    print("ERROR: Database is empty. Please run 'main.py' and ingest data first.")
else:
    print(f"SUCCESS: Loaded {len(df)} tunes from tunes.db")


# 2. Test specific logic functions
if not df.empty:
    
    # Test A: Get tunes from Book 1
    print("\n[TEST 2] Testing 'get_tunes_by_book(1)'...")
    book1 = analysis.get_tunes_by_book(df, 1)
    print(f"Found {len(book1)} tunes in Book 1.")
    print("First 3 results:")
    print(book1[['reference_number', 'title']].head(3).to_string(index=False))

    # Test B: Search for "Reel"
    print("\n[TEST 3] Testing 'search_tunes' for 'Reel'...")
    reels = analysis.search_tunes(df, "Reel")
    print(f"Found {len(reels)} tunes with 'Reel' in the title.")
    print("First 3 results:")
    print(reels[['title', 'tune_type']].head(3).to_string(index=False))

    # Test C: The new feature (Book + Reference)
    print("\n[TEST 4] Testing 'get_tune_by_book_and_ref' (Book 2, Tune 6)...")
    specific_tune = analysis.get_tune_by_book_and_ref(df, 2, 6)
    
    if not specific_tune.empty:
        print("SUCCESS: Found the tune!")
        print(f"Title: {specific_tune.iloc[0]['title']}")
    else:
        print("FAIL: Could not find Book 2 Tune 6.")

print("\n----------------------------------------------------------------")
print("TESTING COMPLETE")
print("----------------------------------------------------------------")
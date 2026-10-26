import pandas as pd

def load_books(csv_path: str = "data/books_sample.csv") -> pd.DataFrame:
    """Load the books dataset and clean it."""
    df = pd.read_csv(csv_path)
    
    # Drop rows with missing descriptions or titles
    df = df.dropna(subset=["title", "description"])
    
    # Ensure ISBN is a string (to preserve leading zeros if any)
    df["isbn13"] = df["isbn13"].astype(str)
    
    # Create the tagged description.
    # We prepend the ISBN so we can map the vector search result back to the row later.
    df["tagged_description"] = df["isbn13"] + " " + df["description"]
    
    return df
import pandas as pd
from fastapi import FastAPI, Query
from typing import List
from pydantic import BaseModel
import os

app = FastAPI()

_books_df = None

def get_books_df():
    global _books_df
    if _books_df is None:
        print("Loading books.csv...")
        csv_path = os.path.join(os.path.dirname(__file__), "books.csv")
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["title", "authors"])
        df["title"] = df["title"].astype(str)
        df["authors"] = df["authors"].astype(str)
        df["genre"] = df["genre"].fillna("Unknown").astype(str)
        df["description"] = df["description"].fillna("").astype(str)
        _books_df = df
        print(f"Loaded {len(df)} books.")
    return _books_df

class Book(BaseModel):
    title: str
    authors: str
    genre: str
    description: str

@app.get("/recommend", response_model=List[Book])
def recommend(
    title: str = Query("", description="Partial or full book title"),
    authors: str = Query("", description="Partial or full author name")
):
    df = get_books_df()  # Load only on first request
    if not title.strip() and not authors.strip():
        return df.head(5).to_dict(orient="records")

    filtered = df.copy()
    if title.strip():
        filtered = filtered[filtered["title"].str.contains(title, case=False, na=False)]
    if authors.strip():
        filtered = filtered[filtered["authors"].str.contains(authors, case=False, na=False)]
    
    return filtered.head(5).to_dict(orient="records")
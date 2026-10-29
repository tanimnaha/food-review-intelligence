"""Text Preprocessing and Dataset Splitting Module for Kolkata FoodLens.

This module provides reproducible text cleaning and stratified splitting
for the Kolkata restaurant intelligence ML pipeline.

Transformations:
1. Contraction expansion (e.g., "don't" -> "do not", "wasn't" -> "was not")
2. URL & Link removal (http/https/www)
3. HTML tag removal (<...>)
4. Emoji preservation (emojis carry strong positive/negative sentiment signals)
5. Lowercasing of alphabetical characters
6. Whitespace and non-standard whitespace normalization
7. Stratified Train (80%) / Validation (10%) / Test (10%) splitting with random seed 42
"""

from __future__ import annotations

import re
from typing import Tuple
import pandas as pd
from sklearn.model_selection import train_test_split

CONTRACTIONS = {
    "ain't": "am not",
    "aren't": "are not",
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'd've": "he would have",
    "he'll": "he will",
    "he'll've": "he will have",
    "he's": "he is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how is",
    "i'd": "I would",
    "i'd've": "I would have",
    "i'll": "I will",
    "i'll've": "I will have",
    "i'm": "I am",
    "i've": "I have",
    "isn't": "is not",
    "it'd": "it would",
    "it'd've": "it would have",
    "it'll": "it will",
    "it'll've": "it will have",
    "it's": "it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she would",
    "she'd've": "she would have",
    "she'll": "she will",
    "she'll've": "she will have",
    "she's": "she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so is",
    "that'd": "that would",
    "that'd've": "that would have",
    "that's": "that is",
    "there'd": "there would",
    "there'd've": "there would have",
    "there's": "there is",
    "they'd": "they would",
    "they'd've": "they would have",
    "they'll": "they will",
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what will",
    "what'll've": "what will have",
    "what're": "what are",
    "what's": "what is",
    "what've": "what have",
    "when's": "when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where is",
    "where've": "where have",
    "who'll": "who will",
    "who'll've": "who will have",
    "who's": "who is",
    "who've": "who have",
    "why's": "why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you would",
    "you'd've": "you would have",
    "you'll": "you will",
    "you'll've": "you will have",
    "you're": "you are",
    "you've": "you have"
}

CONTRACTION_RE = re.compile(
    r"(" + "|".join(re.escape(k) for k in CONTRACTIONS.keys()) + r")",
    flags=re.IGNORECASE,
)
URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
HTML_RE = re.compile(r"<[^>]+?>")
WHITESPACE_RE = re.compile(r"\s+")

def expand_contractions(text: str) -> str:
    def replace(match: re.Match) -> str:
        word = match.group(0).lower()
        expanded = CONTRACTIONS.get(word, match.group(0))
        if match.group(0)[0].isupper():
            return expanded.capitalize()
        return expanded
    return CONTRACTION_RE.sub(replace, text)

def clean_text(text: str, keep_emojis: bool = True) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    cleaned = URL_RE.sub(" ", text)
    cleaned = HTML_RE.sub(" ", cleaned)
    cleaned = expand_contractions(cleaned)
    if not keep_emojis:
        cleaned = re.sub(r'[^\w\s.,!?\'"\-]', ' ', cleaned)
    cleaned = cleaned.lower()
    cleaned = WHITESPACE_RE.sub(" ", cleaned).strip()
    return cleaned

def split_data(
    df: pd.DataFrame,
    target_col: str = "sentiment_label",
    train_size: float = 0.8,
    val_size: float = 0.1,
    test_size: float = 0.1,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    temp_size = val_size + test_size
    train_df, temp_df = train_test_split(
        df,
        test_size=temp_size,
        random_state=random_state,
        stratify=df[target_col],
    )
    val_ratio = val_size / temp_size
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1.0 - val_ratio),
        random_state=random_state,
        stratify=temp_df[target_col],
    )
    return (
        train_df.reset_index(drop=True),
        val_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )

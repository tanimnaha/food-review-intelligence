"""Training script for Syntax-Aware Deep ACOS Neural Network.

Trains SyntaxAwareACOSNet on data/acos_dataset/train.jsonl with validation on val.jsonl.
Saves model checkpoints to models/acos_model/syntax_acos_model.pt.
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.acos_models import SyntaxAwareACOSNet, Vocabulary, CATEGORIES, POLARITIES
from src.syntax_graph import SyntaxGraphEngine

DATA_DIR = ROOT / "data" / "acos_dataset"
MODELS_DIR = ROOT / "models" / "acos_model"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


class ACOSDataset(Dataset):
    def __init__(self, jsonl_path: Path, vocab: Vocabulary, syntax_engine: SyntaxGraphEngine, max_len: int = 40):
        self.samples = []
        self.vocab = vocab
        self.syntax_engine = syntax_engine
        self.max_len = max_len

        cat2idx = {c: i for i, c in enumerate(CATEGORIES)}
        pol2idx = {p: i for i, p in enumerate(POLARITIES)}

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                text = data["text"]
                doc = syntax_engine.parse(text)
                tokens = [t.text for t in doc][:max_len]
                pos_tags = [t.pos_ for t in doc][:max_len]
                dep_tags = [t.dep_ for t in doc][:max_len]

                graph = syntax_engine.build_dependency_graph(doc)
                adj = np.eye(len(tokens), dtype=np.float32)
                for i in range(len(tokens)):
                    for j in range(len(tokens)):
                        if graph.has_edge(i, j) or graph.has_edge(j, i):
                            adj[i, j] = 1.0

                first_q = data["quadruples"][0]
                cat_idx = cat2idx.get(first_q["category"], 0)
                pol_idx = pol2idx.get(first_q["sentiment"], 0)
                is_implicit = 1.0 if first_q.get("type", "explicit") == "implicit" else 0.0

                pad_len = max_len - len(tokens)
                word_ids = vocab.encode_words(tokens) + [0] * pad_len
                pos_ids = vocab.encode_pos(pos_tags) + [0] * pad_len
                dep_ids = vocab.encode_deps(dep_tags) + [0] * pad_len

                padded_adj = np.zeros((max_len, max_len), dtype=np.float32)
                padded_adj[:len(tokens), :len(tokens)] = adj

                self.samples.append({
                    "word_ids": torch.tensor(word_ids, dtype=torch.long),
                    "pos_ids": torch.tensor(pos_ids, dtype=torch.long),
                    "dep_ids": torch.tensor(dep_ids, dtype=torch.long),
                    "adj_matrix": torch.tensor(padded_adj, dtype=torch.float32),
                    "category": torch.tensor(cat_idx, dtype=torch.long),
                    "sentiment": torch.tensor(pol_idx, dtype=torch.long),
                    "is_implicit": torch.tensor([is_implicit], dtype=torch.float32)
                })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


def train_acos_model(epochs: int = 15, batch_size: int = 32, lr: float = 1e-3):
    print("Building vocabulary from training split...")
    train_path = DATA_DIR / "train.jsonl"
    val_path = DATA_DIR / "val.jsonl"

    all_texts = []
    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                all_texts.append(json.loads(line)["text"])

    vocab = Vocabulary(min_freq=1)
    vocab.build_vocab(all_texts)
    print(f"Vocabulary size: {len(vocab.word2idx)} unique tokens")

    vocab_path = MODELS_DIR / "vocab.json"
    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump({
            "word2idx": vocab.word2idx,
            "pos2idx": vocab.pos2idx,
            "dep2idx": vocab.dep2idx
        }, f, indent=2)

    syntax_engine = SyntaxGraphEngine()
    train_dataset = ACOSDataset(train_path, vocab, syntax_engine)
    val_dataset = ACOSDataset(val_path, vocab, syntax_engine)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using device: {device}")

    model = SyntaxAwareACOSNet(
        vocab_size=len(vocab.word2idx),
        word_dim=128,
        pos_dim=32,
        dep_dim=32,
        hidden_dim=128,
        num_categories=len(CATEGORIES),
        num_polarities=len(POLARITIES),
        dropout=0.3
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    cat_criterion = nn.CrossEntropyLoss()
    pol_criterion = nn.CrossEntropyLoss()
    imp_criterion = nn.BCEWithLogitsLoss()

    best_val_loss = float("inf")

    print("\nStarting Training SyntaxAwareACOSNet...")
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0

        for batch in train_loader:
            w = batch["word_ids"].to(device)
            p = batch["pos_ids"].to(device)
            d = batch["dep_ids"].to(device)
            adj = batch["adj_matrix"].to(device)
            cat_targets = batch["category"].to(device)
            pol_targets = batch["sentiment"].to(device)
            imp_targets = batch["is_implicit"].to(device)

            optimizer.zero_grad()
            outputs = model(w, p, d, adj)

            l_cat = cat_criterion(outputs["category_logits"], cat_targets)
            l_pol = pol_criterion(outputs["sentiment_logits"], pol_targets)
            l_imp = imp_criterion(outputs["implicit_logits"], imp_targets)

            loss = l_cat + l_pol + 0.5 * l_imp
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        model.eval()
        val_loss = 0.0
        correct_cat = 0
        correct_pol = 0
        total = 0

        with torch.no_grad():
            for batch in val_loader:
                w = batch["word_ids"].to(device)
                p = batch["pos_ids"].to(device)
                d = batch["dep_ids"].to(device)
                adj = batch["adj_matrix"].to(device)
                cat_targets = batch["category"].to(device)
                pol_targets = batch["sentiment"].to(device)
                imp_targets = batch["is_implicit"].to(device)

                outputs = model(w, p, d, adj)
                l_cat = cat_criterion(outputs["category_logits"], cat_targets)
                l_pol = pol_criterion(outputs["sentiment_logits"], pol_targets)
                l_imp = imp_criterion(outputs["implicit_logits"], imp_targets)
                loss = l_cat + l_pol + 0.5 * l_imp
                val_loss += loss.item()

                pred_cat = outputs["category_logits"].argmax(dim=-1)
                pred_pol = outputs["sentiment_logits"].argmax(dim=-1)

                correct_cat += (pred_cat == cat_targets).sum().item()
                correct_pol += (pred_pol == pol_targets).sum().item()
                total += cat_targets.size(0)

        avg_train = train_loss / len(train_loader)
        avg_val = val_loss / len(val_loader)
        cat_acc = correct_cat / total * 100
        pol_acc = correct_pol / total * 100

        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {avg_train:.4f} | Val Loss: {avg_val:.4f} | Cat Acc: {cat_acc:.1f}% | Pol Acc: {pol_acc:.1f}%")

        if avg_val < best_val_loss:
            best_val_loss = avg_val
            torch.save(model.state_dict(), MODELS_DIR / "syntax_acos_model.pt")

    print(f"\nModel training complete! Best checkpoint saved to {MODELS_DIR / 'syntax_acos_model.pt'}")


if __name__ == "__main__":
    train_acos_model()

"""
Prepares the combined training corpus for Phase 2.
Classes: GENUINE (0) | SCAM (1) | FAKE_NEWS (2)

Run once: python prepare_data.py
"""
import pandas as pd
import os
import requests
from datasets import load_dataset

os.makedirs("model", exist_ok=True)
OUTPUT_PATH = "model/combined_dataset.csv"

# ── 1. SMS Spam → GENUINE / SCAM ──────────────────────────────────────────────
print("Loading SMS Spam dataset...")
sms_ds = load_dataset("sms_spam", split="train", trust_remote_code=True)
sms_df = pd.DataFrame(sms_ds)
sms_df = sms_df.rename(columns={"sms": "text", "label": "raw_label"})
# label: 0 = ham (genuine), 1 = spam (scam)
sms_df["verdict"] = sms_df["raw_label"].map({0: "GENUINE", 1: "SCAM"})
sms_df = sms_df[["text", "verdict"]]
print(f"  SMS samples: {len(sms_df)} | {sms_df['verdict'].value_counts().to_dict()}")

# ── 2. LIAR Dataset → GENUINE / FAKE_NEWS ─────────────────────────────────────
# LIAR label mapping:
#   0: pants-fire  → FAKE_NEWS
#   1: false       → FAKE_NEWS
#   2: barely-true → skip (too ambiguous)
#   3: half-true   → skip
#   4: mostly-true → GENUINE
#   5: true        → GENUINE
print("Loading LIAR dataset...")
liar_ds = load_dataset("liar", trust_remote_code=True)
liar_train = pd.DataFrame(liar_ds["train"])
liar_val   = pd.DataFrame(liar_ds["validation"])
liar_test  = pd.DataFrame(liar_ds["test"])
liar_df = pd.concat([liar_train, liar_val, liar_test], ignore_index=True)

verdict_map = {0: "FAKE_NEWS", 1: "FAKE_NEWS", 4: "GENUINE", 5: "GENUINE"}
liar_df["verdict"] = liar_df["label"].map(verdict_map)
liar_df = liar_df.dropna(subset=["verdict"])          # drop ambiguous middle classes
liar_df = liar_df.rename(columns={"statement": "text"})
liar_df = liar_df[["text", "verdict"]]
print(f"  LIAR samples: {len(liar_df)} | {liar_df['verdict'].value_counts().to_dict()}")

# ── 3. Combine + balance ───────────────────────────────────────────────────────
combined = pd.concat([sms_df, liar_df], ignore_index=True)
combined = combined.dropna(subset=["text", "verdict"])
combined["text"] = combined["text"].str.strip()
combined = combined[combined["text"].str.len() > 5]

print(f"\nRaw combined: {len(combined)} samples")
print(combined["verdict"].value_counts())

# Undersample to balance classes — cap at smallest class × 1.5
min_class_count = combined["verdict"].value_counts().min()
cap = int(min_class_count * 1.5)
balanced = (
    combined.groupby("verdict", group_keys=False)
    .apply(lambda x: x.sample(min(len(x), cap), random_state=42))
    .reset_index(drop=True)
)
balanced = balanced.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nBalanced dataset: {len(balanced)} samples")
print(balanced["verdict"].value_counts())

balanced.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved to {OUTPUT_PATH}")
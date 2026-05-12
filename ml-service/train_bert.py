"""
Fine-tunes distilbert-base-uncased on the combined 3-class dataset.
Run on GPU (Colab or local CUDA): python train_bert.py
Output: model/bert_checkpoint/  (model + tokenizer files)
"""
import pandas as pd
import numpy as np
import torch
import os
from datasets import Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score

# ── Config ─────────────────────────────────────────────────────────────────────
DATA_PATH     = "model/combined_dataset.csv"
MODEL_NAME    = "distilbert-base-uncased"
SAVE_PATH     = "model/bert_checkpoint"
MAX_LEN       = 128      # enough for most SMS + short claims
BATCH_SIZE    = 32       # reduce to 16 if OOM on small GPU
EPOCHS        = 4
LEARNING_RATE = 2e-5
SEED          = 42

# Label scheme — MUST match FastAPI main.py
LABEL2ID = {"GENUINE": 0, "SCAM": 1, "FAKE_NEWS": 2}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ── Load data ──────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df["label"] = df["verdict"].map(LABEL2ID)
df = df.dropna(subset=["label"])
df["label"] = df["label"].astype(int)

train_df, test_df = train_test_split(df, test_size=0.15, random_state=SEED, stratify=df["label"])
train_df, val_df  = train_test_split(train_df, test_size=0.12, random_state=SEED, stratify=train_df["label"])

print(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")
print("Label distribution (train):", train_df["label"].value_counts().to_dict())

# ── Tokenizer ──────────────────────────────────────────────────────────────────
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

def tokenize(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LEN,
    )

def to_hf_dataset(df_):
    ds = Dataset.from_dict({"text": df_["text"].tolist(), "label": df_["label"].tolist()})
    return ds.map(tokenize, batched=True, batch_size=256).with_format("torch")

train_ds = to_hf_dataset(train_df)
val_ds   = to_hf_dataset(val_df)
test_ds  = to_hf_dataset(test_df)

# ── Model ──────────────────────────────────────────────────────────────────────
model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=3,
    id2label=ID2LABEL,
    label2id=LABEL2ID,
)
model.to(device)

# ── Metrics ───────────────────────────────────────────────────────────────────
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1_macro": f1_score(labels, preds, average="macro"),
    }

# ── Training args ──────────────────────────────────────────────────────────────
args = TrainingArguments(
    output_dir="model/bert_runs",
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE * 2,
    learning_rate=LEARNING_RATE,
    weight_decay=0.01,
    warmup_ratio=0.1,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1_macro",
    greater_is_better=True,
    logging_steps=50,
    seed=SEED,
    fp16=torch.cuda.is_available(),  # mixed precision on GPU only
    report_to="none",                # disable W&B
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
)

# ── Train ──────────────────────────────────────────────────────────────────────
print("\nStarting training...")
trainer.train()

# ── Evaluate on test set ───────────────────────────────────────────────────────
print("\n── Test Set Evaluation ──")
preds_output = trainer.predict(test_ds)
test_preds   = np.argmax(preds_output.predictions, axis=-1)
test_labels  = preds_output.label_ids

print(classification_report(
    test_labels, test_preds,
    target_names=list(LABEL2ID.keys())
))

# ── Save model + tokenizer ─────────────────────────────────────────────────────
os.makedirs(SAVE_PATH, exist_ok=True)
trainer.save_model(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)
print(f"\nModel saved to {SAVE_PATH}")
print("Copy this folder back to ml-service/model/bert_checkpoint/")
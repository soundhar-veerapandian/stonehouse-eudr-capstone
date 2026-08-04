# dds_evaluate_ml.py — score the extractor across all unseen documents
import re
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from dds_documents import make_documents
from dds_extractor import extract_fields, train_classifier, predict_commodity

# ---- NEW: extract the description itself from raw text (closing the loop) ----
def extract_description(text):
    for pattern in [r"Product:\s*(.+)",                       # template 1
                    r"Consignment from .*?:\s*(.+?)\s*—",     # template 2
                    r"- Description:\s*(.+?)\s*\(HS"]:        # template 3
        m = re.search(pattern, text)
        if m:
            return m.group(1).strip()
    return ""

docs = make_documents(200)
train_docs, test_docs = train_test_split(docs, test_size=0.30, random_state=42)
vectorizer, clf = train_classifier(train_docs)

# ---- score every field across the 60 unseen documents ----
scores = {"ref": 0, "hs": 0, "qty": 0, "desc": 0}
y_true, y_pred = [], []

for text, key in test_docs:
    f = extract_fields(text)
    desc = extract_description(text)
    if f["ref"] == key["ref"]:                      scores["ref"] += 1
    if f["hs"]  == key["hs"]:                       scores["hs"]  += 1
    if f["qty"] == key["qty"]:                      scores["qty"] += 1
    if desc     == key["description"]:              scores["desc"] += 1
    y_true.append(key["commodity"])
    y_pred.append(predict_commodity(vectorizer, clf, desc))

n = len(test_docs)
print(f"=== EXTRACTION ACCURACY ({n} unseen documents) ===")
for field, s in scores.items():
    print(f"  {field:<6} {s}/{n}  ({s/n*100:.0f}%)")

print(f"\n=== COMMODITY CLASSIFICATION ===")
print(f"  accuracy: {accuracy_score(y_true, y_pred)*100:.1f}%")
labels = sorted(set(y_true))
print(f"\n  Confusion matrix (rows=truth, cols=predicted) {labels}")
for lbl, row in zip(labels, confusion_matrix(y_true, y_pred, labels=labels)):
    print(f"  {lbl:<8} {row}")

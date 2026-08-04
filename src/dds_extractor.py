# dds_extractor.py — reads DDS documents: regex for structure, ML for meaning
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from dds_documents import make_documents

# ---------- STAGE 1: regex extraction (rigid-format fields) ----------
def extract_fields(text):
    out = {}
    m = re.search(r"DDS-\d\d-\d{5}", text)                 # the reference shape
    out["ref"] = m.group(0) if m else None
    m = re.search(r"HS\s*(?:code:)?\s*(\d{4})", text)      # 'HS 4401' or 'HS code: 4401'
    out["hs"] = m.group(1) if m else None
    m = re.search(r"(?:Quantity:|net weight|Net quantity:)\s*([\d,]+\.?\d*)\s*kg",
                  text, re.IGNORECASE)                     # three quantity phrasings
    out["qty"] = float(m.group(1).replace(",", "")) if m else None
    return out

# ---------- STAGE 2: the commodity classifier (free text -> label) ----------
def train_classifier(train_docs):
    texts  = [key["description"] for _, key in train_docs]   # e.g. "Firelogs 700g"
    labels = [key["commodity"]   for _, key in train_docs]   # e.g. "wood"
    vectorizer = TfidfVectorizer()                # words -> importance numbers
    X = vectorizer.fit_transform(texts)           # learn vocabulary, transform
    clf = MultinomialNB()                         # Naive Bayes
    clf.fit(X, labels)                            # learn word->commodity statistics
    return vectorizer, clf

def predict_commodity(vectorizer, clf, description):
    X = vectorizer.transform([description])       # same vocabulary, new text
    return clf.predict(X)[0]

# ---------- Put it together and demonstrate ----------
if __name__ == "__main__":
    docs = make_documents(200)

    # the sacred split: train on 70%, test ONLY on unseen 30%
    train_docs, test_docs = train_test_split(docs, test_size=0.30, random_state=42)
    print(f"Training on {len(train_docs)} documents, testing on {len(test_docs)} unseen\n")

    vectorizer, clf = train_classifier(train_docs)

    # demonstrate on one unseen document
    text, key = test_docs[0]
    fields = extract_fields(text)
    desc_guess = key["description"]          # (step 3 will extract this too)
    commodity_pred = predict_commodity(vectorizer, clf, desc_guess)

    print("=== UNSEEN DOCUMENT ===");  print(text)
    print("\n=== MACHINE'S READING ===")
    print("Extracted reference:", fields["ref"])
    print("Extracted HS code:  ", fields["hs"])
    print("Extracted quantity: ", fields["qty"])
    print("Predicted commodity:", commodity_pred)
    print("\n=== TRUTH (answer key) ===");  print(key)

# benchmark_models.py — all model evaluations, printed for review
import sqlite3, random, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing

MODELS = {"Multinomial Naive Bayes": MultinomialNB,
          "Logistic Regression":     LogisticRegression,
          "Linear SVM":              LinearSVC}
PARAMS = {"Multinomial Naive Bayes": {}, "Logistic Regression": {"max_iter":1000}, "Linear SVM": {}}

def evaluate(Xtr, ytr, Xte, yte, title, cv_data=None):
    print("\n" + "="*78); print(title)
    print(f"{'Model':<26}{'Accuracy':>10}{'Precision':>11}{'Recall':>9}{'F1':>8}{'5-fold CV':>16}")
    for name, M in MODELS.items():
        pipe = make_pipeline(TfidfVectorizer(), M(**PARAMS[name]))
        pipe.fit(Xtr, ytr); pred = pipe.predict(Xte)
        acc = accuracy_score(yte, pred)
        p, r, f, _ = precision_recall_fscore_support(yte, pred, average="macro", zero_division=0)
        cvtxt = ""
        if cv_data:
            cv = cross_val_score(make_pipeline(TfidfVectorizer(), M(**PARAMS[name])),
                                 cv_data[0], cv_data[1],
                                 cv=StratifiedKFold(5, shuffle=True, random_state=42))
            cvtxt = f"{cv.mean()*100:.1f}% ± {cv.std()*100:.1f}"
        print(f"{name:<26}{acc*100:>9.1f}%{p*100:>10.1f}%{r*100:>8.1f}%{f*100:>7.1f}%{cvtxt:>16}")
    # detail for the chosen model
    pipe = make_pipeline(TfidfVectorizer(), MultinomialNB()); pipe.fit(Xtr, ytr); pred = pipe.predict(Xte)
    print("\nNaive Bayes — per-class report:"); print(classification_report(yte, pred, zero_division=0))
    print("Confusion matrix [cattle, soy, wood]:")
    for lbl, row in zip(["cattle","soy","wood"], confusion_matrix(yte, pred, labels=["cattle","soy","wood"])):
        print(f"  {lbl:<8}{row}")

# ---------- EXPERIMENT 1: baseline vocabulary (from your database) ----------
conn = sqlite3.connect("dds_system.db")
rows = conn.execute("SELECT product_description, commodity FROM dds LIMIT 200").fetchall(); conn.close()
X = [r[0] for r in rows]; y = [r[1] for r in rows]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
evaluate(Xtr, ytr, Xte, yte, "EXPERIMENT 1 — BASELINE SYNTHETIC VOCABULARY", cv_data=(X, y))

# ---------- EXPERIMENT 2: unseen vocabulary (stress test) ----------
TRAIN = {"wood":["Toilet tissue rolls","Firelogs 700g","Luxury soft toilet tissue 9 roll",
                 "Comfort toilet tissue 4 roll","Firelighters 60s","Kitchen towel 2ply"],
         "cattle":["Beef pet food complete","Paws beef complete 2.5kg","Complete dog food beef"],
         "soy":["Complete dog food (soy)","Soybean oil blend","Dry dog food soya"]}
TEST  = {"wood":["Quilted bathroom paper 12pk","Kiln dried hardwood log net","Wood wool ignition blocks",
                 "Centrefeed blue roll 2ply","Compressed heat briquette","Household paper towel jumbo"],
         "cattle":["Meat and animal derivatives dinner 400g","Rich in prime steak adult chunks",
                   "Bovine protein canine meal","Premium cattle-derived pet dinner"],
         "soy":["Vegetable protein canine blend","Soya meal feed grade","Plant protein dog kibble",
                "Refined vegetable oil 20 litre"]}
Xtr2 = [d for c, ds in TRAIN.items() for d in ds for _ in range(12)]
ytr2 = [c for c, ds in TRAIN.items() for d in ds for _ in range(12)]
Xte2 = [d for c, ds in TEST.items() for d in ds]
yte2 = [c for c, ds in TEST.items() for d in ds]
evaluate(Xtr2, ytr2, Xte2, yte2, "EXPERIMENT 2 — UNSEEN VOCABULARY (STRESS TEST)")
print("\nPer-item predictions:")
pipe = make_pipeline(TfidfVectorizer(), MultinomialNB()); pipe.fit(Xtr2, ytr2)
for d, t in zip(Xte2, yte2):
    pr = pipe.predict([d])[0]
    print(f"  {'OK  ' if pr==t else 'MISS'} {d[:42]:<43} true={t:<7} pred={pr}")

# ---------- EXPERIMENT 3: forecast model comparison ----------
conn = sqlite3.connect("dds_system.db")
df = pd.read_sql("SELECT submission_date FROM dds", conn); conn.close()
df["submission_date"] = pd.to_datetime(df["submission_date"])
s = df.set_index("submission_date").resample("ME").size()
H = 6; train, test = s[:-H], s[-H:]
x = np.arange(len(train))
mae  = lambda a, b: float(np.mean(np.abs(np.array(a)-np.array(b))))
rmse = lambda a, b: float(np.sqrt(np.mean((np.array(a)-np.array(b))**2)))
sl, ic = np.polyfit(x, train.values, 1)
res = {
 "Naive (last value)":              np.repeat(train.values[-1], H),
 "Mean of last 3 months":           np.repeat(train.values[-3:].mean(), H),
 "OLS linear trend (project)":      sl*np.arange(len(train), len(train)+H)+ic,
 "Simple exponential smoothing":    SimpleExpSmoothing(train.values.astype(float)).fit().forecast(H),
 "Holt's linear trend":             ExponentialSmoothing(train.values.astype(float), trend="add").fit().forecast(H),
 "Holt-Winters (additive, m=12)":   ExponentialSmoothing(train.values.astype(float), trend="add",
                                      seasonal="add", seasonal_periods=12).fit().forecast(H)}
print("\n" + "="*78); print("EXPERIMENT 3 — FORECAST COMPARISON (6-month holdout)")
print(f"{'Model':<34}{'MAE':>9}{'RMSE':>9}")
for k, v in sorted(res.items(), key=lambda kv: mae(test, kv[1])):
    print(f"{k:<34}{mae(test,v):>9.2f}{rmse(test,v):>9.2f}")

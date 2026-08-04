# dds_documents.py — turns database records into realistic DDS text documents
import sqlite3
import random

random.seed(7)   # reproducible document variations

# Three phrasing templates — same information, different wording/layout
TEMPLATES = [
 ("DUE DILIGENCE STATEMENT\nReference: {ref}\nOperator: {op}, {addr} (EORI: {eori})\n"
  "Supplier: {sup}\nProduct: {desc}\nHS code: {hs}\nQuantity: {qty} kg\n"
  "Country of production: {country}\nGeolocation: {lat}, {lon}\n"
  "Production date: {pdate}\nPrior DDS: {prior}\nSubmitted: {sdate}"),
 ("DDS {ref} | submitted {sdate}\n{op} ({eori}), {addr}\n"
  "Consignment from {sup}: {desc} — net weight {qty}kg, HS {hs}.\n"
  "Produced in {country} on {pdate} at coordinates {lat} {lon}.\n"
  "Upstream reference: {prior}"),
 ("Statement of Due Diligence pursuant to Regulation (EU) 2023/1115\n"
  "Ref no. {ref}\nThe operator {op} confirms due diligence for the following consignment:\n"
  "- Description: {desc} (HS {hs})\n- Supplier: {sup}\n- Net quantity: {qty} kg\n"
  "- Origin: {country}, plot at {lat}, {lon}\n- Produced: {pdate}\n"
  "- Prior statement: {prior}\nFiled {sdate}"),
]

def make_documents(n=200, db="dds_system.db"):
    conn = sqlite3.connect(db)
    rows = conn.execute("""SELECT dds_reference, operator_name, operator_address,
        operator_eori, supplier_name, commodity, hs_code, product_description,
        quantity_kg, country_of_production, geolocation_lat, geolocation_lon,
        production_date, prior_dds_reference, submission_date
        FROM dds ORDER BY dds_reference LIMIT ?""", (n,)).fetchall()
    conn.close()

    documents = []   # list of (document_text, answer_key) pairs
    for r in rows:
        (ref, op, addr, eori, sup, commodity, hs, desc,
         qty, country, lat, lon, pdate, prior, sdate) = r
        text = random.choice(TEMPLATES).format(
            ref=ref, op=op, addr=addr, eori=eori, sup=sup, desc=desc, hs=hs,
            qty=qty, country=country,
            lat="N/A" if lat is None else round(lat, 3),
            lon="N/A" if lon is None else round(lon, 3),
            pdate=pdate, prior=prior if prior else "none", sdate=sdate)
        answer_key = {"ref": ref, "hs": hs, "qty": qty, "commodity": commodity,
                      "description": desc}
        documents.append((text, answer_key))
    return documents

if __name__ == "__main__":
    docs = make_documents(200)
    print("Generated", len(docs), "documents\n")
    print("=== SAMPLE DOCUMENT ===")
    print(docs[0][0])
    print("\n=== ITS ANSWER KEY ===")
    print(docs[0][1])

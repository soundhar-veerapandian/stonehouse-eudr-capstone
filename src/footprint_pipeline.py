"""
Stonehouse EUDR Capstone - Workstream A
Packaging carbon-footprint pipeline (real 2024 data)
Product packaging materials -> NACE/EXIOBASE sector -> Ireland GHG intensity -> tCO2e
Also flags EUDR-relevant (wood-derived) material exposure.
Author: <your name>  |  Data: Green Streets packaging specs + EXIOBASE hybrid v3.8 GHG intensities
"""
import pand
as as pd, re, warnings
warnings.filterwarnings("ignore")
UP = "/mnt/user-data/uploads/"
clean = lambda cols: [re.sub(r"\s+", " ", str(c)).strip() for c in cols]

# ---------- 1. Load packaging specs (one row per product x packaging component) ----------
GS = UP + "Green_Streets_-_STO001_Packaging-Specs_2024_-_BM_Analysis_v1_4.xlsx"
pkg = pd.read_excel(GS, "HSWHProdsMerged"); pkg.columns = clean(pkg.columns)
pkg = pkg[pkg["Base Material"].notna()].copy()
pkg["pc"] = pd.to_numeric(pkg["Product Code"], errors="coerce")
pkg["comp_g"] = pd.to_numeric(pkg["Weight"], errors="coerce") * pd.to_numeric(pkg["Number of Packaging Type"], errors="coerce").fillna(1)

# ---------- 2. Load 2024 volumes; true units sold = cases x case-qty ----------
vol = pd.read_excel(GS, "HSWH2024VolMrg"); vol.columns = clean(vol.columns)
vol["pc"] = pd.to_numeric(vol["Product Code"], errors="coerce")
vol = vol[vol["pc"].notna()].copy()
vol["units_2024"] = pd.to_numeric(vol["Total Volume 2024"], errors="coerce") * pd.to_numeric(vol["Case Qty"], errors="coerce")
vol["brand"] = vol["Description"].astype(str).str.upper().apply(
    lambda d: "White Hat" if "WHITE HAT" in d else ("Homestead" if "HOMESTEAD" in d else "Other own-brand"))
volm = vol.groupby("pc").agg(units_2024=("units_2024","sum"),
                             brand=("brand","first"),
                             vol_desc=("Description","first")).reset_index()

# ---------- 3. Material -> EXIOBASE production sector (NACE Rev.2) ----------
# Mapping is documented & editable - this is the "Research: NACE code" deliverable.
MAT2SECTOR = {  # specific material -> exact EXIOBASE 'Description'
 "Cardboard":"Production of paper and paper products","Paper":"Production of paper and paper products",
 "Composite Paper":"Production of paper and paper products",
 "Wood":"Production of wood and straw (except furniture)",
 "LDPE - Low-Density PolyEthylene":"Production of plastics, basic","HDPE - High-Density PolyEthylene":"Production of plastics, basic",
 "PET - PolyEthylene Terephthalate":"Production of plastics, basic","PP - PolyPropylene":"Production of plastics, basic",
 "Composite Plastic":"Production of plastics, basic",
 "Steel":"Production of basic iron and steel and of ferro-alloys and first products thereof",
 "Composite Metal":"Production of basic iron and steel and of ferro-alloys and first products thereof"}
EUDR_BASE = {"Wood","Paper/Card"}   # wood-derived -> EUDR 'wood' commodity exposure

# ---------- 4. EXIOBASE Ireland (IE) GHG intensities (tCO2e per tonne) ----------
ghg = pd.read_excel(UP+"EXIOBASE-hybrid_v3_8-beta1_GHG_intensities.xlsx","GHG production - hybrid",header=1)
ghg.columns = clean(ghg.columns)
desc_c=[c for c in ghg.columns if "escription" in c][0]; nace2_c=[c for c in ghg.columns if "rev2" in c.lower()][0]
unit_i=list(ghg.columns).index("Unit")
ctry_cols=list(ghg.columns)[unit_i+1:]          # all country/region factor columns
for c in ctry_cols: ghg[c]=pd.to_numeric(ghg[c],errors="coerce")
ghg["GLOBAL"]=ghg[ctry_cols].mean(axis=1,skipna=True)   # global-average proxy
fac = ghg.dropna(subset=[desc_c]).drop_duplicates(desc_c).set_index(desc_c)
def intensity(sector):                          # IE if Ireland produces it, else global avg
    ie=fac.loc[sector,"IE"]
    return (float(ie),"IE") if pd.notna(ie) else (float(fac.loc[sector,"GLOBAL"]),"Global avg")
def nace(sector): return str(fac.loc[sector,nace2_c])

pkg["sector"]=pkg["Specific Material"].map(MAT2SECTOR)
pkg=pkg[pkg["sector"].notna()].copy()
pkg["nace_rev2"]=pkg["sector"].map(nace)
pkg["IE_tCO2e_per_t"]=pkg["sector"].map(lambda s:intensity(s)[0])
pkg["Factor source"]=pkg["sector"].map(lambda s:intensity(s)[1])
pkg["EUDR_relevant"]=pkg["Base Material"].isin(EUDR_BASE)

# ---------- 5. Join volumes & compute footprint ----------
df=pkg.merge(volm,on="pc",how="inner")
df["pkg_tonnes_2024"]=df["comp_g"]*df["units_2024"]/1e6
df["tCO2e_2024"]=df["pkg_tonnes_2024"]*df["IE_tCO2e_per_t"]

detail=df[["pc","Product Name","brand","Department","Supplier Name","Base Material","Specific Material",
           "Packaging Level","nace_rev2","sector","IE_tCO2e_per_t","Factor source","comp_g","units_2024",
           "pkg_tonnes_2024","tCO2e_2024","EUDR_relevant"]].rename(columns={
           "pc":"Product Code","Supplier Name":"Supplier","comp_g":"Pkg g/unit","units_2024":"Units 2024"})

# ---------- 6. Summaries ----------
by_mat=df.groupby("Base Material").agg(tonnes=("pkg_tonnes_2024","sum"),tCO2e=("tCO2e_2024","sum")).reset_index().sort_values("tCO2e",ascending=False)
by_eudr=df.groupby(df["EUDR_relevant"].map({True:"EUDR-relevant (wood-derived)",False:"Non-EUDR"})).agg(tonnes=("pkg_tonnes_2024","sum"),tCO2e=("tCO2e_2024","sum")).reset_index().rename(columns={"EUDR_relevant":"Category"})
by_brand=df.groupby("brand").agg(tCO2e=("tCO2e_2024","sum")).reset_index().sort_values("tCO2e",ascending=False)
top=df.groupby(["pc","Product Name","brand"]).agg(tCO2e=("tCO2e_2024","sum")).reset_index().sort_values("tCO2e",ascending=False).head(15)

tot=df["tCO2e_2024"].sum(); eud=df.loc[df.EUDR_relevant,"tCO2e_2024"].sum()
print(f"Products covered: {df['pc'].nunique()} | components: {len(df)}")
print(f"TOTAL packaging footprint 2024: {tot:,.0f} tCO2e")
print(f"EUDR-relevant (wood-derived) share: {eud:,.0f} tCO2e = {eud/tot*100:.1f}%")
print("\nBy material:\n", by_mat.to_string(index=False))
print("\nIE intensities used (tCO2e/t):")
for s in sorted(set(df.sector)):
    v,src=intensity(s); print(f"  {nace(s):>6}  {s[:50]:<50} {v:6.3f}  [{src}]")

for o in [(detail,"detail"),(by_mat,"by_mat"),(by_eudr,"by_eudr"),(by_brand,"by_brand"),(top,"top")]:
    o[0].to_pickle(f"/home/claude/proj/{o[1]}.pkl")

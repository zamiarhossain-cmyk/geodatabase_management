import arcpy
import os
from collections import defaultdict, Counter

#INPUT GDBs
digi_gdb   = r"D:\GIS_work\Python_works\BAR_BAR_Wazirpur_Digi.gdb"
rawgeo_gdb = r"D:\GIS_work\BAR_BAR_Wazirpur_RawGeo.gdb"


def list_all_featureclasses(gdb):
    arcpy.env.workspace = gdb
    fcs = []
    fcs.extend(arcpy.ListFeatureClasses() or [])
    for fds in arcpy.ListDatasets(feature_type="feature") or []:
        fcs.extend(
            [os.path.join(fds, fc)
             for fc in arcpy.ListFeatureClasses(feature_dataset=fds) or []]
        )
    return fcs


def parse_name(fc_name):
    """
    Returns (JL, SHEET, TYPE) or None
    """
    parts = fc_name.split("_")
    if len(parts) < 7:
        return None

    jl = parts[3]
    sheet = parts[4]
    ltype = parts[-1]   # LD / LRG etc.
    return jl, sheet, ltype


def analyze_gdb(gdb, valid_types):
    fcs = list_all_featureclasses(gdb)

    type_counter = Counter()
    sheet_map = defaultdict(list)

    for fc in fcs:
        name = os.path.basename(fc)
        parsed = parse_name(name)
        if not parsed:
            continue

        jl, sheet, ltype = parsed
        if ltype in valid_types:
            type_counter[ltype] += 1
            sheet_map[(jl, sheet)].append(name)

    return type_counter, sheet_map


#RUN ANALYSIS
digi_types   = {"LD", "MD", "SD", "PD", "ND"}
rawgeo_types = {"LRG", "MRG", "SRG", "PRG", "NRG"}

digi_count, digi_sheets     = analyze_gdb(digi_gdb, digi_types)
rawgeo_count, rawgeo_sheets = analyze_gdb(rawgeo_gdb, rawgeo_types)

#COUNTS
print("\nDIGI LAYER COUNTS")
for t in sorted(digi_types):
    print(f"{t}: {digi_count[t]}")

print("\nRAWGEO LAYER COUNTS")
for t in sorted(rawgeo_types):
    print(f"{t}: {rawgeo_count[t]}")

#SHEET VALIDATION
print("\nSHEET VALIDATION (DIGI to RAWGEO)")

all_keys = set(digi_sheets.keys()) | set(rawgeo_sheets.keys())

for (jl, sheet) in sorted(all_keys):
    digi_layers = digi_sheets.get((jl, sheet), [])
    raw_layers  = rawgeo_sheets.get((jl, sheet), [])

    if not digi_layers:
        print(f"MISSING in DIGI → JL {jl}, Sheet {sheet}")

    if not raw_layers:
        print(f"MISSING in RAWGEO → JL {jl}, Sheet {sheet}")

    if len(digi_layers) != len(set(digi_layers)):
        print(f"DUPLICATE in DIGI → JL {jl}, Sheet {sheet}")

    if len(raw_layers) != len(set(raw_layers)):
        print(f"DUPLICATE in RAWGEO → JL {jl}, Sheet {sheet}")

print("\nCHECK COMPLETE")
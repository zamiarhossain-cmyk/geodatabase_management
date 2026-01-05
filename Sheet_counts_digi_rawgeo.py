import arcpy
import os
from collections import defaultdict, Counter

#INPUT GDBs
digi_gdb   = r"D:\GIS_work\Python_works\BAR_BAR_Wazirpur_Digi.gdb" #Location of the digitized geodatabase
rawgeo_gdb = r"D:\GIS_work\BAR_BAR_Wazirpur_RawGeo.gdb" #Location of the Rawgeo geodatabase


def list_all_featureclasses(gdb):
    arcpy.env.workspace = gdb
    fcs = []

    fcs.extend(arcpy.ListFeatureClasses() or [])

    for fds in arcpy.ListDatasets(feature_type="feature") or []:
        for fc in arcpy.ListFeatureClasses(feature_dataset=fds) or []:
            fcs.append(os.path.join(fds, fc))

    return fcs


def parse_name(fc_name):
    """
    Expected:
    BAR_BAK_WAZ_053_001_RS_LD
    Returns (JL, SHEET, TYPE)
    """
    parts = fc_name.split("_")
    if len(parts) < 7:
        return None

    jl    = parts[3]
    sheet = parts[4]
    ltype = parts[-1]
    return jl, sheet, ltype


def analyze_gdb(gdb, valid_types):
    fcs = list_all_featureclasses(gdb)

    type_counter = Counter()
    sheet_types  = defaultdict(list)

    for fc in fcs:
        name = os.path.basename(fc)
        parsed = parse_name(name)
        if not parsed:
            continue

        jl, sheet, ltype = parsed
        if ltype in valid_types:
            type_counter[ltype] += 1
            sheet_types[(jl, sheet)].append(ltype)

    return type_counter, sheet_types


#TYPE MAPPING
type_map = {
    "LD": "LRG",
    "MD": "MRG",
    "SD": "SRG",
    "PD": "PRG",
    "ND": "NRG"
}
reverse_map = {v: k for k, v in type_map.items()}

digi_types   = set(type_map.keys())
rawgeo_types = set(type_map.values())

#RUN ANALYSIS
digi_count, digi_sheets     = analyze_gdb(digi_gdb, digi_types)
rawgeo_count, rawgeo_sheets = analyze_gdb(rawgeo_gdb, rawgeo_types)

#COUNT REPORT
print("\nLAYER TOTALS")
for d_type in sorted(digi_types):
    r_type = type_map[d_type]
    print(f"{d_type}: {digi_count[d_type]} | {r_type}: {rawgeo_count[r_type]}")

#CROSS-CHECK
print("\nDIGI to RAWGEO SHEET VALIDATION")

all_keys = set(digi_sheets.keys()) | set(rawgeo_sheets.keys())

for jl, sheet in sorted(all_keys):
    digi_found = digi_sheets.get((jl, sheet), [])
    raw_found  = rawgeo_sheets.get((jl, sheet), [])

    # DIGI to RAWGEO missing
    for d_type in digi_found:
        expected_r = type_map[d_type]
        if expected_r not in raw_found:
            print(f"MISMATCH: JL {jl} Sheet {sheet} has {d_type} but MISSING {expected_r}")

    # RAWGEO to DIGI missing
    for r_type in raw_found:
        expected_d = reverse_map[r_type]
        if expected_d not in digi_found:
            print(f"MISMATCH: JL {jl} Sheet {sheet} has {r_type} but MISSING {expected_d}")

    # Duplicate detection
    if len(digi_found) != len(set(digi_found)):
        print(f"DUPLICATE in DIGI to JL {jl}, Sheet {sheet}")

    if len(raw_found) != len(set(raw_found)):
        print(f"DUPLICATE in RAWGEO to JL {jl}, Sheet {sheet}")

print("\nCHECK COMPLETE")


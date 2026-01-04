import arcpy
import os
from collections import defaultdict

input_gdb = r"D:\GIS_work\BAR_BAR_Wazirpur_Geo.gdb"
arcpy.env.workspace = input_gdb

def list_all_featureclasses(gdb):
    all_fcs = []
    all_fcs.extend(arcpy.ListFeatureClasses() or [])
    for fds in arcpy.ListDatasets(feature_type='feature') or []:
        fcs = arcpy.ListFeatureClasses(feature_dataset=fds) or []
        all_fcs.extend([os.path.join(fds, fc) for fc in fcs])
    return all_fcs

all_fcs = list_all_featureclasses(input_gdb)

if not all_fcs:
    print("No feature classes found.")
    raise SystemExit

jl_dict = defaultdict(list)

for fc in all_fcs:
    name = os.path.basename(fc)
    parts = name.split("_")

    if len(parts) < 7:
        continue

    jl = parts[3]
    prefix = parts[5]      
    family_stage = parts[-1]
    family = family_stage[0]   
    stage = family_stage[1:]

    jl_dict[jl].append({
        "name": name,
        "prefix": prefix,
        "family": family,
        "stage": stage
    })

# ------------------ DETECT REAL OVERLAPS ------------------
conflict_found = False

for jl, layers in jl_dict.items():
    checker = defaultdict(set)

    for lyr in layers:
        key = (lyr["family"], lyr["stage"])
        checker[key].add(lyr["prefix"])

    for (family, stage), prefixes in checker.items():
        if len(prefixes) > 1:
            conflict_found = True
            print(f"\n CONFLICT FOUND")
            print(f"JL: {jl}")
            print(f"Layer Family: {family}")
            print(f"Stage: {stage}")
            print("Conflicting layers:")
            for lyr in layers:
                if lyr["family"] == family and lyr["stage"] == stage:
                    print(f"  {lyr['name']}")

if not conflict_found:
    print("No invalid overlaps found.")
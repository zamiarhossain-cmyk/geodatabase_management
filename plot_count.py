import arcpy
import os

#PATHS
geo_gdb    = r"D:\GIS_work\BAR_BAR_Wazirpur_Geo.gdb"
merged_gdb = r"D:\GIS_work\BAR_BAR_Wazirpur_MergedMG.gdb"
merged_fc_name = "BAR_BAR_Wazirpur_MG_MERGED"

#COUNT MG IN GEO GDB
def count_geo_mg_features(gdb):
    arcpy.env.workspace = gdb
    total = 0
    details = {}

    # Root
    for fc in arcpy.ListFeatureClasses() or []:
        if fc.endswith("_MG"):
            cnt = int(arcpy.management.GetCount(fc)[0])
            details[fc] = cnt
            total += cnt

    # Feature datasets
    for fds in arcpy.ListDatasets(feature_type="feature") or []:
        for fc in arcpy.ListFeatureClasses(feature_dataset=fds) or []:
            if fc.endswith("_MG"):
                fc_path = os.path.join(fds, fc)
                cnt = int(arcpy.management.GetCount(fc_path)[0])
                details[fc_path] = cnt
                total += cnt

    return total, details

#COUNT MERGED MG
merged_fc = os.path.join(merged_gdb, merged_fc_name)

if not arcpy.Exists(merged_fc):
    raise RuntimeError(f"Merged MG feature class NOT FOUND:\n{merged_fc}")

merged_count = int(arcpy.management.GetCount(merged_fc)[0])

#RUN COMPARISON
geo_total, geo_details = count_geo_mg_features(geo_gdb)

print(f"Geo GDB MG total     : {geo_total}")
print(f"Merged MG feature cnt: {merged_count}")
import arcpy
import os

input_gdb = r"D:\GIS_work\BAR_BAR_Wazirpur_Geo.gdb"
arcpy.env.workspace = input_gdb
output_folder = r"D:\GIS_work"
output_gdb_name = "BAR_BAR_Wazirpur_MG.gdb"
output_gdb = os.path.join(output_folder, output_gdb_name)

# Create output GDB if it doesn't exist
if not arcpy.Exists(output_gdb):
    arcpy.management.CreateFileGDB(output_folder, output_gdb_name)
    print(f"[CREATED] {output_gdb}")


def list_all_featureclasses(gdb):
    all_fcs = []
    all_fcs.extend(arcpy.ListFeatureClasses() or [])

    for fds in arcpy.ListDatasets(feature_type='feature') or []:
        fds_fcs = arcpy.ListFeatureClasses(feature_dataset=fds) or []
        all_fcs.extend([os.path.join(fds, fc) for fc in fds_fcs])

    return all_fcs

all_fcs = list_all_featureclasses(input_gdb)
print(f"[INFO] Total feature classes found: {len(all_fcs)}")

mg_layers = [fc for fc in all_fcs if fc.endswith("_MG")]

if not mg_layers:
    print("No MG layers found to copy.")
else:
    for fc in mg_layers:
        if os.path.dirname(fc) != input_gdb:
            fds_name = os.path.basename(os.path.dirname(fc))
            out_fds = os.path.join(output_gdb, fds_name)
            if not arcpy.Exists(out_fds):
                arcpy.management.CreateFeatureDataset(output_gdb, fds_name)
            out_fc = os.path.join(out_fds, os.path.basename(fc))
        else:
            out_fc = os.path.join(output_gdb, os.path.basename(fc))

        arcpy.management.CopyFeatures(fc, out_fc)
        print(f"[COPIED] {fc} to {out_fc}")

print("All MG layers copied.")
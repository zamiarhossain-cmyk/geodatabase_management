import arcpy
import os

#Geodatabase paths
input_gdb = r"D:\GIS_work\Python_works\BAR_BAR_Wazirpur_RawGeo.gdb"
base_dir = os.path.dirname(input_gdb)

#Feature class groups
digitized_groups = ("_LD", "_MD", "_SD", "_PD", "_ND")
rawgeo_groups = ("_LRG", "_MRG", "_SRG", "_PRG", "_NRG")
geo_groups = ("_LG", "_MG", "_SG", "_PG", "_NG")

digitized_to_rawgeo = {
    "_LD": "_LRG",
    "_MD": "_MRG",
    "_SD": "_SRG",
    "_PD": "_PRG",
    "_ND": "_NRG"
}

rawgeo_to_geo = {
    "_LRG": "_LG",
    "_MRG": "_MG",
    "_SRG": "_SG",
    "_PRG": "_PG",
    "_NRG": "_NG"
}


def list_all_featureclasses(gdb):
    arcpy.env.workspace = gdb
    all_fcs = []


    all_fcs.extend(arcpy.ListFeatureClasses() or [])


    for fds in arcpy.ListDatasets(feature_type='feature') or []:
        arcpy.env.workspace = os.path.join(gdb, fds)
        all_fcs.extend([os.path.join(fds, fc) for fc in arcpy.ListFeatureClasses() or []])

    return all_fcs

all_fcs = list_all_featureclasses(input_gdb)

if not all_fcs:
    print("[INFO] No feature classes found. Exiting.")
else:
    #Detection
    has_digitized = any(fc.endswith(digitized_groups) for fc in all_fcs)
    has_rawgeo    = any(fc.endswith(rawgeo_groups) for fc in all_fcs)
    has_geo       = any(fc.endswith(geo_groups) for fc in all_fcs)

    if has_digitized:
        stage_to_process = "Digitized"
        out_gdb_name = "BAR_BAR_Wazirpur_RawGeo.gdb"
        stage_map = digitized_to_rawgeo
    elif has_rawgeo:
        stage_to_process = "RawGeo"
        out_gdb_name = "BAR_BAR_Wazirpur_Geo.gdb"
        stage_map = rawgeo_to_geo
    else:
        stage_to_process = None
        print("[INFO] Nothing to process: all layers are already GEO or invalid.")

    if stage_to_process:
        out_gdb = os.path.join(base_dir, out_gdb_name)
        if not arcpy.Exists(out_gdb):
            arcpy.management.CreateFileGDB(base_dir, os.path.basename(out_gdb))
            print(f"[CREATED] {out_gdb}")


        for fc in all_fcs:
            renamed = False
            for old_suf, new_suf in stage_map.items():
                if fc.endswith(old_suf):
                    # Handle feature datasets: preserve dataset path in output
                    if os.path.dirname(fc) != input_gdb:
                        fds_name = os.path.basename(os.path.dirname(fc))
                        out_fds = os.path.join(out_gdb, fds_name)
                        if not arcpy.Exists(out_fds):
                            arcpy.management.CreateFeatureDataset(out_gdb, fds_name)
                        out_fc = os.path.join(out_fds, os.path.basename(fc)[:-len(old_suf)] + new_suf)
                    else:
                        out_fc = os.path.join(out_gdb, os.path.basename(fc)[:-len(old_suf)] + new_suf)

                    arcpy.management.CopyFeatures(fc, out_fc)
                    print(f"[{stage_to_process}] {fc} to {out_fc}")
                    renamed = True
                    break

            if not renamed:
                if fc.endswith(geo_suffixes):
                    print(f"[SKIP] Already GEO: {fc}")
                else:
                    print(f"[WARNING] Unknown/invalid groups: {fc}")
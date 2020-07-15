import os
import arcpy
from arcpy.da import UpdateCursor as uc
import pandas
import fclist
from random import randrange as rr

# USER CONFIGURATION
# data_file in OLD configuration - expects correct sheet name w/ only 3 fields.
# fields in OLD configuration -  are jurisdiction, date, & percent.
# New Configuration has 25 fields date, Allegany, Anne Arundel, ...
# All values after the header are percentages.
# table_config determines which function runs (populate_fc or new_populate_fc)
# Note: there is also a it_worked var that calls "create_fcs_from_template()"
# that may need to be uncommented (near the end of the script).
table_config = "new_config" # "old_config"
data_file = r"C:\Users\john.churchill\Documents\PROJECTS\Recovery_Dashboard\Daily_Positivity_Data_by_Jurisdiction.xlsx" 
sheet_name = "pivot" # "old"
fd_name = "new_data3"
out_ws = r"C:\Users\john.churchill\Documents\PROJECTS\Recovery_Dashboard\MasterCaseTracker_updated_7_13_2020.gdb"
# template_fc = r"C:\Users\john.churchill\Documents\PROJECTS\Recovery_Dashboard\TS_seven_day_v2.gdb\template_county_bnd_gen_DoIT"
template_fc = r"C:\Users\john.churchill\Documents\PROJECTS\Recovery_Dashboard\dummy_data.gdb\template_fc3"
merge_these = False # set to True to conduct the merge
merged_output_name = "\\time_series_3_16_to_7_13" # If merge_these what are
dummy_data = False # Set to True to Generate DEMO DATA
# we going to call the output (output will be created in the out_ws)
# USER CONFIGURATION

# Test First to see if fd exists
if not arcpy.Exists(os.path.join(out_ws, fd_name)):
    # Creating a spatial reference object
    desc = arcpy.Describe(template_fc)
    sr = desc.spatialReference
    arcpy.CreateFeatureDataset_management(out_ws, fd_name, sr)

def create_fc(fc):
    #arcpy.CreateFeatureClass_management(fc)
    arcpy.CopyFeatures_management(template_fc, os.path.join(out_ws, fd_name, fc))
    return None

def new_populate_fc(fc, date_df):
    # New Version of populate_fc function to accommodate the unpivoted table
    # uses a subset pandas dataframe to populate a feature class
    # with Cases and Date Values by County and Date
    this_fc = os.path.join(out_ws, fd_name, fc)
    field_names = ["County", "Cases", "Date"]
    with uc(this_fc, field_names) as upd_cursor:
        for row in upd_cursor:
            for _index, dfrow in date_df.iterrows():
                row[1] = dfrow[row[0]]
                row[2] = dfrow['date']
                upd_cursor.updateRow(row)
    return None

def populate_fc(fc, date_df):
    # Old Version
    # uses a subset pandas dataframe to populate a feature class
    # with Cases and Date values by County and Date
    this_fc = os.path.join(out_ws, fd_name, fc)
    field_names = ["County", "Cases", "Date"]
    with uc(this_fc, field_names) as upd_cursor:
        for row in upd_cursor:
            for _index, dfrow in date_df.iterrows():
                if row[0] == dfrow['jurisdiction']:
                    if dummy_data:
                        row[1] = get_dummy_data(dfrow['percent'])
                    else:
                        row[1] = dfrow['percent']
                    row[2] = dfrow['date']
                    upd_cursor.updateRow(row)
    return None

def create_fcs_from_template():
    # uses a template feature class and a list of and 
    # feature class names to create multiple copies of the template.
    for fc_name in fclist.fc_names:
        create_fc(fc_name)
    return True

def get_dummy_data(tru_value):
    rand_value = rr(0, 45, 2) / 100
    dummy_value = tru_value * rand_value
    return dummy_value

def create_df(df, datestring):
    # can send the master_df and a single date (type=string)
    # returns the subset dataframe to use with the update cursor (populate_fc function)
    date_df = df['date']==datestring
    date_df_only = df[date_df]
    return date_df_only

def merge_all_fcs(list_of_fcs, out_fc):
    rslt = arcpy.Merge_management(list_of_fcs, out_fc)
    fcnum = str(len(list_of_fcs))
    if rslt:
        print()
        print(fcnum + " Feature Classes were Merged into " + out_fc)
    return None

master_df = pandas.read_excel(open(data_file, 'rb'), sheet_name = sheet_name)

def read_df_by_date(datestring):
    # Uses global <master_df> to create subset df and print values.
    # This will only work if table_config == "old_config"
    df = master_df['date']==datestring
    df_only = master_df[df]
    for _index, row in df_only.iterrows():
        if table_config == "old_config":
            print(row['jurisdiction'] + " - " + str(row['percent']))
        elif table_config == "new_config":
            print(_index, "-", str(row))
    return None

# Used for testing
# short_date_list = ["2020-03-16", "2020-03-17"]

def process_all_in_list(thelist):
    # runs the populate_fc fnxn on all fcs in a list
    for item in thelist:
        my_fc = fclist.fc_date_lookup[item]
        my_df = create_df(master_df, item)
        if table_config == "new_config":
            new_populate_fc(my_fc, my_df)
        elif table_config == "old_config":
            populate_fc(my_fc, my_df)
    return None

# it_worked = False
# OPTION A Uncomment the next line to create new fcs
it_worked = create_fcs_from_template() # generates n feature 
# classes (fcs) from a template fc
if it_worked:
    process_all_in_list(fclist.date_list)

# OPTION B do it anyway (uncomment the next line)
# THIS OPTION is for when the fcs already exist but you wish to write over the data in the tables
#process_all_in_list(fclist.date_list)

if merge_these:
    # boolean value set at the top of the script determines
    # whether or not you wish to merge all these feature classes
    arcpy.env.workspace = out_ws + "\\" + fd_name
    all_feature_classes = arcpy.ListFeatureClasses()
    merged_output = out_ws + merged_output_name
    merge_all_fcs(all_feature_classes, merged_output)

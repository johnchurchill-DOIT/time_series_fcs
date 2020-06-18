import os
import arcpy
import pandas
import fclist


fd_name = "v1"
out_ws = r"C:\Users\john.churchill\Documents\PROJECTS\Recovery_Dashboard\TS_seven_day.gdb"
template_fc = r"C:\Users\john.churchill\Documents\PROJECTS\Recovery_Dashboard\MasterCaseTracker_TimeSeries.gdb\Template_County_FC_v2"

# Test First to see if fd exists
if not arcpy.Exists(os.path.join(out_ws, fd_name)):
    arcpy.CreateFeatureDataset_management(out_ws, fd_name)

def create_fc(fc):
    #arcpy.CreateFeatureClass_management(fc)
    arcpy.CopyFeatures_management(template_fc, os.path.join(out_ws, fd_name, fc))

def populate_fc(fc, date_df):
    # uses a subset pandas dataframe to populate a feature class
    # with Cases and Date values by County and Date
    this_fc = os.path.join(out_ws, fd_name, fc)
    field_names = ["County", "Cases", "Date"]
    with arcpy.da.UpdateCursor(this_fc, field_names) as upd_cursor:
        for row in upd_cursor:
            for index, dfrow in date_df.iterrows():
                if row[0] == dfrow['jurisdiction']:
                    row[1] = dfrow['percent']
                    row[2] = dfrow['date']
                    upd_cursor.updateRow(row)

def create_fcs_from_template():
    # uses a template feature class and a list of and 
    # feature class names to create multiple copies of the template.
    for fc_name in fclist.fc_names:
        create_fc(fc_name)
    return True

def create_df(df, datestring):
    # can send the master_df and a single date (type=string)
    # returns the subset dataframe to use with the update cursor (populate_fc function)
    date_df = df['date']==datestring
    date_df_only = df[date_df]
    return date_df_only


master_df = pandas.read_excel(open(r'C:\Users\john.churchill\Documents\PROJECTS\Recovery_Dashboard\Daily_Positivity_Data_by_Jurisdiction.xlsx', 'rb'), sheet_name = 'Sheet2')

def read_df_by_date(datestring):
    # Uses global <master_df> to create subset df and print values.
    df = master_df['date']==datestring
    df_only = master_df[df]
    for index, row in df_only.iterrows():
        print(row['jurisdiction'] + " - " + str(row['percent']))

# Used for testing
# short_date_list = ["2020-03-16", "2020-03-17"]

def process_all_in_list(thelist):
    # runs the populate_fc fnxn on all fcs in a list
    for item in thelist:
        my_fc = fclist.fc_date_lookup[item]
        my_df = create_df(master_df, item)
        populate_fc(my_fc, my_df)

# OPTION A Uncomment the next line to create new fcs
it_worked = create_fcs_from_template() # generates n feature 
# classes (fcs) from a template fc
if it_worked:
    process_all_in_list(fclist.date_list)

# OPTION B do it anyway (uncomment the next line)
#process_all_in_list(fclist.date_list)

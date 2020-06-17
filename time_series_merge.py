import os
import arcpy
import pandas
from fclist import fc_names
from fclist import date_list

fd_name = "v1"
out_ws = r"C:\Users\john.churchill\Documents\PROJECTS\Recovery_Dashboard\TS_seven_day.gdb"
template_fc = r"C:\Users\john.churchill\Documents\PROJECTS\Recovery_Dashboard\MasterCaseTracker_TimeSeries.gdb\Template_County_FC_v2"

# ToDo TEST FIRST TO SEE IF fd EXISTS
if not arcpy.Exists(os.path.join(out_ws, fd_name)):
    arcpy.CreateFeatureDataset_management(out_ws, fd_name)

def create_fc(fc):
    #arcpy.CreateFeatureClass_management(fc)
    arcpy.CopyFeatures_management(template_fc, os.path.join(out_ws, fd_name, fc))


def populate_fc(fc, date_df):
    field_names = ["County", "Cases", "Date"]
    with arcpy.da.UpdateCursor(fc, field_names) as upd_cursor:
        for row in upd_cursor:
            #value_dict = {}
            for index, dfrow in date_df.iterrows():
                if row[0] == dfrow['jurisdiction']:
                    row[1] = dfrow['percent']
                    row[2] = dfrow['date']
                    upd_cursor.updateRow(row)
                #value_dict[dfrow['jurisdiction']] = (dfrow['date'], dfrow['percent'])
                #print(dfrow['jurisdiction'])
            #row[1] = value_dict[dfrow[0][1]] # percent
            #row[2] = value_dict[dfrow[0][0]] # date
            #upd_cursor.updateRow(row)
            
            # go through the pandas subset dataframes
        #for name in fc_names:
        #    print(name)

def create_fcs_from_template():
    # uses a template feature class and a list of and 
    # feature class names to create multiple copies of the template.
    for fc_name in fc_names:
        create_fc(fc_name)

def create_df(df, datestring):
    # can send the master_df and a single date (type=string)
    # returns the subset dataframe to use with the update cursor (populate_fc function)
    date_df = df['date']=='2020-03-19'
    date_df_only = df[date_df]
    return date_df_only

# call populate_fc on each layer created
#def setup_data(datelist):
#    # SHOULD create and return a large dictionary of all percent values for jurisdiction by date
#    # master_df is the master dataframe (the entire spreadsheet)
# master_dictionary = {}
master_df = pandas.read_excel(open(r'C:\Users\john.churchill\Documents\PROJECTS\Recovery_Dashboard\Daily_Positivity_Data_by_Jurisdiction.xlsx', 'rb'), sheet_name = 'Sheet2')
#    return master_df
#    ####df_3_19 = master_df['date']=='2020-03-19'
#    ####df_3_19_only = master_df[df_3_19]
#    ####for index, row in df_3_19_only.iterrows():
#    ####    print(row['jurisdiction'] + " - " + str(row['percent']))

#my_master_df = setup_data(full_datelist)
short_date_list = ["2020-03-16", "2020-03-17"]
for item in short_date_list:
    my_df = create_df(master_df, item)
    for index, row in my_df.iterrows():
        print(row['jurisdiction'] + " - " + str(row['percent']))
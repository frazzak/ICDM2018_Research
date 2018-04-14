#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 16:47:58 2018

@author: phn1x
"""

import sys,os
import csv
import pandas as pd
import re
import numpy as np


#Prep Dataframe to have metadata for parsing using pandas data parsing and cleaning
#May not be needed  
 
#lookup = '''Dollar Amounts in Thousands'''
#delimiter = ','
#nCols = 5
#fileparse_info = pd.DataFrame(
#        {'1stLinePattern' : lookup,
#         'FilePaths' : paths,
#         'SkipRows' : 'null',
#         'nCols' : nCols, #Fixed columns for now, TODO: Dynamic col number.
#         'Delimiter': delimiter
#        }
#        )  
 


#Loop through fileparseinfo datagrame
#for i in range(0,fileparse_info.shape[0]):
#    print("Opening File: ",fileparse_info['FilePaths'][i])
#    with open(fileparse_info['FilePaths'][i]) as myFile:
#        for num, line in enumerate(myFile, 1):
#            if lookup in line:
#                print('found at line:', num,' Ncols:', len(line))
#                fileparse_info['SkipRows'][i] = num
#                print(line)
#                break

#fileparse_info

#Testing import of 1 File.
#Skip first  lines from page 1 TODO: check if consistent for ReportName FFIEC101 
# 2014: Skip 8 rows
# 2015: No Skip
# 2016: Skip 10 rows
# 2017: Skip 10 rows
#Get all Schedule Names and do proper mapping for each report
    #FFIEC 101 Schedules A-S 2014-2017
    #FFIEC 102 4 pages, no Schedules only categories
    #FRY15 Scheules A-F, 2013-2014, A-G 2015 -2017
    #

 #Start at line  with "",Dollar Amounts in Thousands,AAAB,,
  
repattern = r'\.{2,}'
#Clean up columns
def column_cleanup(repattern ,tableobj_tmp, fillna = '', verbose = True, nafill = False):
    for i in range(0,tableobj_tmp.shape[1]):
        if nafill:
            if verbose:
                print("Filling NaNs")
            tableobj_tmp.iloc[:,i].fillna(fillna)
        if verbose:
            print("Replace consecutive dots in columns:", i)
        
        if tableobj_tmp.iloc[:,i].isnull().all():
            if verbose:
                print("Skipping Column: all NaN")
        elif tableobj_tmp.iloc[:,i].isnull().any():
            if verbose:
                print("Found NaNs in column")
                print(tableobj_tmp.iloc[:,i])
            for y in range(0,tableobj_tmp.shape[0]):
                if tableobj_tmp.iloc[y,i] is np.nan:
                    pass
                else:
                    if verbose:
                        print("Trim whitespaces and Removing Pattern by Row")
                    tableobj_tmp.iloc[y,i] = re.sub(repattern,'',tableobj_tmp.iloc[y,i])
                    tableobj_tmp.iloc[y,i].strip()
        else:   
            tableobj_tmp.iloc[:,i] = tableobj_tmp.iloc[:,i].str.replace(repattern,'')
            if verbose:
                print("Trim whitespaces")
            tableobj_tmp.iloc[:,i] = tableobj_tmp.iloc[:,i].str.strip() 
            
    return(tableobj_tmp)


#Check for the Schedule titles that were successfully parsed
for i in range(0,len(test)):
    #print(test[i].shape)
    test[i] = column_cleanup(repattern,test[i],verbose = False)
    for x in range(0,test[i].shape[0]):
        if  "Schedule" in test[i].iloc[x,0]:
            print(test[i].iloc[x,0])
         

#Using Tabula  multiple table read off the csv directly.
  #Maybe a cleaner way to interpret data.
#Tabula Conversion PDF to CSV
#How to get Tabula Dataframe from PDF
#, pandas_options = {'line_terminator': '/n'}
#test = tabula.read_pdf(test_file, pages = 'all', guess = True, multiple_tables = True)
#TODO:Search out Section Titles
#TODO:Collapse /r impacted rows , search via index code column 5


#Report_Info test_file
reportinfo_location = os.path.join(os.path.dirname(test_file),'../Report_Info/FFIEC_ReportSchedules_Tabbed_2.txt')
ReportsMeta = pd.read_table(reportinfo_location, encoding= 'latin_1')
ReportsMeta[['Report','Page','Cleaned_title']][ReportsMeta['Report'] == 'FFIEC101']

#Identify pattern to collapse multi line and shift elements appropirately.
#index = []
#for i in range(0,test_tmp.shape[0]):
#    if test_tmp.iloc[i,4] is np.nan:
#        print(i,False,test_tmp.iloc[i,4],test_tmp.iloc[i,0])
#        index.append(False)
#    elif test_tmp.iloc[i,0].startswith(test_tmp.iloc[i,4]):
#        print(i,True,test_tmp.iloc[i,4],test_tmp.iloc[i,0])
#        index.append(True)
#    else:
#         print(i,False,test_tmp.iloc[i,4],test_tmp.iloc[i,0])
#         index.append(False)

#indexpd = pd.Series(index)


#Accurate Mappings
#test_tmp[indexpd == False]


#for i in range(0,test_tmp.shape[0]):
#    if test_tmp.iloc[i,4] is not np.nan and test_tmp.iloc[i,0].startswith(test_tmp.iloc[i,4]):
#        print(i,True,test_tmp.iloc[i,4],test_tmp.iloc[i,0])
#        index.append(True)
    
#    elif test_tmp.iloc[i,0] is not np.nan and test_tmp.iloc[i,4] is np.nan: 
#        print(i,"Needs to be collapsed")
    
    
#    elif test_tmp.iloc[i,4] is np.nan and test_tmp.iloc[i,0] is np.nan:
#        print(i, "No Values")
    
#    else:    
#         print(i,False,test_tmp.iloc[i,4],test_tmp.iloc[i,0])
#         index.append(False)

##################################################


#Find and tag rows with appropriate labels and identify collapse required rows.
def report_item_tagger_collapser(test_tmp):
    coll_idx = []
    failed_idx = []
    indexcode_idx = test_tmp.shape[1] - 1
    indexcode_ridx = test_tmp.shape[0] - 1
    for i in range(0,indexcode_ridx):
        
        #For FFIEC101
#        if i == indexcode_ridx:
#            break
        if test_tmp.iloc[i,0] is not np.nan and '..' in test_tmp.iloc[i,0] and test_tmp.iloc[i,indexcode_idx] is not np.nan and  test_tmp.iloc[i,0].endswith(test_tmp.iloc[i,indexcode_idx]) :
           
            print(test_tmp.iloc[i,0],'| Aligned Properly')
            #pass
        elif test_tmp.iloc[i,0] is not np.nan and test_tmp.iloc[i,0].endswith('(not applicable)'):
            print(test_tmp.iloc[i,0],'| Not Applicable')
            test_tmp.iloc[i,indexcode_idx] = 'Not Applicable'
            coll_idx.append(i)
        elif test_tmp.iloc[i,0] is not np.nan  and '.' not in test_tmp.iloc[i,0] and test_tmp.iloc[i,1:test_tmp.shape[1]].isnull().all():
            print(test_tmp.iloc[i,0],'| SectionInfo')
            test_tmp.iloc[i,indexcode_idx] = 'SectionInfo'
        
        
        elif test_tmp.iloc[i,[0,indexcode_idx]].isnull().all() or "Dollar Amounts in Thousands" in test_tmp.iloc[i,0] and test_tmp.iloc[i,1:indexcode_idx - 1].notnull().any(): 
            print(test_tmp.iloc[i,1],test_tmp.iloc[i,2],test_tmp.iloc[i,3],'| HeaderInfo')
            test_tmp.iloc[i,indexcode_idx] = 'HeaderInfo'
            #pass
        
        elif test_tmp.iloc[i,0] is not np.nan and '..' not in test_tmp.iloc[i,0] and test_tmp.iloc[i,1:indexcode_idx].isnull().all():
            #print(test_tmp.iloc[i,0],test_tmp.iloc[i,1],test_tmp.iloc[i,2],test_tmp.iloc[i,3],test_tmp.iloc[i,4],' Collapse Rows to Below')
            str_tmp = []
            
            #pass
            while test_tmp.iloc[i,0] is not np.nan and '..' not in test_tmp.iloc[i,0]  and test_tmp.iloc[i,1:indexcode_idx].isnull().all():
               print("Collapsing row:", i,":",test_tmp.iloc[i,0])
               test_tmp.iloc[i,indexcode_idx] = "To Be Deleted"
               str_tmp.append(test_tmp.iloc[i,0])
               coll_idx.append(i)
               i = i + 1
               if i == indexcode_ridx + 1:
                   print("End of Report Line")
                   i = i - 1
                   break
                   
            if test_tmp.iloc[i,0] is not np.nan and  '..' in test_tmp.iloc[i,0] or test_tmp.iloc[i,1:indexcode_idx].notnull().all() and '..' in test_tmp.iloc[i,1]:
                str_tmp.append(test_tmp.iloc[i,0])
                print(" ".join(str_tmp),test_tmp.iloc[i,1],test_tmp.iloc[i,2],test_tmp.iloc[i,3],test_tmp.iloc[i,indexcode_idx],"| Collapsed")
                print("Updating Row")
                test_tmp.iloc[i,0] = " ".join(str_tmp)
                #print("Deleting Collapsed Rows")
                  
                str_tmp = []
        #elif test_tmp.iloc[i,0] is not np.nan and  '..' in test_tmp.iloc[i,0] or '..' in test_tmp.iloc[i,1] and  test_tmp.iloc[i,1] is not np.nan and test_tmp.iloc[i,2] is not np.nan and test_tmp.iloc[i,3] is not np.nan and test_tmp.iloc[i,4] is not np.nan :
            #print(test_tmp.iloc[i,0],test_tmp.iloc[i,1],test_tmp.iloc[i,2],test_tmp.iloc[i,3],test_tmp.iloc[i,4],"| Collapse Above to Here")
            #pass
        elif test_tmp.iloc[i,indexcode_idx] is np.nan:
            print(test_tmp.iloc[i,0],test_tmp.iloc[i,1],test_tmp.iloc[i,2],test_tmp.iloc[i,3],test_tmp.iloc[i,indexcode_idx], '| FAILED')
            failed_idx.append(i)
    try:
        print("Deleting index ", coll_idx)
        test_tmp = test_tmp.drop(test_tmp.index[coll_idx])
    
    except Exception as a:
        print(a)      
        print("Delete Failed")
    print("Failed Parsing on:", failed_idx)
    return(test_tmp)


#Compatibility 5 columns 
#[1, 2, 5, 6, 18, 23, 24, 34, 35]
    
    #FFIEC101 page index [1,2,6]
        #Pages 2-5 may be most useful and easiest to parse.  
            #Dynmaic Column detection for parsing required.
    #FFIEC102
        #All 6 tables from the report should be parseable.
            #Dynamic Column detection and robust row tagging and detection required.
    #FRY15, FRY9LP Parsable
    #BHPR will need customized parsing due to some columns requiring splititng and not index column.

homepath = os.environ['HOME']
basepath = os.path.join(homepath,'ICDM_Research/Stress_Test_Research/StressTest_Research/')
sourcefolder = os.path.join(basepath,"tabula_csv")
os.listdir(sourcefolder)
ReportName_prefix = 'FFIEC101_1069778'
ReportName_suffix = '.PDF.csv'
paths = [ os.path.join(sourcefolder,fn) for fn in os.listdir(sourcefolder) if fn.startswith(ReportName_prefix) & fn.endswith(ReportName_suffix)]

test_file = paths[len(paths) - 1]
test_file = os.path.join(os.path.dirname(test_file),'../unsecured_pdf_complete',os.path.basename(test_file).replace('.csv','.pdf'))
test_file_data = [test_file]
test_file_data.extend(os.path.basename(test_file.replace('.PDF.pdf',"")).split("_"))

if test_file_data[1] == "FFIEC101":
    filepages = "2-5"
elif test_file_data[1] in ["FFIEC102","FRY15","FRY9LP","BHCPR"]:
    filepages = "all"

    
    
    
report = tabula.read_pdf(test_file_data[0], pages = filepages, guess = True, multiple_tables = True)


library
len(report)

result_df = pd.DataFrame()
for i in range(0,len(report)):        
    testtmp = pd.DataFrame.copy(report[i],deep=True)
    testtmp.shape
    testtmp = report_item_tagger_collapser(testtmp)
    testtmp = column_cleanup(repattern,testtmp,verbose = False)
    testtmp = testtmp.reset_index(drop=True)
    print(testtmp.shape)
    #result_df.merge(testtmp)
    


strtemp = "2.11. Total derivative exposures (sum of items 2.4, 2.5, 2.6 and 2.9, minus items 2.7, 2.8, and 2.10) ................................................................................................................."


strtemp.replace(repattern," ")

re.sub(repattern,"",strtemp)

indexcode_idx = testtmp.shape[1] - 1
i = 13

testtmp.iloc[i,0] is not np.nan and '..' not in testtmp.iloc[i,0]  and testtmp.iloc[i,1:indexcode_idx].isnull().all()








report_item_tagger_collapser(test[1]











# Use Cols from 0-5, Avoids error
#Read in CSV Object
#Add Skip Row 
#Add Usage of columns, or get number of columns
#Add iterator for paths
#Export Cleaned file.
#Add looping
i = 0
tableobj_tmp = pd.read_table(fileparse_info['FilePaths'][i], sep = delimiter,quotechar = '"', skiprows = fileparse_info['SkipRows'][i] - 1,usecols = range(0,fileparse_info['nCols'][i]))



        







list(tableobj_tmp.columns.values)
#FFIEC Headers
tableobj_tmp.columns = ["Variable_Description_1","Variable_Description_2","MNEMONIC_CODE","Amount","IndexCode"]


tableobj_tmp.info()
#Clean up Amount Column
#Fill NA with 0.
tableobj_tmp.fillna(0,inplace = True)

#Find and update Amount columns that have Mnemonic codes that need to be shifted over right column
alpha = '[^a-zA-Z]'
alphanumeric = '[^a-zA-Z0-9]'
#Starts with letter then ends with numbers
#Some codes are numbers
Mnemonic_code = '^[a-zA-Z]+[0-9]*$'
#Starts with 1 letter then followed by 3 numbers
Mnemonic_code_2 = '[a-zA-Z]{1}\d{3}'
Mnemonic_code_3 = '[a-zA-Z]{1}[a-zA-Z0-9]{3}'
Mnemonic_code_4 = '^[A-Z]+[0-9]*$'
Mnemonic_code_5 = '^[A-X]+[0-9]*$'

index_loc = (tableobj_tmp['Amount'].str.len() == 4)
index_loc2 = (tableobj_tmp['Amount'].str.match(Mnemonic_code).fillna(False))

index_loc2_1 = (tableobj_tmp['Amount'].str.match(Mnemonic_code))
index_loc2_2 = (tableobj_tmp['Amount'].str.match(Mnemonic_code_3).fillna(False))
index_loc2_3 = (tableobj_tmp['Amount'].str.match(Mnemonic_code_4).fillna(False))

index_loc2_4 = (tableobj_tmp['Amount'].str.match(Mnemonic_code_5).fillna(False))

tableobj_tmp['Variable_Description_2'].unique()


tableobj_tmp[index_loc2_4]


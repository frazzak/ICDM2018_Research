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
homepath = os.environ['HOME']
basepath = os.path.join(homepath,'ICDM_Research/Stress_Test_Research/StressTest_Research/')
sourcefolder = os.path.join(basepath,"tabula_csv")

os.listdir(sourcefolder)
#FFIEC101 2015
# Schedules A : S



ReportName_prefix = 'FFIEC101_1069778'

ReportName_suffix = '.PDF.csv'
paths = [ os.path.join(sourcefolder,fn) for fn in os.listdir(sourcefolder) if fn.startswith(ReportName_prefix) & fn.endswith(ReportName_suffix)]


#Prep Dataframe to have metadata for parsing using pandas data parsing and cleaning
  
 
lookup = '''Dollar Amounts in Thousands'''
delimiter = ','
nCols = 5
fileparse_info = pd.DataFrame(
        {'1stLinePattern' : lookup,
         'FilePaths' : paths,
         'SkipRows' : 'null',
         'nCols' : nCols, #Fixed columns for now, TODO: Dynamic col number.
         'Delimiter': delimiter
        }
        )  
 


#Loop through fileparseinfo datagrame
for i in range(0,fileparse_info.shape[0]):
    print("Opening File: ",fileparse_info['FilePaths'][i])
    with open(fileparse_info['FilePaths'][i]) as myFile:
        for num, line in enumerate(myFile, 1):
            if lookup in line:
                print('found at line:', num,' Ncols:', len(line))
                fileparse_info['SkipRows'][i] = num
                print(line)
                break

fileparse_info

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
            tableobj_tmp.iloc[:,i].fillna(fillna)
        if verbose:
            print("Replace consecutive dots in columns:", i)
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
test_file = fileparse_info['FilePaths'][0]
test_file = os.path.join(os.path.dirname(test_file),'../unsecured_pdf_complete',os.path.basename(test_file).replace('.csv','.pdf'))
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



test_tmp = test[1]
#column_cleanup(repattern,test[1], nafill = True)


test_tmp.iloc[17,[0]].str.startswith(test_tmp.iloc[17,[4]])

len(test_tmp.iloc[17,4])

test_tmp.iloc[17,0][2].str.startswith(test_tmp.iloc[:,4])
#Identify pattern to collapse multi line and shift elements appropirately.
index = []
for i in range(0,test_tmp.shape[0]):
    if test_tmp.iloc[i,4] is np.nan:
        print(i,False,test_tmp.iloc[i,4],test_tmp.iloc[i,0])
        index.append(False)
    elif test_tmp.iloc[i,0].startswith(test_tmp.iloc[i,4]):
        print(i,True,test_tmp.iloc[i,4],test_tmp.iloc[i,0])
        index.append(True)
    else:
         print(i,False,test_tmp.iloc[i,4],test_tmp.iloc[i,0])
         index.append(False)

indexpd = pd.Series(index)


#Accurate Mappings
#test_tmp[indexpd == False]


for i in range(0,test_tmp.shape[0]):
    if test_tmp.iloc[i,4] is not np.nan and test_tmp.iloc[i,0].startswith(test_tmp.iloc[i,4]):
        print(i,True,test_tmp.iloc[i,4],test_tmp.iloc[i,0])
        index.append(True)
    
    elif test_tmp.iloc[i,0] is not np.nan and test_tmp.iloc[i,4] is np.nan: 
        print(i,"Needs to be collapsed")
    
    
    elif test_tmp.iloc[i,4] is np.nan and test_tmp.iloc[i,0] is np.nan:
        print(i, "No Values")
    
    else:    
         print(i,False,test_tmp.iloc[i,4],test_tmp.iloc[i,0])
         index.append(False)

##################################################


#Find and tag rows with appropriate labels and identify collapse required rows.
def report_item_tagger_collapser(test_tmp):
    coll_idx = []
    for i in range(0,test_tmp.shape[0]):
        
        
        if test_tmp.iloc[i,0] is not np.nan and '..' in test_tmp.iloc[i,0] and test_tmp.iloc[i,4] is not np.nan and  test_tmp.iloc[i,0].startswith(test_tmp.iloc[i,4]) :
            print(test_tmp.iloc[i,0],'| Aligned Properly')
            #pass
        elif test_tmp.iloc[i,0] is not np.nan and test_tmp.iloc[i,0].endswith('(not applicable)')  and '..' not in test_tmp.iloc[i,0]:
            print(test_tmp.iloc[i,0],'| Not Applicable')
            test_tmp.iloc[i,4] = 'Not Applicable'
            #pass
        elif test_tmp.iloc[i,0] is not np.nan  and '.' not in test_tmp.iloc[i,0] and test_tmp.iloc[i,1] is np.nan and test_tmp.iloc[i,2] is np.nan and test_tmp.iloc[i,3] is np.nan and test_tmp.iloc[i,4] is np.nan:
            print(test_tmp.iloc[i,0],'| SectionInfo')
            test_tmp.iloc[i,4] = 'SectionInfo'
        
        
        elif test_tmp.iloc[i,0] is np.nan and test_tmp.iloc[i,1] is not np.nan and  '..' not in test_tmp.iloc[i,1] and test_tmp.iloc[i,2] is not np.nan and test_tmp.iloc[i,3] is  np.nan and test_tmp.iloc[i,4] is np.nan: 
            print(test_tmp.iloc[i,1],test_tmp.iloc[i,2],test_tmp.iloc[i,3],'| HeaderInfo')
            test_tmp.iloc[i,4] = 'HeaderInfo'
            #pass
        
        elif test_tmp.iloc[i,0] is not np.nan and '..' not in test_tmp.iloc[i,0]  and test_tmp.iloc[i,1] is np.nan and test_tmp.iloc[i,2] is np.nan and test_tmp.iloc[i,3] is np.nan and test_tmp.iloc[i,4] is np.nan:
            #print(test_tmp.iloc[i,0],test_tmp.iloc[i,1],test_tmp.iloc[i,2],test_tmp.iloc[i,3],test_tmp.iloc[i,4],' Collapse Rows to Below')
            str_tmp = []
            
            #pass
            while test_tmp.iloc[i,0] is not np.nan and '..' not in test_tmp.iloc[i,0]  and test_tmp.iloc[i,1] is np.nan and test_tmp.iloc[i,2] is np.nan and test_tmp.iloc[i,3] is np.nan and test_tmp.iloc[i,4] is np.nan:
               print("Collapsing row:", i,":",test_tmp.iloc[i,0])
               test_tmp.iloc[i,4] = "To Be Deleted"
               str_tmp.append(test_tmp.iloc[i,0])
               coll_idx.append(i)
               i = i + 1
            if test_tmp.iloc[i,0] is not np.nan and  '..' in test_tmp.iloc[i,0] or '..' in test_tmp.iloc[i,1] and  test_tmp.iloc[i,1] is not np.nan and test_tmp.iloc[i,2] is not np.nan and test_tmp.iloc[i,3] is not np.nan and test_tmp.iloc[i,4] is not np.nan:
                str_tmp.append(test_tmp.iloc[i,0])
                print(" ".join(str_tmp),test_tmp.iloc[i,1],test_tmp.iloc[i,2],test_tmp.iloc[i,3],test_tmp.iloc[i,4],"| Collapsed")
                print("Updating Row")
                test_tmp.iloc[i,0] = " ".join(str_tmp)
                #print("Deleting Collapsed Rows")
                  
                str_tmp = []
        #elif test_tmp.iloc[i,0] is not np.nan and  '..' in test_tmp.iloc[i,0] or '..' in test_tmp.iloc[i,1] and  test_tmp.iloc[i,1] is not np.nan and test_tmp.iloc[i,2] is not np.nan and test_tmp.iloc[i,3] is not np.nan and test_tmp.iloc[i,4] is not np.nan :
            #print(test_tmp.iloc[i,0],test_tmp.iloc[i,1],test_tmp.iloc[i,2],test_tmp.iloc[i,3],test_tmp.iloc[i,4],"| Collapse Above to Here")
            #pass
        else:
            print(test_tmp.iloc[i,0],test_tmp.iloc[i,1],test_tmp.iloc[i,2],test_tmp.iloc[i,3],test_tmp.iloc[i,4], '| FAILED')
    try:
        print("Deleting index ", coll_idx)
        test_tmp = test_tmp.drop(test_tmp.index[coll_idx])
    
    except Exception as a:
        print(a)      
        print("Delete Failed")
   
    return(test_tmp)



test = tabula.read_pdf(test_file, pages = 'all', guess = True, multiple_tables = True)
testtmp = test[5]
testtmp2 = report_item_tagger_collapser(testtmp)
testtmp2 = column_cleanup(repattern,testtmp2,verbose = True)


testtmp.shape
testtmp2.shape

testtmp2

parsesheet = []
for i in range(0,len(test)):
    if test[i].shape[1] >= 2 and test[i].shape[1] <= 6:
        print(i,":",test[i].shape)
        parsesheet.append(i)


for i in parsesheet:
    report_item_tagger_collapser(test[i])














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


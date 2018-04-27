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
# 2017: Skip 10 rows
#Get all Schedule Names and do proper mapping for each report
    #FFIEC 101 Schedules A-S 2014-2017
    #FFIEC 102 4 pages, no Schedules only categories
    #FRY15 Scheules A-F, 2013-2014, A-G 2015 -2017
    
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





#Clean up columns
def column_cleanup(repattern = None, tableobj_tmp = None, fillna = '', verbose = True, nafill = False):
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
                    print("Removing Consecutive periods and space patterns")
                    if repattern is None:
                        print("No REGEX Pattern, will match known patterns")
                        repattern = r'\.{2,}'
                        tableobj_tmp.iloc[y,i] = re.sub(repattern,'',tableobj_tmp.iloc[y,i])
                        repattern1 = r'[ ]\.{1,}'
                        if bool(re.match(repattern1,tableobj_tmp.iloc[y,i])):
                            print("Removing spaces and period pattern")
                            tableobj_tmp.iloc[y,i] = re.sub(repattern1,'',tableobj_tmp.iloc[y,i])
                        tableobj_tmp.iloc[y,i].strip()
                    else:
                        tableobj_tmp.iloc[y,i] = re.sub(repattern,'',tableobj_tmp.iloc[y,i])
                        tableobj_tmp.iloc[y,i].strip()
        else:   

            if repattern is None:
                repattern = r'\.{2,}'
                tableobj_tmp.iloc[:,i] = tableobj_tmp.iloc[:,i].str.replace(repattern,'')
                repattern = r'[ ]\.{1,}' 
                tableobj_tmp.iloc[:,i] = tableobj_tmp.iloc[:,i].str.replace(repattern,'')
            else:
                tableobj_tmp.iloc[:,i] = tableobj_tmp.iloc[:,i].str.replace(repattern,'')
            
            
            if verbose:
                print("Trim whitespaces")
            tableobj_tmp.iloc[:,i] = tableobj_tmp.iloc[:,i].str.strip() 
            
    return(tableobj_tmp)






def report_column_alignmentstruct(tabulaList_df = None, ReportType = "FFIEC101", ReportData = None):    
    i = 0
    coll_idx = []
    result_df = tabulaList_df
    if ReportType == "FFIEC101":
        print("Processing FFIEC101")
        print(len(result_df))
        while i < len(result_df):
            print(i, ReportData)
            repattern2 = r'[ ]\.{1,}'
            deletedflag = False
            for y in range(0,result_df[i].shape[0]):    
                #print(i,y)

                if result_df[i].iloc[y,0] is np.nan and result_df[i].iloc[y,1].endswith("Dollar Amounts in Thousands"): #Should we dynamically look for the Section?
                    print("Found Header Misalignment for columns, Correcting.")
                    result_df[i].iloc[y,0] = "Dollar Amounts in Thousands"
                    result_df[i].iloc[y,1] = np.nan
                elif result_df[i].iloc[y,0] is np.nan and result_df[i].iloc[y,1].startswith("Dollar Amounts in Thousands") and not result_df[i].iloc[y,1].endswith("Dollar Amounts in Thousands"):
                    print("Found Header Misalignment that needs parsing, Correcting.")
                    result_df[i].iloc[y,0] = "Dollar Amounts in Thousands"
                    result_df[i].iloc[y,1] = result_df[i].iloc[y,1].split("Dollar Amounts in Thousands ")[-1]
                elif result_df[i].iloc[y,1] is not np.nan and  bool(re.match(repattern2,result_df[i].iloc[y,1])):
                    print("Found Consecutive space and periods to remove") 
                    result_df[i].iloc[y,1] =  re.sub(repattern2,"",result_df[i].iloc[y,1]).strip()
                elif result_df[i].iloc[y,0] is np.nan and result_df[i].iloc[y,1:].str.startswith("Percentage").any() and result_df[i].iloc[y,result_df[i].shape[1] -1] == "HeaderInfo" :
                    print("Description Misalignment: Description in Amounts") 
                    result_df[i].iloc[y,0] =  "Percentage"
                    result_df[i].iloc[y,2] = np.nan
                    
                elif result_df[i].iloc[y,0] is np.nan and result_df[i].iloc[y,1:result_df[i].shape[1] - 2].str.startswith("(Column ").any() and result_df[i].iloc[y,result_df[i].shape[1] -1] == "HeaderInfo" :
                    print("Additional Parsing Required For this table, not including in list: (Column [A-Z])") 
                    #del result_df[i] #After deletion of report, next i and reset or rows required
                    coll_idx.append(i)
                    deletedflag = True
                    break
                
                elif result_df[i].iloc[y,1:result_df[i].shape[1] - 1].fillna("").str.endswith("Percentage").all() and result_df[i].iloc[y,0] is not np.nan and  result_df[i].iloc[y,result_df[i].shape[1] - 1] is np.nan:
                    print("Additional Parsing Required For this table, not including in list: Percentage") 
                    #del result_df[i] #After deletion of report, next i and reset or rows required
                    coll_idx.append(i)
                    deletedflag = True
                    break
              
            if not deletedflag:
                print("Replacing Blanks with NaNs")
                result_df[i].replace(r'^\s*$', np.nan, regex=True, inplace = True)
                print ("Drop Columns that are all NaN")
                result_df[i]= result_df[i].dropna(axis=1,how='all')            
                #print(result_df[i])
                FFIEC101_ColumnsBase = ["Description", "ReportCode","Amount","IndexInfo","Report_Type","Report_RSSD","Report_Date"]
                print("Adding Column Names")
                result_df[i]["Report_Type"] = ReportData[0] 
                result_df[i]["Report_RSSD"] = ReportData[1]
                result_df[i]["Report_Date"] = ReportData[2]
                print(i, result_df[i].columns.values)
                result_df[i].columns = FFIEC101_ColumnsBase
                print(i, result_df[i].columns.values)
            i += 1            
             
    elif ReportType in ["FFIEC102","FRY15","FRY9LP","BHCPR"]:
        print("To be developed")
    else: print("Report Type Not Found")

    try:
        print("Deleting index ", coll_idx)
        for i in sorted(coll_idx, reverse=True):
            del result_df[i]
    except Exception as a:
        print(a)      
        print("Delete Failed")     
    
    return (result_df)
    


def report_parser_dataframer(reportsourcefolder = "/Users/phn1x/ICDM_Research/Stress_Test_Research/StressTest_Research/unsecured_pdf_complete/", reportfilepath = None, extension = ".PDF.pdf"):
    result_df = list()
    master_result_list = list()
    FFIEC101_ColumnsBase = ["Description", "ReportCode","Amount","IndexInfo","Report_Type","Report_RSSD","Report_Date"]
    if isinstance(reportfilepath, list):
        
        for y in reportfilepath:                 
            ReportData = os.path.basename(y).replace(extension,"").split("_")
            print("Determining Report Type to set parameters for:",y)
            if ReportData[0] == "FFIEC101":
                print("Processing:",ReportData[0])
                filepages = "2-5"    
                print("Processing Tables with Tabula")
                report = tabula.read_pdf(y, pages = filepages, guess = True, multiple_tables = True)
                
                for i in range(0,len(report)):        
                    testtmp = pd.DataFrame.copy(report[i],deep=True)
                    testtmp = report_item_tagger_collapser(testtmp)
                    testtmp = column_cleanup(None,testtmp,verbose = False)
                    print("Adding Report Reference Data")
                    #print("Adding Column Names")
                    #testtmp.columns = FFIEC101_ColumnsBase
                    #testtmp["Report_Type"] = ReportData[0] 
                    #testtmp["Report_RSSD"] = ReportData[1]
                    #testtmp["Report_Date"] = ReportData[2]
                    testtmp = testtmp.reset_index(drop=True)
                    result_df.append(pd.DataFrame(testtmp))
                print("Aligning Columns and adding Column Names")
                result_df = report_column_alignmentstruct(result_df,ReportData[0], ReportData)
                print("Concatenating Dataframes")
                result_df = pd.concat(result_df, ignore_index = True)
                master_result_list.append(result_df)
            master_result = pd.concat(master_result_list)
            returnobj = master_result.dropna(axis=1,how='all')  
            returnobj = returnobj.reset_index(drop = True)
    else:
        ReportData = os.path.basename(reportfilepath).replace(extension,"").split("_")
        if ReportData[0] == "FFIEC101":
            print("Processing:",ReportData[0])
            filepages = "2-5"    
            print("Processing Tables with Tabula")
            report = tabula.read_pdf(reportfilepath, pages = filepages, guess = True, multiple_tables = True)
            
            for i in range(0,len(report)):        
                testtmp = pd.DataFrame.copy(report[i],deep=True)
                testtmp = report_item_tagger_collapser(testtmp)
                testtmp = column_cleanup(None,testtmp,verbose = False)
                testtmp = testtmp.reset_index(drop=True)
                #testtmp = testtmp.reset_index(axis = 1,drop=True)
                print("Adding Report Reference Data")
                #testtmp["Report_Type"] = ReportData[0] 
                #testtmp["Report_RSSD"] = ReportData[1]
                #testtmp["Report_Date"] = ReportData[2]
                result_df.append(pd.DataFrame(testtmp))
            print("Aligning Columns and adding Column Names")
            result_df = report_column_alignmentstruct(result_df,ReportData[0], ReportData)
            print("Concatenating Dataframes")
            master_result = pd.concat(result_df)
            returnobj = master_result.dropna(axis=1,how='all')  
            #returnobj = returnobj.reset_index(drop = True)
            
    return(returnobj)


    


###File path variables
# File naming and renameing for input.
homepath = os.environ['HOME']
basepath = os.path.join(homepath,'ICDM_Research/Stress_Test_Research/StressTest_Research/')
sourcefolder = os.path.join(basepath,"unsecured_pdf_complete")
os.listdir(sourcefolder)
ReportName_prefix = 'FFIEC101_1039502'
ReportName_suffix = '20151231.PDF.pdf'
paths = [ os.path.join(sourcefolder,fn) for fn in os.listdir(sourcefolder) if fn.startswith(ReportName_prefix) & fn.endswith(ReportName_suffix)]
########

del(result_ffiec101)

result_ffiec101 = report_parser_dataframer(reportsourcefolder = "/Users/phn1x/ICDM_Research/Stress_Test_Research/StressTest_Research/unsecured_pdf_complete/", reportfilepath = paths, extension = ".PDF.pdf")
result_ffiec101.shape



#############Testing
#report = tabula.read_pdf(paths[0], pages = filepages, guess = True, multiple_tables = True)


#len(report)

#for i in range(0,len(report)):
#    
#    print("TableInfo:",i,report[i].shape)
#    for y in range(0,report[i].shape[0]): 
        #if  report[i].iloc[y,0] is not np.nan and report[i].iloc[y,report[i].shape[1] - 1] is np.nan and 
#        if  report[i].iloc[y,1:report[i].shape[1] -1 ].fillna("").str.startswith("Percentage").all() :
#                #print(report[i].iloc[y,:])
#                print("Additional Parsing Required For this table, not including in list: Percentage") 
#                print("Table:",i," Row:",y)
#                print(report[i].iloc[y,1:report[i].shape[1] -1 ])
#                print(report[i].iloc[y,1:report[i].shape[1] -1 ].str.startswith("Percentage").all())
#        else:
#            continue
##################### Misc
#Find and update Amount columns that have Mnemonic codes that need to be shifted over right column
#alpha = '[^a-zA-Z]'
#alphanumeric = '[^a-zA-Z0-9]'
#Starts with letter then ends with numbers
#Some codes are numbers
#Mnemonic_code = '^[a-zA-Z]+[0-9]*$'
#Starts with 1 letter then followed by 3 numbers
#Mnemonic_code_2 = '[a-zA-Z]{1}\d{3}'
#Mnemonic_code_3 = '[a-zA-Z]{1}[a-zA-Z0-9]{3}'
#Mnemonic_code_4 = '^[A-Z]+[0-9]*$'
#Mnemonic_code_5 = '^[A-X]+[0-9]*$'

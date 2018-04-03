#Generic Functions to pull data from FFEIC
#Library Dependencies

if (!require("dplyr")) {
  install.packages("dplyr")
}
library("dplyr")

if (!require("stringr")) {
  install.packages("stringr")
}
library(stringr)

if (!require("selectr")) {
  install.packages("selectr")
}
library("selectr")

if (!require("httr")) {
  install.packages("httr")
}
library("httr")

if (!require("xml2")) {
    install.packages("xml2")
}
library(xml2)

if (!require("rvest")) {
  install.packages("rvest")
}
library("rvest")


# Global Variables

  
  #WebAPI Url Link Creator
FFIEC_BHC_WebAPI_UrlCreator = function(RSSD_IDs,ReportDates,ReportTypes,downloadpath){
  print("Initializaing Results Object")
  WebAPI_Links = data.frame()
  Report_Generator_Api = c()
  Report_Download_Link = c()
  WebApiUrlObj = c()
  for (RSSD_ID in RSSD_IDs)
  {
    
    for (ReportDate in ReportDates) 
      {
      
      for (ReportType in ReportTypes)
        {
        
          print(paste0("Generating WebAPI Requests for: ",RSSD_ID, " ",ReportDate," ", ReportType))
        
          Report_Generator_Api = paste0("https://www.ffiec.gov/nicpubweb/nicweb/FinancialReport.aspx?parID_RSSD=",RSSD_ID,"&parDT=",ReportDate,"&parRptType=",ReportType)
          
          
          Report_Download_Link = paste0("https://www.ffiec.gov/nicpubweb/NICDataCache/",ReportType,"/",ReportType,"_",RSSD_ID,"_",ReportDate,".PDF")
          
          WebApiUrlObj = data.frame (RSSD_ID,ReportType,ReportDate,ReportGeneratorURL = Report_Generator_Api, ReportDownload = Report_Download_Link, ReportAPILink_Redirect = paste0(Report_Generator_Api,"&redirectPage=FinancialReport.aspx"), downloadpath, filename = paste0(ReportType,"_",RSSD_ID,"_",ReportDate,".PDF"))    
          print(paste0("Generated WebApiUrlObj, Combing with Results WebAPI Requests for:"))
          
          WebAPI_Links = rbind(WebAPI_Links,WebApiUrlObj)   
          print(paste0("Row Binding Complete"))
          
               }
          }
      }
  print(paste0("Updating Data Structures"))
  WebAPI_Links$ReportDate = as.Date(WebAPI_Links$ReportDate,format = '%Y%m%d' )
  WebAPI_Links$ReportGeneratorURL = as.character(WebAPI_Links$ReportGeneratorURL)
  WebAPI_Links$ReportDownload = as.character(WebAPI_Links$ReportDownload)
  WebAPI_Links$ReportAPILink_Redirect = as.character(WebAPI_Links$ReportAPILink_Redirect)
  WebAPI_Links$downloadpath = as.character(WebAPI_Links$downloadpath)
  
  print(paste0("Updating Data Structures Returning Result Object"))
  
  return(WebAPI_Links)
}  

  #WebAPI Url Link Downloader
WebAPI_URLLink_Downloader = function(BHCWebAPILinks, clearfiles = FALSE, cleardir = FALSE)
  {


  
        
  
      #Generate the File Requests and download file
      DownloadStatusLog = data.frame()
#      assign(DownloadStatusLog,eniv = .GlobalEnv)
      cleardir_counter = 0 
      for(i in 1:nrow(BHCWebAPILinks))
      {
        
        tempobj = BHCWebAPILinks[i,]
        tempdownloadfilepath = paste0(tempobj[["downloadpath"]],tempobj[["filename"]]) 
       
        if(cleardir && cleardir_counter == 0 ){
          print(paste0("Deleting ALL Files in Directory: ",tempobj[["downloadpath"]]))
          do.call(file.remove, list(list.files(tempobj[["downloadpath"]], full.names = TRUE)))
          cleardir_counter = cleardir_counter + 1
        }
        else
        if(clearfiles){
         print(paste0("Deleting if Exists: ",tempdownloadfilepath))
          if (file.exists(tempdownloadfilepath))
            {
            file.remove(tempdownloadfilepath)
          
        
         print(paste0("Generating File Request to FFIEC for:", tempobj$RSSD_ID, " ", tempobj$ReportType, " ", tempobj$ReportDate  ))
        GenerateFileRequest = GET(tempobj[["ReportAPILink_Redirect"]])
        
        #Download the Files
        print(paste0("Attempting to Download File: ", tempobj[["ReportDownload"]], tempobj[["downloadpath"]]))
#        download.file(tempobj[["ReportDownload"]], tempdownloadfilepath, quiet = TRUE )   
        tryCatch({download.file(tempobj[["ReportDownload"]], tempdownloadfilepath, quiet = FALSE ) }, error=function(err) { warning("file could not be downloaded") 
          
          print(paste0("FAILED to Download File: ", tempobj[["ReportDownload"]], " to ", tempdownloadfilepath))
          
          resultobj = data.frame(RSSD_ID = as.character(tempobj$RSSD_ID), 
                                 ReportType = as.character(tempobj$ReportType),
                                 ReportDate = as.character(tempobj$ReportDate),
                                 ReportFilename = as.character(tempobj$filename),
                                 DownloadFilePath =  as.character(tempdownloadfilepath), 
                                 Status = "FAILED - 404") 
          
          DownloadStatusLog = rbind(DownloadStatusLog, resultobj)
          
          
          })
        }
        
        if (!file.exists(tempdownloadfilepath)) {
          print(paste0("FAILED to Download File: ", tempobj[["ReportDownload"]], " to ", tempdownloadfilepath))
          
          resultobj = data.frame(RSSD_ID = as.character(tempobj$RSSD_ID), 
                                   ReportType = as.character(tempobj$ReportType),
                                   ReportDate = as.character(tempobj$ReportDate),
                                   ReportFilename = as.character(tempobj$filename),
                                   DownloadFilePath =  as.character(tempdownloadfilepath), 
                                   Status = "FAILED") 
        }
          }
        else{
          print(paste0("SKIPPED File: ",tempdownloadfilepath))
          resultobj = data.frame(RSSD_ID = as.character(tempobj$RSSD_ID), 
                                 ReportType = as.character(tempobj$ReportType),
                                 ReportDate = as.character(tempobj$ReportDate),
                                 ReportFilename = as.character(tempobj$filename),
                                 DownloadFilePath =  as.character(tempdownloadfilepath), 
                                 Status = "Skipped-Exists") 
        
          DownloadStatusLog = rbind(DownloadStatusLog, resultobj)
        }  
          #setInternet2(TRUE)
          #download.file(fileURL ,destfile,method="auto") }
          #load("./data/samsungData.rda")
        
        resultobj = data.frame(RSSD_ID = as.character(tempobj$RSSD_ID), 
                                  ReportType = as.character(tempobj$ReportType),
                                  ReportDate = as.character(tempobj$ReportDate),
                                  ReportFilename = as.character(tempobj$filename),
                                  DownloadFilePath =  as.character(tempdownloadfilepath), 
                                  Status = "OK") 
        
        DownloadStatusLog = rbind(DownloadStatusLog, resultobj)
        
      }
    
      return(DownloadStatusLog)
    
  }

#BHC List Generator

BHC_Meta_Data_List_Generator = function (base_site, dates = NULL) {
    #Get list of dates so we can get all BHCs for different dates to create reference BHC table.
    
    #Loop through Dates Vector and generate request\response
    topBHC  = data.frame()
    #Read base site
    webpage = read_html(base_site)
    
    #Collect hidden attributes
    hidden = setNames(
      html_nodes(webpage, "input[type='hidden']") %>% html_attr("value"),
      html_nodes(webpage, "input[type='hidden']") %>% html_attr("name")
    ) 
    if(is.null(dates)){ dates = 1}
      
    for(i in 1:length(dates))
      {
      
     
      if(dates[i]=='20171231' || dates[i] == 1 ){
        tempwebpage_obj = webpage
        tmptbl <- tempwebpage_obj %>%
          html_nodes("#dgTop50") %>%
          html_table(fill = TRUE) %>%
          .[[1]]
        } else {
      #Post with hidden attributes , generate a request
      requestpost = 
        POST(
          url = base_site, 
          add_headers(
            Origin = "https://www.rutgers.edu", 
            `User-Agent` = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.52 Safari/537.36", 
            Referer = base_site
          ), 
          body = list(
            `__EVENTTARGET` = "", 
            `__EVENTARGUMENT` = "", 
            `__VIEWSTATE` = hidden["__VIEWSTATE"],
            `__VIEWSTATEGENERATOR` = hidden["__VIEWSTATEGENERATOR"],
            `__EVENTVALIDATION` = hidden["__EVENTVALIDATION"],
            DateDropDown = dates[i]
          ), 
          encode = "form"
        )  
      #Store response as parsed content
      tempwebpage_obj = content(requestpost, as="parsed")
      #Parse Table
      tryCatch({tmptbl = tempwebpage_obj %>%
        html_nodes("#dgTop50") %>%
        html_table(fill = TRUE) %>%
        .[[1]]}, error=function(err) { warning(paste0("Could not Parse Table for :",dates[i]))})
        }
       
      #Check if Date of page matches with iterated date
      select =  tempwebpage_obj %>%
        html_nodes("option") %>%
        html_attr("value") 
      selected_idx =  tempwebpage_obj %>%
        html_nodes("option") %>%
        html_attr("selected") 
      selval = select[which(selected_idx == "selected")]
      
      if(dates[i] != selval ){
        print(paste0("Iterated Date:",dates[i], " does not MATCH website date:",selval))
      }
      
      
      
      #Combine iterated tables for later combination.
      temptopBHC = as.data.frame(tmptbl)
      
      #Column Transformations
      temptopBHC$Rank = as.factor(temptopBHC$Rank)
      temptopBHC$Location = as.factor(temptopBHC$Location)
      temptopBHC$RSSD_ID = as.factor(
        gsub("[\\(\\)]", "", regmatches(temptopBHC$`Institution Name (RSSD ID)`, gregexpr("\\(.[0-9]*?\\)", temptopBHC$`Institution Name (RSSD ID)`))))
      temptopBHC$Institution_Name = as.factor(
        gsub("\\(.[0-9]*?\\)", "", temptopBHC$`Institution Name (RSSD ID)`)
      )
      #Need to remove trailing spaces.
      #sub("\\s+$", "", x)
      
      #Remove the original column
      temptopBHC$`Institution Name (RSSD ID)` = NULL
      
      #Generate Date Column
      temptopBHC$ReportDate = as.Date(rep(strsplit(names(temptopBHC)[3]," ")[[1]][1], times = nrow(temptopBHC)), format = '%m/%d/%Y')
      
      
      #Update Column Names
      names(temptopBHC)[3] = 'Total_Assets'
      
      #Update Total Assets Column
      temptopBHC$Total_Assets = as.numeric(str_replace_all(temptopBHC$Total_Assets, "[^[:alnum:]]", ""))
      topBHC = rbind(topBHC,temptopBHC)
      temptopBHC = NULL
      tempwebpage_tbl = NULL
      tmptbl = NULL
    }
    
    
      
    return(topBHC)   
}
    
#Create Folder Creation Structure.
File_Folder_Organizer = function(downloadlogobj, sourcedir, destdir , remove = TRUE, copy = TRUE)
  {

  if(remove){
    print(paste0("Deleting All Existing Directories: ",destdir))
    if (length(list.dirs(destdir)) > 0) unlink(destdir,recursive = TRUE)
       }
    #create dir if doesnt exist
  
  if(!dir.exists(destdir)){
    print(paste0("Creating Destination Directory:",destdir))
    dir.create(destdir)
    }
  print(paste0("Changing Working Directory to:",destdir))
  

  #Directory Creation based on Institution Name_RSSD, Report Name, Report Date, Report Type 
  
  #For files that are OK in Log and exisit
  tempcopyobjlog = filter(downloadlogobj, Status == 'OK') 
  print(paste0("Preparing to copy ",nrow(tempcopyobjlog),' files.'))
  for(i in 1:nrow(tempcopyobjlog))
  {
  #Check if file exists
  print(paste0("Checking if file exists: ",tempcopyobjlog$DownloadFilePath[i]))    
    if(file.exists(as.character(tempcopyobjlog$DownloadFilePath[i])))
      {
  
    #Check InstitutionName Dir and create
    
    tempinstrssd = paste0(destdir,tempcopyobjlog$Institution_Name[i],'| ',tempcopyobjlog$RSSD_ID[i])
    tempreportdir = paste0(tempinstrssd,'/',tempcopyobjlog$ReportType[i])
    #tempreportdate = paste0(tempreportdir,'/',as.character(tempcopyobjlog$ReportDate.y)[i])
    print(paste0("Checking directory path: ",tempreportdir))  
      if(!isTRUE(file.info(tempreportdir)$isdir)){dir.create(tempreportdir, recursive=TRUE)}
          if(copy){
                          print(paste0("Copying File to directory path"))
                          file.copy(as.character(tempcopyobjlog$DownloadFilePath[i]),
                                    tempreportdir, overwrite = TRUE)
                  } 
          if(!copy)
                 {
                    print(paste0("Moving File to directory path"))
                    file.rename(from = as.character(tempcopyobjlog$DownloadFilePath[i]),  
                                to = paste0(tempreportdir,'/',tempcopyobjlog$ReportFilename[i]))
                  }              
                    
          } else {print("File Does not Exist")}
        
      }
        
          print(paste0("File organization Complete"))
  
      }
      
#Entry Point
  
#Variables
destdir = "/Users/phn1x/ICDM_Research/Stress_Test_Research/StressTest_Research/FFIEC_Reports/"
basedir = "/Users/phn1x/ICDM_Research/Stress_Test_Research/StressTest_Research/"
rawdatadir = "/Users/phn1x/ICDM_Research/Stress_Test_Research/StressTest_Research/raw_pdf/"
ReportDates = c("20171231","20161231","20151231","20141231","20131231","20121231")
ReportTypes = c("BHCPR","FRY9C","FRY9LP","FRY15","FFIEC101","FFIEC102")

setwd("/Users/phn1x/ICDM_Research/Stress_Test_Research/StressTest_Research")
#Website Base
base_site = "https://www.ffiec.gov/nicpubweb/nicweb/HCSGreaterThan10B.aspx"

topBHC = BHC_Meta_Data_List_Generator(base_site,ReportDates)
#Download reports per RSSD and Date.
RSSD_IDs = unique(topBHC$RSSD_ID)
#unique(rawresults[,c("RSSD_ID","Institution_Name")]))

downloadpath = rawdatadir
dir.create(file.path(downloadpath))

BHCWebAPILinks = FFIEC_BHC_WebAPI_UrlCreator(RSSD_IDs,ReportDates,ReportTypes,downloadpath)


DownloadBHCLog = WebAPI_URLLink_Downloader(BHCWebAPILinks)

#Join on RSSD_ID Institute names
# TODO: Enhance Functions to handle the TopBHC and attach to object or merge.
DownloadBHCLog_a = merge(unique(topBHC[,c("RSSD_ID","Institution_Name","Location")]),DownloadBHCLog, by = "RSSD_ID")

#FIX bad dir from improper working dir
#DownloadBHCLog_a$DownloadFilePath = gsub('/FFIEC_Reports/','/',DownloadBHCLog_a$DownloadFilePath)

#Put files into directories.
#Make sure that the destination for donwload is accurate from the log.
File_Folder_Organizer(DownloadBHCLog_a, sourcedir = rawdatadir,
                  destdir = destdir, remove = TRUE,copy = FALSE)

#TODO: Convert files into readable tables
#TODO: Store data into databases and dataframes.
#TODO: Analyze data with respect to CCAR and Stress Tests







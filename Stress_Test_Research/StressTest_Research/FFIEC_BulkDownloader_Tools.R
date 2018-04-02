#Generic Functions to pull data from FFEIC
#Library Dependencies

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
WebAPI_URLLink_Downloader = function(BHCWebAPILinks, clearfiles = TRUE, cleardir = TRUE){


  
        
  
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
          if (file.exists(tempdownloadfilepath)) file.remove(tempdownloadfilepath)
          
        }
        
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
        if (!file.exists(tempdownloadfilepath)) {
          print(paste0("FAILED to Download File: ", tempobj[["ReportDownload"]], " to ", tempdownloadfilepath))
          
          resultobj = data.frame(RSSD_ID = as.character(tempobj$RSSD_ID), 
                                   ReportType = as.character(tempobj$ReportType),
                                   ReportDate = as.character(tempobj$ReportDate),
                                   ReportFilename = as.character(tempobj$filename),
                                   DownloadFilePath =  as.character(tempdownloadfilepath), 
                                   Status = "FAILED") 
  
          DownloadStatusLog = rbind(DownloadStatusLog, resultobj)
          
          #setInternet2(TRUE)
          #download.file(fileURL ,destfile,method="auto") }
          #load("./data/samsungData.rda")
        } 
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

    #Read base site
    webpage = read_html(base_site)
    
    
    #Get list of dates so we can get all BHCs for different dates to create reference BHC table.
    
    
    
    select =  webpage %>%
      html_nodes("option") %>%
      html_attr("value") 
    selected_idx =  webpage %>%
      html_nodes("option") %>%
      html_attr("selected") 
    
    selected_val = select[which(selected_idx == "selected")]
    
    
    #Get Tables for to walk through all BHCs
    #tbls = html_nodes(webpage, "table")
    
    tbls_ls <- webpage %>%
      html_nodes("#dgTop50") %>%
      html_table(fill = TRUE) %>%
      .[[1]]
    
    topBHC = as.data.frame(tbls_ls)
    
    #Column Transformations
    topBHC$Rank = as.factor(topBHC$Rank)
    topBHC$Location = as.factor(topBHC$Location)
    topBHC$RSSD_ID = as.factor(
      gsub("[\\(\\)]", "", regmatches(topBHC$`Institution Name (RSSD ID)`, gregexpr("\\(.[0-9]*?\\)", topBHC$`Institution Name (RSSD ID)`))))
    topBHC$Institution_Name = as.factor(
      gsub("\\(.[0-9]*?\\)", "", topBHC$`Institution Name (RSSD ID)`)
    )
    #Need to remove trailing spaces.
    #sub("\\s+$", "", x)
    
    #Remove the original column
    topBHC$`Institution Name (RSSD ID)` = NULL
    
    #Generate Date Column
    topBHC$ReportDate = as.Date(rep(strsplit(names(topBHC)[3]," ")[[1]][1], times = nrow(topBHC)), format = '%m/%d/%Y')
    

    #Update Column Names
    names(topBHC)[3] = 'Total_Assets'
    
    #Update Total Assets Column
    topBHC$Total_Assets = as.numeric(str_replace_all(topBHC$Total_Assets, "[^[:alnum:]]", ""))
 
    return(topBHC)   
}
    
#Entry Point


#Website Base
base_site = "https://www.ffiec.gov/nicpubweb/nicweb/HCSGreaterThan10B.aspx"

topBHC = BHC_Meta_Data_List_Generator(base_site)



#Download reports per RSSD and Date.
RSSD_IDs = topBHC$RSSD_ID
ReportDates = c("20171231","20161231","20151231")
ReportTypes = c("BHCPR","FRY9C","FRY9LP","FRY15","FFIEC101","FFIEC102")
downloadpath = paste0(getwd(),"/raw_pdf/" )  
dir.create(file.path(downloadpath))

BHCWebAPILinks = FFIEC_BHC_WebAPI_UrlCreator(RSSD_IDs,ReportDates,ReportTypes,downloadpath)
View(head(BHCWebAPILinks))


DownloadBHCLog = WebAPI_URLLink_Downloader(BHCWebAPILinks)
View(DownloadBHCLog)




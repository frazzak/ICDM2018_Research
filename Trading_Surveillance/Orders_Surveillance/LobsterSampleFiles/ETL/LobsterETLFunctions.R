##Dependencies
if (!require("lubridate")) {
  install.packages("lubridate")
}
library("lubridate")

### Test Variables
wd = "~/Google Drive/Spring 2018/ICDM 2018/Trade Surveillance/LOBSTER_SampleFile/csv"
###

#Add parallelization?
LobsterFileImporter = 
  function(wd,type,header=FALSE)
  {
    setwd(wd)
    results = data.frame()
  #File List to import  
  files2import = list.files(wd,'*.csv')
  
  for ( i in 1:length(files2import))
  {
    #File Name Meta Elements
    FileNameElements = strsplit(files2import[i],'_')
    TempSymbol = FileNameElements[[1]][1]
    TempTradeDate = as.Date(FileNameElements[[1]][2])
    TempFileLevel = as.integer(gsub(".csv","",FileNameElements[[1]][6]))
    TempFileType =  FileNameElements[[1]][5] 

  if(TempFileType == 'message')
  {
    print(paste("Importing File",files2import[i],sep = " "))
      
          results = rbind(results,LobsterMessageFileParser(wd,files2import[i],TempSymbol,TempTradeDate,TempFileLevel,TempFileType,header))
          print("File Import/Transforms Complete")
          
          
    }
  else if (TempFileType == 'orderbook')
  {
      #print("Function no yet available")
  }
  else print("File Type not Recognized")
   

     }
  
  print("Returning Results")
  return(results)
  
  }



#############################################################################

LobsterMessageFileParser = 
    function(wd,filename,TempSymbol,TempTradeDate,TempFileLevel,TempFileType, header)
    {
      setwd(wd)
      tempfileobj = read.csv(filename , header=header)
      print("Checking for Headers")
      if(header == FALSE)(names(tempfileobj) = c('Time', 'Type', 'Order_ID','Size', 'Price', 'Direction' ))
      
      #Transformations
      print("Performing Transformations")
        #Message Blotter Time Adjust
          Trade_Date_Vector = rep(TempTradeDate, times = nrow(tempfileobj['Time']))
      Adj_Time = format(Trade_Date_Vector + seconds(tempfileobj['Time'][,1]) , '%Y-%m-%d %H:%M:%OS6')
      Adj_Time2 = as.POSIXct(Adj_Time,format="%Y-%m-%d %H:%M:%OS", tz = "America/New_York")
      op = options(digits.secs = 6)
      #Update Column
      tempfileobj['TimeAdj'] = Adj_Time2
      #Update Message Blotter to  Adjust Price
      tempfileobj['PriceAdj'] = tempfileobj['Price']/1000
      #Direction Message Blotter Update
      #                         Direction:
      #                       - '-1'  Sell limit order
      #                       - '-2'  Buy limit order
      #                       - NOTE: Execution of a sell (buy)
      #                               limit order corresponds to
      #                               a buyer-(seller-) initiated
      #                               trade, i.e. a BUY (SELL) trade.
      DirectionAdjTransform = Vectorize(function(x)
      {
        switch(as.character(x), 
               '1' = 'Buy',
               '-1' = 'Sell',
               as.character(x)
        )
      },"x")
      
      tempfileobj$DirectionAdj = NA
      tempfileobj$DirectionAdj = sapply(tempfileobj$Direction, DirectionAdjTransform)
      #Add Buyer/Seller iniated Trade Column
      tempfileobj$Initiated = ifelse(tempfileobj$DirectionAdj == 'Buy', 'Seller','Buyer')
      
      
      
      
      #Upate Type Message in Mesage Blotter
      # Event Type:
      # 1: Submission of a new limit order
      # 2: Cancellation (partial deletion of a limit order)
      # 3: Deletion (total deletion of a limit order)
      # 4: Execution of a visible limit order
      # 5: Execution of a hidden limit order
      # 6: Indicates a cross trade, e.g. auction trade
      # 7: Trading halt indicator (detailed information below)
      
      EventTypeTransform = Vectorize(function(x)
      {
        switch(as.character(x), 
               '1' = 'NEW',
               '2' = 'CANCELLATION',
               '3' = 'DELETION',
               '4' = 'EXECUTION VISIBLE ORDER',
               '5' = 'EXECUTION HIDDEN ORDER',
               '6' = 'CROSS TRADE',
               '7' = 'TRADING HALT',
               as.character(x)
        )
      },"x")
      
      tempfileobj$EventTypeAdj = NA
      tempfileobj$EventTypeAdj = sapply(tempfileobj$Type, EventTypeTransform)
      
      print("Creatng Imported Object")
      tempfileobj_post = data.frame(tempfileobj$Order_ID,tempfileobj$EventTypeAdj,TempSymbol,tempfileobj$TimeAdj,tempfileobj$DirectionAdj,tempfileobj$PriceAdj,tempfileobj$Size,tempfileobj$Initiated)
      print("Adding Reordered Headers")
      names(tempfileobj_post) =  c('OrderID', 'EventType_Adj','Symbol','Time_Adj','Direction_Adj', 'Price_Adj', 'Size_Adj','Initiated')
      print("Returning Imported File Object")
      return(tempfileobj_post)
    }







#Entry Point
LobsterMessageFiles_Output = LobsterFileImporter(wd,message)

#summary(LobsterMessageFiles_Output)


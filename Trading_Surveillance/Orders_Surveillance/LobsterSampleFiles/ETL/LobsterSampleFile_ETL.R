#Install Helper Libraries
if (!require("lubridate")) {
  install.packages("lubridate")
}

#Import Sample Orderbook and Message Blotter

AMZN_OrderBook <- read.csv("~/Google Drive/Spring 2018/ICDM 2018/Trade Surveillance/LOBSTER_SampleFile/AMZN_2012-06-21_34200000_57600000_orderbook_10.csv", header=FALSE)

AMZN_Message <- read.csv("~/Google Drive/Spring 2018/ICDM 2018/Trade Surveillance/LOBSTER_SampleFile/AMZN_2012-06-21_34200000_57600000_message_10.csv", header=FALSE)

Symbol = 'AMZN'
Trade_date = as.Date('2012-06-21')
Level = 10

#Need to parse from file name Symbol, Date, Data Type, Level


#Update Header Names
  names(AMZN_Message) = c('Time', 'Type', 'Order_ID','Size', 'Price', 'Direction' )

#Prep Headers for OrderBook  
  orberbook_Header_Pre = c('Ask Price', 'Ask Size','Bid Price','Bid Size')
  header_level_times = length(names(AMZN_OrderBook))/length(orberbook_Header_Pre)
  orberbook_Header_Pre2 = paste(rep(orberbook_Header_Pre, times = header_level_times ) ,rep(1:header_level_times, each = length(orberbook_Header_Pre), times = 1), sep = " ")
  names(AMZN_OrderBook) = orberbook_Header_Pre2
  
#Transformations
  #Message Blotter Time Adjust
  Trade_Date_Vector = rep(Trade_date, times = nrow(AMZN_Message['Time']))
  Adj_Time = format(Trade_Date_Vector + seconds(AMZN_Message['Time'][,1]) , '%Y-%m-%d %H:%M:%OS6')
  Adj_Time2 = as.POSIXct(Adj_Time,format="%Y-%m-%d %H:%M:%OS", tz = "America/New_York")
  op = options(digits.secs = 6)
    #Update Column
    AMZN_Message['TimeAdj'] = Adj_Time2
  #Update Message Blotter to  Adjust Price
    AMZN_Message['PriceAdj'] = AMZN_Message['Price']/1000
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
    
    AMZN_Message$DirectionAdj = NA
    AMZN_Message$DirectionAdj = sapply(AMZN_Message$Direction, DirectionAdjTransform)
    #Add Buyer/Seller iniated Trade Column
    AMZN_Message$Initiated = ifelse(AMZN_Message$DirectionAdj == 'Buy', 'Seller','Buyer')
    
    
    
    
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
    
    AMZN_Message$EventTypeAdj = NA
    AMZN_Message$EventTypeAdj = sapply(AMZN_Message$Type, EventTypeTransform)
    
    

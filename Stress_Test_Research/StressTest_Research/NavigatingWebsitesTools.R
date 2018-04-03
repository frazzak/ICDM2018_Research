#Generic Functions to pull data from FFEIC
#Library Dependencies
#install.packages("devtools")
#install.packages("RSelenium")
#library(devtools)
#devtools::install_github("ropensci/RSelenium")
if (!require("RSelenium")) {
  install.packages("RSelenium")
}

library(RSelenium)


if (!require("RCurl")) {
  install.packages("RCurl")
}

library(RCurl)

if (!require("XML")) {
  install.packages("XML")
}
library(XML)

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

#Insert data into input fields example
#query = "data science"
#loc = "New York"
#session <- html_session("http://www.indeed.com")
#form <- html_form(session)[[1]]
#form <- set_values(form, q = query, l = loc)


#url <- "http://www.footballoutsiders.com/stats/snapcounts"
#pgsession <- html_session(url)
#pgform <-html_form(pgsession)[[3]]

#Dependencies
library(httr)
library(rvest)
#library(tidyverse)
base_site = "https://www.ffiec.gov/nicpubweb/nicweb/HCSGreaterThan10B.aspx"

#Read in the base page
pre_pg <- read_html("https://www.ffiec.gov/nicpubweb/nicweb/HCSGreaterThan10B.aspx")

#Collect hidden attributes
hidden = setNames(
  html_nodes(pre_pg, "input[type='hidden']") %>% html_attr("value"),
  html_nodes(pre_pg, "input[type='hidden']") %>% html_attr("name")
) 

#Post with hidden attributes , generate a request
resquestpost = 
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
              DateDropDown = '20150930'
            ), 
            encode = "form"
          ) 
    #Store response as parsed content
    pg = content(res,as="parsed")
    #Parse Table
    pg %>%
      html_nodes("#dgTop50") %>%
      html_table(fill = TRUE) %>%
      .[[1]]









#base_session = html_session(base_site)
#form_session = html_form(session)[[1]]
#setvalues = set_values(form_session, 
                       "DateDropDown" = '20150930'
                       )
#Does not work since it is aspx
#submit_form(session = base_session, form = setvalues, POST = base_site)

#test = follow_link(session,xpath = '//*[@id="DateDropDown"]/option[2]')


#webpage = read_html(base_site)


#Get list of dates so we can get all BHCs for different dates to create reference BHC table.



select =  webpage %>%
  html_nodes("option") %>%
  html_attr("value") 
selected_idx =  webpage %>%
  html_nodes("option") %>%
  html_attr("selected") 

selected_val = select[which(selected_idx == "selected")]

(selected_val)

#Get Tables for to walk through all BHCs
#tbls = html_nodes(webpage, "table")

tbls_ls <- webpage %>%
  html_nodes("#dgTop50") %>%
  html_table(fill = TRUE) %>%
  .[[1]]

topBHC_test = as.data.frame(tbls_ls)

head(topBHC_test)



library(RCurl)
library(xml2)

curl = getCurlHandle()

#link = "http://indiawater.gov.in/IMISReports/Reports/WaterQuality/rpt_WQM_HabitationWiseLabTesting_S.aspx"

html = getURL(base_site, curl = curl)

#//*[@id="DateDropDown"]/option[1]

params = list('ctl00$ContentPlaceHolder$ddFinYear' = '2005-2006',
              'ctl00$ContentPlaceHolder$ddState' = 'BIHAR')

html2 = postForm(base_site, .params = params, curl = curl)

table = readHTMLTable(html2 )
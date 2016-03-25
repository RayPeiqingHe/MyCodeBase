library(rCharts)
library(reshape2)
library(shiny)
library(plyr)
library(magrittr)
library(ggplot2)
library(openxlsx)

UpdateSelectInput <- function(session, file)
{
  data <- read.xlsx(file$datapath, sheet=1)
  
  if(!exists("inData")) 
  {
    assign("inData", data)
  }
  
  cols <- colnames(inData)
  
  cols <- cols[cols != 'Date']
  
  updateSelectInput(session, "depdentVar",
                    choices = cols,
                    selected = cols[1]
  )
  
  updateCheckboxGroupInput(session, "exVars",
                           choices = cols,
                           selected = NULL
  )
}

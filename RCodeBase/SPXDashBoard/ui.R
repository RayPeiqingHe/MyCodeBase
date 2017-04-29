
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)

shinyUI(fluidPage(

  fluidRow(
    column(3, actionButton("refresh", "Refresh Data", width = "200px"))
  ),
  mainPanel(
  tabsetPanel(
    "S & P 500" %>% 
    tabPanel(
    dygraphOutput("f1", height = "1000px")
    ),
    "Russell 2000" %>% 
    tabPanel(
      dygraphOutput("f2", height = "1000px")
    ) 
    ), style='width: 2100px; height: 1000px'   
  )
))

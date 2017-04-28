
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
  
  verticalLayout(
    dygraphOutput("f1", height = "1000px")
    )
))

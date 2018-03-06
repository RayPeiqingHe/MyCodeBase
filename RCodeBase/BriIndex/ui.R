
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library (DT)
library(plotly)

indexList = c("BRI US Long/Short Equity Index"="bri", 
              "HFRX Equity Hedge Index"="hfrx")

indexCtrl = selectInput("Index", "Fund Index:", indexList)

benchMarkIndexCtrl = selectInput("Index", "Benchmark Index:", indexList)

button = actionButton("refreshButton", "Refresh Data", width = "200px")

shinyUI(fluidPage(

  # Application title
  titlePanel("BRI US Long/Short Equity Index")
  
  ,fluidRow(
            column(4,
                   fluidRow(indexCtrl)
            ),
            column(4,
                   fluidRow(benchMarkIndexCtrl)
            ),
            column(4,
                   fluidRow(div(style="margin-top: 24px", button))
            )
  )
  
  ,titlePanel("Summary Statistics")
  
  ,DT::dataTableOutput('tbl')
  
  ,hr()
  
  ,titlePanel("Growth of $100")
  
  ,dygraphOutput("growth100", height = "500px")
  
  ,hr()
  
  ,titlePanel("Monthly Returns")
  
  ,DT::dataTableOutput('monthlyRet')
  
  ,hr()
  
  ,titlePanel("Draw Down")
  
  ,dygraphOutput("drawDown", height = "500px")
  
  ,titlePanel("DrawdownFrequency Histogram")
  
  ,plotOutput(outputId = "distPlot")
  
  ,fluidRow(12,
            column(6,
                   fluidRow(
                   titlePanel('Regression, Capture')
                   ,DT::dataTableOutput('captureRatio')
                   )
                   ),
            column(6,
                   fluidRow(
                   titlePanel('Linear Regression')
                   ,plotOutput("lmPlot")
                   )
                   )
  )
  
  ,fluidRow(12,
           column(6,
                  fluidRow(
                  titlePanel("Window Analysis")
                  , DT::dataTableOutput('windowAnalysis')
                  )
                  ),
           column(6,
                  fluidRow(
                    titlePanel("Rolling 12 Month Returns")
                  , dygraphOutput("rollingPlot", height = "500px")
                  )
                  )
  )

  ,fluidRow(12,
             column(6,
                    fluidRow(
                      titlePanel("Recent Performance")
                      , DT::dataTableOutput('recentPerformance')
                    )
             ),
             column(6,
                    fluidRow(
                      titlePanel("Annualized Risk/Return")
                      , plotlyOutput("riskReturnPlot")
                    )
             )
   )
))

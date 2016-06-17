
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)

fileInputCtl <- fileInput('inputFile', 'Upload .csv',
              accept=c('text/csv', 
              'text/comma-separated-values,text/plain', '.csv'))

checkBoxCtl <- checkboxGroupInput("periodicity", "Periodicity:",
                c("D" = 1,"M" = 2), selected = 1)

DateRange <- dateRangeInput(
  # GUI input to define the portfolios to view.
  inputId = "date_range",
  label = "Date range",
  start = Sys.Date(),
  end = Sys.Date(),
  min = Sys.Date(),
  max = Sys.Date(),
  format = "mm/dd/yyyy",
  startview = "month",
  weekstart = 0,
  language = "en",
  separator = " to "
  #,width="200px"
)

lookBackInput <- numericInput("lookBack", "Look Back", 60,
                              min = 1, max = 100, width="100px")


exVars <- checkboxGroupInput(

  inputId = "exVars",
  label   = "Select Explainatory Vars",
  
  choices = NULL,
  
  selected = NULL,
  inline                = FALSE
)


ui <- basicPage(
  # Changes by Ray
  # Handler for the popup
  tags$head(tags$script(HTML('Shiny.addCustomMessageHandler("jsCode",function(message) {eval(message.value);});'))
            
  ),
  
  titlePanel(""),
  
  div(style="position: relative;",
      wellPanel(style="position: absolute; width: 400px; left: 0; top: 0; height: auto;",

                fluidRow(column(8, fileInputCtl)
                         , column(3, checkBoxCtl))
                
                ,DateRange
                
                ,lookBackInput
                
                ,selectInput("dependVar", "Select Dependant Var", choices = NULL)
                
                ,actionButton("calculate","Calculate")
                
                ,br()
                
                ,br()
                
                ,wellPanel(exVars)
      )
  )
      ,
      div(style="position: absolute; left: 410px; right: 0; top: 0; height: auto;",
          titlePanel(""),
          mainPanel(tableOutput("t1")

                    ,chartOutput("f2", "nvd3")
                    ,br()
                    ,chartOutput("f1", "nvd3")
                    )
        )
  )

shinyUI(ui)

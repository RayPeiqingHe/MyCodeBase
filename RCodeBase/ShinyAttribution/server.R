
# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)

# Show popup message
ShowPopup <- function(session, msg){
  my_slider_check_test <- msg
  js_string <- 'alert("SOMETHING");'
  js_string <- sub("SOMETHING",my_slider_check_test,js_string)
  
  session$sendCustomMessage(type='jsCode', list(value = js_string))  
}


shinyServer(function(input, output, session) {

  colData <- reactive({

    cols <- c("Date", input$dependVar, input$exVars)
    
    d <- inData[, cols]
    
    d
  })
  
  filterData <- reactive({
    subset(colData(),
           Date >= as.Date(input$date_range[1]) &
             Date <= as.Date(input$date_range[2])
    )
    
  }
  )
  
  periodicity <- reactive({

    if (input$periodicity == 1)
      252.
    else
      12.
  })
  
  lookBack <- reactive({

    input$lookBack
  })
  
  inputFile <- reactive({
    
    input$inputFile
  })
  
  observeEvent(inputFile(), {
    UpdateSelectInput(session, inputFile())
  })
  
  calc <- eventReactive(input$calculate, {
    
    if (lookBack() < 1)
      ShowPopup(session, "Please enter a valid positive number")
    else if (is.null(input$periodicity))
      ShowPopup(session, "Please specify periodicity")
    else if (length(input$exVars) == 0)
      ShowPopup(session, "Please check at least one Explainatory Vars")
    else if (input$date_range[1] > input$date_range[2])
      ShowPopup(session, "Start Date must be less than End Date")
    else if (input$date_range[1] > maxDate || input$date_range[2] < minDate)
      ShowPopup(session, paste("Date range must be between", minDate, "and", maxDate))
    else
    {
      t1 <- T1(filterData(), periodicity(), input$dependVar, input$exVars)
      
      f1 <- F1(filterData(), input$dependVar, input$exVars)
      
      f2 <- F2(filterData(), input$dependVar, input$exVars, input$lookBack)
        
      list(t1 = t1, f1 = f1, f2=f2)
    }
  })
  
  output$t1 <- renderTable({calc()$t1})

  output$f1 <- renderChart2({calc()$f1})
  
  output$f2 <- renderChart2({calc()$f2})
})

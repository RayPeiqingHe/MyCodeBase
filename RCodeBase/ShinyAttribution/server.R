
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
    else
      lookBack()
  })
  
  output$lookBack <- renderText({
    calc()
  })

})

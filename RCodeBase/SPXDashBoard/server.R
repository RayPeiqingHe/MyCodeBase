
# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)

shinyServer(function(input, output) {
  
  v <- reactiveValues(data = NULL)
  
  observeEvent(input$refresh, {
    v$data <- plot()
  })
  
  output$f1 <- renderDygraph({
    if (is.null(v$data))
    {
      plot()
    }
    else
      v$data
  })

})

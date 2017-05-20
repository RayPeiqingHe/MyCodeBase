
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
    
    v$data2 <- plot("RU2000PR", "Russell 2000")
  })
  
  output$f1 <- renderDygraph({
    if (is.null(v$data))
    {
      plot('SP500')
    }
    else
      v$data
  })

  output$f2 <- renderDygraph({
    if (is.null(v$data))
    {
      plot("RU2000PR", "Russell 2000")
    }
    else
      v$data2
  })
})

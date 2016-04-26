# Defines how inputs are used to compute the outputs defined by ui.R
# ==============================================================================

library(shiny)

shinyServer(function(input, output, session) {

    groupBy <- reactive({
      input$groupby
    })   
    
    e <- reactive({
      
      subset(d,
        date >= as.Date(input$date_range[[1]]) &
        date <= as.Date(input$date_range[[2]]) &
        industry %in% c(input$industries, input$Indices)
      )
    }
    )
    
    portfoliosExIndices <- reactive(
      {
        c(input$portfoliosLongOnly, input$portfoliosHedge)
      }
    )
    
    portfolios <- reactive(
    {
      c(input$portfoliosLongOnly, input$portfoliosHedge, 
        sapply(input$Indices, function(x){paste("INDEX -", x)}))
    }
    )
    
    # Changes by Ray
    # Update the date range for MTD button
    observeEvent(input$mtd, {
      UpdateDateRange(session, GetFirstDate(format(Sys.Date(), "%Y"), format(Sys.Date(), "%m")), 
                      as.character(Sys.Date()))
    })
    
    # Update the date range for YTD button
    observeEvent(input$ytd, {
      UpdateDateRange(session, GetFirstDate(format(Sys.Date(), "%Y"), "01"), as.character(Sys.Date()))
    })
    
    # Update the date range for Inception button
    observeEvent(input$inception, {
      UpdateDateRange(session, dateRange[1], dateRange[2])
    })
    
    calc <- function() {F2(e(), portfolios()[1:2])}
    
  output$f1 <- renderChart2({F1(e(), portfolios())})
  
  output$t1 <- renderTable({T1(e(), portfolios()) %>% data.frame})
  
  output$f2 <- renderChart2({calc()$plot})
  
  output$t2 <- renderUI({calc()$text})
  
  output$f3 <- renderChart2({F3(e(), portfolios(), groupBy())})
  
  output$f4 <- renderChart2({F4(e(), portfoliosExIndices())})
})

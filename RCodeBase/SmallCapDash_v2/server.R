# Defines how inputs are used to compute the outputs defined by ui.R
# ==============================================================================

library(shiny)

shinyServer(function(input, output, session) {

    groupBy <- reactive({
      input$groupby
    })   
    
    groupBy2 <- reactive({
      input$groupby2
    })   
    
    industries <- reactive({
      input$industries
    })
    
    e <- reactive({
      subset(d,
        date >= as.Date(input$date_range[[1]]) &
        date <= as.Date(input$date_range[[2]]) &
        industry %in% c(industries(), input$Indices)
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
        if (length(input$Indices) > 0) paste("INDEX - ", input$Indices, sep = ""))
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
    
    observe({
      if (input$selectall > 0) {
        if (input$selectall %% 2 == 0){
          updateCheckboxGroupInput(session=session, 
                                   inputId="industries",
                                   choices = subset(d, portgroup != "INDEX")$industry %>% as.character %>% unique,
                                   selected = subset(d, portgroup != "INDEX")$industry %>% as.character %>% unique)
          
        } else {
          updateCheckboxGroupInput(session=session, 
                                   inputId="industries",
                                   choices = subset(d, portgroup != "INDEX")$industry %>% as.character %>% unique,
                                   selected = c())
          
        }}
    })
    
    calc <- function() {F2(e(), portfolios()[1:2])}
    
  output$f1 <- renderChart2({F1(e(), portfolios())})
  
  output$t1 <- renderTable({T1(e(), portfolios()) %>% data.frame})
  
  output$f2 <- renderChart2({calc()$plot})
  
  output$t2 <- renderUI({calc()$text})
  
  #output$f3 <- renderChart2({F3(e(), portfolios(), groupBy())})
  reactive({F3_2(e(), portfolios(), groupBy())}) %>% bind_shiny("f3")
  
  #output$f4 <- renderChart2({F4(e(), portfoliosExIndices(), groupBy2())})
  #reactive({F4_2(e(), portfoliosExIndices(), groupBy2())}) %>% bind_shiny("f4")
  output$f4 <- renderDygraph({F4_3(e(), portfoliosExIndices(), groupBy2())})
  
  output$f5 <- renderChart2({F5(e(), portfolios())})
})

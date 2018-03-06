
# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(plotly)

shinyServer(function(input, output) {
  
  v <- reactiveValues(data = NULL)
  
  v2 <- reactiveValues(summaryStats = NULL)
  
  observeEvent(input$refresh, {
    v$data <- plotGrowth100()
    v2$summaryStats <- GetSummeyStatistics()
  })
  
  output$growth100 <- renderDygraph({
    input$refreshButton
    
    if (is.null(v$data))
    {
      plotGrowth100('SP500')
    }
    else
      v$data
  })
  
  output$drawDown <- renderDygraph({
    input$refreshButton
    
    plotDrawDown()
  })
  
  # render DT
  output$tbl <- DT::renderDataTable({
    
    input$refreshButton
    
    if (is.null(v2$summaryStats))
      v2$summaryStats <- GetSummeyStatistics()
    
    DT::datatable(v2$summaryStats, 
              rownames = FALSE, 
              options = list(
                paging = FALSE,
                searching = FALSE, info=FALSE))
  })
  
  output$text2 <- renderUI({
    HTML("Monthly Returns")
  })
  
  output$monthlyRet <- DT::renderDataTable({
    input$refreshButton
    
    DT::datatable(calendarReturns(), options=list(
                                             paging = FALSE,
                                             searching = FALSE, info=FALSE)) %>%
      formatPercentage(1:13, digits = 2)
    })
  
  output$distPlot <- renderPlot({
    input$refreshButton
    
    returnHistogram()
  })
  
  output$captureRatio <- DT::renderDataTable(
    {
      input$refreshButton
      DT::datatable(GetCaptureStatistics(), 
                  rownames = FALSE,  
                  options=list(
                  paging = FALSE,
                  searching = FALSE, info=FALSE)) %>%
                  formatPercentage(1:13, digits = 2)
    }
  )
  
  output$lmPlot <- renderPlot({
    input$refreshButton
    
    getLinearRegressionPlot()
  })
  
  output$windowAnalysis <- DT::renderDataTable({
    input$refreshButton
    
    DT::datatable(GetWindowAnalysis(), 
                  rownames = FALSE,  
                  options=list(
                    paging = FALSE,
                    searching = FALSE, info=FALSE))
  }
  )
  
  output$rollingPlot <- renderDygraph({
    input$refreshButton
    
    getRolling12MonthsReturnPlot()
  })
  
  output$recentPerformance <- DT::renderDataTable({
    input$refreshButton
    
    DT::datatable(GetRecentPerformance(), 
                  rownames = FALSE,  
                  options=list(
                    paging = FALSE,
                    searching = FALSE, info=FALSE)) %>%
      formatPercentage(1:13, digits = 2)
  }
  )
  
  output$riskReturnPlot <- renderPlotly({
    input$refreshButton
    
    plotRiskReturnScatter()
  })
})

library(rCharts)
library(reshape2)
library(shiny)
library(plyr)
library(magrittr)
library(ggplot2)
library(openxlsx)
library(PerformanceAnalytics)

ExcelDate <- function(dt) {as.Date(dt - 2, origin="1900-1-1")}

percent_format <- "#!function(y) {return y.toFixed(2)}!#"

# Percent format ##.##%
percent_format2 <- "#! function(d) {return (d*100).toFixed(2) + '%' } !#"

UpdateSelectInput <- function(session, file)
{
  data <- read.xlsx(file$datapath, sheet=1)
  
  data <- arrange(data, Date)
  
  data["Date"] <- lapply(data["Date"], ExcelDate)
  
  assign("inData", data, envir = .GlobalEnv)
  
  assign("minDate", min(inData[,"Date"]), envir = .GlobalEnv)
         
  assign("maxDate", max(inData[,"Date"]), envir = .GlobalEnv)
  
  cols <- colnames(inData)
  
  cols <- cols[cols != 'Date']
  
  updateSelectInput(session, "dependVar",
                    choices = cols,
                    selected = cols[1]
  )
  
  updateCheckboxGroupInput(session, "exVars",
                           choices = cols,
                           selected = NULL
  )
  
  updateDateRangeInput(session, "date_range",
                       label = NULL,
                       start = min(inData[,"Date"]),
                       end = max(inData[,"Date"]))
}


T1 <- function(d, pd) {
  
  data_cols <- colnames(d)[colnames(d) != 'Date']
  
  # Maximum drawdown
  ts_ret <- xts(d[data_cols], d$Date)
  
  d <- d[,data_cols]
  
  # Annual Return
  tb <- t(data.frame((apply(d + 1, 2, prod) ^ (pd / nrow(d)) - 1) * 100))
  
  rownames(tb) <- "Annual Rets"
  
  # Vol
  vol <- t(data.frame(apply(d, 2, sd) * 100 * sqrt(pd)))
  
  rownames(vol) <- "vol"
  
  # Sharpe
  sharpe <- tb / vol
  
  rownames(sharpe) <- "sharpe"
  
  tb <- rbind(tb, vol, sharpe, maxDrawdown(ts_ret) * 100)
}

F1 <- function(d, dependVar, exVars) {

  fit <- lm(d[[dependVar]] ~ . , data = d[exVars])
  
  
  
  pred <- fitted(fit)
  
  d <- cbind(d, pred)[, c(dependVar, "pred")]
  
  colnames(d) <- c("y", "x")
  
  d <- cbind(d, size="8", s="Regression")
  
  out <- nPlot(y ~ x,
               data  = d,
               type  = "scatterChart"
               ,group = "s"
  ) %T>%
    
    .$yAxis(tickFormat=percent_format2, axisLabel=dependVar) %T>%
    .$xAxis(tickFormat=percent_format2, axisLabel=paste("Predicted",dependVar)) %T>%
    .$set(width=900, height=600) %T>%
    .$chart(
      size		= '#! function(d){return d.size} !#'
      ,showControls	= FALSE
    )
    
  out
}

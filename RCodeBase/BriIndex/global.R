library(quantmod)
library(shiny)
library(dygraphs)
library(TTR)
library(DT)
library(PerformanceAnalytics)
library(lubridate)
library(scales)
library(plotly)

rm(list=ls())

options("getSymbols.warning4.0"=FALSE)

startDate <<- "2014-01-01"

briIndex <<- NULL
hfrxIndex <<- NULL
firstDateOfYear <- paste0(format(Sys.Date(), "%Y"), "-01-01::") 

# Use SPX data as sample
GetDataBriIndexData <- function(ticker="SP500",from=startDate)
{
  data <- getSymbols(ticker,auto.assign = FALSE, src='FRED')
  
  data <- data[paste0(startDate, "::")]
  
  data <- na.omit(data[,ncol(data)])
  
  colnames(data) <- "BRI_US_Long_Short_Equity_Index"
  
  briIndex <<- data
}

GeTDataHfrxIndexData <- function(ticker="SP500",from=startDate)
{
  data <- getSymbols(ticker,auto.assign = FALSE, src='FRED')
  
  data <- data[paste0(startDate, "::")]
  
  data <- na.omit(data[,ncol(data)])
  
  data <- SMA(data[,1],n=50)
  
  colnames(data) <- "HFRX_Equity_Hedge_Index"
  
  hfrxIndex <<- data  
}

GetSummeyStatistics <- function()
{
  if (is.null(briIndex))
    GetDataBriIndexData()
  
  col1 <- c('Average Annualized Return'
           ,'Annualized Standard Deviation'
           ,'Sharpe Ratio'
           ,'Year To Date Return'
           ,'Last 12 Months Return'
           ,'Last 36 Months Return'
           ,'Growth of $100')
  
  briIndexRet <- na.omit((briIndex - lag(briIndex)) / lag(briIndex))
  annualizedRet <- Return.annualized(briIndexRet, scale = NA, geometric = FALSE)
  annualizedVol <- StdDev.annualized(briIndexRet, scale = NA)
  sharp <- SharpeRatio.annualized(briIndexRet, scale = NA, geometric = FALSE)
  ytdReturn <- Return.annualized(briIndexRet[firstDateOfYear], scale = NA)
  last_12m_date <- Sys.Date() %m-% months(12)
  last_36m_date <- Sys.Date() %m-% months(36)
  last_12m_ret <- Return.annualized(briIndexRet[paste0(format(last_12m_date, "%Y-%m-%d"), "::")], 
                                    scale = NA, geometric = FALSE)
  last_36m_ret <- Return.annualized(briIndexRet[paste0(format(last_36m_date, "%Y-%m-%d"), "::")], 
                                    scale = NA, geometric = FALSE)
  
  colDat <- as.vector(briIndex)
  
  growth100 <- 100 * colDat[length(colDat)] / colDat[1]
  
  max_Drop_Down <- maxDrawdown(briIndexRet, geometric = FALSE)
  
  avg_draw_down_length <- AverageLength(briIndexRet)
  
  # monthlyRet <- apply.monthly(briIndexRet, mean)
  
  avgDownMonth <- 0
    
  avgUpMonth <- 0
  
  pertNeg <- nrow(briIndexRet[briIndexRet < 0]) / nrow(briIndexRet)
  
  pertPos <- 1. - pertNeg
  
  yield <- 0
  
  col3 <- c('Max Draw Down'
            ,'Length of Draw Down'
            ,'Average Down Month'
            ,'Average Up Month'
            ,'Percent Negative'
            ,'Percent Positive'
            ,'Yield')
  
  perc <- c(customPercent(annualizedRet), customPercent(annualizedVol), 
            round(sharp, 2),
            customPercent(ytdReturn), customPercent(last_12m_ret)
            ,customPercent(last_36m_ret), round(growth100, 2))
  
  perc2 <- c(customPercent(max_Drop_Down), paste(round(avg_draw_down_length, 0), " days")
             ,customPercent(avgDownMonth), customPercent(avgUpMonth)
             ,customPercent(pertNeg), customPercent(pertPos), customPercent(yield))
  
  dat <- data.frame(Statistics = col1
                    ,Result = perc
                    ,Statistics = col3
                    ,Result = perc2
                    )
  
  colnames(dat) <- c('', '', '', '')
  
  dat
}

customPercent <- function(num)
{
  if (num < 0)
    paste0("(", percent(num * -1), ")")
  else
    percent(num)
}


plotDrawDown <- function(ticker="^GSPC", title = "Draw Down")
{
  if (is.null(briIndex))
    GetDataBriIndexData()
  
  if (is.null(hfrxIndex))
    GeTDataHfrxIndexData()
  
  data <- cbind(briIndex, hfrxIndex)
  
  dataRet <- na.omit((data - lag(data)) / lag(data))
  
  dataDrawDown <- PerformanceAnalytics:::Drawdowns(dataRet)
  
  # dygraph(dataDrawDown, main="Drawdown") %>%
  #   dySeries(colnames(briIndex)[1], strokeWidth = 2, axis = 'y2', fillGraph = TRUE, color = "blue") %>%
  #   dySeries(colnames(hfrxIndex)[1], strokeWidth = 2, color = "red") %>%
  #   dyLegend(width = 800, show = "follow")
  
  plotTS(dataDrawDown, "", "follow", showPercentage=TRUE)
}


plotGrowth100 <- function(ticker="^GSPC", title = "SPX 500")
{
  if (is.null(briIndex))
     GetDataBriIndexData()
  
  if (is.null(hfrxIndex))
      GeTDataHfrxIndexData()

  data <- cbind(briIndex, hfrxIndex)
  
  ts <- na.omit(data)
  
  # scale both columns to 100
  ts[, 1] <- ts[, 1] / drop(coredata(ts[1, 1]))
  
  ts[, 2] <- ts[, 2] / drop(coredata(ts[1, 2]))
  
  ts <- ts * 100
  
  plotTS(ts, "")
}

plotTS <- function(ts, title, show="always", showPercentage=FALSE)
{
  p <- dygraph(ts, main = title) %>%
    dySeries(colnames(briIndex), strokeWidth = 2, axis = 'y2', fillGraph = TRUE, color = "blue") %>%
    dySeries(colnames(hfrxIndex), strokeWidth = 2, color = "red") %>%
    dyLegend(width = 800, show = show) 
  
  if (isTRUE(showPercentage))
  {
    p <- p %>%
      dyAxis("y",
             valueFormatter = "function(v){return (v*100).toFixed(1) + '%'}",
             axisLabelFormatter = "function(v){return (v*100).toFixed(0) + '%'}") %>%
      dyAxis("y2",
             valueFormatter = "function(v){return (v*100).toFixed(1) + '%'}",
             axisLabelFormatter = "function(v){return (v*100).toFixed(0) + '%'}")
  }
  
  p
}

calendarReturns <- function()
{
  if (is.null(briIndex))
    GetDataBriIndexData()  
  
  briIndexMonthlyRet <- do.call(cbind, lapply(briIndex, monthlyReturn))
  
  table.CalendarReturns(briIndexMonthlyRet, geometric = FALSE, as.perc=FALSE, digits=5)
}

returnHistogram <- function()
{
  if (is.null(briIndex))
    GetDataBriIndexData()
  
  briIndexMonthlyRet <- do.call(cbind, lapply(briIndex, monthlyReturn))
  
  bins <- 30
  
  bins <- seq(min(briIndexMonthlyRet[, 1]), max(briIndexMonthlyRet[, 1]), 
              length.out = bins + 1)
  
  h <- hist(briIndexMonthlyRet, breaks = bins, col = "#75AADB", border = "orange",
       xlab = "Monthly Return (%)",
       main = "Frequency Histogram")
}

getLinearRegressionPlot <- function() {

  if (is.null(briIndex))
    GetDataBriIndexData()
  
  if (is.null(hfrxIndex))
    GeTDataHfrxIndexData()
  
  data <- cbind(briIndex, hfrxIndex)
  
  annualizedRet <- na.omit((data - lag(data)) / lag(data))
  
  annualizedRet <- as.data.frame(annualizedRet)
  
  model <- lm(BRI_US_Long_Short_Equity_Index~HFRX_Equity_Hedge_Index
              , data = annualizedRet)
  
  plot(y = annualizedRet$BRI_US_Long_Short_Equity_Index, 
       x = annualizedRet$HFRX_Equity_Hedge_Index, xlab="",ylab="", panel.first = grid(),
       main = "BRIndex Returns (Y-Axis) vs. Comparison Series Returns (X-Axis)")
  
  abline(model, col = "blue", lwd = 2)
  
  legend("topleft", bty="n", legend=paste("R2 =", 
          format(summary(model)$adj.r.squared, digits=4)))

}

GetCaptureStatistics <- function()
{
  if (is.null(briIndex))
    GetDataBriIndexData()
  
  if (is.null(hfrxIndex))
    GeTDataHfrxIndexData()
  
  col <- c('Alpha (Annual)'
          ,'Beta'
          ,'Correlation'
          ,'R^2'
          ,'Up Capture'
          ,'Down Capture'
          ,'Capture Spread'
          ,'Up # Ratio'
          ,'Down # Ratio'
          ,'Ratio Spread'
          ,'Up Outperform'
          ,'Down Outperform'
          ,'Total Outperform')
  
  briRet <- do.call(cbind, lapply(briIndex, monthlyReturn))
  
  hfrxRet <- do.call(cbind, lapply(hfrxIndex, monthlyReturn))
  
  upDown <- UpDownRatios(briRet, hfrxRet, side=c("Up", "Down"), 
                         method = c("Capture", "Number", "Percent"))
  
  data <- cbind(briIndex, hfrxIndex)
  
  annualizedRet <- na.omit((data - lag(data)) / lag(data))
  
  annualizedRet <- as.data.frame(annualizedRet)
  
  model <- lm(BRI_US_Long_Short_Equity_Index~HFRX_Equity_Hedge_Index
              , data = annualizedRet)
  
  perc <- c(customPercent(model$coefficients[1]), 
            customPercent(model$coefficients[2]), 
            customPercent(cor(annualizedRet[, 1], annualizedRet[, 2])) , 
            customPercent(summary(model)$adj.r.squared),
            upDown[1], upDown[2], upDown[1] - upDown[2],
            upDown[3], upDown[4], upDown[3] - upDown[4],
            upDown[5], upDown[6], (upDown[5] + upDown[6]) / 2)
  
  dat <- data.frame(Statistics = col
                    ,Result = perc)
  
  dat
}

getRolling12MonthsReturnPlot <- function() {
  if (is.null(briIndex))
    GetDataBriIndexData()
  
  if (is.null(hfrxIndex))
    GeTDataHfrxIndexData()
  
  data <- cbind(briIndex, hfrxIndex)
  
  monthlyRet <- do.call(cbind, lapply(data, monthlyReturn))
  
  colnames(monthlyRet) <- colnames(data)
  
  rollReturn <- na.omit(rollapply(monthlyRet,12,function(x) prod(x+1)-1))
  
  plotTS(rollReturn, "", showPercentage=TRUE)
}

colMax <- function(data) sapply(data, max, na.rm = TRUE)

upPert <- function(data) { length(data[data > 0]) / length(data)}

getWindowStats <- function(data)
{
  monthlyRet <- do.call(cbind, lapply(data, monthlyReturn))
  
  roll6MonsReturn <- na.omit(rollapply(monthlyRet, 6, function(x) prod(x+1)-1))
  
  roll12MonsReturn <- na.omit(rollapply(monthlyRet, 12, function(x) prod(x+1)-1))
  
  perc <- c(
    round(length(roll6MonsReturn), 0)
    ,customPercent(max(roll6MonsReturn))
    ,customPercent(min(roll6MonsReturn))
    ,customPercent(mean(roll6MonsReturn))
    ,customPercent(upPert(roll6MonsReturn))
    ,customPercent(mean(roll6MonsReturn[roll6MonsReturn > 0]))
    ,customPercent(mean(roll6MonsReturn[roll6MonsReturn < 0]))
    ,customPercent(sd(roll6MonsReturn))
    ,round(length(roll12MonsReturn), 0)
    ,customPercent(max(roll12MonsReturn))
    ,customPercent(min(roll12MonsReturn))
    ,customPercent(mean(roll12MonsReturn))
    ,customPercent(upPert(roll12MonsReturn))
    ,customPercent(mean(roll12MonsReturn[roll12MonsReturn > 0]))
    ,customPercent(mean(roll12MonsReturn[roll12MonsReturn < 0]))
    ,customPercent(sd(roll12MonsReturn))
  )
  
  perc
}

GetWindowAnalysis <- function()
{
  if (is.null(briIndex))
    GetDataBriIndexData()
  
  if (is.null(hfrxIndex))
    GeTDataHfrxIndexData()
  
  col <- c('Periods 6 Mon'
           ,'Best 6 Mon'
           ,'Worst 6 Mon'
           ,'Average 6 Mon'
           ,'% Up 6 Mon'
           ,'Ave. 6 Mon Gain'
           ,'Ave. 6 Mon Loss'
           ,'Ave 6 Mon St Dev'
           ,'Periods 12 Mon'
           ,'Best 12 Mon'
           ,'Worst 12 Mon'
           ,'Average 6 Mon'
           ,'% Up 12 Mon'
           ,'Ave. 12 Mon Gain'
           ,'Ave. 12 Mon Loss'
           ,'Ave 12 Mon St Dev')
  
  perc1 <- getWindowStats(briIndex)
  
  perc2 <- getWindowStats(hfrxIndex)
  
  col1 <- colnames(briIndex)[1]
  
  col2 <- colnames(hfrxIndex)[1]
  
  dat <- data.frame(Statistics = col
                    ,col1 = perc1
                    ,col2 = perc2)
  
  colnames(dat) <- c('', col1, col2)
  
  dat
}

GetRecentPerformance <- function()
{
  if (is.null(briIndex))
    GetDataBriIndexData()
  
  if (is.null(hfrxIndex))
    GeTDataHfrxIndexData()
  
  minus1Year <- Sys.Date() - years(1)
  
  minus3Year <- Sys.Date() - years(3)
  
  minus5Year <- Sys.Date() - years(5)
  
  briIndexRet <- na.omit((briIndex - lag(briIndex)) / lag(briIndex))
  
  bri_last_1y_ret <- Return.annualized(briIndexRet[paste0(format(minus1Year, "%Y-%m-%d"), "::")], 
                                    scale = NA, geometric = FALSE)
  
  bri_last_3y_ret <- Return.annualized(briIndexRet[paste0(format(minus3Year, "%Y-%m-%d"), "::")], 
                                       scale = NA, geometric = FALSE)
  
  bri_last_5y_ret <- Return.annualized(briIndexRet[paste0(format(minus5Year, "%Y-%m-%d"), "::")], 
                                       scale = NA, geometric = FALSE)
  
  hfrxIndexRet <- na.omit((hfrxIndex - lag(hfrxIndex)) / lag(hfrxIndex))
  
  hfrx_last_1y_ret <- Return.annualized(hfrxIndexRet[paste0(format(minus1Year, "%Y-%m-%d"), "::")], 
                                       scale = NA, geometric = FALSE)
  
  hfrx_last_3y_ret <- Return.annualized(hfrxIndexRet[paste0(format(minus3Year, "%Y-%m-%d"), "::")], 
                                       scale = NA, geometric = FALSE)
  
  hfrx_last_5y_ret <- Return.annualized(hfrxIndexRet[paste0(format(minus5Year, "%Y-%m-%d"), "::")], 
                                       scale = NA, geometric = FALSE)
  
  col <- c('Recent 1 Year'
           ,'Recent 3 Year'
           ,'Recent 5 Year')
  
  dat <- data.frame(Statistics = col
                    ,col1 = c(bri_last_1y_ret, bri_last_3y_ret, bri_last_5y_ret)
                    ,col2 = c(hfrx_last_1y_ret, hfrx_last_3y_ret, hfrx_last_5y_ret))
  
  colnames(dat) <- c('', colnames(briIndex)[1], colnames(hfrxIndex)[1])
  
  dat
}

plotRiskReturnScatter <- function()
{
  if (is.null(briIndex))
    GetDataBriIndexData()
  
  if (is.null(hfrxIndex))
    GeTDataHfrxIndexData()
  
  briIndexRet <- na.omit((briIndex - lag(briIndex)) / lag(briIndex))
  
  hfrxIndexRet <- na.omit((hfrxIndex - lag(hfrxIndex)) / lag(hfrxIndex))
  
  briAnnualizedRet <- Return.annualized(briIndexRet)
  
  briAnnualizedRisk <- StdDev.annualized(briIndexRet)
  
  hfrxAnnualizedRet <- Return.annualized(hfrxIndexRet)
  
  hfrxAnnualizedRisk <- StdDev.annualized(hfrxIndexRet)
  
  data <- data.frame(fund = c(colnames(briIndex)[1], colnames(hfrxIndex)[1])
                    ,risk = c(briAnnualizedRisk, hfrxAnnualizedRisk)
                    ,return = c(briAnnualizedRisk, hfrxAnnualizedRisk))
  
  row.names(data) <- c(colnames(briIndex)[1], colnames(hfrxIndex)[1])
  
  p <- plot_ly(data, x = ~risk, y = ~return, type = 'scatter', mode = 'markers',
               marker = list(size = 10)) %>%
    add_annotations(x = data$risk,
                    y = data$return,
                    text = rownames(data),
                    xref = "x",
                    yref = "y",
                    showarrow = TRUE,
                    arrowhead = 4,
                    arrowsize = .5,
                    ax = 20,
                    ay = -40) %>% 
    layout(yaxis = list(tickformat = "%"))
}
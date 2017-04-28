library(quantmod)
library(shiny)
library(dygraphs)
library(TTR)
library(mailR)

options("getSymbols.warning4.0"=FALSE)

startDate <<- "2014-01-01"

address <- "ray.peiqing.he@gmail.com"

msg <<- ""

sma_param <- c(5, 20, 50, 250)

GetDataFromYahooFinance <- function(ticker="^GSPC",from=startDate)
{
  data <- getSymbols(ticker,from = from, env = NULL)
  
  data <- data[,ncol(data)]
  
  for (p in sma_param)
  {
    data <- cbind(data, SMA(data[,1],n=p))
  }
  
  fieldNames <- paste0("SMA(", sma_param, ")")
  
  colnames(data) <- c(ticker, fieldNames)
  
  data <- data[sma_param[length(sma_param)]:nrow(data),]
  
  data
}

CheckSMA <- function(ts)
{
  sma_250 <- ts[nrow(ts), ncol(ts)]
  
  msg <<- ""
  
  for (p in seq_along(sma_param[-length(sma_param)]))
  {
    sma <- ts[nrow(ts), 1 + p]
    
    if (abs(sma - sma_250) / sma_250 <= 0.05)
    {
      SendMail(sma_param[p], index(ts[nrow(ts), ]))
      
      break
    }
  }
}

SendMail <- function(day, date)
{
  subject <- paste(day, "day moving average gets within 5% of the 250 day moving average")
  
  sender <- address # Replace with a valid address
  recipients <- c(address) # Replace with one or more valid addresses
  email <- send.mail(from = sender,
                     to = recipients,
                     subject=subject,
                     body = subject,
                     smtp = list(host.name = "aspmx.l.google.com", port = 25),
                     authenticate = FALSE,
                     send = FALSE)
  
  print(paste(date, subject))
  
  msg <<- subject
}

plot <- function()
{
  ticker="^GSPC"
  
  ts <- GetDataFromYahooFinance(ticker=ticker)
  
  CheckSMA(ts)
  
  title <- "SPX 500"
  
  if (msg != "")
    title = msg
  
  dygraph(ts, main = title) %>%
    dySeries(ticker, axis = 'y2', fillGraph = TRUE) %>%
    dyLegend(width = 800, show = "always")
}

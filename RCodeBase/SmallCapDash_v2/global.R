# Requirements
# ------------------------------------------------------------------------------
#options(repos = c(CRAN = "http://cran.rstudio.com"))
# sapply(c(              # Load required packages, install if missing.
#   "rCharts",
#   "reshape2",
#   "shiny",             # Web front end.
#   "plyr",              # Data manipulation.
#   "magrittr",          # Forward-pipes.
#   "ggplot2",           # Plotting.
#   "openxlsx"           # Reading Excel files
# ), function(pack) {
#   if(!pack %in% installed.packages()) {install.packages(pack)}
#   require(pack, character.only=TRUE)
# })

library(rCharts)
library(reshape2)
library(shiny)
library(plyr)
library(magrittr)
library(ggplot2)
library(openxlsx)


# Settings & Data
# ------------------------------------------------------------------------------

#data_file <- file.path("data", "SmallCap_NewDataFormat.xlsx")

data_file <- file.path("data", "SmallCap_Shiny.csv")

ExcelDate <- . %>% {as.Date(. - 2, origin="1900-1-1")}

csvDate <- . %>% {as.Date(., "%m/%d/%Y")}

ConvertNumeric <- . %>% {if (is.numeric(.)) as.numeric(.) else 0}


# Changes by Ray
# Format the input data frame by changing column name and format date value
colMapping <- function(data){
  
  colnames(data) = tolower(colnames(data))
  
  mapping = list('tradedate'='date', 'markettitle'="instrument", 
                 'porttype'="sectorname", "industrysector" = "industry"
                 ,"silopnl_percent"="daily.return")
  
  
  for( key in names(mapping) ){ 
    colnames(data)[colnames(data)==key] <- mapping[[key]]
  }
  
  data["date"] <- lapply(data["date"], csvDate)
  
  data["daily.return"] <- lapply(data["daily.return"], ConvertNumeric)
  
  data
}

DataGet <- . %>% {
  read.csv(data_file) %>% colMapping %T>%
  {.[, c("sectorname", "instrument")] %<>% lapply(factor)} %T>%
  {colnames(.) %<>% gsub("daily.return", "r", .)} %>%
  cbind(industry = paste("industry"))   # delete when you have the data.
}

if(!exists("d")) {assign("d", DataGet())}

# Changes by Ray
# Store the min date and max date from data
# We use it as the start date and end date when users clicke Inception button
dateRange <<- c(d$date %>% min, d$date %>% max)


# Functions
# ------------------------------------------------------------------------------

DailyReturns <- function(d, cum, fun) {
  # Mean return per portfolio per day.

  # `cum` is either TRUE or FALSE (logical).
  # `fun` is either `mean` or `sum`.

  # Sort df using sectorname and date
  d %<>% arrange(sectorname, date)

  d[,"r", drop=FALSE] %>%
  {aggregate(.,list(date=d$date, sectorname=d$sectorname), fun, na.rm=T)} %T>%
  {if(cum) {.$r <- tapply(.$r, .$sectorname, cumsum) %>% unlist}}
}


# NVD3 Formats
# ------------------------------------------------------------------------------

percent_format <- "#!function(y) {return y.toFixed(2)}!#"

# Changes by Ray
# Reference: https://github.com/ramnathv/rCharts/issues/80
# change d3.time.format into d3.time.format.utc
yearmonth_format <- "#!function(d) {
  return d3.time.format.utc('%x')(new Date(d * 24 * 60 * 60 * 1000));
}!#"

# Percent format ##.##%
percent_format2 <- "#! function(d) {return (d*100).toFixed(2) + '%' } !#"

# Figures and tables
# --------------------------------------------------------------------------------

F1 <- function(d, p) {
  # Cumulative returns per portfolio.
  # `p` list of portfolios to plot.
  # `d` data.
  
  d %<>%
    subset(sectorname %in% p) %>%
    DailyReturns(cum=T, fun=mean) %T>%
    {.$r %<>% {round(. * 100, 2)}} %>%
    {.[, c("date", "sectorname", "r")]}

  # for(s in p) {
  #   d %<>% {
  #     rbind(
  #       .,
  #       data.frame(
  #         date=(min(subset(., sectorname == s)$date) - 1), sectorname=s, r=0
  #       )
  #     )
  #   }
  # }

  d %<>% arrange(sectorname, date)
  
  print(head(d))
  
  out <- nPlot(r ~ date,
    data  = d,
    group = "sectorname",
    type  = "lineChart",
    reduceXTicks = FALSE
  ) %T>%

  .$yAxis(tickFormat=percent_format) %T>%
  .$xAxis(tickFormat=yearmonth_format, rotateLabels=-45) %T>%
    
  .$chart(margin = list(bottom=100)) %T>%
  .$set(width=1350, height=900)

  out
}



T1 <- function(d, p) {
  # Cumulative returns per portfolio.
  # `p` list of portfolios to plot.
  # `d` data.

  d %<>% subset(sectorname %in% p)

  DailyReturns(d, cum=F, fun=mean) %T>%
  {.$r %<>% {round(. * 100, 2)}} %>% {
    aggregate(
      .$r,
      list(.$sectorname),
      . %>% {c(
        #Return=sum(.),
        # Changes by Ray
        # Change to use Annualized return
        Return=(prod(1 + . / 100) ^ (252. / length(.)) - 1) * 100,
        Risk=(sd(.) * sqrt(252)),
        "Max Rtn" = max(.),
        "Ave. Rtn" = mean(.),
        "Median Rtn" = median(.),
        "Min Rtn" = min(.),
        "% Positive" = (mean(. > 0) * 100) %>% round(2) )
        #"% Positive" = (nrow(.>0)/nrow(.)))
        }
  )} %T>%

  {colnames(.) %<>% sapply(. %>% substring(., 2, length(.)))} -> out
  
  out[,2] %T>%
    {rownames(.) <- out[,1]} %T>%
    #{colnames(.) <- c("Return", "Risk", "MaxRtn", "AvgRtn","MedRtn", "MinRtn", "PcPositive")}
    {colnames(.) <- c("Return", "Risk", "MaxRtn", "AvgRtn","MedRtn", "MinRtn", "PcPositive")}
}


F2 <- function(d, p) {
  # Scatter chart of daily returns for two portfolios.
  # `p` list of portfolios to plot.
  # `d` data.


  d %<>%
    subset(sectorname %in% p) %>%
    DailyReturns(cum=F, fun=mean) %T>%
    {.$r %<>% {round(. * 100, 2)}} %>%
    {dcast(data=., formula=date ~ sectorname, value.var="r")[,-1]} %T>%
    {colnames(.) <- c("x", "y")} %>%
    {.[complete.cases(.),]} %>%
    cbind(s="Actual", size="1.5") %>%
    {rbind(
       .,
       lm(y~x, .) %>%
       {model=.;
        seq(min(.$model[,2]), max(.$model[,2]), length.out=200) %>%
        cbind(
          x=.,
          y=predict(model, newdata=data.frame(x=.)),
          s="Regression",
          size="1"
        )}
    )} %T>%
    {.$s %<>% as.character} %T>%
    {.[, 1:2] %<>% lapply(as.numeric)}

  corr <- subset(d, s == "Actual") %>% {cor(.[,"x"], .[,"y"])} %>% round(4)

  print(d)
  
  nPlot(y~x,
    data  = d,
    type  = "scatterChart",
    group = "s"
  ) %T>%

  .$yAxis(tickFormat=percent_format) %T>%
  .$xAxis(tickFormat=percent_format, axisLabel=paste("Correlation =",corr)) %T>%
  .$set(width=900, height=600) %T>%
  .$chart(
     sizeRange		= c(2, 80),
     size		= '#! function(d){return d.size} !#',
     showControls	= FALSE
  )
}


F3 <- function(d, p) {
  #  Scatterchart of return per asset per portfolio.

  d %<>%
    subset(sectorname %in% p) %>%
    {aggregate(.[,"r", drop=F], list(sectorname=.$sectorname, ticker=.$instrument), sum)} %T>%
    {.$sectorname %<>% factor} %T>%
    {.$p <- .$sectorname %>% as.numeric} %T>%
    {.$r %<>% {round(100 * ., 2)}}

  nPlot(r~p,
    data  = d,
    type  = "scatterChart",
    group = "sectorname"
  ) %T>%

  .$yAxis(tickFormat=percent_format) %T>%
  .$xAxis(tickValues=1:length(p)) %T>%
  .$set(width=900, height=600) %T>%
  .$chart(
    forceX       = c(.5, length(p) + .5),
    showControls = T,
    sizeRange=c(100, 100),
    showXAxis = FALSE,
    tooltips = TRUE,
    tooltipContent = 
      "#! function(key, x, y, e){
        return '<h3>' + e.point.ticker + '</h3> <br><h4> Current position: ' + e.point.r + '</h4>'
      } !#"

  )
}


# Changes byvRay
# Area chart for Net exposure
F4 <- function(d, p) {
  # Net exposure of the combined portfolio.
  # `d` data.
  
  d = subset(d, sectorname %in% p)
  
  d <- aggregate((d$longmarketvalue + d$shortmarketvalue) / d$netassets, by=list(date=d$date), FUN=sum)
  
  colnames(d) <- c("date", "netexposure")
  
  out <- nPlot(netexposure ~ date,
               data  = d,
               #type  = "lineChart",
               type = 'stackedAreaChart', id = 'chart',
               reduceXTicks = FALSE
  ) %T>%
    
    .$yAxis(tickFormat=percent_format2) %T>%
    .$xAxis(tickFormat=yearmonth_format, rotateLabels=-45) %T>%
    
    .$chart(margin = list(bottom=100)) %T>%
    .$set(width=900, height=600)
  
  out
}

# Changes by Ray
# Update the date range input widget using with the given start and end date
UpdateDateRange <- function(session, start, end){
  
  # Popup error message when start > max date
  # or end < min date
  if (end <= dateRange[1] || start >= dateRange[2]){

      msg = paste("No data between", start, "between", end)
      
      msg = "No data for current month"
      
      ShowPopup(session, msg)
  }
  else
      updateDateRangeInput(session, "date_range",
                       label = NULL,
                       start = start,
                       end = end)
}

# Changes by Ray
# Show popup message
ShowPopup <- function(session, msg){
  my_slider_check_test <- msg
  js_string <- 'alert("SOMETHING");'
  js_string <- sub("SOMETHING",my_slider_check_test,js_string)
  
  session$sendCustomMessage(type='jsCode', list(value = js_string))  
}

# Changes by Ray
# Return the first date using the given year and month
GetFirstDate <- function(yr, mon){

  firstDateInMonth <- paste(yr, "-", mon, "-01", sep="")
  
  return(firstDateInMonth)
}

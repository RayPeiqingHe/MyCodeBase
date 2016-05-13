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
library(ggvis)
library(dygraphs)
library(htmlwidgets)
library(dplyr, warn.conflicts = FALSE)
library(xts)


# Settings & Data
# ------------------------------------------------------------------------------

#data_file <- file.path("data", "SmallCap_NewDataFormat.xlsx")

#data_file <- file.path("data", "SmallCap_Shiny.csv")

data_file <- file.path("data", "Shiny_Example.csv")

ExcelDate <- . %>% {as.Date(. - 2, origin="1900-1-1")}

csvDate <- . %>% {as.Date(., "%Y-%m-%d")}

cum.na <- function(x) { 
  x[which(is.na(x))] <- 0 
  return(cumsum(x)) 
}

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
  
  #data["date"] <- lapply(data["date"], ExcelDate)
  
  data
}

DataGet <- . %>% {
  read.csv(data_file, na.strings = "NULL", stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM") %>% colMapping %T>%
  #read.xlsx(data_file, sheet=1) %>% colMapping %T>%
  {.[, c("sectorname", "instrument")] %<>% lapply(factor)} %T>%
  {colnames(.) %<>% gsub("daily.return", "r", .)} %>%
  cbind(industry = paste("industry"))   # delete when you have the data.
}

if(!exists("d")) 
{
  assign("d", DataGet())
  
  d[is.na(d$industry),]$industry <- "NA"
  
  d[d$portgroup == "INDEX",]["positionallocation"] = 1
}

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
  
  d[d$positionallocation != 0,c("date", "sectorname", "pnl_percent", "positionallocation"), drop=FALSE] %>%
  {aggregate(cbind(pnl_percent, positionallocation)~date+sectorname, data=., fun, na.rm=T)} %T>%
  {.$r = (.$pnl_percent / .$positionallocation)} %T>%
  {if(cum) {.$r <- tapply(.$r, .$sectorname, cum.na) %>% unlist}}
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
  
  d %<>% arrange(sectorname, date)
  
  d[d$date == d[1,]$date,]$pnl_percent <- 0
  
  d[d$date == d[1,]$date,]$positionallocation <- 1
  
  d %<>%
    subset(sectorname %in% p) %>%
    DailyReturns(cum=T, fun=sum) %T>%
    {.$r %<>% {round(. * 100, 4)}} %>%
    {.[, c("date", "sectorname", "r")]}
  
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
  
  d <- d[d$date != d[1,]$date,]
  
  DailyReturns(d, cum=F, fun=sum) %T>%
  {.$r %<>% {round(. * 100, 5)}} %>% {
    aggregate(
      .$r,
      list(.$sectorname),
      . %>% {c(
        # Changes by Ray
        # Change to use Annualized return
        Return=sum(.,na.rm=TRUE) * 252. / length(.),
        Risk=(sd(.,na.rm=TRUE) * sqrt(252)),
        "Max Rtn" = max(.,na.rm=TRUE),
        "Ave. Rtn" = mean(.,na.rm=TRUE),
        "Median Rtn" = median(.,na.rm=TRUE),
        "Min Rtn" = min(.,na.rm=TRUE),
        "% Positive" = (mean(. > 0,na.rm=TRUE) * 100) %>% round(2) )
        }
  )} %T>%

  {colnames(.) %<>% sapply(. %>% substring(., 2, length(.)))} -> out
  
  out[,2] %T>%
    {rownames(.) <- out[,1]} %T>%
    {colnames(.) <- c("Return", "Risk", "MaxRtn", "AvgRtn","MedRtn", "MinRtn", "PcPositive")}
}


F2 <- function(d, p) {
  # Scatter chart of daily returns for two portfolios.
  # `p` list of portfolios to plot.
  # `d` data.

  d %<>% subset(sectorname %in% p)
  
  d <- d[d$date != d[1,]$date,]
  
  d %<>%
    subset(sectorname %in% p) %>%
    DailyReturns(cum=F, fun=sum) %T>%
    {.$r %<>% {round(. * 100, 5)}} %>%
    {dcast(data=., formula=date ~ sectorname, value.var="r")[,-1]} %T>%
    {colnames(.) <- c("x", "y")} %>%
    {.[complete.cases(.),]} %>%
    cbind(s="Actual", size="1.5") 
  
  model <- lm(y~x, d)
  
  d %<>%
    {rbind(
       .,
       model %>%
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
  
  xlabel <- paste("Regression between", p[2], "(y) and", p[1], "(x)")
  
  plot <- nPlot(y~x,
    data  = d,
    type  = "scatterChart",
    group = "s"
  ) %T>%

  .$yAxis(tickFormat=percent_format) %T>%
  .$xAxis(tickFormat=percent_format, axisLabel=
            xlabel) %T>%
  .$set(width=1350, height=900) %T>%
  .$chart(
     sizeRange		= c(2, 80),
     size		= '#! function(d){return d.size} !#',
     showControls	= FALSE
  )
  
  corrText <- paste("Corr = ", corr)
  alpha <- paste("Alpha =", round(coefficients(model)[1], 7))
  beta <- paste("Beta =", round(coefficients(model)[2], 4))
  
  text <- HTML(paste(corrText, alpha, beta, sep = '<br/>'))
  
  list(plot=plot, text=text)
}


F3 <- function(d, p, groupby) {
  #  Scatterchart of return per asset per portfolio.
  
  d %<>% subset(sectorname %in% p)
  
  d <- d[d$date != d[1,]$date,]
  
  d %<>%
    subset(sectorname %in% p) %>%
    {aggregate(.[,"prc_change", drop=F], list(sectorname=.$sectorname, industry = .$industry, ticker=.$instrument), 
               function(x)sum(na.exclude(x)))} %T>%
    {.$sectorname %<>% factor} %T>%
    {.$p <- .$sectorname %>% as.numeric} %T>%
    {.$prc_change %<>% {round(100 * ., 2)}}
  
  plot <- nPlot(prc_change~p,
    data  = d,
    type  = "scatterChart",
    group = groupby
  ) %T>%
    
  .$yAxis(tickFormat=percent_format) %T>%
  .$xAxis(tickValues=1:length(p)) %T>%
  #.$xAxis(tickValues=p.f) %T>%
  .$set(width=1200, height=800) %T>%
  .$chart(
    forceX       = c(.5, length(p) + .5),
    showControls = TRUE,
    sizeRange=c(100, 100),
    showXAxis = FALSE,
    tooltips = TRUE,
    tooltipContent =
      "#! function(key, x, y, e){
        return '<h3>' + e.point.ticker + '</h3> <br><h4> Current position: ' + e.point.prc_change + '</h4>'
      } !#"
  )
  
  plot
}


F3_2 <- function(d, p, groupby) {
  #  Scatterchart of return per asset per portfolio.
  
  if (nrow(d) > 0 && length(p) > 0)
  {
    d %<>% subset(sectorname %in% p)
  
    d <- d[d$date != d[1,]$date,]
  
    d %<>%
      subset(sectorname %in% p) %>%
      {aggregate(.[,"prc_change", drop=F], list(sectorname=.$sectorname, industry = .$industry, ticker=.$instrument), 
                 function(x)sum(na.exclude(x)))} %T>%
                 {.$sectorname %<>% ordered(., levels = p)} %T>%
                 {.$prc_change %<>% {round(100 * ., 2)}}
    d$key = paste(d$sectorname, d$industry, ":", d$ticker, sep='') 
  
    d$zero = 0
    
    d$groups = d[, groupby]
    
    # Add error bar for mean
    agg <- aggregate(d[,"prc_change", drop=F], list(groups=d$groups), FUN = mean)
    
    colnames(agg) = c("groups", "mean_prc_change")
  
    d <- merge(d, agg, by="groups", all=TRUE)
    
    # Add error bar for median
    agg <- aggregate(d[,"prc_change", drop=F], list(groups=d$groups), FUN = median)
    
    colnames(agg) = c("groups", "median_prc_change")
    
    d <- merge(d, agg, by="groups", all=TRUE)
    
    plot <- ggvis(d, x = ~groups, y = ~prc_change, key := ~key, fill = ~groups) %>% 
      layer_points() %>%
      set_options(width = 1700, height = 900) %>%
      add_axis("y", format = ".2f", title = "") %>%
      add_axis("x", title = "", properties = axis_props(
        axis = list(stroke = "black", strokeWidth = 1)
        ,labels = list(stroke = "black", strokeWidth = 0.5))) %>%
      layer_paths(x = ~groups, y = ~zero, stroke:="black",  strokeWidth := 3) %>%
      layer_text(x = ~groups, y = ~mean_prc_change, text:="-------",
                 fontSize := 30, fill:="red", baseline:="middle", align:="center") %>%
      layer_text(x = ~groups, y = ~median_prc_change, text:="-------",
                 fontSize := 30, fill:="blue", baseline:="middle", align:="center") %>%      
      layer_points(size := 200, opacity := 0.4 )%>%
      add_tooltip(getTooltip2, "hover") 
  }
  else
  {
    d <- d[0,]
    
    plot <- ggvis(d, x = ~sectorname, y = ~prc_change) %>% 
      layer_points() %>%
      set_options(width = 1500, height = 900)
  }
  
  plot
}

# Changes byvRay
# Area chart for Net exposure
F4 <- function(d, p, groupby) {
  # Net exposure of the combined portfolio.
  # `d` data.
  
  d[d$date == d[1,]$date,]$pnl_percent <- 0
  
  d[d$date == d[1,]$date,]$positionallocation <- 1
  
  d <- subset(d, sectorname %in% p)
  
  d$groups <- d[, groupby]
  
  d <- aggregate((d$longmarketvalue + d$shortmarketvalue) / d$netassets, 
                 by=list(date=d$date, groups=d$groups)
                 , FUN=sum, na.rm=T)
  
  colnames(d) <- c("date", "groups", "netexposure")
  
  out <- nPlot(netexposure ~ date,
               data  = d,
               #type  = "lineChart",
               type = 'stackedAreaChart', id = 'chart', group = "groups",
               reduceXTicks = FALSE
  ) %T>%
    
    .$yAxis(tickFormat=percent_format2) %T>%
    .$xAxis(tickFormat=yearmonth_format, rotateLabels=-45) %T>%
    
    .$chart(margin = list(bottom=100)) %T>%
    .$set(width = 1350, height = 900)
  
  out
}

# Changes by Ray
# Area chart for Net exposure
F4_2 <- function(d, p, groupby) 
{
  # Net exposure of the combined portfolio.
  # `d` data.
  
  if (nrow(d) > 0 && length(p) > 0)
  {
    d[d$date == d[1,]$date,]$pnl_percent <- 0
    
    d[d$date == d[1,]$date,]$positionallocation <- 1
    
    d <- subset(d, sectorname %in% p)
    
    d$groups <- d[, groupby]
    
    d <- aggregate((d$longmarketvalue + d$shortmarketvalue) / d$netassets, 
                   by=list(date=d$date, groups=d$groups)
                   , FUN=sum, na.rm=T)
    
    d$groups <- as.character(d$groups)
    
    colnames(d) <- c("date", "groups", "netexposure")
    
    out <- d %>% 
      group_by(date) %>%
      mutate(to = cumsum(netexposure), from = c(0, to[-n()])) %>%
      ggvis(x=~date, fill=~groups) %>% 
      group_by(groups) %>% 
      layer_ribbons(y = ~from, y2 = ~to) %>%
      set_options(width = 1350, height = 900) %>%
      add_axis("y", format = ".2%", title = "") %>%
      add_axis("x", format = "%m/%d/%Y",  
               title = "", 
               properties = axis_props(labels = list(angle = -45, align = "right")))  %>%
      add_tooltip(getTooltip, "hover")
      
  }
  else
  {
    d <- d[0,]
    
    out <- ggvis(d, x = ~sectorname, y = ~r) %>% 
      layer_ribbons() %>%
      set_options(width = 1350, height = 900)
  }
  
  out
}

F4_3 <- function(d, p, groupby) 
{
  d[d$date == d[1,]$date,]$pnl_percent <- 0
  
  d[d$date == d[1,]$date,]$positionallocation <- 1
  
  d <- subset(d, sectorname %in% p)
  
  d$groups <- d[, groupby]
  
  d <- aggregate((d$longmarketvalue + d$shortmarketvalue) / d$netassets, 
                 by=list(date=d$date, groups=d$groups)
                 , FUN=sum, na.rm=T)
  
  colnames(d) <- c("date", "groups", "netexposure")
  
  d <- split(d, d$groups, drop = TRUE)
  
  d <- lapply(d, reg)
  
  d <- Reduce(merge.all, d)
  
  data_cols <- colnames(d)[colnames(d) != 'date']
  
  ts <- xts(d[data_cols], d$date)
  
  dygraph(ts) %>%
    dyOptions(stackedGraph = TRUE) %>%
    dyAxis("x",valueFormatter=JS(getFullDay), axisLabelFormatter=JS(getFullDay)) %>%
    dyAxis(
      "y",
      label = "",
      independentTicks = TRUE,
      valueFormatter = 'function(d){return (d*100).toFixed(2) + "%"}',
      axisLabelFormatter = 'function(d){return (d*100).toFixed(2) + "%"}'
    ) %>%
    dyRangeSelector(height = 20) %>%
    dyLegend(width = 600)
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

getTooltip <- function(dat){
  
  #date <- dat$date
  from <- dat$from
  to <- dat$to

  paste(paste("Date:", as.Date(dat$date / 86400000, origin='1970-01-01')),
        paste("Exposure:", (to - from)),
        sep = "<br />")
}

getTooltip2 <- function(data){
  paste0(substring(data$key, regexpr(":",data$key)[1] + 1), "<br>", as.character(data$prc_change), "%")
}

merge.all <- function(x, y) {
  merge(x, y, all=TRUE, by="date")
}


reg <- function(x)
{
  t <- x[, c("date", "netexposure")]
  
  colnames(t) <- c("date", as.character(x[1, "groups"]))
  
  t
}

getFullDay <- 'function(d) {
date = new Date(d);
return (date.getMonth()+1) + "/" + date.getDate() + "/" + date.getFullYear(); }'

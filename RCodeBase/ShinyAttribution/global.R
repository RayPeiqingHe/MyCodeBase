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

yearmonth_format <- "#!function(d) {
  return d3.time.format.utc('%x')(new Date(d * 24 * 60 * 60 * 1000));
}!#"

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


T1 <- function(d, pd, dependVar, exVars) {
  
  fit <- lm(d[[dependVar]] ~ . , data = d[exVars])
  
  data_cols <- colnames(d)[colnames(d) != 'Date']
  
  # Maximum drawdown
  ts_ret <- xts(d[data_cols], d$Date)
  
  mdd <- maxDrawdown(ts_ret) * 100
  
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
  
  # Ret / DD
  retDD <- tb / mdd
  rownames(retDD) = "Ret/DD"
  
  # Beta
  coeff <- t(data.frame(coefficients(fit)))
  
  # Rename columns since the lm function prefic and postfix single quote to 13D
  colnames(coeff) = c(dependVar, exVars)
  
  # Alpha
  alpha <- coeff
  
  rownames(coeff) = "Beta"
  
  coeff[, dependVar] <- NA
  
  rownames(alpha) = "Alpha (10e-4)"
  
  alpha[, exVars] <- NA
  
  tb <- rbind(tb, vol, sharpe, mdd, retDD, coeff, alpha * 10000)
  
  t(tb)
}

F1 <- function(d, dependVar, exVars) {

  fit <- lm(d[[dependVar]] ~ . , data = d[exVars])
  
  pred <- fitted(fit)
  
  d <- cbind(d, pred)[, c(dependVar, "pred")]
  
  colnames(d) <- c("y", "x")
  
  # Plot of the best fit line
  bestFit <- lm(y ~ x , data = d)
  
  bestFitLine <- fitted(bestFit)
  
  d <- cbind(d, size="1", s="Regression")
  
  d %<>%
  {rbind(
    .,
    lm(y~x, .) %>%
    {model=.;
    seq(min(.$model[,2]), max(.$model[,2]), length.out=200) %>%
      cbind(
        x=.,
        y=predict(model, newdata=data.frame(x=.)),
        s="Best Fit",
        size="1"
      )}
  )} %T>%
  {.$s %<>% as.character} %T>%
  {.[, 1:2] %<>% lapply(as.numeric)}
  
  out <- nPlot(y ~ x,
               data  = d,
               type  = "scatterChart"
               ,group = "s"
  ) %T>%
    
    .$yAxis(tickFormat=percent_format2, axisLabel=dependVar) %T>%
    .$xAxis(tickFormat=percent_format2, axisLabel=paste("Predicted",dependVar)) %T>%
    .$set(width=1125, height=600) %T>%
    .$chart(
      size		= '#! function(d){return d.size} !#'
      ,showControls	= FALSE
    )
    
  out
}

F2 <- function(d, dependVar, exVars, lookback) {
  
  data_cols <- colnames(d)[colnames(d) != 'Date']
  
  # Convert to time series object
  ts_ret <- xts(d[data_cols], d$Date)
  
  dolm <- function(x) coef(lm(x[,dependVar] ~ ., data = x[, exVars]))
  
  reg <- na.omit(rollapplyr(ts_ret, lookback, dolm, by.column = FALSE))
  
  reg <- data.frame(date=index(reg), coredata(reg))
  
  d <- reg[, c("date", "X.Intercept.")]
  
  # d is the data frame of date and alpha
  colnames(d) <- c("date", "y")
  
  # left contaisn the upper bound of alpha
  alphaMax <- max(d$y)
  
  d <- cbind(d, s = "Alpha")
  
  y_list <- list(Alpha = list(type="bar", yAxis = 2))
  
  for (col in colnames(reg))
  {
    if (col != "X.Intercept." && col != "date")
    {
      tmp <- cbind(reg[, c("date", col)], s = col)
      
      colnames(tmp) <- c("date", "y", "s")
      
      d <- rbind(d, tmp)
      
      y_list[[col]] <- list(type="line", yAxis = 1)
    }
  }
  
  betaMax <- max(d[d$s != "Alpha", ]$y)
  
  out <- nPlot(y ~ date,
               data  = d,
               type  = "multiChart"
               ,group = "s"
  ) 
  
  #Set which axes the item should follow
  out$params$multi <- y_list
  
  #Format xAxis from R date format to JS time format
  #Printed as dd-mm-yyyy
  out$xAxis(
    tickFormat=yearmonth_format, rotateLabels=-45
  )
  
  out$set(width=1125, height=600)
  
  alphaFormat = "d3.format( '.2%' )"
  
  betaFormat = "d3.format( '.2f' )"
  
  #for multi we need yAxis1 and yAxis2
  #but there is not a method like for yAxis and xAxis
  #so let's do it the hacky way in the template
  out$setTemplate( script = getFormatMultiChartYAxesScript(
    betaMax * -1, betaMax, alphaMax * -1, alphaMax, betaFormat, alphaFormat
  ))
  
  out
}

# Script for formatting multiChart's y-axes scale and tick mark format
getFormatMultiChartYAxesScript <-
  function(lowLeftY, highLeftY, lowRightY, highRightY,
           leftYTickFuncString, rightYTickFuncString){
    script <-
      paste0(
        "<script>
        $(document).ready(function(){
        draw{{chartId}}()
        });
        
        function draw{{chartId}}(){  
        var opts = {{{ opts }}},
        data = {{{ data }}}
        
        if (!(opts.type==='pieChart')) {
        var data = d3.nest()
        .key(function(d){
        return opts.group === undefined ? 'main' : d[opts.group]
        })
        .entries(data);
        }
        
        //loop through to give an expected x and y
        //then give the type and yAxis hopefully provided by R
        data.forEach(
        function(variables) {
        variables.values.forEach(
        function(values){
        values.x = values[opts.x];
        values.y = values[opts.y];
        }
        );
        variables.type = opts.multi[variables.key].type;
        variables.yAxis = opts.multi[variables.key].yAxis;
        }
        );
        
        nv.addGraph(function() {
        var chart = nv.models[opts.type]()
        //.x(function(d) { return d[opts.x] })
        //.y(function(d) { return d[opts.y] })
        // Shrink the width a bit such that both axes' tick marks can fit
        .width(opts.width - 25)
        .height(opts.height)
        
        {{{ chart }}}
        
        {{{ xAxis }}}
        
        {{{ x2Axis }}}
        
        // here is the problem we need yAxis1 and yAxis2
        // for now let's manually specify

                // here is how we could force the y Axis range or limits
                chart.yDomain1([", lowLeftY,",", highLeftY,"]);

                // y Axis limits for right axis
                chart.yDomain2 ([", lowRightY, ",", highRightY, "]);

                // format so 10000 appears as 10k, apply thousand seperator as well
                chart.yAxis1.tickFormat(", leftYTickFuncString, ");

                chart.yAxis2.tickFormat(", rightYTickFuncString, ");

                d3.select('#' + opts.id)
        .append('svg')
        .datum(data)
        .transition().duration(500)
        .call(chart);
        
        nv.utils.windowResize(chart.update);
        return chart;
        });
        };
        </script>")
    return(script)
  }
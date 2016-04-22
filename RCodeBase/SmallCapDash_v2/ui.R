

# Elements
# ------------------------------------------------------------------------------


PortfoliosLongOnly <- function()
{
  checkboxGroupInput(
    # GUI input to define the portfolios to view.
    inputId = "portfoliosLongOnly",
    label   = "Long Only Models",
    
    choices = subset(d, portgroup == "LongOnly")$sectorname %>% as.character %>% unique,
    
    selected   = c("13D","CORE","Focus25") ,
    
    inline = FALSE
  )
}

PortfoliosHedge <- function()
{
  checkboxGroupInput(
    # GUI input to define the portfolios to view.
    inputId = "portfoliosHedge",
    label   = "Hedge",
    
    choices = subset(d, portgroup == "Hedge")$sectorname %>% as.character %>% unique,
    
    selected   = c("Protective Equity") ,
    
    inline = FALSE
  )
}

Indices <- function()
{
  checkboxGroupInput(
    # GUI input to define the portfolios to view.
    inputId = "Indices",
    label   = "Indices",
    
    choices = subset(d, portgroup == "INDEX")$industry %>% as.character %>% unique,
    
    selected   = subset(d, portgroup == "INDEX")$industry %>% as.character %>% unique,
    
    inline = FALSE
  )  
}

Industries <- . %>% {checkboxGroupInput(
  # GUI input to define the portfolios to view.
  inputId = "industries",
  label   = "Industries",

  choices = subset(d, portgroup != "INDEX")$industry %>% as.character %>% unique,

  selected = subset(d, portgroup != "INDEX")$industry %>% as.character %>% unique,
  inline                = FALSE
)}


DateRange <- . %>% {dateRangeInput(
  # GUI input to define the portfolios to view.
  inputId = "date_range",
  label = "Date range",
  start = d$date %>% min,
  end = d$date %>% max,
  min = d$date %>% min,
  max = d$date %>% max,
  format = "mm/dd/yyyy",
  startview = "month",
  weekstart = 0,
  language = "en",
  separator = " to "
  #,width="200px"
)}



# Interface
# ------------------------------------------------------------------------------

ui2 <- shinyUI(basicPage(
  # Changes by Ray
  # Handler for the popup
  tags$head(tags$script(HTML('Shiny.addCustomMessageHandler("jsCode",function(message) {eval(message.value);});'))
  ),
  
  titlePanel("RQSI SmallCap Dashboard"),
  
  div(style="position: relative;",
      wellPanel(style="position: absolute; width: 300px; left: 0; top: 0; height: auto;",
                
                PortfoliosLongOnly()
                
                ,PortfoliosHedge()
                
                ,Industries()
                
                ,DateRange()
                
                # Changes by Ray
                # Add the buttons for MTD, YTD, Since Inception
                ,fluidRow(
                  
                  column(3,
                         actionButton("mtd", label = "MTD")),
                  
                  column(3,
                         actionButton("ytd", label = "YTD")),
                  
                  column(3,
                         actionButton("inception", label = "Inception"))
                )
                ,Indices()
              
      ),
      div(style="position: absolute; left: 310px; right: 0; top: 0; height: auto;",
          tabsetPanel(
            "Performance" %>% tabPanel(chartOutput("f1", "nvd3"), tableOutput("t1")),
            "Daily Scatterplot" %>% tabPanel(chartOutput("f2", "nvd3")), 
            "Position Distribution"	%>% tabPanel(chartOutput("f3", "nvd3"))
            ,"Exposure" %>% tabPanel(chartOutput("f4", "nvd3"))
          )
      )
  )
)
)

ui2 %>%
shinyUI

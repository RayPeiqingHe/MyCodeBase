

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

GroupBy <- function(id)
{
  selectInput(id, "Group By:",
              c("Sub-Portfolio" = "sectorname",
                "Industry" = "industry"))
  
}

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
  tags$head(
    tags$script(HTML('Shiny.addCustomMessageHandler("jsCode",function(message) {eval(message.value);});'))
  ),
  
  titlePanel("RQSI SmallCap Dashboard"),
  
  div(style="position: relative;",
      wellPanel(style="position: absolute; width: 300px; left: 0; top: 0; height: auto;",
                
                PortfoliosLongOnly()
                
                ,PortfoliosHedge()
                
                ,Industries()
                
                ,actionButton("selectall", label="Select/Deselect all")
                
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
      div(align = "center", style="position: absolute; left: 310px; right: 0; top: 0; height: auto;",
          tabsetPanel(
            "Performance" %>% 
              tabPanel(
                chartOutput("f1", "nvd3"), 
                tableOutput("t1"),
                tags$script(HTML("
                        var p = document.getElementById('t1')
                        $(p).attr('align', 'center');"))
                ),
            "Daily Scatterplot" %>% 
              tabPanel(
                chartOutput("f2", "nvd3"),
                htmlOutput("t2"),
                tags$script(HTML("
                                 var p = document.getElementById('t2')
                                 $(p).attr('align', 'center');"))
                ), 
            "Position Distribution"	%>% tabPanel(
              GroupBy("groupby")
              #,chartOutput("f3", "nvd3")
              ,ggvisOutput("f3")
              )
            
            ,"Exposure" %>% tabPanel
            (
            GroupBy("groupby2")
            #,chartOutput("f4", "nvd3")
            #,ggvisOutput("f4")
            ,dygraphOutput("f4", width = "1300px", height = "800px")
            )
          )
      )
  )
)
)

ui2 %>%
shinyUI

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;

/*
Every url starts as:

http://ichart.yahoo.com/table.csv?s=

Then, it needs a stock name (e.g.: Microsoft):

http://ichart.yahoo.com/table.csv?s=MSFT

A From Date (e.g.: 01/01/2000):

http://ichart.yahoo.com/table.csv?s=MSFT&a=0&b=1&c=2000

A To Date (e.g.: 24/12/2014):

http://ichart.yahoo.com/table.csv?s=MSFT&a=0&b=1&c=2000&d=11&e=24&f=2014

Resolution of the data (daily, weekly, etc):

http://ichart.yahoo.com/table.csv?s=MSFT&a=0&b=1&c=2000&d=11&e=24&f=2014&g=w

File format:

http://ichart.yahoo.com/table.csv?s=MSFT&a=0&b=1&c=2000&d=11&e=24&f=2014&g=w&ignore=.csv
 
 * Example: http://ichart.finance.yahoo.com/table.csv?s=IBM&a=1&b=25&c=2009&d=11&e=13&f=2010&g=d&ignore=.csv

 Get Dividend only data
 * 
 * http://ichart.finance.yahoo.com/x?s=IBM&a=00&b=2&c=1962&d=04&e=25&f=2011&g=v&y=0&z=30000
 * 
 */

namespace YahooFinanceDownloader
{
    public enum frequency
    {
        daily,
        weekly,
        month,
        yearly
    }

    public class HistoricalStock
    {
        public string ticker { get; set; }
        public DateTime Date { get; set; }
        public double Open { get; set; }
        public double High { get; set; }
        public double Low { get; set; }
        public double Close { get; set; }
        public double Volume { get; set; }
        public double AdjClose { get; set; }

        public override string ToString()
        {
            return string.Format("{0},{1},{2},{3},{4},{5},{6},{7}", ticker, Date.ToString("yyyy-MM-dd"), Open, High, Low, Close, Volume, AdjClose);
        } 
    }

    public class HistoricalStockDownloader
    {
        private static string getUrlString(string ticker, DateTime startDate, DateTime endDate, frequency freq)
        {
            int startDay = startDate.Day;
            int startMonth = startDate.Month - 1;
            int startYear = startDate.Year;

            int endDay = endDate.Day;
            int endMonth = endDate.Month - 1;
            int endYear = endDate.Year;

            string freqStr = "d";

            if (freq == frequency.weekly)
                freqStr = "w";
            else if (freq == frequency.month)
                freqStr = "m";
            else if (freq == frequency.yearly)
                freqStr = "y";

            //string url = string.Format("http://ichart.finance.yahoo.com/table.csv?s={0}&c={1}", ticker, yearToStartFrom);

            string url = string.Format("http://ichart.finance.yahoo.com/table.csv?s={0}&a={1}&b={2}&c={3}&d={4}&e={5}&f={6}&g={7}&ignore=.csv", ticker,
                startMonth, startDay, startYear, endMonth, endDay, endYear, freqStr);

            return url;
        }

        private static string getUrlStringAll(string ticker, string fields)
        {
            string url = string.Format("http://ichart.finance.yahoo.com/table.csv?s={0}&a=0&b=1&c=2015&d=7&e=7&f={1}&g=d&ignore=.csv", ticker, fields);

            return url;
        }

        public static List<HistoricalStock> DownloadDataAll(string ticker, string fields, out string header)
        {
            List<HistoricalStock> retval = null;

            using (WebClient web = new WebClient())
            {
                string data = web.DownloadString(getUrlStringAll(ticker, fields));

                retval = GetSecurityObjFromURL(data, ticker, out header);
            }

            return retval;
        }

        public static List<HistoricalStock> DownloadData(string ticker, DateTime startDate, DateTime endDate, out string header, frequency freq = frequency.daily)
        {
            List<HistoricalStock> retval = null;

            using (WebClient web = new WebClient())
            {
                string data = web.DownloadString(getUrlString(ticker, startDate, endDate, freq));

                retval = GetSecurityObjFromURL(data, ticker, out header);
            }

            return retval;
        }

        private static List<HistoricalStock> GetSecurityObjFromURL(string data, string ticker, out string header)
        {
            List<HistoricalStock> retval = new List<HistoricalStock>();

            data = data.Replace("\r", "");

            string[] rows = data.Split(new string[] { "\n" }, StringSplitOptions.None);

            header = rows[0];

            //First row is headers so Ignore it
            for (int i = 1; i < rows.Length; i++)
            {
                if (rows[i].Replace("n", "").Trim() == "") continue;

                string[] cols = rows[i].Split(',');

                HistoricalStock hs = new HistoricalStock();
                hs.ticker = ticker;
                hs.Date = Convert.ToDateTime(cols[0]);
                hs.Open = Convert.ToDouble(cols[1]);
                hs.High = Convert.ToDouble(cols[2]);
                hs.Low = Convert.ToDouble(cols[3]);
                hs.Close = Convert.ToDouble(cols[4]);
                hs.Volume = Convert.ToDouble(cols[5]);
                hs.AdjClose = Convert.ToDouble(cols[6]);

                retval.Add(hs);
            }

            return retval;
        }
    }
}

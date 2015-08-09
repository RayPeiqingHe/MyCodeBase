using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Data.SqlClient;
using YahooFinanceDownloader;
using System.Configuration;
using System.Data;
using SQLLib;
using log4net;
using log4net.Config;

namespace YahooPriceBatchLoader
{
    class Program
    {
        private static readonly ILog logger = 
          LogManager.GetLogger(typeof(Program));
    
        static Program()
        {
            XmlConfigurator.Configure();
        }

        static void Main(string[] args)
        {
            string connstr = ConfigurationManager.AppSettings["SQLConnection"];

            string stagingTable = ConfigurationManager.AppSettings["StagingTableName"];

            string sp_OHLC = ConfigurationManager.AppSettings["InsertOHLC"];

            using (SQLUtils sql = new SQLUtils(connstr))
            {
                try
                {
                    string query = ConfigurationManager.AppSettings["SelectSerityMaster"];

                    DataTable dtSecurities = new DataTable();

                    sql.GetTableFromQuery(query, dtSecurities);

                    string headers = string.Empty;

                    foreach (DataRow row in dtSecurities.Rows)
                    {
                        string ticker = row["Ticker"].ToString();

                        if (row["InsertDate"] == DBNull.Value)
                        {
                            List<HistoricalStock> retval = HistoricalStockDownloader.DownloadData(ticker, new DateTime(2015, 1, 1),
                                new DateTime(2015, 8, 7), out headers);

                            sql.BulkInsert<HistoricalStock>(stagingTable, retval);
                        }
                    }
                }
                catch (Exception ex)
                {
                    logger.Error(ex.Message);
                }
            }
        }
    }
}

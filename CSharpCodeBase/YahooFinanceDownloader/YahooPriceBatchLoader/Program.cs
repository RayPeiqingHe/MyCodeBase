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
            logger.Info("Batch Loader starts...");

            string connstr = ConfigurationManager.AppSettings["SQLConnection"];

            string stagingTable = ConfigurationManager.AppSettings["StagingTableName"];

            string sp_OHLC = ConfigurationManager.AppSettings["InsertOHLC"];

            string clearStagingTable = ConfigurationManager.AppSettings["ClearStagingTable"];

            using (SQLUtils sql = new SQLUtils(connstr))
            {
                try
                {
                    string query = ConfigurationManager.AppSettings["SelectSerityMaster"];

                    DataTable dtSecurities = new DataTable();

                    sql.GetTableFromQuery(query, dtSecurities);

                    string headers = string.Empty;

                    sql.RunCommand(clearStagingTable);

                    foreach (DataRow row in dtSecurities.Rows)
                    {
                        string ticker = row["Ticker"].ToString();

                        DateTime lastDivDate = HistoricalStockDownloader.GetLatestDivDate(ticker);

                        if (row["InsertDate"] == DBNull.Value || lastDivDate.Date >= DateTime.Today.Date)
                        {
                            List<HistoricalStock> retval = HistoricalStockDownloader.DownloadDataAll(ticker, out headers);

                            sql.BulkInsert<HistoricalStock>(stagingTable, retval);

                            sql.RunCommand(sp_OHLC);

                            logger.Info(string.Format("Historical quotes download completed for {0}", ticker));
                        }
                    }
                }
                catch (Exception ex)
                {
                    logger.Error(ex.Message);
                }
            }

            logger.Info("Batch Loader completes...");

#if DEBUG
            Console.ReadLine();
#endif
        }
    }
}

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;
using System.Diagnostics;

namespace YahooFinanceDownloader
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            this.MaximumSize = this.Size;

            this.MinimumSize = this.Size;

            dtpStart.Value = DateTime.Today.AddDays(-1);

            dtpEndDate.Value = DateTime.Today;

            pbGetPrice.Visible = false;

            tbFilepath.Text = @"C:\Users\Ray\Documents\temp\QuoteFiles";

            bgwFileDownload.RunWorkerCompleted += bgwFileDownload_RunWorkerCompleted;
        }

        private void btnDownload_Click(object sender, EventArgs e)
        {
            //if (tbSymbols.Lines.Length == 0)
            //{
            //    MessageBox.Show("Must provide at least one ticker!");

            //    return;
            //}

            if (tbFilepath.Text == string.Empty)
            {
                MessageBox.Show("Must provide file path for donwload!");

                return;
            }

            List<string> tickers = new List<string>();
            for (int i = 0; i < tbSymbols.Lines.Length; i++)
            {
                string ticker = tbSymbols.Lines[i].Trim();

                if (!string.IsNullOrEmpty(ticker))
                    tickers.Add(ticker);
# if DEBUG
                MessageBox.Show(ticker);
#endif
            }

            //if (tickers.Count == 0)
            //{
            //    MessageBox.Show("Must provide at least one valid ticker!");

            //    return;
            //}

            string filePath = tbFullName.Text;

            List<object> args = new List<object>();

            args.Add(filePath);

            args.Add(dtpStart.Value);

            args.Add(dtpEndDate.Value);

            args.Add(tickers);

            bgwFileDownload.RunWorkerAsync(args);

            this.Enabled = false;

            pbGetPrice.Visible = true;
        }

        private void bgwFileDownload_DoWork(object sender, DoWorkEventArgs e)
        {

            List<object> args = (List<object>)e.Argument;

            string path = args[0].ToString();

            DateTime startDate = (DateTime)args[1];

            DateTime endDate = (DateTime)args[2];

            List<string> tickers = (List<string>)args[3];

            bool hasHeader = false;

            string header = string.Empty;

            using (System.IO.StreamWriter file = new System.IO.StreamWriter(path))
            {
                foreach (string s in tickers)
                {
                    List<HistoricalStock> prices = HistoricalStockDownloader.DownloadData(s, startDate, endDate, out header);

                    if (!hasHeader)
                    {
                        file.WriteLine(header);

                        hasHeader = true;
                    }

                    foreach (HistoricalStock price in prices)
                    {
                        file.WriteLine(price.ToString());
                    }

                    prices.Clear();
                }
            }
        }

        void bgwFileDownload_RunWorkerCompleted(object sender, System.ComponentModel.RunWorkerCompletedEventArgs e)
        {
            if (e.Cancelled == true)
            {
                MessageBox.Show("Canceled!");
            }
            else if (e.Error != null)
            {
                MessageBox.Show(string.Format("Error: {0}{1}{2}", e.Error.Message, Environment.NewLine, e.Error.StackTrace));
            }
            else
            {
                MessageBox.Show("Done!");

                Process.Start(tbFullName.Text);
            }

            this.Enabled = true;

            pbGetPrice.Visible = false;
        }

        private void tbFilepath_TextChanged(object sender, EventArgs e)
        {
            tbFullName.Text = Path.Combine(tbFilepath.Text, "Export.txt");
        }

        private void btnClear_Click(object sender, EventArgs e)
        {
            tbSymbols.Clear();
        }
    }
}

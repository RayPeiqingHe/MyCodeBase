namespace YahooFinanceDownloader
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.tbSymbols = new System.Windows.Forms.TextBox();
            this.gbStartDate = new System.Windows.Forms.GroupBox();
            this.dtpStart = new System.Windows.Forms.DateTimePicker();
            this.gbEndDate = new System.Windows.Forms.GroupBox();
            this.dtpEndDate = new System.Windows.Forms.DateTimePicker();
            this.btnDownload = new System.Windows.Forms.Button();
            this.gbFilePath = new System.Windows.Forms.GroupBox();
            this.tbFilepath = new System.Windows.Forms.TextBox();
            this.bgwFileDownload = new System.ComponentModel.BackgroundWorker();
            this.pbGetPrice = new System.Windows.Forms.ProgressBar();
            this.tbFullName = new System.Windows.Forms.TextBox();
            this.btnClear = new System.Windows.Forms.Button();
            this.groupBox1.SuspendLayout();
            this.gbStartDate.SuspendLayout();
            this.gbEndDate.SuspendLayout();
            this.gbFilePath.SuspendLayout();
            this.SuspendLayout();
            // 
            // groupBox1
            // 
            this.groupBox1.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.groupBox1.Controls.Add(this.tbSymbols);
            this.groupBox1.Location = new System.Drawing.Point(12, 45);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(845, 216);
            this.groupBox1.TabIndex = 0;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Stock Sysmbols";
            // 
            // tbSymbols
            // 
            this.tbSymbols.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tbSymbols.Location = new System.Drawing.Point(3, 27);
            this.tbSymbols.Multiline = true;
            this.tbSymbols.Name = "tbSymbols";
            this.tbSymbols.Size = new System.Drawing.Size(839, 186);
            this.tbSymbols.TabIndex = 0;
            // 
            // gbStartDate
            // 
            this.gbStartDate.Controls.Add(this.dtpStart);
            this.gbStartDate.Location = new System.Drawing.Point(15, 285);
            this.gbStartDate.Name = "gbStartDate";
            this.gbStartDate.Size = new System.Drawing.Size(401, 60);
            this.gbStartDate.TabIndex = 1;
            this.gbStartDate.TabStop = false;
            this.gbStartDate.Text = "Start Date:";
            // 
            // dtpStart
            // 
            this.dtpStart.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dtpStart.Format = System.Windows.Forms.DateTimePickerFormat.Short;
            this.dtpStart.Location = new System.Drawing.Point(3, 27);
            this.dtpStart.Name = "dtpStart";
            this.dtpStart.Size = new System.Drawing.Size(395, 31);
            this.dtpStart.TabIndex = 0;
            // 
            // gbEndDate
            // 
            this.gbEndDate.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.gbEndDate.Controls.Add(this.dtpEndDate);
            this.gbEndDate.Location = new System.Drawing.Point(485, 287);
            this.gbEndDate.Name = "gbEndDate";
            this.gbEndDate.Size = new System.Drawing.Size(369, 56);
            this.gbEndDate.TabIndex = 2;
            this.gbEndDate.TabStop = false;
            this.gbEndDate.Text = "End Date:";
            // 
            // dtpEndDate
            // 
            this.dtpEndDate.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dtpEndDate.Format = System.Windows.Forms.DateTimePickerFormat.Short;
            this.dtpEndDate.Location = new System.Drawing.Point(3, 27);
            this.dtpEndDate.Name = "dtpEndDate";
            this.dtpEndDate.Size = new System.Drawing.Size(363, 31);
            this.dtpEndDate.TabIndex = 0;
            // 
            // btnDownload
            // 
            this.btnDownload.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.btnDownload.Location = new System.Drawing.Point(41, 594);
            this.btnDownload.Name = "btnDownload";
            this.btnDownload.Size = new System.Drawing.Size(312, 85);
            this.btnDownload.TabIndex = 3;
            this.btnDownload.Text = "Download";
            this.btnDownload.UseVisualStyleBackColor = true;
            this.btnDownload.Click += new System.EventHandler(this.btnDownload_Click);
            // 
            // gbFilePath
            // 
            this.gbFilePath.Controls.Add(this.tbFilepath);
            this.gbFilePath.Location = new System.Drawing.Point(18, 370);
            this.gbFilePath.Name = "gbFilePath";
            this.gbFilePath.Size = new System.Drawing.Size(833, 100);
            this.gbFilePath.TabIndex = 4;
            this.gbFilePath.TabStop = false;
            this.gbFilePath.Text = "Down Load locaition";
            // 
            // tbFilepath
            // 
            this.tbFilepath.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tbFilepath.Location = new System.Drawing.Point(3, 27);
            this.tbFilepath.Name = "tbFilepath";
            this.tbFilepath.Size = new System.Drawing.Size(827, 31);
            this.tbFilepath.TabIndex = 0;
            this.tbFilepath.TextChanged += new System.EventHandler(this.tbFilepath_TextChanged);
            // 
            // bgwFileDownload
            // 
            this.bgwFileDownload.DoWork += new System.ComponentModel.DoWorkEventHandler(this.bgwFileDownload_DoWork);
            // 
            // pbGetPrice
            // 
            this.pbGetPrice.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.pbGetPrice.Location = new System.Drawing.Point(31, 722);
            this.pbGetPrice.Name = "pbGetPrice";
            this.pbGetPrice.Size = new System.Drawing.Size(803, 23);
            this.pbGetPrice.Style = System.Windows.Forms.ProgressBarStyle.Marquee;
            this.pbGetPrice.TabIndex = 5;
            // 
            // tbFullName
            // 
            this.tbFullName.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Left | System.Windows.Forms.AnchorStyles.Right)));
            this.tbFullName.Location = new System.Drawing.Point(24, 458);
            this.tbFullName.Name = "tbFullName";
            this.tbFullName.ReadOnly = true;
            this.tbFullName.Size = new System.Drawing.Size(821, 31);
            this.tbFullName.TabIndex = 6;
            // 
            // btnClear
            // 
            this.btnClear.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.btnClear.Location = new System.Drawing.Point(503, 594);
            this.btnClear.Name = "btnClear";
            this.btnClear.Size = new System.Drawing.Size(304, 85);
            this.btnClear.TabIndex = 7;
            this.btnClear.Text = "Clear Tickers";
            this.btnClear.UseVisualStyleBackColor = true;
            this.btnClear.Click += new System.EventHandler(this.btnClear_Click);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(12F, 25F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(869, 773);
            this.Controls.Add(this.btnClear);
            this.Controls.Add(this.tbFullName);
            this.Controls.Add(this.pbGetPrice);
            this.Controls.Add(this.gbFilePath);
            this.Controls.Add(this.btnDownload);
            this.Controls.Add(this.gbEndDate);
            this.Controls.Add(this.gbStartDate);
            this.Controls.Add(this.groupBox1);
            this.Name = "Form1";
            this.Text = "Yahoo Finance download";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.gbStartDate.ResumeLayout(false);
            this.gbEndDate.ResumeLayout(false);
            this.gbFilePath.ResumeLayout(false);
            this.gbFilePath.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.TextBox tbSymbols;
        private System.Windows.Forms.GroupBox gbStartDate;
        private System.Windows.Forms.DateTimePicker dtpStart;
        private System.Windows.Forms.GroupBox gbEndDate;
        private System.Windows.Forms.DateTimePicker dtpEndDate;
        private System.Windows.Forms.Button btnDownload;
        private System.Windows.Forms.GroupBox gbFilePath;
        private System.Windows.Forms.TextBox tbFilepath;
        private System.ComponentModel.BackgroundWorker bgwFileDownload;
        private System.Windows.Forms.ProgressBar pbGetPrice;
        private System.Windows.Forms.TextBox tbFullName;
        private System.Windows.Forms.Button btnClear;
    }
}


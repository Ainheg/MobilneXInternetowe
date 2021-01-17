
namespace CourierWinFormsApp
{
    partial class MainForm
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
            this.labelTable = new System.Windows.Forms.DataGridView();
            this.label1 = new System.Windows.Forms.Label();
            this.refreshButton = new System.Windows.Forms.Button();
            this.packageTable = new System.Windows.Forms.DataGridView();
            this.label2 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.sendButton = new System.Windows.Forms.Button();
            this.errLabel = new System.Windows.Forms.Label();
            this.logoutButton = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)(this.labelTable)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.packageTable)).BeginInit();
            this.SuspendLayout();
            // 
            // labelTable
            // 
            this.labelTable.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.labelTable.Location = new System.Drawing.Point(421, 22);
            this.labelTable.Name = "labelTable";
            this.labelTable.ReadOnly = true;
            this.labelTable.RowHeadersWidthSizeMode = System.Windows.Forms.DataGridViewRowHeadersWidthSizeMode.AutoSizeToDisplayedHeaders;
            this.labelTable.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.labelTable.Size = new System.Drawing.Size(632, 199);
            this.labelTable.TabIndex = 0;
            this.labelTable.SelectionChanged += new System.EventHandler(this.OnLabelSelected);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Comic Sans MS", 20F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(238)));
            this.label1.Location = new System.Drawing.Point(12, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(372, 38);
            this.label1.TabIndex = 1;
            this.label1.Text = "Well-Sent Aplikacja Kuriera";
            // 
            // refreshButton
            // 
            this.refreshButton.Font = new System.Drawing.Font("Microsoft Sans Serif", 15F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(238)));
            this.refreshButton.Location = new System.Drawing.Point(19, 345);
            this.refreshButton.Name = "refreshButton";
            this.refreshButton.Size = new System.Drawing.Size(365, 44);
            this.refreshButton.TabIndex = 2;
            this.refreshButton.Text = "Pobierz etykiety i paczki";
            this.refreshButton.UseVisualStyleBackColor = true;
            this.refreshButton.Click += new System.EventHandler(this.OnRefreshButtonClick);
            // 
            // packageTable
            // 
            this.packageTable.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.packageTable.Location = new System.Drawing.Point(421, 239);
            this.packageTable.Name = "packageTable";
            this.packageTable.ReadOnly = true;
            this.packageTable.RowHeadersWidthSizeMode = System.Windows.Forms.DataGridViewRowHeadersWidthSizeMode.AutoSizeToDisplayedHeaders;
            this.packageTable.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.packageTable.Size = new System.Drawing.Size(632, 199);
            this.packageTable.TabIndex = 3;
            this.packageTable.SelectionChanged += new System.EventHandler(this.OnPackageSelection);
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(421, 6);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(47, 13);
            this.label2.TabIndex = 4;
            this.label2.Text = "Etykiety:";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(421, 224);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(42, 13);
            this.label3.TabIndex = 5;
            this.label3.Text = "Paczki:";
            // 
            // sendButton
            // 
            this.sendButton.Enabled = false;
            this.sendButton.Font = new System.Drawing.Font("Microsoft Sans Serif", 15F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(238)));
            this.sendButton.Location = new System.Drawing.Point(19, 293);
            this.sendButton.Name = "sendButton";
            this.sendButton.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.sendButton.Size = new System.Drawing.Size(365, 46);
            this.sendButton.TabIndex = 6;
            this.sendButton.UseVisualStyleBackColor = true;
            this.sendButton.Click += new System.EventHandler(this.OnSendButtonClick);
            // 
            // errLabel
            // 
            this.errLabel.AutoSize = true;
            this.errLabel.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(238)));
            this.errLabel.ForeColor = System.Drawing.Color.DarkRed;
            this.errLabel.Location = new System.Drawing.Point(19, 51);
            this.errLabel.Name = "errLabel";
            this.errLabel.Size = new System.Drawing.Size(0, 20);
            this.errLabel.TabIndex = 7;
            // 
            // logoutButton
            // 
            this.logoutButton.Font = new System.Drawing.Font("Microsoft Sans Serif", 15F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(238)));
            this.logoutButton.Location = new System.Drawing.Point(19, 395);
            this.logoutButton.Name = "logoutButton";
            this.logoutButton.Size = new System.Drawing.Size(365, 43);
            this.logoutButton.TabIndex = 8;
            this.logoutButton.Text = "Wyloguj się i wyjdź";
            this.logoutButton.UseVisualStyleBackColor = true;
            this.logoutButton.Click += new System.EventHandler(this.Logout);
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1065, 450);
            this.Controls.Add(this.logoutButton);
            this.Controls.Add(this.errLabel);
            this.Controls.Add(this.sendButton);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.packageTable);
            this.Controls.Add(this.refreshButton);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.labelTable);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "MainForm";
            this.Text = "Well-Sent";
            ((System.ComponentModel.ISupportInitialize)(this.labelTable)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.packageTable)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.DataGridView labelTable;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Button refreshButton;
        private System.Windows.Forms.DataGridView packageTable;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Button sendButton;
        private System.Windows.Forms.Label errLabel;
        private System.Windows.Forms.Button logoutButton;
    }
}


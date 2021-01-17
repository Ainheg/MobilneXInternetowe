using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace CourierWinFormsApp
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            LoginForm lf = new LoginForm();
            DialogResult dr = lf.ShowDialog();
            if (dr == DialogResult.OK)
            {
                Application.Run(new MainForm(lf.Client, lf.Token));
            }
        }
    }
}

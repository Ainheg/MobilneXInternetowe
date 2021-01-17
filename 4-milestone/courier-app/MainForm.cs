using JWT.Builder;
using JWT.Algorithms;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using dotenv.net;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Net.Http;
using dotenv.net.Utilities;
using Auth0.OidcClient;

namespace CourierWinFormsApp
{
    public partial class MainForm : Form
    {
        List<LabelInfo> labels;
        List<PackageInfo> packages;
        dynamic currentSelected;
        string oauth_token;
        string token;
        string API_URL;
        string JWT_SECRET;
        static HttpClient httpClient;
        static readonly StringBuilder sb = new StringBuilder();
        static Auth0Client client;

        public MainForm(Auth0Client c, string t)
        {
            DotEnv.AutoConfig();
            API_URL = new EnvReader().GetStringValue("API_URL");
            //API_URL = "http://127.0.0.1:2100";
            JWT_SECRET = new EnvReader().GetStringValue("JWT_SECRET");
            httpClient = new HttpClient { BaseAddress = new Uri(API_URL) };
            client = c;
            oauth_token = t;
            this.ControlBox = false;
            InitializeComponent();
            GenerateToken();
            httpClient.DefaultRequestHeaders.Add("Authorization", String.Format("Bearer {0}", token));
        }

        private async void OnRefreshButtonClick(object sender, EventArgs e)
        {
            await RefreshTables();
            RefreshSendButton();
            _ = ShowErrorMessages();
        }
        private async void OnSendButtonClick(object sender, EventArgs e)
        {
            try
            {
                if (currentSelected is LabelInfo) await AddPackage();
            }
            catch 
            {
                sb.AppendLine("Nie udało się nawiązać połączenia z API");
            }
            try
            {
                if (currentSelected is PackageInfo) await UpdatePackage();
            }
            catch
            {
                sb.AppendLine("Nie udało się nawiązać połączenia z API");
            }
            await RefreshTables();
            _ = ShowErrorMessages();
        }

        private void GenerateToken()
        {            
            token = new JwtBuilder()
                .WithAlgorithm(new HMACSHA256Algorithm())
                .WithSecret("%C9}RYdkH5L]8{mb/YH,p7wjFbjPh$")
                .AddClaim("exp", DateTimeOffset.UtcNow.AddHours(24).ToUnixTimeSeconds())
                .AddClaim("sub", "courier-app")
                .AddClaim("aud", "well-sent-web-service")
                .AddClaim("iss", "well-sent-courier-app")
                .AddClaim("usr", "courier")
                .Encode();
            
            //token = " ";
        }
        private async Task AddPackage()
        {
            HttpResponseMessage response = await httpClient.PostAsync(currentSelected.Links["packages:create"].href, null);
            try
            {                
                response.EnsureSuccessStatusCode();
            }
            catch (HttpRequestException e)
            {
                Console.WriteLine("Exception mesydż: " + e.Message);
                sb.AppendLine("Tworzenie paczki: " + ((int)response.StatusCode).ToString() + " " + response.StatusCode.ToString());
            }
        }

        private async Task UpdatePackage()
        {
            HttpResponseMessage response = await httpClient.PutAsync(currentSelected.Links["packages:update_status"].href, null);
            try
            {
                response.EnsureSuccessStatusCode();
            }
            catch (HttpRequestException e)
            {
                Console.WriteLine(e.Message);
                sb.AppendLine("Zmiana statusu paczki: " + ((int)response.StatusCode).ToString() + " " + response.StatusCode.ToString());
            }
        }

        private void RefreshSendButton()
        {
            if (currentSelected == null)
            {
                sendButton.Text = "";
                sendButton.Enabled = false;
            }

            if (currentSelected is LabelInfo)
            {
                if (currentSelected.Links.ContainsKey("packages:create"))
                {
                    sendButton.Text = "Wyślij paczkę";
                    sendButton.Enabled = true;
                } 
                else
                {
                    sendButton.Text = "";
                    sendButton.Enabled = false;
                }
            }
            if (currentSelected is PackageInfo)
            {
                if (currentSelected.Links.ContainsKey("packages:update_status"))
                {                   
                    sendButton.Text = "Zmień status";
                    sendButton.Enabled = true;                
                }
                else
                {
                    sendButton.Text = "";
                    sendButton.Enabled = false;
                }
            }
        }

        private async Task RefreshTables()
        {
            try
            {
                dynamic labelsData = JsonConvert.DeserializeObject(await GetLabels());
                var labelsArray = labelsData["_embedded"].labels;
                labels = labelsArray.ToObject<List<LabelInfo>>();
                labelTable.DataSource = labels;
                labelTable.AutoResizeColumns(DataGridViewAutoSizeColumnsMode.AllCells);
                labelTable.Columns["Deliverto"].HeaderText = "Adres";
                labelTable.Columns["Name"].HeaderText = "Adresat";
                labelTable.Columns["Size"].HeaderText = "Rozmiar";
                labelTable.Columns["Sender"].HeaderText = "Nadawca";
                labelTable.Columns["Links"].Visible = false;
                labelTable.ClearSelection();
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                sb.AppendLine("Pobieranie etykiet: Nie udało połączyć z API");
            }
            try 
            { 
            dynamic packagesData = JsonConvert.DeserializeObject(await GetPackages());
            var packagesArray = packagesData["_embedded"].packages;
            packages = packagesArray.ToObject<List<PackageInfo>>();
            packageTable.DataSource = packages;
            packageTable.AutoResizeColumns(DataGridViewAutoSizeColumnsMode.AllCells);
            packageTable.Columns["Deliverto"].HeaderText = "Adres";
            packageTable.Columns["Name"].HeaderText = "Adresat";
            packageTable.Columns["Size"].HeaderText = "Rozmiar";
            packageTable.Columns["Sender"].HeaderText = "Nadawca";
            packageTable.Columns["Links"].Visible = false;
            packageTable.ClearSelection();
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                sb.AppendLine("Pobieranie paczek: Nie udało się połączyć z API");
            }
            currentSelected = null;
            RefreshSendButton();
        }

        private async Task<String> GetLabels()
        {
            string json = "";
            HttpResponseMessage response = await httpClient.GetAsync("/api/labels");
            try
            {                
                json = await response.Content.ReadAsStringAsync();
                response.EnsureSuccessStatusCode();
            }
            catch(HttpRequestException e)
            {
                Console.WriteLine(e.Message);
                sb.AppendLine("Pobieranie etykiet: " + ((int)response.StatusCode).ToString() + " " + response.StatusCode.ToString());
            }
            return json;
        }
        private async Task<String> GetPackages()
        {
            string json = "";
            HttpResponseMessage response = await httpClient.GetAsync("/api/packages");
            try
            {
                response.EnsureSuccessStatusCode();
                json = await response.Content.ReadAsStringAsync();
            }
            catch (HttpRequestException e)
            {
                Console.WriteLine(e.Message);
                sb.AppendLine("Pobieranie paczek: " + ((int)response.StatusCode).ToString() + " " + response.StatusCode.ToString());
            }
            return json;
        }

        private void OnLabelSelected(object sender, EventArgs e)
        {
            var rowsCount = labelTable.SelectedRows.Count;
            if (rowsCount <=0 || rowsCount > 1)
            {
                RefreshSendButton();
                return;
            }
            var row = labelTable.SelectedRows[0];
            currentSelected = (LabelInfo)row.DataBoundItem;
            packageTable.ClearSelection();
            RefreshSendButton();
        }

        private void OnPackageSelection(object sender, EventArgs e)
        {
            var rowsCount = packageTable.SelectedRows.Count;
            if (rowsCount <= 0 || rowsCount > 1)
            {
                RefreshSendButton();
                return;
            }
            var row = packageTable.CurrentRow;
            currentSelected = (PackageInfo)row.DataBoundItem;
            labelTable.ClearSelection();
            RefreshSendButton();
        }

        private async Task ShowErrorMessages()
        {
            errLabel.Text = sb.ToString();
            sb.Clear();
            await Task.Delay(8000);
            errLabel.Text = "";
        }

        private async void Logout(object sender, EventArgs e)
        {
            await client.LogoutAsync();
            this.Close();
        }

        protected override void OnClosed(EventArgs e)
        {
            _ = client.LogoutAsync();
            base.OnClosed(e);
        }
    }
}

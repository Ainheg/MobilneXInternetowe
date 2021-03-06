﻿using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Auth0.OidcClient;
using dotenv.net;
using dotenv.net.Utilities;

namespace CourierWinFormsApp
{
    public partial class LoginForm : Form
    {
        public Auth0Client Client { get; private set; }
        private int Attempts { get; set; } 
        public string Token { get; private set; }
        public LoginForm()
        {
            DotEnv.AutoConfig();
            Auth0ClientOptions clientOptions = new Auth0ClientOptions
            {
                Domain = new EnvReader().GetStringValue("AUTH0_DOMAIN"),
                ClientId = new EnvReader().GetStringValue("AUTH0_CLIENTID")
            };
            Client = new Auth0Client(clientOptions);
            clientOptions.PostLogoutRedirectUri = clientOptions.RedirectUri;
            InitializeComponent();    
        }
        private async void OauthLogin()
        {
            var loginResult = await Client.LoginAsync();
            if (loginResult.IsError)
            {
                Console.WriteLine($"An error occurred during login: {loginResult.Error}");
            }
            else
            {
                this.DialogResult = DialogResult.OK;
                Token = loginResult.IdentityToken;
                Console.WriteLine(Token);
            }
        }

        private void LoginClick(object sender, EventArgs e)
        {
            OauthLogin();
            if (DialogResult == DialogResult.OK)
            {
                this.Close();
            }
        }
    }
}

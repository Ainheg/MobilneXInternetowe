using Newtonsoft.Json;
using System.Collections.Generic;

namespace CourierWinFormsApp
{
    class LabelInfo
    {
        public string Sender { get; set; }
        public string Name { get; set; }
        public string Deliverto { get; set; }
        public string Size { get; set; }
        public string UID { get; set; }
        [JsonProperty("_links")]
        public Dictionary<string, LinkInfo> Links { get; set; }
    }
    class PackageInfo
    {
        public string Sender { get; set; }
        public string Name { get; set; }
        public string Deliverto { get; set; }
        public string Size { get; set; }
        public string UID { get; set; }
        public string Status { get; set; }
        [JsonProperty("_links")]
        public Dictionary<string, LinkInfo> Links { get; set; }
    }

    class LinkInfo
    {
        public string href { get; set; }
    }
}

# wooliesR - download eReceipts in machine-readable format
## Downloading eReceipts from your personal Everyday Rewards (Woolworths awards) account

11.01.2024: **UPDATE** New Woolworhts API endpoint data and walk-through on scraping your own ereceipts using Python notebook in 'ereceipt_scrape' folder. Old source codes for the web dashboard and chrome extension are moved to V0 folder, as they are not used anymore for the production dashboard and have only historical meaning. More useful code snippets are coming soon - press star!

**If you shop at Woolworth Supermarkets in Australia and use their Everyday (ex-Woolworths) Rewards Program, you can opt-in for and access your shopping receipts in digital form on their app and web account.** The eReceipts at Woolies look precisely like their paper version. You can download individual dockets as pdfs. If you want to see all your shops in one place, you would (presumably) have to copy-paste them from pdfs one by one into your spreadsheet.

I didn't like it. I like my data in sql and csv. I had to find a way to download all eReceipts from my account in JSON format using a simple script (granted, both mobile app and web app are actually fed by a basic REST API).

  > What I discovered from it shocked me: apparently, over the year, I have spent three times more money on Woolies roast chickens than on anything else :facepalm:

I published first simple DIY script for WW eReceipts here as early as 2021. But as the Woolies APIs are developing further, I publish updates.

Besides, I made all my findings available in easy-to-use solution for scraping, consolidating and plotting your retail data at [myshopdash.app](https://myshopdash.app), where you can use a specialised Chrome extension + smart backend doing processing/data enrichment to get more from your shopping data. 

### Quick start with myshopdash.app
1. **Install** client-side downloader that is a Google Chrome Extension called [myShopDash](https://chrome.google.com/webstore/detail/myshopdata-for-everyday-r/kjnoihdmllddkmfhikjlkbfcdcmghhji).

2. Open the Everyday Rewards website, **log in** and navigate to the Point activity page - the Extension insert a new prominent green download button there
3. **Run** the downloader - click the button and follow the prompts
4. When the download is done, you will have a choice - download your data as a raw json dump directly to your computer or open data in the web viewer that I put together for you. The viewer parses the json and present it as tables and charts. It provides a 'download as Excel (csv) file' feature as well.

It has a demo mode, and support eReceipt from Coles as well - check it out: https://myshopdash.app/


## Under the hood
### Client-side part - scraper
📁 `/ereceipts_scrape`

The client (browser) side part is a Chrome Browser Extension that injects
an API downloader client into a logged-in page of the woolies website, so that
user can pull out their data. The downloading happens locally. The Extension does not
send data to the internet (until the user press the button that explicitly
offers it). 

The request formats and the reverse-engeneered API are described in /ereceipt_scrape/scraper.ipynb 

### Server-side part
Coming soon: example code snippets for parsing and enrichment your scrapes.

Parsers are written in Python, and not only organise and store all the data, but also enrich it (i.e. adding department and aisles info to your bought items).
The current dashboard is build on vueJS and ChartsJS, and the code will be published as a separate repository. Previous version was based on Dash/Plotly - see the sources in /V0 folder

## Some extra details
#### Legal
You can use any of this code, but I don't take any responsibility for the results whatsoever. It is possibly against Wollies' T&C to use their site in such a way, and if they block you or come for you or nuke your house, it will not be my fault.
   * _Woolworths, if you read this: don't sue me, hire me! And I love your roast chicken!_

#### Online security
Obviously, you shouldn't enter your auth info anywhere except for the wollies website itself and do not give your password or one-time codes to anyone. My scripts don't ask you your password; you only enter your password at Woolies sites.


# wooliesR - Download eReceipts in Machine-Readable Format

## Downloading eReceipts from your personal Everyday Rewards (Woolworths Rewards) account

**11.01.2024 UPDATE:** New Woolworths API endpoint data and a walk-through on scraping your own e-receipts using a Python notebook are available in the 'ereceipt_scrape' folder. Old source codes for the web dashboard and Chrome extension have been moved to the V0 folder, as they are no longer used for the production dashboard and have only historical significance. More useful code snippets are coming soon - stay tuned!

**If you shop at Woolworth Supermarkets in Australia and use their Everyday (ex-Woolworths) Rewards Program, you can opt-in and access your shopping receipts in digital form on their app and web account.** The e-receipts at Woolies look exactly like their paper version. You can download individual dockets as PDFs. However, if you want to see all your receipts in one place, you would have to copy-paste them from PDFs one by one into your spreadsheet.

I found this process inconvenient and prefer my data in SQL and CSV. Therefore, I developed a simple script to download all e-receipts from my account in JSON format using a script (both the mobile app and web app are fed by a basic REST API).

> What I discovered shocked me: apparently, over the year, I have spent three times more money on Woolies roast chickens than on anything else! 🤦

I initially published the first simple DIY script for Woolworths e-receipts in 2021, and as Woolworths APIs continue to evolve, I periodically release updates.

Additionally, I have made all my findings available in an easy-to-use solution for scraping, consolidating, and plotting retail data at [myshopdash.app](https://myshopdash.app). You can use a specialized Chrome extension and a smart backend for processing/data enrichment to get more insights from your shopping data.

### Quick Start with myshopdash.app

1. **Install** the client-side downloader, a Google Chrome Extension called [myShopDash](https://chrome.google.com/webstore/detail/myshopdata-for-everyday-r/kjnoihdmllddkmfhikjlkbfcdcmghhji).
2. Open the Everyday Rewards website, **log in**, and navigate to the Point activity page - the Extension inserts a new prominent green download button there.
3. **Run** the downloader - click the button and follow the prompts.
4. When the download is complete, you will have a choice - download your data as a raw JSON dump directly to your computer or open the data in the web viewer. The viewer parses the JSON and presents it as tables and charts. It also provides a 'download as Excel (CSV) file' feature.

It has a demo mode and supports e-receipts from Coles as well - check it out: [myshopdash.app](https://myshopdash.app/).

## Under the Hood

### Client-side Part - Scraper
📁 `/ereceipts_scrape`

The client (browser) side part is a Chrome Browser Extension that injects an API downloader client into a logged-in page of the Woolies website, allowing the user to pull out their data. The downloading happens locally, and the Extension does not send data to the internet (until the user presses the button that explicitly offers it).

The request formats and the reverse-engineered API are described in `/ereceipt_scrape/scraper.ipynb`.

### Server-side Part

Coming soon: example code snippets for parsing and enriching your scrapes.

Parsers are written in Python and not only organize and store all the data but also enrich it (i.e., adding department and aisle info to your bought items). The current dashboard is built on VueJS and ChartsJS, and the code will be published as a separate repository. The previous version was based on Dash/Plotly - see the sources in the `/V0` folder.

## Some Extra Details

### Legal

You can use any of this code, but I don't take any responsibility for the results whatsoever. It may be against Woolies' T&C to use their site in such a way, and if they block you or take action, it will not be my fault.
   * _Woolworths, if you read this: don't sue me, hire me! And I love your roast chicken!_

### Online Security

Obviously, you shouldn't enter your auth info anywhere except for the Woolies website itself and do not give your password or one-time codes to anyone. My scripts don't ask you for your password; you only enter your password on Woolies' sites.

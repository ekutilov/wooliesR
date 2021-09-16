# wooliesR - download eReceipts in machine-readable format
## Downloading eReceipts from Everyday Rewards (Woolworths awards) account

15.09.2021: **_NEW!_** A Big Repository Revamp! More code than ever and all about Woolies!

If you shop at Woolworth Supermarkets in Australia and use their Everyday (ex-Woolworths) Rewards Program, you can opt-in for and access your shopping receipts in digital form on their app and web account. The eReceipts look precisely like their paper version. You can download individual dockets as pdfs. If you want to see all your shops in one place, you would (presumably) have to copy-paste them from pdfs one by one into your spreadsheet.

I didn't like it. I like my data in sql and csv. I had to find a way to download all eReceipts from my account in JSON format using a simple script (granted, both mobile app and web app are actually fed by a basic REST API).

  > What I discovered from it shocked me: apparently, over the year, I have spent three times more money on Woolies roast chickens than on anything else :facepalm:

I published some simple DIY script for it in early 2021, but if you prefer a rounded, easy-to-use solution, you have it now too.

### Quick start
1. **Install** client-side downloader that is a Google Chrome Extension called myShopData.

    _At this stage, I haven't got it approved for the Store (yet?), but you can download sources and
attach it as an 'unpacked extension' in Chrome's Developer mode._
2. Open the Everyday Rewards website, **log in** and navigate to the Point activity page (the Extension
has a direct link for it - just click the extension button)
3. **Run** the downloader - click the button and follow the prompts
4. When the download is done, you will have a choice - download your data as a
raw json dump directly or open data in the external viewer that I put together for you. The viewer parses the json and present it as tables and charts. It provides a 'download as
Excel file' feature as well. When used without my Chrome Extension, it will open in
a demo mode - check it out: https://myshopdash.appspot.com/dashapp/


## Under the hood
### Client-side part
📁 `/extension`

The client (browser) side part is a Chrome Browser Extension that injects
an API downloader client into a logged-in page of the woolies website, so that
user can pull out their data. The downloading happens locally. The Extension does not
send data to the internet (until the user press the button that explicitly
offers it).


### Server-side part
📁 `/dashboard`

Written in Python using Flask and Plotly/Dash. Ready for deployment in App Engine.
It takes a messy json gotten from Woolworths API and parse it getting ready for
visualising and analysis. A lot to be done there yet in terms of extracting more
meaningful insights from the data.
### Demo data
📁 `/demo_data`

The json files that the server-side tested on and ran in a demo mode on. You can use it to familiarise yourself with the format.

### Simple scripts
📁 `/_sample_scripts`

Simplified downloading JS scripts that you can inject yourself into the webpages
to understand how it works, how API works etc. There are also a couple of R scripts
can be used for parsing this data (I personally think R scripts easier to read than Python code, so that's that).

## Some extra details
#### Legal
You can use any of this code, but I don't take any responsibility for the results whatsoever. It is possibly against Wollies' T&C to use their site in such a way, and if they block you or come for you or nuke your house, it will not be my fault.
   * _Woolworths, if you read this: don't sue me, hire me! And I love your roast chicken!_

#### Online security
Obviously, you shouldn't enter your auth info anywhere except for the wollies website itself and do not give your password or one-time codes to anyone. These scripts don't ask you your password; they just work within the genuine site's environment.
#### Bugs and errors
It is just to be expected that the code (especially the server part) will not
work with every instance of user data, as it is very data-specific. It uses an API
that is not publicly open and documented. The API may also change without notice.
The code has been tested on available data, but the variants are endless. If
it does not work with your data, please, report and consider sharing your
data. If something is wrong, lets troubleshooting begin!
Some of the possible reasons the downloading has not been finished correctly might be: the session expired by timeout (there was too long between the login and the script run), your IP is temporarily blocked because script generates too many requests (system alledges ddos).
Possible reasons for the dashboard being unable to display the data are the presence of
a type of transaction that can not be recognised by parser, unexpected symbols in a json
string etc.

# wolliesR - download eReceipts in machine-readable format
#### How to download eReceipts from Everyday Rewards (Woolworths awards) account
If you shop at Woolworth Supermarkets in Australia and use their Everyday (ex Woolworths) Rewards Program, you can opt-in for and access your shopping receipts in digital form on their app and the web account. The eReceipts look precisely like their paper version. You can download individual cheques as pdfs. If you want to see all your shops together, you would probably need to copy-paste them from pdfs one by one. I didn't like it. I like my data in sql and csv. I found how to download all eReceipts from my account in JSON format using a simple script (granted, as both mobile app and web app are actually fed by a standard REST API). 
  * What I discovered from it shocked me: apparently, over the year, I have spent three times more money on Woolies roast chickens than on anything else :facepalm:	
### Quick start
Here's how I have done it and my code. You can follow (at your own risk).
1. Open Everyday Rewards website, log in and navigate to the Activity page [https://www.woolworthsrewards.com.au/index.html#/my-activity] (including passing 2FA if necessary)
2. Staying on this page, open Developers Javascript Console (Opt-Comm-J/Shift-Ctrl-J/*View>Developer>JS Console* in Chrome, Opt-Comm-C/Sh-Cntl-C/*Develop>Shop JS Console* in Safary)
3. Copy JS code from `downloader.js` into console's command line (after `>`) and enter to execute. It takes some while, but there are log messages to keep track on
4. The page will change to a new one with only two text fields on. These need to be copied and pasted into two separate plain text files; those are your data in a plain JSON format
      * JSON files can be viewed, transformed and analysed in many modern tools (I'm sure Excel can read it now, I guess one can use Alteryx, Tableau, Python, Javascript and so on). They also might be copied directly into one of the online JSON parsing tools to see them in more user-friendly formatting (google 'parse json online' and 'json to table online').
6.  I'm a R-guy, so I have just build a script to transform my data into a tidy table 
      * `woolworth_cleaning.R` reads the two files from the current working directory (named `list_example.json` and `receipts_example.json` in this case, the files are also provided for reference), transforms them into 2 tidy tables, parse text data where necessary and writes `transactions_list.csv` and `all_items.csv` that can be directly opened in MS Excel. `woolworth_analysis.R` shows a few examples of how this data can be summarised on-the-fly in R
      * (to be done: put on a jupyter notebook with the code)

### Details
#### Legal
You can use any of this code, but I don't take any responsibility for the results whatsoever. It is possibly against Wollies' T&C to use their site in such a way, and if they block you or come for you or nuke your house, it will not be my fault.
   * Wollworths, if you read this: don't sue me, hire me! And I love your roast chicken! 

Besides, I am not a java coder, it is a just a handy makeshift solution. If it crashes, it is to be expected. It is possible that at some point Woolworths will just roll out a native eReceipt bulk export feature, and this will become obsolete.
#### Online security
Obviously, you shouldn't enter your auth info anywhere except for the wollies website itself and do not give your password or one-time codes to anyone. This script doesn't ask you your password; it just works within the site's environment. It also does not upload or save your information anywhere. You can (and should) check that the code doesn't compromise your personal information before you use it. 
#### Bugs and errors
The script does not check if the requests to the API are executed correctly (does not even save the respond status code) and the replies are returned with the correct return code. Check through the resulting files to make sure you have all your eReceipts in them. In `examples` files you can see how they should look like. If something is wrong, lets troubleshooting begin!
On the surface, some of the possible reasons the downloading has not been finished correctly might be: the session expired by timeout (there was too long between the login and the script run), your IP is temporarily blocked because script generates too many requests (system alledges ddos).
The process is tested on my data only in Chrome and Safary.
#### From JSON to table
JSON is a ubiquitous format for storing data, but it is semi-structured, so there is no straight way to convert it into a flat table. There will be "nesting" (tables within a table cell) happening. You can see an example of how to parse it in my scripts. 

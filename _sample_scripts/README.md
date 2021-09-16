## wooliesR - download eReceipts in machine-readable format
### Basic scripts
I wrote this js code in 2021 to showcase how Woolworths Rewards App API works and how
it can be used to collect your data (well, it belongs to user, doesn't it, so the users
should be able to download it it they want).
#### Directions
1. Open Everyday Rewards website, log in and navigate to the Activity page [https://www.woolworthsrewards.com.au/index.html#/my-activity] (including passing 2FA if necessary)
2. Staying on this page, open Developers Javascript Console (Opt-Comm-J/Shift-Ctrl-J/*View>Developer>JS Console* in Chrome, Opt-Comm-C/Sh-Cntl-C/*Develop>Shop JS Console* in Safary)
3. Copy JS code from `downloader.js` into console's command line (after `>`) and enter to execute. It takes some while, but there are log messages to keep track on
4. The page will change to a new one with a text field on. The text from it needs to be copied and pasted into a plain text file; those are your data in a plain JSON format.
      * JSON files can be viewed, transformed and analysed in many modern tools (I'm sure Excel can read it now, I guess one can use Alteryx, Tableau, Python, Javascript and so on). They also might be copied directly into one of the online JSON parsing tools to see them in more user-friendly formatting (google 'parse json online' and 'json to table online').
5.  I'm a R-guy, so I have built an R script to transform my data into a tidy table
      * `woolworth_cleaning.R` reads the two files from the current working directory (named `list_example.json` and `receipts_example.json` in this case, the files are also provided for reference), transforms them into 2 tidy tables, parse text data where necessary and writes `transactions_list.csv` and `all_items.csv` that can be directly opened in MS Excel. `woolworth_analysis.R` shows a few examples of how this data can be summarised on-the-fly in R
      * (TODO: put on a jupyter notebook with the code)

### Details
#### Legal
Again, you can use any of this code, but I don't take any responsibility for the results whatsoever. It might be against Wollies' T&C to use their site in such a way, and if they block you or come for you or nuke your house, it will not be my fault.

It is possible that Woolworths will just roll out a native eReceipt bulk export feature at some point, and this will become obsolete.
#### Security
This script doesn't ask you your password; it just works within the site's environment. It also does not upload or save your information anywhere. You can (and should) check that the code doesn't compromise your personal information before you use it.
#### Bugs and errors
The script does not check if the requests to the API are executed correctly (does not even save the response status code) and the replies are returned with the correct return code. Check through the resulting files to make sure you have all your eReceipts in them. In `examples` files, you can see how they should look like.
#### From JSON to table
JSON is a ubiquitous format for storing data, but it is semi-structured, so there is no straightforward way to convert it into a flat table. There will be "nesting" (tables within a table cell) happening. You can see an example of how to parse it in my scripts.

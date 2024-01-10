require(tidyverse)
require(jsonlite)

# ==> change directory if necessary
setwd("~/Documents/RStudio/woolworth/js")

list_j <- read_json(path ='list_example.json', simplifyVector = FALSE, simplifyDataFrame = TRUE, 
                    flatten = TRUE) 
ereceipts_j <- read_json(path ='receipts_example.json', simplifyVector = FALSE, 
                    simplifyDataFrame = FALSE, flatten = T) %>% unlist(recursive = F) 

ereceipts <- ereceipts_j %>% tibble() %>% rename(data = everything()) %>% 
  unnest_wider(data) %>% 
  unnest_wider(download, names_sep = '.') %>% 
  unnest_wider(details, names_sep = '.') %>%
  unnest_wider(details.1, names_sep = '.') %>% 
  unnest_wider(details.2, names_sep = '.') %>%
  unnest_wider(details.3, names_sep = '.') %>% 
  unnest_wider(details.4, names_sep = '.') %>%
  unnest_wider(details.5, names_sep = '.') %>% 
  unnest_wider(details.4.receiptTotal, names_sep = '.') %>%
  unnest_wider(details.4.gst, names_sep = '.') 

# now parse the ereceipts data into itemised list of purchases (unroll the nested 'items' column)
# (you still can group the final dataset on the transaction level by field 'key' or join with the unprocessed data

all_items <- ereceipts %>% 
  select(key, details.3.items) %>% 
  unnest_longer(details.3.items) %>%
  unnest_wider(details.3.items) %>%
  mutate(
    price_reduced_note =  lead(str_detect(description, 'PRICE REDUCED'), default = FALSE) %>%
                          if_else(lead(description), ""), 
    prefixHash =  str_starts(description, '#'),
    description = prefixHash %>% if_else(str_remove(description, '#'), description)
        ) %>%
  mutate(
    is_second_line = str_detect(description, 'Qty ') | str_detect(description, 'NET @'),
    description2   = is_second_line %>% if_else(description, ''),
    Description    = is_second_line %>% if_else(lag(description), description),
    prefixChar     = is_second_line %>% if_else(lag(prefixChar), prefixChar)
        ) %>%
  filter(amount!="") %>% select(-is_second_line) %>%
  extract(description2, 
          regex = "Qty ([0-9]+) @ \\$([0-9]+\\.[0-9]+) each",
          into = c('Qty', 'Price'), remove = FALSE) %>%
  extract(description2,
          regex = '([0-9]+\\.[0-9]+) ([a-y]+) NET @ \\$([0-9]+\\.[0-9]+)/[a-y]+',
          into = c('Qty2', 'Unit', 'Price2'), remove = FALSE) %>%
  mutate(
        Qty =   ifelse(!is.na(Qty),   Qty,   if_else(!is.na(Qty2),   Qty2,   '1')) %>% as.numeric,
        Price = ifelse(!is.na(Price), Price, if_else(!is.na(Price2), Price2, amount)) %>% as.numeric,
        Amount = amount %>% as.numeric
        ) %>%
  replace_na(list(Unit = 'ea', prefixChar = '', price_reduced_note = '')) %>%
  select(key, 
         Description, 
         Qty, 
         Unit, 
         Price, 
         Amount, 
         prefixChar, 
         prefixHash, 
         price_reduced_note)

# Now tidy transaction list  
# First, our statement includes of not only eReceipts but some other purchases 
# (i.e. in gas stations etc that don't provide eReceipts)

ereceipts_list <- list_j %>% filter(receiptKey != "") 
# receipts_others <- receipts_list %>% filter(receiptKey == "") # if you want to analyse other transactions (lacking eReceipts)

ereceipts_list_tidy <- ereceipts %>%
  mutate(
    Total = details.2.total %>% str_replace('\\$', '') %>% as.numeric,
    GST = details.4.gst.amount %>% str_replace('\\$', '') %>% as.numeric,
    NItems = details.4.receiptTotal.description %>% str_extract('[0-9]+'),
        ) %>%
  rowwise() %>%  
  mutate(Savings = list(str_match(details.6$savings, '\\$([0-9]+\\.[0-9]+) ')[2])) %>% unnest(Savings) %>%
  full_join(ereceipts_list, by = c('key' = 'receiptKey')) %>% arrange(key)%>%
  replace_na(list(GST = 0, Savings = 0)) %>%
  select(key,
         Title = details.1.title,
         StoreName = storeName,
         Address = details.1.content,
         StoreN = details.1.storeNo,
         Total,
         GST,
         NItems,
         Savings,
         Points = pointsEarned,
         DateTime = transactionDate
  )

# save to CSV as below to download and export somewhere else 
# (or check ;analysis' script for examples in R)

write_csv(all_items, file = 'all_items.csv')
write_csv(ereceipts_list_tidy, file = 'transactions_list.csv')



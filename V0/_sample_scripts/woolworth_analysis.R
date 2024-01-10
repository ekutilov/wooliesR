require(lubridate)

#stats

# TOP-10 articles by quantity you bought
all_items %>% group_by(Description) %>% summarise(n = sum(Qty)) %>% arrange(-n) %>% top_n(10)

# TOP-10 priciest items you bought (per unit price)
all_items %>% arrange(desc(Price)) %>% top_n(10)

# your spendings by month
ereceipts_list_tidy %>% mutate(ym = paste0(year(DateTime), '-', formatC(month(DateTime), width = 2, flag = '0'))) %>% 
  group_by(ym) %>% summarise(a = sum(Total))

# your spendings by hour of day
ereceipts_list_tidy %>% mutate(hr = formatC(hour(DateTime), width = 2, flag = '0')) %>% 
  group_by(hr) %>% summarise(a = sum(Total)) 


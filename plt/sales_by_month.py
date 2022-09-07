#!/bin/python3
from datetime import datetime
import fdb
from calendar import prevmonth,nextmonth

'''Getting dates, of current month and a year ago, simple subtraction'''
x = (datetime.now().year, datetime.now().month, 1) #starting date, curr month
date1 = datetime(*x)
datelist=[x[:2]]
[datelist.append(prevmonth(*datelist[-1])) for y in range(1,14)] #list of previous months
t = datelist[-1] #minus 12 months
datelist.pop(0)
date2 = datetime(*t,1)
'''connection to fbdb'''
con = fdb.connect(dsn='vps:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='kb8X3a1G', charset ='WIN1251')
cur = con.cursor()

'''GETTING COMPANY NAMES AND SALES FOR EACH COMPANY'''
get_comp_names = "select sw.group_name, sw.num from TOVAR_MOVE tm, vnakl vn, TOVAR_NAME tn, print_view_sklad('0','{}') sw WHERE tm.tovar_id = tn.num AND tm.doc_id = vn.num AND sw.num = tn.tip AND tm.doc_type_id = 1 AND tm.from_sklad_id = '{}' AND tm.mdate >= '{}' AND tm.mdate <= '{}' GROUP BY sw.group_name, sw.num"
get_sales = "select SUM(SALE_OUT_TOVAR_SUMA) from pribil_fifo_v1({}, '{}', '{}', {}, 0, -1) pr, print_view_sklad(0,{}) gr where (pr.sale_out_tovar_kolvo - pr.sale_from_out_tovar_kolvo) > 0 AND gr.num = pr.tip"

'''MAKE SQL SUM BY BRAND BY MONTH'''



def fetch_sales(shop, date_begin, date_end):
    '''function to get sales given shop id and dates; returns x as company name and y as company id in a list of lists'''
    cmd = get_comp_names.format(shop, shop, date_begin, date_end)
    cur.execute(cmd)
    sales = cur.fetchall()
    return(sales)

saks_sales = fetch_sales(6, date2, date1)

for x, y in saks_sales:
        cmd = get_sales.format(shop, date_s1, date_s2, y, shop) #replace 270 with y
        cur.execute(cmd)
        company_sales = cur.fetchall()
        print(x, date_s1, date_s2)
        print(company_sales)
        #company_stores = fetch_stores(shop, today, y)
        #company_storage = fetch_storage(storage, today,y)
        array.append(company_sales)
    print(array)

def sales_sum(shop, date_s1, date_s2, sales_in_shop):
    '''fetching sales sum, provided previous data on sales, shop id, dates, and lasly - shop name'''
    array = []
    for x, y in sales_in_shop:
        cmd = get_sales.format(shop, date_s1, date_s2, y, shop) #replace 270 with y
        cur.execute(cmd)
        company_sales = cur.fetchall()
        print(x, date_s1, date_s2)
        print(company_sales)
        #company_stores = fetch_stores(shop, today, y)
        #company_storage = fetch_storage(storage, today,y)
        array.append(company_sales)
    print(array)
    
#for tup in datelist:
#    f = sales_sum(6,datetime.strftime(datetime(*tup,1), '%Y/%m/%d'), datetime.strftime(datetime(*nextmonth(*tup),1), '%Y/%m/%d'), saks_sales)
#    print(f)
#allsum = [sales_sum(6,datetime.strftime(datetime(*tup,1), '%Y/%m/%d'), datetime.strftime(datetime(*nextmonth(*tup),1), '%Y/%m/%d'), saks_sales) for tup in datelist]
    
#sales_sum(6, datetime.strftime(date2, '%Y/%m/%d'), datetime.strftime(date1, '%Y/%m/%d'), saks_sales)

#!/usr/bin/python3
import fdb
from calendar import monthrange, month_name
import codecs
import csv
import time
import os
from datetime import datetime
#------------------------TIME PERIOD-----------------------------------
curr_month = int(time.strftime('%m'))
month = str(curr_month - 1 if curr_month > 1 else 12)
year = time.strftime('%Y')
last_day_of_month = monthrange(int(year), int(month))[1]
date1 = year + " , " + month + " , 01"
date2 = year + " , " + month + " , " + str(last_day_of_month)
date_s1 = year + "/" + month + "/01"
date_s2 = year + "/" + month + "/" + str(last_day_of_month)
file_pref =  '_' + year + '_' + month_name[int(month)]
today = year + " , " + str(curr_month) + " , 01"
#------------------------STORE ID'S------------------------------------
yarval = 2
saks = 6
odessa = 3
yarval_name = "Ярославов Вал, Киев"
odessa_name = "Ланжероновская, Одесса"
saks_name = "Саксаганского 37, Киев"
#-----------------------FDB CONNECTION OPTIONS-------------------------
con = fdb.connect(dsn='vps:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='kb8X3a1G', charset ='WIN1251')
cur = con.cursor()
header = ['Поставщик', 'Код', 'Товар', 'Цена', 'К-во', 'Сумма']
#----------------------GETTING COMPANY NAMES AND SALES FOR EACH COMPANY------------
get_comp_names = "select sw.group_name, sw.num from TOVAR_MOVE tm, vnakl vn,\
 TOVAR_NAME tn, print_view_sklad('0','{}') sw WHERE tm.tovar_id = tn.num AND tm.doc_id = vn.num \
 AND sw.num = tn.tip AND tm.doc_type_id = 1 AND tm.from_sklad_id = '{}' AND tm.mdate >= '{}' AND tm.mdate <= '{}'\
  GROUP BY sw.group_name, sw.num"
get_sales = "select gr.group_name, pr.kod, pr.name,\
 ((pr.sale_in_tovar_suma - pr.sale_from_in_tovar_suma + pr.sale_over_out_tovar_suma) / (pr.sale_out_tovar_kolvo - pr.sale_from_out_tovar_kolvo)),\
CAST (pr.SALE_OUT_TOVAR_KOLVO - pr.SALE_FROM_OUT_TOVAR_KOLVO as integer),\
CAST ((pr.sale_in_tovar_suma - pr.sale_from_in_tovar_suma + pr.sale_over_out_tovar_suma) as integer)\
 from pribil_fifo_v1({}, '{}', '{}', {}, 0, -1) pr,\
 print_view_sklad(0, {}) gr where (pr.sale_out_tovar_kolvo - pr.sale_from_out_tovar_kolvo) > 0  AND gr.num = pr.tip ORDER BY gr.group_name, pr.kod, pr.name"
#----------------------NEW----GETTING-STORAGE-DATA---------------------------------
get_stored = "select gr.group_name, t.kod, t.name, t.cena, s.z_kolvo, ((s.z_kolvo * t.cena)) from view_sklad_zal({}, '{}') s, tovar_name t, print_view_sklad({}, {}) gr\
 WHERE s.num = t.num AND t.tip = gr.num AND s.z_kolvo > 0"

header = ['Пр-в', 'Код', 'Товар', 'Цена', 'К-во', 'Сумма']


def fetch_sales(shop, date_begin, date_end):
    '''function to get sales given shop id and dates; returns x as company name and y as company id in a list of lists'''
    cmd = get_comp_names.format(shop, shop, date_begin, date_end)
    cur.execute(cmd)
    sales = cur.fetchall()
    return(sales)

def fetch_stores(shop, today, y):
    '''function to get stored goods given shop id and dates; returns x as company name and y as company id in a list of lists'''
    ''' to be invoked from within sales_details function! '''
    cmd = get_stored.format(shop, today, y, shop)
    cur.execute(cmd)
    stores = cur.fetchall()
    return(stores)


yarval_sales = fetch_sales(yarval, date1, date2)
odessa_sales = fetch_sales(odessa, date1, date2)
saks_sales = fetch_sales(saks, date1, date2)
#----------------------CHANGING WORKING DIRECTORY----------------------------------
working_dir = "/tmp/reports_" + month
if not os.path.exists(working_dir):
    os.makedirs(working_dir)
os.chdir(working_dir)


def sales_details(shop, date_s1, date_s2, sales_in_shop, shop_name):
    '''fetching sales, provided previous data on sales, shop id, dates, and lasly - shop name'''
    for x, y in sales_in_shop:
        cmd = get_sales.format(shop, date_s1, date_s2, y, shop)
        cur.execute(cmd)
        company_sales = cur.fetchall()
        company_stores = fetch_stores(shop, today, y)
        
        try:
           with codecs.open(x.replace("/",".") + file_pref + ".csv", 'a', encoding='cp1251') as f:
                csv_out = csv.writer(f, delimiter=";")
                csv_out.writerow([shop_name, "", datetime.now()])
                csv_out.writerow(header)
                csv_out.writerow(['Продажи:'])
                for row in company_sales:
                    csv_out.writerow(row)
                csv_out.writerow(["Остатки:"])
                for row in company_stores:
                    row = list(row)
                    row[4] = int(row[4])
                    csv_out.writerow(row)
                f.close()

        except IOError:
            with codecs.open(x.replace("/",".") + file_pref + ".csv", 'w', encoding='cp1251') as f:
                csv_out = csv.writer(f, delimiter=";")
                csv_out.writerow([shop_name, "", datetime.now()])
                csv_out.writerow(header)
                csv_out.writerow(['Продажи:'])
                for row in sales_in_shop:
                    csv_out.writerow(row)
                csv_out.writerow(["Остатки:"])
                for row in company_stores:
                    row[4] = int(row[4])
                    csv_out.writerow(row)
                f.close()
       
sales_details(saks, date_s1, date_s2, saks_sales, saks_name)
sales_details(yarval, date_s1, date_s2, yarval_sales, yarval_name)
sales_details(odessa, date_s1, date_s2, odessa_sales, odessa_name)


con.close()

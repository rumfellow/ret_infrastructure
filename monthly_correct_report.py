#!/usr/bin/python3
import fdb
from calendar import monthrange
from calendar import month_name
import codecs
import csv
import time
#------------------------TIME PERIOD-----------------------------------
print('Input month:', end=' ')
month = input()
year = time.strftime('%Y')
last_day_of_month = monthrange(int(year), int(month))[1]
date1 = year + " , " + month + " , 01"
date2 = year + " , " + month + " , " + str(last_day_of_month)
date_s1 = year + "/" + month + "/01"
date_s2 = year + "/" + month + "/" + str(last_day_of_month)
file_pref =  '_' + year + '_' + month_name[int(month)]
#------------------------STORE ID'S------------------------------------
yarval = 2
saks = 6
odessa = 3
#-----------------------FDB CONNECTION OPTIONS-------------------------
con = fdb.connect(dsn='vps:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='kb8X3a1G', charset ='WIN1251')
cur = con.cursor()
header = ['Пр-в', 'Код', 'Товар', 'Цена', 'К-во', 'Сумма']
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
#----------------------FETCHING YARVAL SALES, COMP NAME/ID ONLY---------------------
cmd = get_comp_names.format(yarval,yarval, date1, date2)
cur.execute(cmd)
sales_yarval = cur.fetchall()

#----------------------FETCHING YARVAL COMPANY SAILS DETAILS------------------------
for x, y in sales_yarval:
    cmd = get_sales.format(yarval,date_s1, date_s2, y, yarval)
    cur.execute(cmd)
    company_sales = cur.fetchall()
    with codecs.open(x.replace("/",".") + file_pref + ".csv", 'w', encoding='cp1251') as f:
        csv_out = csv.writer(f, delimiter = ";")
        csv_out.writerow(["Ярославов Вал, Киев"])
        csv_out.writerow(header)
        for row in company_sales:
            csv_out.writerow(row)

#----------------------FETCHING SAKS SALES, COMP NAME/ID ONLY---------------------
cmd = get_comp_names.format(saks, saks, date1, date2)
cur.execute(cmd)
sales_saks = cur.fetchall()

#----------------------FETCHING SAKS COMPANY SAILS DETAILS------------------------
for x, y in sales_saks:
    cmd = get_sales.format(saks,date_s1, date_s2, y,saks)
    cur.execute(cmd)
    company_sales = cur.fetchall()
    try:
        with codecs.open(x.replace("/",".") + file_pref + ".csv", 'a', encoding='cp1251') as f:
            csv_out = csv.writer(f, delimiter=";")
            csv_out.writerow(["Саксаганского, Киев"])
            for row in company_sales:
                csv_out.writerow(row)
    except IOError:
        with codecs.open(x.replace("/",".") + file_pref + ".csv", 'w', encoding='cp1251') as f:
            csv_out = csv.writer(f, delimiter=";")
            csv_out.writerow(["Саксаганского, Киев"])
            csv_out.writerow(header)
            for row in company_sales:
                csv_out.writerow(row)

#----------------------FETCHING ODESSA SALES, COMP NAME/ID ONLY---------------------
cmd = get_comp_names.format(odessa, odessa, date1, date2)
cur.execute(cmd)
sales_odessa = cur.fetchall()

#----------------------FETCHING ODESSA COMPANY SAILS DETAILS------------------------
for x, y in sales_odessa:
    cmd = get_sales.format(odessa,date_s1, date_s2, y,odessa)
    cur.execute(cmd)
    company_sales = cur.fetchall()
    try:
        with codecs.open(x.replace("/",".") + file_pref + ".csv", 'a', encoding='cp1251') as f:
            csv_out = csv.writer(f, delimiter=";")
            csv_out.writerow(['Ланжероновская, Одесса'])
            for row in company_sales:
                csv_out.writerow(row)
    except IOError:
        with codecs.open(x.replace("/",".") + file_pref + ".csv", 'w', encoding='cp1251') as f:
            csv_out = csv.writer(f, delimiter=";")
            csv_out.writerow("Ланжероновская, Одесса")
            csv_out.writerow(header)
            for row in company_sales:
                csv_out.writerow(row)

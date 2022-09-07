#!/usr/bin/python3
import fdb
from datetime import datetime
import codecs
import csv
#------------------------TIME PERIOD-----------------------------------
date1 = "2017 , 12 , 01 , 0, 0"
date2 = "2017 , 12 , 31 , 0, 0"
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
get_sales = "select sw.group_name, tm.from_cena, tn.name, tn.cena,  SUM(tm.from_kolvo) AS tov_kolvo, SUM(tm.from_kolvo*tn.cena) AS tov_cena from TOVAR_MOVE tm, vnakl vn,\
 TOVAR_NAME tn, print_view_sklad('0','{}') sw WHERE tm.tovar_id = tn.num AND tm.doc_id = vn.num \
 AND sw.num = tn.tip AND tm.doc_type_id = 1 AND tm.from_sklad_id = '{}' AND tm.mdate >= '{}' AND tm.mdate <= '{}'\
  AND sw.num = '{}' GROUP BY 1, 2, 3, 4"
#----------------------FETCHING YARVAL SALES, COMP NAME/ID ONLY---------------------
cmd = get_comp_names.format(yarval, yarval, date1, date2)
cur.execute(cmd)
sales_yarval = cur.fetchall()

#----------------------FETCHING YARVAL COMPANY SAILS DETAILS------------------------
for x, y in sales_yarval:
    cmd = get_sales.format(yarval, yarval, date1, date2, y)
    cur.execute(cmd)
    company_sales = cur.fetchall()
    with codecs.open(x+".csv", 'w', encoding='cp1251') as f:
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
    cmd = get_sales.format(saks, saks, date1, date2, y)
    cur.execute(cmd)
    company_sales = cur.fetchall()
    try:
        with codecs.open(x + ".csv", 'a', encoding='cp1251') as f:
            csv_out = csv.writer(f, delimiter=";")
            csv_out.writerow(["Саксаганского, Киев"])
            for row in company_sales:
                csv_out.writerow(row)
    except IOError:
        with codecs.open(x + ".csv", 'w', encoding='cp1251') as f:
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
    cmd = get_sales.format(odessa, odessa, date1, date2, y)
    cur.execute(cmd)
    company_sales = cur.fetchall()
    try:
        with codecs.open(x + ".csv", 'a', encoding='cp1251') as f:
            csv_out = csv.writer(f, delimiter=";")
            csv_out.writerow(["Ланжероновская, Одесса"])
            for row in company_sales:
                csv_out.writerow(row)
    except IOError:
        with codecs.open(x + ".csv", 'w', encoding='cp1251') as f:
            csv_out = csv.writer(f, delimiter=";")
            csv_out.writerow(["Ланжероновская, Одесса"])
            csv_out.writerow(header)
            for row in company_sales:
                csv_out.writerow(row)


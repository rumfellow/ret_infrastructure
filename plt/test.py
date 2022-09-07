#!/usr/bin/python3
import fdb
import calendar
from datetime import datetime
import matplotlib.pyplot as plt

nw = datetime.now()
con = fdb.connect(dsn='vps:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='kb8X3a1G', charset ='WIN1251')
cur = con.cursor()

full_weeks_this_month = calendar.Calendar().monthdatescalendar(2019,5)
full_weeks_prev_year_month = calendar.Calendar().monthdatescalendar(2018,5)
#print(full_weeks_this_month, full_weeks_prev_year_month)


def day_sales():
    #date1 = str(year) + "," + " " + str(month)+ "," + " " + str(day)+ "," + " " + "0"+ "," + " " + "0"
    #date1 = datetime(2019,5,10)
    #print(date1)
    cur.execute("select tn.cena_r from TOVAR_MOVE tm, vnakl vn,\
 TOVAR_NAME tn, print_view_sklad('0','6') sw WHERE tm.tovar_id = tn.num AND tm.doc_id = vn.num \
 AND sw.num = tn.tip AND tm.doc_type_id = 1 AND tm.from_sklad_id = '6' AND tm.mdate = '%s'" % datetime(2019,5,10))
    row = cur.fetchall()
    sales = sum([x[0] for x in row])
    print(sales)
    return sales
day_sales()

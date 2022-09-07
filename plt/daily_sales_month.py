#!/usr/bin/python3
import fdb
import calendar
from datetime import datetime
import matplotlib.pyplot as plt

nw = datetime.now()
con = fdb.connect(dsn='vps:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='kb8X3a1G', charset ='WIN1251')
cur = con.cursor()
this_month = []
prev_year_month = []
days_total = calendar.monthrange(nw.year,nw.month)[1]
print('Введите номер месяца: ')
month = int(input())

def day_sales():
    date1 = str(year) + "," + " " + str(month)+ "," + " " + str(day)+ "," + " " + "0"+ "," + " " + "0"
    cur.execute("select tn.cena_r from TOVAR_MOVE tm, vnakl vn,\
 TOVAR_NAME tn, print_view_sklad('0','6') sw WHERE tm.tovar_id = tn.num AND tm.doc_id = vn.num \
 AND sw.num = tn.tip AND tm.doc_type_id = 1 AND tm.from_sklad_id = '6' AND tm.mdate = '%s'" % date1)
    row = cur.fetchall()
    sales = sum([x[0] for x in row])
    return sales

for x in range(1,days_total):
    day = x
    year = nw.year
    this_month.append(day_sales())
    year = nw.year - 1
    prev_year_month.append(day_sales())


print(this_month, prev_year_month)


plt.style.use('seaborn-whitegrid')
xaxis = range(1,days_total)
plt.plot(xaxis, this_month, color = 'g', label=calendar.month_name[month])
plt.plot(xaxis, prev_year_month, color = 'orange', label='Previous year')
plt.xlabel(f"Сумма текущего месяца = {sum(this_month)};  сумма предыдущего: {sum(prev_year_month)}")
plt.xticks(xaxis)
plt.legend()
plt.show()




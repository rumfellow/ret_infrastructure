#!/usr/bin/python3
import fdb
import calendar
from datetime import datetime
import matplotlib.pyplot as plt

nw = datetime.now()
con = fdb.connect(dsn='vps:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='kb8X3a1G', charset ='WIN1251')
cur = con.cursor()

days_total = calendar.monthrange(nw.year,nw.month)[1]
print('Введите номер месяца: ')
month = int(input())
this_month = calendar.Calendar().monthdatescalendar(nw.year, month)
prev_year_month = calendar.Calendar().monthdatescalendar(nw.year - 1, month)
#print(this_month)
print(prev_year_month)
this_month_sales = []
prev_year_month_sales = []
def day_sales():
    cur.execute("select tn.cena_r from TOVAR_MOVE tm, vnakl vn,\
 TOVAR_NAME tn, print_view_sklad('0','6') sw WHERE tm.tovar_id = tn.num AND tm.doc_id = vn.num \
 AND sw.num = tn.tip AND tm.doc_type_id = 1 AND tm.from_sklad_id = '6' AND tm.mdate = '%s'" % x)
    row = cur.fetchall()
    sales = sum([r[0] for r in row])
    return sales

for a in range(len(this_month)):
    for x in this_month[a]:
        this_month_sales.append(day_sales())

for a in range(len(prev_year_month)):    
    for x in prev_year_month[a]:
        prev_year_month_sales.append(day_sales())



plt.style.use('seaborn-whitegrid')
#xaxis = [s.strftime("%d") for s in this_month for s in s] #flatup of datetime
plt.plot(this_month_sales, color = 'g', label=calendar.month_name[month])
plt.plot(prev_year_month_sales, color = 'orange', label='Прошлый год')
mylabels=['Пн','Вт','Ср','Чт','Пт','Сб','Вс']
plt.xlabel(f"Месяцы с полными неделями. Начало первой недели текущего месяца: {this_month[0][0]}, в прошлом году: {prev_year_month[0][0]} \n Конец текущего месяца: {this_month[-1][-1]}, в прошлом году:{prev_year_month[-1][-1]}")
plt.xticks(ticks=range(0,35), labels=mylabels*5)
plt.legend()
plt.show()

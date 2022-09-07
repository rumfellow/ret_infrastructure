#!/bin/python3
from datetime import datetime
import fdb
from calendar import prevmonth,nextmonth
import matplotlib.pyplot as plt

'''connection to fbdb'''
con = fdb.connect(dsn='vps:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='kb8X3a1G', charset ='WIN1251')
cur = con.cursor()

'''GETTING COMPANY NAMES AND SALES FOR EACH COMPANY'''
get_comp_names = "select sw.group_name, sw.num from TOVAR_MOVE tm, vnakl vn, TOVAR_NAME tn, print_view_sklad('0','{}') sw WHERE tm.tovar_id = tn.num AND tm.doc_id = vn.num AND sw.num = tn.tip AND tm.doc_type_id = 1 AND tm.from_sklad_id = '{}' AND tm.mdate >= '{}' AND tm.mdate <= '{}' GROUP BY sw.group_name, sw.num"
#get_sales = "select SUM(SALE_OUT_TOVAR_SUMA) from pribil_fifo_v1({}, '{}', '{}', {}, 0, -1) pr, print_view_sklad(0,{}) gr where (pr.sale_out_tovar_kolvo - pr.sale_from_out_tovar_kolvo) > 0 AND gr.num = pr.tip"
get_sales = "SELECT SUM(tm.from_suma) AS tov_suma FROM tovar_move tm, vnakl vn, print_view_sklad({},6) sw, tovar_name tn WHERE tm.doc_type_id = 1 AND tm.doc_id = vn.num AND tm.mdate >= '{}' AND tm.mdate <= '{}' AND sw.num = tn.tip AND tm.tovar_id = tn.num AND tm.from_sklad_id = 6 HAVING SUM(tm.from_kolvo) > 0"

'''setting 1 year period in datetime format '''
this_year = (datetime.now().year, datetime.now().month, 1) #this month: Y,m,1
previous_year = this_year[0] - 1,*this_year[1:]
period_start = datetime(*previous_year)
period_end = datetime(*this_year)

'''setting date lists'''
previous_months = [prevmonth(*this_year[:2])]
for x in range(1,12):
    previous_months.append(prevmonth(*previous_months[-1]))
previous_months = previous_months[::-1]
current_months = [this_year[:2]]
for x in range(1,12):
    current_months.append(prevmonth(*current_months[-1]))
current_months = current_months[::-1]

'''setting plotting details'''
def plot(datelist, result, brand):
    result_unpacked = [0 if x == [] else x[0][0] for x in result]
    dates_converted = [datetime.strftime(datetime(*x,1), '%Y/%m') for x in datelist]
    fig,ax = plt.subplots()
    ax.bar(dates_converted, result_unpacked, label="Продажи")
    ax.text(0.0, 1.05, f"Дата отчета: {datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')}", transform=ax.transAxes, fontsize=10, verticalalignment='top')
    ax.legend()
    plt.suptitle(brand)
    brand = brand.replace("/","")
    #plt.figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    size = plt.gcf()
    size.set_size_inches(18.5, 10.5)
    #plt.show()
    plt.savefig(f"/tmp/{brand}.png", dpi=100)
    plt.close('all')

'''fetching list of sales for the last year'''
def fetch_sales(shop, date_begin, date_end):
    '''function to get sales given shop id and dates; returns x as company name and y as company id in a list of lists'''
    cmd = get_comp_names.format(shop, shop, date_begin, date_end)
    cur.execute(cmd)
    sales = cur.fetchall()
    return(sales)

saks_sales = fetch_sales(6, period_start, period_end)
'''function to fetch sales by brand by period'''
def sales_sum(shop, date_s1, date_s2, brand_id):
    cmd = get_sales.format(brand_id, date_s1, date_s2)
    cur.execute(cmd)
    company_sales = cur.fetchall()
    return(company_sales)
    
'''main loop that goes through brandlist and then iterates each brand over 12 months'''
for b, i in saks_sales:
    result = []
    for x,y in zip(previous_months, current_months):
        #print(datetime.strftime(datetime(*x, 1,), '%Y/%m/%d'), datetime.strftime(datetime(*y, 1,), '%Y/%m/%d'))
        #print(sales_sum(6, datetime.strftime(datetime(*x, 1,), '%Y/%m/%d'), datetime.strftime(datetime(*y, 1,), '%Y/%m/%d'), i))
        result.append(sales_sum(6, datetime.strftime(datetime(*x, 1,), '%Y/%m/%d'), datetime.strftime(datetime(*y, 1,), '%Y/%m/%d'), i))
    print(result)
    print(b)
    print(previous_months)
    plot(previous_months, result, b)

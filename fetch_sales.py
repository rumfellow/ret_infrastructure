#!/usr/bin/python3
import fdb
from datetime import datetime
import pprint
#nw = datetime.now()
#x = str(nw.year) + "," + " " + str(nw.month)+ "," + " " + str(nw.day)+ "," + " " + "0"+ "," + " " + "0"
yarval = 2
saks = 6
odessa = 3
con = fdb.connect(dsn='vps:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='kb8X3a1G', charset ='WIN1251')
cur = con.cursor()
date1 = datetime(2017 , 12 , 27)
date2 = datetime(2017 , 12 , 27)
pp = pprint.PrettyPrinter(indent=0, compact=4)
print("report for", datetime.now())
default = "select sw.group_name, tn.kod, tn.name, tn.cena_r from TOVAR_MOVE tm, vnakl vn,\
 TOVAR_NAME tn, print_view_sklad('0','{}') sw WHERE tm.tovar_id = tn.num AND tm.doc_id = vn.num \
 AND sw.num = tn.tip AND tm.doc_type_id = 1 AND tm.from_sklad_id = '{}' AND tm.mdate >= '{}' AND tm.mdate <= '{}'"
cmd = default.format(yarval, yarval, date1, date2)
print('Kiev')
cur.execute(cmd)
pp.pprint(cur.fetchall())
print('Odessa')
cmd = default.format(odessa, odessa, date1, date2)
cur.execute(cmd)
pp.pprint(cur.fetchall())
print('Saksaganskogo')
cmd = default.format(saks, saks, date1, date2)
cur.execute(cmd)
pp.pprint(cur.fetchall())

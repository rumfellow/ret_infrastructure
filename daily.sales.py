#!/usr/bin/python3
import fdb
from datetime import datetime
nw = datetime.now()
date1 = str(nw.year) + "," + " " + str(nw.month)+ "," + " " + str(nw.day)+ "," + " " + "0"+ "," + " " + "0"
con = fdb.connect(dsn='localhost:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='kb8X3a1G', charset ='WIN1251')
cur = con.cursor()
#pp = pprint.PrettyPrinter(indent=0, compact=4)
print('Saksaganskogo', str(nw.day) + "/" + str(nw.month) + "/" + str(nw.year))
cur.execute("select sw.group_name, tn.kod, tn.name, tn.cena_r from TOVAR_MOVE tm, vnakl vn,\
 TOVAR_NAME tn, print_view_sklad('0','6') sw WHERE tm.tovar_id = tn.num AND tm.doc_id = vn.num \
 AND sw.num = tn.tip AND tm.doc_type_id = 1 AND tm.from_sklad_id = '6' AND tm.mdate = '%s'" % date1)
row = cur.fetchall()
for x in row:
	print(*x)
print("Сума дня: ", sum([x[3] for x in row]))

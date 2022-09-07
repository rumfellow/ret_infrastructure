#!/bin/python3
import fdb
import time
from pandas import read_csv
import io

'''SQL PART'''
today = time.strftime('%Y, %m, %d') + ", 0, 0"
con = fdb.connect(dsn='gate/3053:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='TunaFishIsFree!', charset ='UTF8')
cur = con.cursor()
x = "select gr.group_name, t.kod, t.name, t.cena_r, t.tov_scancode_in, s.z_kolvo, ((s.z_kolvo * t.cena)) from view_sklad_zal_all('%s') s, \
tovar_name t, print_view_sklad_all(1) gr\
 WHERE s.num = t.num AND t.tip = gr.num AND s.z_kolvo > 0 AND s.sklad_id = gr.sklad_id AND s.sklad_id > 0 AND t.visible = 1" %today
cur.execute(x)
stores=cur.fetchall()

'''CSV PART'''
#shopify header length - 47 rows
shopify_header=['Handle','Title','Body (HTML)','Vendor','Type','Tags','Published',\
                'Option1 Name','Option1 Value','Option2 Name','Option2 Value',\
                'Option3 Name','Option3 Value','Variant SKU','Variant Grams',\
                'Variant Inventory Tracker','Variant Inventory Qty',\
                'Variant Inventory Policy','Variant Fulfillment Service',\
                'Variant Price','Variant Compare At Price',\
                'Variant Requires Shipping','Variant Taxable','Variant Barcode',\
                'Image Src','Image Position','Image Alt Text','Collection','Gift Card','SEO Title',\
                'SEO Description','Google Shopping / Google Product Category',\
                'Google Shopping / Gender','Google Shopping / Age Group',\
                'Google Shopping / MPN','Google Shopping / AdWords Grouping',\
                'Google Shopping / AdWords Labels','Google Shopping / Condition',\
                'Google Shopping / Custom Product','Google Shopping / Custom Label 0',\
                'Google Shopping / Custom Label 1','Google Shopping / Custom Label 2',\
                'Google Shopping / Custom Label 3','Google Shopping / Custom Label 4',\
                'Variant Image','Variant Weight Unit','Variant Tax Code','Cost per item',\
                'Status']

#ukrsklad supplied fields - usklad_sku, usklad_title, usklad_qty, usklad_price,
#usklad_barcode, 

table = ['{usklad_sku},{usklad_title},,{vendor},,,True,Title,Default Title,,,,,{usklad_sku},,shopify,{usklad_qty},\
deny,manual,{usklad_price},,true,false,{usklad_barcode},,,,{collection},false,,,,,,,,,,,,,,,,,kg,,,active'\
.format(usklad_sku=x[1], usklad_title=x[2].replace(',',''), vendor=x[0], usklad_qty=x[5], usklad_price=x[3], usklad_barcode=x[4], collection='Women') for x in stores]

read_csv(io.StringIO('\n'.join(table))).to_csv('/tmp/shopify_product_import.csv', header=shopify_header, index=False)

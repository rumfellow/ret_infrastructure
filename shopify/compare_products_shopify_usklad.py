import requests
from pandas import DataFrame as df
import fdb
import time
import csv

'''FIRST PART === GRABBING SKUS FROM SHOPIFY'''

url='api_key:pass@site.myshopify.com/admin/api/2021-07/'

r={'products':[]}
#number of iterations for get_products function
x=[1,2,3]
fields='&fields=id,products,variants'
#fields=''
def get_products(dic, lastid): 
    """Recursively iterate over X to get 250 unit chunks of all products"""
    while len(x) > 0:
        f = requests.get(url+'products.json?limit=250'+fields+'&since_id='+str(lastid)).json()
        print(r)
        [r['products'].append(x) for x in f['products']]
        x.pop()
        get_products(r, str(r['products'][-1]['id']))
    return(r)


def check_list_validity():
    count = requests.get(url+'products/count.json').json()
    status = 0 if len(allprod['products']) == count['count'] else 1
    return status

allprod=get_products(r,0)
allprod_df=df(allprod['products'])
variants = [x for x in allprod_df['variants']]
shopify_skus=[]
for x in variants:
    for m in x:
        shopify_skus.append(int(m['sku']))


if check_list_validity() == 1:
    raise ValueError('Quantity of items in allprod array different from count.json')
else:
    pass

'''SECOND PART === GRABBING PRODUCT IDS FROM UKRSKLAD'''

today = time.strftime('%Y, %m, %d') + ", 0, 0"
con = fdb.connect(dsn='gate/3053:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='DBPASS', charset ='UTF8')
cur = con.cursor()
x = "select gr.group_name, t.kod, t.name, t.cena_r, t.tov_scancode_in, s.z_kolvo, ((s.z_kolvo * t.cena)) from view_sklad_zal_all('%s') s, \
tovar_name t, print_view_sklad_all(1) gr\
 WHERE s.num = t.num AND t.tip = gr.num AND s.z_kolvo > 0 AND s.sklad_id = gr.sklad_id AND s.sklad_id > 0 AND t.visible = 1" %today
cur.execute(x)
stores=cur.fetchall()
ukrsklad_skus=[int(x[1]) for x in stores]


'''THIRD PART === COMPARING AND RETURNING DIFF IN CSV'''
allrecords="select gr.group_name, t.kod, t.name, t.cena_r, t.tov_scancode_in, s.z_kolvo, ((s.z_kolvo * t.cena)) from view_sklad_zal_all('%s') s, \
tovar_name t, print_view_sklad_all(1) gr\
 WHERE s.num = t.num AND t.tip = gr.num AND s.sklad_id = gr.sklad_id AND s.sklad_id > 0 AND t.visible = 1" %today
cur.execute(allrecords)
allrecords=cur.fetchall()

ukrsklad_skus = frozenset(ukrsklad_skus)
shopify_skus = frozenset(shopify_skus)
not_on_site= ukrsklad_skus - shopify_skus
not_in_ukrsklad = shopify_skus - ukrsklad_skus

reference_dict = {x[1]:x[0]+" - "+x[2] for x in allrecords}
not_on_site_list = list(zip(not_on_site, [reference_dict[str(x)] for x in not_on_site]))
not_on_sklad_list = list(zip(not_in_ukrsklad, [reference_dict[str(x)] for x in not_in_ukrsklad]))

not_on_site_list = sorted(not_on_site_list, key=lambda x: x[1])
not_on_sklad_list = sorted(not_on_sklad_list, key=lambda x: x[1])

with open('/tmp/site_sklad_discrepancies.csv', 'w') as csv_file:  
    writer = csv.writer(csv_file)
    writer.writerow([" ","Позиции в наличии на сайте, но не в Укрскладе"])
    writer.writerow(["Код","Товар"])
    for key, value in not_on_sklad_list:
        writer.writerow([key, value])
    writer.writerow([" ","Позиции в наличии в Укрскладе, но не на сайте"])
    writer.writerow(["Код","Товар"])
    for key, value in not_on_site_list:
        writer.writerow([key, value])


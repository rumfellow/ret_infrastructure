import requests
from pandas import DataFrame as df
import fdb
import time
import csv

'''FIRST PART === GRABBING VARIANTS FROM SHOPIFY'''

url='https://api_key:pass@site.myshopify.com/admin/api/2021-07/'
r={'products':[]}
def get_products(dic, lastid, chunks=[3,2,1], fields='&fields=id,products,variants', ): 
    """Recursively iterate over X to get 250 unit chunks of all products"""
    while len(chunks) > 0:
        f = requests.get(url+'products.json?limit=250'+fields+'&since_id='+str(lastid)).json()
        print("Receiving 250 unit chunk #",chunks[-1],"from Shopify")
        [r['products'].append(x) for x in f['products']]
        chunks.pop()
        get_products(r, str(r['products'][-1]['id']))
    return(r)

allprod=get_products(r,0)
allprod_df=df(allprod['products'])

print("Flattenning variants list")
variants = [x for x in allprod_df['variants']]
variants = df(variants)
flat_variants=df(filter(None,variants.values.reshape(-1)))
sku_inventory_id_dict = {x['sku']:x['inventory_item_id'] for x in flat_variants.iloc}

'''SECOND PART === GETTING DAILY EXPENDITURE'''

print('Receiving list of goods that left warehouse')
testday = '2021, 08, 28, 0, 0'

#today = time.strftime('%Y, %m, %d') + ", 0, 0"

con = fdb.connect(dsn='gate/3053:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='DBPASS', charset ='UTF8')
cur = con.cursor()
outgoing="select s.from_kolvo, t.name, t.kod from sklad_view_1(6,'2021, 08, 31, 0, 0', '2021, 08, 31, 0, 0') s, tovar_name t \
WHERE s.from_kolvo > 0 AND s.num = t.num"
cur.execute(outgoing)
outgoing=cur.fetchall()

incoming="select s.to_kolvo, t.name, t.kod from sklad_view_1(6,'2021, 08, 31, 0, 0', '2021, 08, 31, 0, 0') s, tovar_name t \
WHERE s.to_kolvo > 0 AND s.num = t.num"
cur.execute(incoming)
incoming=cur.fetchall()

outgoing_to_push = list(set(outgoing)-set(incoming))
print(len(outgoing),'items are expended')
outgoing_sku_quantity_dict = {x[2]:x[0] for x in outgoing_to_push}

ultimate_list=[[outgoing_sku_quantity_dict[x], sku_inventory_id_dict[x]] for x in outgoing_sku_quantity_dict.keys() & sku_inventory_id_dict.keys()]
    

'''FUNCTION + JSON PAYLOAD + PUSHING UPDATED PRICES VIA REST'''

def quantity_update(item_id, quantity,location=61354115234):
    payload = {'location_id': location, 'inventory_item_id': int(item_id), 'available_adjustment': -int(quantity)}
    endpoint = 'inventory_levels/adjust.json'
    response = requests.post(url+endpoint,json=payload)
    time.sleep(3)
    print(response)


print('Checking items to update & pushing prices via REST API if needed')    
if len(ultimate_list) > 0:
    print('Number of discrepant quantity of inventory:',len(ultimate_list))
    for x in ultimate_list:
        print('Adjusting quantity of', x[1], 'by', -x[0])
        quantity_update(x[1],x[0])
        time.sleep(3)
else:
    print('Nope, all in  sync')

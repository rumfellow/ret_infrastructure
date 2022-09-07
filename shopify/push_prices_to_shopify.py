import requests
from pandas import DataFrame as df
import fdb
import time
import csv

'''FIRST PART === GRABBING SKUS FROM SHOPIFY'''

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

'''SECOND PART === CREATING REFERENCE DICTIONARY FROM UKRSKLAD'''
print('Receiving full 20k products list from UkrSklad')
today = time.strftime('%Y, %m, %d') + ", 0, 0"
con = fdb.connect(dsn='gate/3053:/var/lib/firebird/data/Sklad.tcb', user='sysdba', password='DBPASS', charset ='UTF8')
cur = con.cursor()
allrecords="select gr.group_name, t.kod, t.name, t.cena_r, t.tov_scancode_in, s.z_kolvo, ((s.z_kolvo * t.cena)) from view_sklad_zal_all('%s') s, \
tovar_name t, print_view_sklad_all(1) gr\
 WHERE s.num = t.num AND t.tip = gr.num AND s.sklad_id = gr.sklad_id AND s.sklad_id > 0 AND t.visible = 1" %today
cur.execute(allrecords)
allrecords=cur.fetchall()

'''CROSS-REFERENCING PRICES, CREATING LIST OF PRODUCT IDS AND PRICES TO CORRECT'''

reference_dict = {x[1]:x[3] for x in allrecords}
wrongs=[]
for x in flat_variants.iloc:
    if reference_dict[x['sku']] != float(x['price']):
        wrongs.append([x['id'], reference_dict[x['sku']]])

    else:
        pass
	

'''FUNCTION + JSON PAYLOAD + PUSHING UPDATED PRICES VIA REST'''

def price_update(x,y):
    payload = {'variant': {'id': x, 'price': y}}
    endpoint = 'variants/'+str(x)+'.json'
    response = requests.put(url+endpoint,json=payload)
    print(response)

print('Checking items to update & pushing prices via REST API if needed')    
if len(wrongs) > 0:
    print('Number of discrepant prices:',len(wrongs))
    for x,y in wrongs:
        print('Changing the price of ', x, ' to ', y)
        price_update(int(x),int(y))
        time.sleep(3)
else:
    print('Nope, all in sync')


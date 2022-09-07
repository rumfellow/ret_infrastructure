import requests

url='https://api_key:pass@site.myshopify.com/admin/api/2021-07/'

r={'products':[]}
#x=[*range(1,8)]
x=[1]
fields='&fields=id,title,vendor,handle,status,price,barcode,inventory_quantity,options'
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

if check_list_validity() == 1:
    raise ValueError('Quantity of items in allprod array different from count.json')
else:
    pass

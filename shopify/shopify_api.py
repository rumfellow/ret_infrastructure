import shopify
import binascii
import os
import requests
shopify.Session.setup(api_key='key', secret='secret')

shop_url = "site.myshopify.com"
api_version = '2020-10'
state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
redirect_uri = "482ua.myshopify.com/admin/api/2021-07/"
scopes = ['read_products', 'read_orders']

newSession = shopify.Session(shop_url, api_version)
auth_url = newSession.create_permission_url(scopes, redirect_uri, state)
# redirect to auth_url
session = shopify.Session(shop_url, api_version)
access_token = session.request_token('request_params')

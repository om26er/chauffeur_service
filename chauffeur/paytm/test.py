#!/usr/bin/python3

from chauffeur.paytm.checksum import generate_checksum

MERCHANT_KEY = 'kbzk1DSbJiV_O3p5'
TRANSACTION_URL = 'https://pguat.paytm.com/oltp-web/processTransaction'
data_dict = {
    'REQUEST_TYPE': 'DEFAULT',
    'MID': 'WorldP64425807474247',
    'ORDER_ID': '@@@!!!!___',
    'TXN_AMOUNT': '1',
    'CUST_ID': 'acfff@paytm.com',
    'INDUSTRY_TYPE_ID': 'Retail',
    'WEBSITE': 'worldpressplg',
    'CHANNEL_ID': 'WEB',
}

param_dict = data_dict.copy()
param_dict['CHECKSUMHASH'] = generate_checksum(data_dict,MERCHANT_KEY)


def assemble_html():
    html = str()
    html += '<h1>Merchant Check Out Page</h1></br>'
    html += '<form method="post" action="{}" name="f1">'.format(
                TRANSACTION_URL)
    html += '<table border="1">'
    html += '<tbody>'
    for key in param_dict:
        html += '<input type="hidden" name="{}" value="{}">'.format(
                    key.strip(), param_dict[key].strip())
    html += '</tbody>'
    html += '</table>'
    html += '<script type="text/javascript">'
    html += 'document.f1.submit();'
    html += '</script>'
    html += '</form>'
    return html

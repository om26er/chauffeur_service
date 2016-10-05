#!/usr/bin/python3

from chauffeur.paytm.checksum import verify_checksum

MERCHANT_KEY = 'kbzk1DSbJiV_O3p5'

response_dict = {}


def read_response_and_show_result(params):
    checksum = None
    for i in params.keys():
        response_dict[i] = params[i].value
        if i == 'CHECKSUMHASH':
            checksum = params[i].value

    if 'GATEWAYNAME' in response_dict:
        if response_dict['GATEWAYNAME'] == 'WALLET':
            response_dict['BANKNAME'] = 'null'

    verify = verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify and response_dict['RESPCODE'] == '01':
        return '<h1>Order Successful</h1>'
    else:
        return '<h1>Order Unsuccessful because {}</h1>'.format(
            response_dict['RESPMSG'])

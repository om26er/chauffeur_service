import json

from chauffeur.paytm import checksum

MERCHANT_KEY = 'CqSZYfZbmEJONJtf'


def generate(params):
    params.update(
        {'CHECKSUMHASH': checksum.generate_checksum(params, MERCHANT_KEY)}
    )
    params.update({'payt_STATUS': '1'})
    return json.dumps(params, separators=(',', ':'))


def verify(params):
    if 'GATEWAYNAME' in params and params['GATEWAYNAME'] == 'WALLET':
            params['BANKNAME'] = 'null'

    verified = checksum.verify_checksum(
        params,
        MERCHANT_KEY,
        params['CHECKSUMHASH']
    )
    if verified:
        params['IS_CHECKSUM_VALID'] = 'Y'
    else:
        params['IS_CHECKSUM_VALID'] = 'N'
    param_dict = json.dumps(params, separators=(',', ':'))

    result = str()
    result += '<head>'
    result += '<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-I">'
    result += '<title>Paytm</title>'
    result += '<script type="text/javascript">'
    result += 'function response(){'
    result += 'return document.getElementById("response").value;'
    result += '}'
    result += '</script>'
    result += '</head>'
    result += 'Redirect back to the app<br>'
    result += '<form name="frm" method="post">'
    result += '<input type="hidden" id="response" name="responseField" value=\'' + param_dict + '\'>'
    result += '</form>'
    return result

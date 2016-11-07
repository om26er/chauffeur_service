import json
import os
import requests

from chauffeur_service.helpers import ConfigHelpers


OTP_GENERATION_URL = 'https://sendotp.msg91.com/api/generateOTP'
CONFIG_FILE = os.path.expanduser('~/chauffeur_config.ini')
config_helpers = ConfigHelpers(CONFIG_FILE)


def request_sms_otp(country_code, mobile_number):
    data = {
        'countryCode': country_code,
        'mobileNumber': mobile_number,
        'getGeneratedOTP': 'true'
    }
    headers = {'application-Key': config_helpers.get_msg91_api_key()}
    request = requests.post(
        OTP_GENERATION_URL,
        data=json.dumps(data),
        headers=headers
    )
    out = json.loads(request.text)
    if out.get('status') == 'success':
        return out.get('response').get('oneTimePassword')
    else:
        return -1

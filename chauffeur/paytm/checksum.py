import base64
import string
import random
import hashlib

from Crypto.Cipher import AES

IV = '@@@@&&&&####$$$$'
BLOCK_SIZE = 16


def _generate_checksum(param_dict_or_string, merchant_key, salt=None):
    if isinstance(param_dict_or_string, dict):
        params_string = _get_param_string(param_dict_or_string)
    elif isinstance(param_dict_or_string, str):
        params_string = param_dict_or_string
    else:
        raise ValueError('param_dict_or_string must be a dict or string.')
    salt = salt if salt else _generate_id(4)
    final_string = '{}|{}'.format(params_string, salt)
    hasher = hashlib.sha256(final_string.encode())
    hash_string = hasher.hexdigest()
    hash_string += salt
    return _encode(hash_string, IV, merchant_key)


def generate_checksum(param_dict, merchant_key, salt=None):
    return _generate_checksum(param_dict, merchant_key, salt=salt)


def generate_checksum_by_str(param_str, merchant_key, salt=None):
    return _generate_checksum(param_str, merchant_key, salt=salt)


def _verify_checksum(param_dict_or_string, merchant_key, checksum):
    if isinstance(param_dict_or_string, dict):
        if 'CHECKSUMHASH' in param_dict_or_string:
            param_dict_or_string.pop('CHECKSUMHASH')

    calculated_checksum = _generate_checksum(
        param_dict_or_string,
        merchant_key,
        salt=_decode(checksum, IV, merchant_key)[-4:]
    )
    return calculated_checksum == checksum


def verify_checksum(param_dict, merchant_key, checksum):
    return _verify_checksum(param_dict, merchant_key, checksum)


def verify_checksum_by_str(param_str, merchant_key, checksum):
    return _verify_checksum(param_str, merchant_key, checksum)


def _generate_id(
        size=6,
        chars=string.ascii_uppercase + string.digits + string.ascii_lowercase
):
    return ''.join(random.choice(chars) for _ in range(size))


def _get_param_string(params):
    params_string = []
    for key in sorted(params.keys()):
        value = params[key]
        params_string.append('' if value == 'null' else str(value))
    return '|'.join(params_string)


def _add_pad(encodable):
    data_length = len(encodable)
    return encodable + (BLOCK_SIZE - data_length % BLOCK_SIZE) * \
        chr(BLOCK_SIZE - data_length % BLOCK_SIZE)


def _remove_pad(decodable):
    return decodable[0:-ord(decodable[-1])]


def _encode(to_encode, iv, key):
    # Pad
    to_encode = _add_pad(to_encode)
    # Encrypt
    c = AES.new(key, AES.MODE_CBC, iv)
    to_encode = c.encrypt(to_encode)
    # Encode
    to_encode = base64.b64encode(to_encode)
    return to_encode


def _decode(to_decode, iv, key):
    # Decode
    to_decode = base64.b64decode(to_decode)
    # Decrypt
    c = AES.new(key, AES.MODE_CBC, iv)
    to_decode = c.decrypt(to_decode)
    if type(to_decode) == bytes:
        # convert bytes array to str.
        to_decode = to_decode.decode()
    # remove pad
    return _remove_pad(to_decode)

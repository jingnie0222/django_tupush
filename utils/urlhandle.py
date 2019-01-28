def urlencode(_target, _encoding, _errors):
    if isinstance(_target, dict):
        _result = ''
        if _encoding:
            for _key, _value in _target.items():
                _result = _result + "&" + _key + '=' + hex2url(_value.encode(encoding=_encoding, errors=_errors))
        else:
            for _key, _value in _target.items():
                _result = _result + "&" + _key + '=' + _value
        _result = _result.replace("&", "", 1)
    elif isinstance(_target, str):
        if _encoding:
            _result = hex2url(_target.encode(encoding=_encoding, errors=_errors))
        else:
            _result = _target
    else:
        _result = ''
    return _result


def hex2url(_byte):
    _result = ''
    for _num in _byte:
        _result += '%{:0>2x}'.format(_num).upper()
    return _result


def urldecode(_str, _encoding, _errors):
    _str2list = _str.split("&")
    _dict = {}
    for _item in _str2list:
        _item2list = _item.split("=", 1)
        if len(_item2list) == 2:
            _key = _item2list[0]
            _value_temp = _item2list[1]
            _value_temp = _value_temp.replace("+", urlencode(" ", _encoding, "ignore"))
            _value_temp_list = _value_temp.split('%')
            _value_adjust = ''
            for i in range(0,len(_value_temp_list)):
                if i == 0:
                    if _value_temp_list[i]:
                        for j in _value_temp_list[i]:
                            _value_adjust += '{:0>2x}'.format(ord(j)).upper()
                    else:
                        for _item in _value_temp_list[i]:
                            _value_adjust += _item[:2]
                            for j in _item[2:]:
                                _value_adjust += '{:0>2x}'.format(ord(j)).upper()
                else:
                    _value_adjust += _value_temp_list[i][:2]
                    for j in _value_temp_list[i][2:]:
                        _value_adjust += '{:0>2x}'.format(ord(j)).upper()
            
            try:
                if _encoding:
                    _value = bytes.fromhex(_value_adjust).decode(_encoding, errors=_errors)
                else:
                    _value = _item2list[1]
                _dict[_key] = _value

            except Exception as e:
                print("ERROR", e, _item)
                return {}
        else:
            print("ERROR", _item)
            return {}
    return _dict


def value_decode(_str, _encoding, _errors):
    if not isinstance(_str, str):
        return ''
    try:
        _value_temp = _str.replace("+", urlencode(" ", _encoding, "ignore"))
        _value_temp_list = _value_temp.split('%')
        _value_adjust = ''
        for i in range(0,len(_value_temp_list)):
            if i == 0:
                if _value_temp_list[i]:
                    for j in _value_temp_list[i]:
                        _value_adjust += '{:0>2x}'.format(ord(j)).upper()
                else:
                    for _item in _value_temp_list[i]:
                        _value_adjust += _item[:2]
                        for j in _item[2:]:
                            _value_adjust += '{:0>2x}'.format(ord(j)).upper()
            else:
                _value_adjust += _value_temp_list[i][:2]
                for j in _value_temp_list[i][2:]:
                    _value_adjust += '{:0>2x}'.format(ord(j)).upper()

        if _encoding:
            _value = bytes.fromhex(_value_adjust).decode(_encoding, errors=_errors)
        else:
            _value = __str
        return _value
    except Exception as e:
        print("ERROR", e, _str)
        return ''


def value_encode(_str, _encoding, _errors):
    if not isinstance(_str, str):
        return ''
    try:
        if _encoding:
            _return_str = hex2url(_str.encode(encoding=_encoding, errors=_errors))
        else:
            _return_str = _str
        return _return_str
    except Exception as e:
        print("ERROR", e, _str)
        return ''


if __name__ == '__main__':
    print(urlencode({'a': '北京', 'b':'web', 'c':'0'}, 'utf_16_le', 'ignore'))
    print(urldecode('a=%53%5F+&b=%64%00', 'utf_16_le', 'ignore'))
    print(value_decode("%53%5F+%64%00", 'utf_16_le', 'ignore'))
    print(value_encode("当", 'utf_16_le', 'ignore'))
    print(value_encode("当", 'gbk', 'ignore'))

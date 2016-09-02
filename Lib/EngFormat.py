__author__ = 'HS'

class Format():


    def FloatToString(self,value,d):
        #format double to string with cutting 0s and adding Unit
        if value >= 1e9:
            k = value/1e9
            sf = "%." + str(d) + "fG"
            s = sf % k
        elif value >= 1e6:
            k = value/1e6
            sf = "%." + str(d) + "fM"
            s = sf % k
        elif value >= 1e3:
            k = value/1e3
            sf = "%." + str(d) + "fk"
            s = sf % k
        else:
            k = value
            sf = "%." + str(d) + "f"
            s = sf % k

        return s

    def StringToFloat(self,s):
        #format double to string
        _f = 1
        _p = s.find('K')
        if _p >= 0: _f = 1e3
        _p = s.find('M')
        if _p >= 0: _f = 1e6
        _p = s.find('G')
        if _p >= 0: _f = 1e9
        _p = s.find('k')
        if _p >= 0: _f = 1e3
        _p = s.find('m')
        if _p >= 0: _f = 1e6
        _p = s.find('g')
        if _p >= 0: _f = 1e9
        _ds = ""
        for x in s:
            if x >= '0' and x <= '9' or x == '.':
                _ds += x
        try:
            _df = float(_ds)
            _df *= _f
        except Exception:
            _df = 0
        return _df
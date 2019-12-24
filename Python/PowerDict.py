

class PowerDict(dict):
    def __init__(self, *keywords, **arguments):
        super().__init__(*keywords, **arguments)
        self._updated = False

    def set(self, *keywords, value):
        if isinstance(value, (str, int))
            if self.get(*keywords) == value:
                return self

        self._updated = True
        if len(keywords) == 1:
            super().__setitem__(keywords[0], value)
        else:
            self[keywords[0]] = self.get(keywords[0], default=PowerDict({})).set(*keywords[1:], value=value)
        return self

    def isUpdated(self):
        return self._updated

    def get(self, *keywords, default=None):
        if len(keywords) == 1:
            val = super().get(keywords[0], default)
            return PowerDict(val) if isinstance(val, dict) else val
        try:
            return self.get(keywords[0], default=default).get(*keywords[1:], default=default)
        except Exception as e:
            return default


if __name__ == '__main__':
    originData = {
        'first': {
            'second': {
                'third': 'deepData'
            }
        }
    }
    print( "Normal get originData['first']['second']['third']: ", originData['first']['second']['third'] )
    newData = PowerDict(originData)
    print( "Origin method newData['first']['second']['third']: ", newData['first']['second']['third'] )
    print( "New method newData.get('first', 'second', 'third'): ", newData.get('first', 'second', 'third') )

    print( "Will follow data updated", newData.isUpdated() )
    newData.set('first', 'second', 'third', value='deepData')
    print( "Duplicate value write: ", newData.isUpdated() )
    newData.set('first', 'second', 'third', value='newDeepData')
    print( "different value write", newData.isUpdated() )
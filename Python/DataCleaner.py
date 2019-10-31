import pandas as pd
import re
import math

class DataCleaner():
    rule = ''
    def __init__(self, originData):
        self.originData = originData
    
    def getFullRegexRule(self, reverse: bool=False):
        return r'[^{}]'.format(self.rule) if reverse else r'[{}]'.format(self.rule)
    
    def reserved(self):
        return self.subString(self.originData, self.getFullRegexRule(True))
    
    def exclude(self):
        return self.subString(self.originData, self.getFullRegexRule())
    
    def subString(self, inputData, regRule):
        if isinstance(inputData, pd.Index):
            inputData = inputData.to_series()

        if isinstance(inputData, pd.Series):
            inputData = inputData.apply(lambda x: self.subString(x, regRule))
        elif isinstance(inputData, pd.DataFrame):
            inputData.columns = self.subString(list(inputData.columns), regRule)
            inputData.index = self.subString( inputData.index, regRule )
            for column in inputData:
                if isinstance(column, float) and math.isnan(column):
                    continue
                inputData[column] = self.subString(inputData[column], regRule)
        elif isinstance(inputData, list):
            inputData = [ self.subString(x, regRule) for x in inputData]
        elif isinstance(inputData, str):
            inputData = re.sub(regRule, '', inputData)

        return inputData
    
    def number(self, width=None):
        self.rule += '\d'
        return self
    
    def space(self):
        self.rule += '\s'
        return self
    
    def english(self, case=None):
        if case == 'uppercase' or case is None:
            self.rule += 'A-Z'
        if case == 'lowercase' or case is None:
            self.rule += 'a-z'
        return self
    
    def chinese(self):
        self.rule += '\u4e00-\u9fa5'
        return self
    
    def word(self):
        self.rule += '\w'
        return self


if __name__ == '__main__':
    origin = '1A 2B ab：中　文cd，efg 3C 4D'
    print( 'reserved number&space:', DataCleaner(origin).number().space().reserved() )
    print( 'reserved english(lowercase):', DataCleaner(origin).english(case='lowercase').reserved() )
    print( 'reserved chinese:', DataCleaner(origin).chinese().reserved() )
    print( '--------' )
    print( 'exclude number&space:', DataCleaner(origin).number().space().exclude() )
    print( 'exclude english(lowercase):', DataCleaner(origin).english(case='lowercase').exclude() )
    print( 'exclude chinese:', DataCleaner(origin).chinese().exclude() )
    print( '--------' )
    print( 'suport multiple data type' )
    origin = [ '1A 2B ab：中', '　文cd，efg 3C 4D']
    print( 'list reserved number:', DataCleaner(origin).number().reserved() )
    print( 'Series reserved number:' )
    print( DataCleaner( pd.Series(origin) ).number().reserved() )
    print( 'DataFrame reserved number:' )
    print( DataCleaner( pd.DataFrame(origin) ).number().reserved() )


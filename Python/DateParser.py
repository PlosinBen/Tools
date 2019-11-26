#!/usr/bin/python3
import sys
import importlib
import inspect
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Date():
    closureFormat = '%Y-%m-%d'
    def __init__(self,
            inputFormat='%Y-%m-%d',
            input = None,
            outputFormat='%Y-%m-%d',
            output = None,

            frequency='d', 

            replace:dict = {'q1':'01', 'q2':'04', 'q3':'07', 'q4':'10'},
            month = None,

            span: int = 0,
            minguo: bool = False,
            response = 'str',
            
            delta:dict = None
        ):

        self.originParseConfig = {
            'inputFormat': inputFormat if input is None else input,
            'outputFormat': outputFormat if output is None else output,
            'span': span,
            'frequency': frequency,
            'minguo': minguo,
            'response': response,
            'replace': replace if month is None else month,
            'delta': delta
        }

    def _loadPackages(self):
        self.packages = []
        packages = ['pandas']
        for packageName in packages:
            if importlib.util.find_spec(packageName) is not None:
                setattr(sys.modules[__name__], packageName,  importlib.import_module(packageName))
                self.packages.append(packageName)

    def parse(self, inputData, **argument):
        self._loadPackages()

        if 'pandas' in self.packages:

            if isinstance(inputData, pandas.DatetimeIndex):
                inputData = inputData.strftime(self.inputFormat).to_series()
            elif isinstance(inputData, pandas.Index):
                inputData = inputData.to_series()

            if isinstance(inputData, pandas.Series):
                return inputData.apply( lambda x: self.parse(x, **argument) )

        if isinstance(inputData, list):
            return [ self.parse(inputString, **argument) for inputString in inputData ]
        elif isinstance(inputData, datetime):
            argument['inputFormat'] = self.closureFormat
            return self.parse(inputData.strftime(argument['inputFormat']), **argument)
        elif isinstance(inputData, str):
            return self._parse(inputData, **argument)

        return inputData

    def _parse(self, inputString, **argument):
        if 'input' in argument:
            argument['inputFormat'] = argument['input']
        if 'output' in argument:
            argument['outputFormat'] = argument['output']
        if 'month' in argument:
            argument['replace'] = argument['month']

        self.inputString = inputString
        self.dt = None

        pipeProcess = [
            self._initInputString,
            self._replaceInputDate,
            self._readInputDate,
            self._formatFrequencyAndSpan,
            self._formatResponse,
        ]

        for process in pipeProcess:
            methodSignature = inspect.signature(process)
            pipeParams = { param.name: argument.get( param.name ) if param.name in argument else self.originParseConfig.get( param.name ) for param in methodSignature.parameters.values() }
            result = process( **pipeParams )
        return result

    def _initInputString(self):
        self.inputString = str(self.inputString).lower()
        return self

    def _replaceInputDate(self, replace:dict):
        for find, replaceTo in replace.items():
            find = find.lower()
            if find in self.inputString:
                self.inputString = self.inputString.replace(find, replaceTo)
                break
        return self

    def _readInputDate(self, inputFormat, minguo:bool):
        if isinstance(inputFormat, list):
            for formatPart in inputFormat:
                try:
                    self._readInputDate(formatPart, minguo)
                    print( self.dt )
                    break
                except Exception as e:
                    continue
            if self.dt is None:
                print('[WARNING] ValueError: {} does not match format {}'.format(self.inputString, str(inputFormat)))
            return self

        if inputFormat == '%s':
            self.dt = datetime.fromtimestamp(int(self.inputString))
            return self

        originString = self.inputString
        if minguo:
            try:
                # year < minguo 100
                minguoFormat = inputFormat.replace('%Y', '%y')
                year = datetime.strptime(originString, minguoFormat).strftime('%y')
            except Exception as e:
                # year > minguo 100
                minguoFormat = inputFormat.replace('%Y', '%j')
                year = datetime.strptime(originString, minguoFormat).strftime('%j')
            originString = originString.replace(year, str( int(year) + 1911 ))

        try:
            self.dt = datetime.strptime(originString, inputFormat)
        except Exception as e:
            print('[WARNING] ValueError: {} does not match format {}'.format(self.inputString, str(inputFormat)))

        return self

    def _formatFrequencyAndSpan(self, frequency:str, span:int, delta:dict):
        dt = self.dt
        span = span
        if frequency == 'y':
            dt = dt.replace(month=1, day=1)
            datetimeDelta = relativedelta(years=span)
        elif frequency == 'm':
            dt = dt.replace(day=1)
            datetimeDelta = relativedelta(months=span)
        elif frequency == 'q':
            dt = dt.replace(month=((dt.month - 1) // 3)*3 + 1, day=1)
            datetimeDelta = relativedelta(months=span*3)
        elif frequency == 'd':
            datetimeDelta = relativedelta(days=span)
        elif frequency == 'w':
            datetimeDelta = relativedelta(months=span*7)
        
        self.dt = dt + datetimeDelta
        if delta is not None:
            #years=0, months=0, days=0, leapdays=0, weeks=0, hours=0, minutes=0, seconds=0, microseconds=0
            self.dt += relativedelta(**delta)

        return self

    def _formatResponse(self, outputFormat:str, response:str):
        return {
            'str': self.dt.strftime( outputFormat ),
            'datetime': self.dt,
            'timestamp': int(time.mktime(self.dt.timetuple()))
        }.get(response)

    def today(self, **argument):
        argument['intpuFormat'] = self.closureFormat
        argument['minguo'] = False
        result = self.parse(datetime.now(), **argument)

        if self.originParseConfig.get('minguo') or argument.get('minguo') == True:
            result = result.replace( str(self.dt.year), str(self.dt.year - 1911))
        return result

def today(**argument):
    return Date().today(**argument)

if __name__ == '__main__':
    originDate = '2018-05-05'

    date = Date('%Y/%m/%d')
    print('2018/05/05 input parse: ', date.parse('2018/05/05') )

    date = Date(output='%d-%m-%Y')
    print(originDate + ' output parse: ', date.parse(originDate) )

    date = Date(frequency='y', span=1)
    print(originDate + ' freq=y span=1: ', date.parse(originDate) )

    date = Date(frequency='y', span=-2)
    print(originDate + ' freq=y span=-2: ', date.parse(originDate) )

    date = Date(frequency='q')
    print(originDate + ' freq=q: ', date.parse(originDate) )

    date = Date(frequency='q', span=3)
    print(originDate + ' freq=q span=3: ', date.parse(originDate) )

    date = Date(frequency='q', span=-2)
    print(originDate + ' freq=q span=-2: ', date.parse(originDate) )

    date = Date('%Y %d %m', frequency='m', span=1, month={
        'Jan.': '03'
        })
    print('2018 5 Jan. freq=m span=1 month={Jan.:03}: ',  date.parse('2018 5 Jan.') )

    date = Date('%Y-%m')
    print('2018-Q3 default quarterly to month: ',  date.parse('2018-Q3') )

    date = Date('%Y%m')
    print('2018Q3 default quarterly to month: ',  date.parse('2018Q3') )

    date = Date(minguo=True)
    print('107-02-01 minguo year nad quarterly: ',  date.parse('107-02-01') )

    date = Date('%Y%m', frequency='q', minguo=True, span=-1)
    print('107Q2 minguo year and freq=q span=-1: ',  date.parse('107Q2') )

    #multi input type
    date = Date(['%Y%m', '%Y %b'])
    print("2018 Jul multi input type ['%Y%m', '%Y %b']: ",  date.parse('2018 Jul') )
    print("201802 multi input type ['%Y%m', '%Y %b']: ",  date.parse('201802') )

    print("201802 same object output last params [span=1]",  date.parse('201802', span=1) )
    print("201802 same object output last params [frequency=y]",  date.parse('201802', frequency='y') )


    print("201802 respnose time object ",  date.parse('201802', response='time') )
    print("201802 respnose datetime object ",  date.parse('201802', response='datetime') )

    print("get today", date.today() )
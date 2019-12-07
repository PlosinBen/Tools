#!/usr/bin/python3
import sys
import importlib
import inspect
import time
import datetime
import warnings

#init packages
_packages = []
for packageName, packageImportPamras in {
            #name, import params
            #like import pandas as pandas
            'pandas': 'pandas',
            #like from dateutil.relativedelta import relativedelta as relativedelta
            'relativedelta': ('dateutil.relativedelta', 'relativedelta')
        }.items():
    packageImportPamras = (packageImportPamras, ) if isinstance(packageImportPamras, str) else packageImportPamras
    if importlib.util.find_spec(packageImportPamras[0]) is not None:
        importModule = importlib.import_module(packageImportPamras[0])

        if len(packageImportPamras) > 1:
            importModule = getattr(importModule, packageImportPamras[1])
        setattr(sys.modules[__name__], packageName, importModule)
        _packages.append(packageName)

class DateTimeDelta():
    def __init__(self, 
            years=0, months=0, 
            #origin datetime.timedelta suport
            days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0
        ):
        self.years = years
        self.months = months
        self.days = days
        self.weeks = weeks

        self.seconds = seconds
        self.microseconds = microseconds
        self.milliseconds = milliseconds
        self.minutes = minutes
        self.hours = hours

    def __radd__(self, dt:datetime):
        dt = self.spanYearsMonths(dt)
        return self.spanTimedelta(dt)

    def __rsub__(self, dt:datetime):
        dt = self.spanYearsMonths(dt, -1)
        return self.spanTimedelta(dt, -1)

    def spanTimedelta(self, dt, operator:int = 1):
        delta = datetime.timedelta(self.days, self.seconds, self.microseconds, self.milliseconds, self.minutes, self.hours, self.weeks)
        if operator == -1:
            return dt - delta
        return dt + delta

    def spanYearsMonths(self, dt, operator:int = 1):
        year = dt.year
        month = dt.month

        month += self.months * operator
        year += self.years * operator
        if month > 12:
            year += month // 12
            month = month % 12

        if month < 1:
            year -= abs(month // 12) + 1
            month = 12 - ( month % 12 )

        return dt.replace(year=year, month=month)

def makeDateTimeDelta(**argument):
    if 'relativedelta' in _packages:
        return relativedelta(**argument)
    else:
        warnings.warn("[Warning]recommended datetime delta use 'dateutil.relativedelta'", DeprecationWarning)
        return DateTimeDelta(**argument)

class Date():
    closureFormat = '%Y-%m-%d'
    def __init__(self,
            inputFormat='%Y-%m-%d',
            outputFormat='%Y-%m-%d',
            frequency='d', 
            replace:dict = {'q1':'01', 'q2':'04', 'q3':'07', 'q4':'10'},
            month = None,
            span: int = 0,
            minguo: bool = False,
            response = 'str',
            delta:dict = None,
            errors:str = 'raise',
            onError = None
        ):

        self.originParseConfig = {
            'inputFormat': inputFormat,
            'outputFormat': outputFormat,
            'span': span,
            'frequency': frequency,
            'minguo': minguo,
            'response': response,
            'replace': replace,
            'delta': delta,
            'errors': errors,
            'onError': onError
        }

    def parse(self, inputData, **argument):
        global _packages
        if 'pandas' in _packages:

            if isinstance(inputData, pandas.DatetimeIndex):
                argument['inputFormat'] = self.closureFormat
                inputData = inputData.strftime(argument['inputFormat']).to_series()
            elif isinstance(inputData, pandas.Index):
                inputData = inputData.to_series()

            if isinstance(inputData, pandas.Series):
                return inputData.apply( lambda x: self.parse(x, **argument) )

        if isinstance(inputData, list):
            return [ self.parse(inputString, **argument) for inputString in inputData ]
        elif isinstance(inputData, datetime.datetime):
            argument['inputFormat'] = self.closureFormat
            return self.parse(inputData.strftime(argument['inputFormat']), **argument)
        elif isinstance(inputData, str):
            return self._parse(inputData, **argument)

        return inputData

    def _parse(self, inputString, **argument):
        self.inputString = inputString
        self.dt = None

        pipeProcess = [
            self._initInputString,
            self._replaceInputDate,
            self._readInputDate,
            self._formatFrequencyAndSpan,
            self._formatResponse,
        ]

        try:
            for process in pipeProcess:
                methodSignature = inspect.signature(process)
                pipeParams = { param.name: argument.get( param.name ) if param.name in argument else self.originParseConfig.get( param.name ) for param in methodSignature.parameters.values() }
                result = process( **pipeParams )
            return result
        except Exception as e:
            errors = argument.get('errors') if 'errors' in argument else self.originParseConfig.get('errors')
            onError = argument.get('onError') if 'onError' in argument else self.originParseConfig.get('onError')
            if errors == 'raise':
                raise ValueError(str(e))
            elif errors == 'coerce':
                return onError

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
                    break
                except Exception as e:
                    continue
            if self.dt is None:
                raise ValueError('{} does not match format {}'.format(self.inputString, str(inputFormat)))
            return self

        if inputFormat == '%s':
            self.dt = datetime.datetime.fromtimestamp(int(self.inputString))
            return self

        originString = self.inputString
        if minguo:
            try:
                # year < minguo 100
                minguoFormat = inputFormat.replace('%Y', '%y')
                year = datetime.datetime.strptime(originString, minguoFormat).strftime('%y')
            except Exception as e:
                # year > minguo 100
                minguoFormat = inputFormat.replace('%Y', '%j')
                year = datetime.datetime.strptime(originString, minguoFormat).strftime('%j')
            originString = originString.replace(year, str( int(year) + 1911 ))

        try:
            self.dt = datetime.datetime.strptime(originString, inputFormat)
        except Exception as e:
            raise ValueError('[{}] cannot strptime to [{}]'.format(self.inputString, str(inputFormat)))

        return self

    def _formatFrequencyAndSpan(self, frequency:str, span:int, delta:dict):
        dt = self.dt
        span = 0 if span is None else span

        if frequency == 'y':
            dt = dt.replace(year=dt.year + span, month=1, day=1)
            datetimeDelta = makeDateTimeDelta(years=span)
        elif frequency == 'm':
            dt = dt.replace(day=1)
            datetimeDelta = makeDateTimeDelta(months=span)
        elif frequency == 'q':
            dt = dt.replace(month=((dt.month - 1) // 3)*3 + 1, day=1)
            datetimeDelta = makeDateTimeDelta(months=span*3)
        elif frequency == 'd':
            datetimeDelta = makeDateTimeDelta(days=span)
        elif frequency == 'w':
            datetimeDelta = makeDateTimeDelta(months=span*7)

        self.dt = dt + datetimeDelta
        if delta is not None:
            #years=0, months=0, days=0, leapdays=0, weeks=0, hours=0, minutes=0, seconds=0, microseconds=0
            self.dt += makeDateTimeDelta(**delta)

        return self

    def _formatResponse(self, outputFormat:str, response:str):
        return {
            'str': self.dt.strftime( outputFormat ),
            'datetime': self.dt,
            'timestamp': int(time.mktime(self.dt.timetuple()))
        }.get(response, self.dt)

    def today(self, **argument):
        minguo = argument.get('minguo', False)
        argument['minguo'] = False

        argument['intpuFormat'] = self.closureFormat
        result = self.parse(datetime.datetime.now(), **argument)

        if self.originParseConfig.get('minguo') or minguo == True:
            result = result.replace( str(self.dt.year), str(self.dt.year - 1911))
        return result

def today(**argument):
    return Date().today(**argument)

if __name__ == '__main__':
    originDate = '2018-05-05'


    date = Date('%Y/%m/%d')
    print('2018/05/05 input parse: ', date.parse('2018/05/05') )

    date = Date(outputFormat='%d-%m-%Y')
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

    date = Date('%Y %d %m', frequency='m', span=1, replace={
        'Jan.': '03'
        })
    print('2018 5 Jan. freq=m span=1 month={Jan.:03}: ',  date.parse('2018 5 Jan.') )

    date = Date('%Y-%m')
    print('2018-Q3 default quarterly to month: ',  date.parse('2018-Q3') )

    date = Date('%Y%m')
    print('2018Q3 default quarterly to month: ',  date.parse('2018Q3') )

    date = Date('%Y-%m-%d', delta={'months':-1, 'days':1})
    print('2018-01-01 delta -1 month & 1 day: ',  date.parse('2018-01-01') )

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

    print("get today", today(minguo=True) )
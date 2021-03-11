import requests
import os
import zipfile
import time
import pandas as pd

class LvrLand():
    domain = "https://plvr.land.moi.gov.tw"
    tempPath = "./file/"
    
    columns = []
    
    def __checkTempPath(self, path:str = ''):
        if not os.path.isdir(path):
            os.makedirs(path)
        
        return self
    
    
    def download(self, year, session):
        url = self.domain + "/DownloadSeason?season={}S{}&type=zip&fileName=lvr_landcsv.zip".format(year, session)

        dirName = "{}/{}-{}/".format(self.tempPath, year, session)
        self.__checkTempPath(dirName)
        
        zipFileName = "{}/original.zip".format(dirName)
        
        if os.path.exists(zipFileName):
            return self
        
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(zipFileName, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):  
                    f.write(chunk)

        with zipfile.ZipFile(zipFileName, 'r') as zip_ref:
            zip_ref.extractall(dirName)
        
        return self
    
    def loadData(self, year, session):
        dirName = "{}/{}-{}/".format(self.tempPath, year, session)
        
        df = pd.read_csv(dirName + "a_lvr_land_a.csv", header=None)
        
        headers = df.iloc[:2].transpose()
        
        columnFilter = [headers[col].isin(self.columns) for col in headers]
        columnFilter = columnFilter[0] | columnFilter[1]
        
        headers = headers[columnFilter]
        
        df = df.filter(items=headers.index)
        
        df.columns = headers[0]
        
        return df.iloc[2:]
    
    def setTempPath(self, path):
        self.tempPath = path
        
        return self
    
    def setColumns(self, *args):
        self.columns = args
        
        return self
    
    def setDataset(self, dataset):
        self.dataset = dataset
        
        return self
    
    def get(self, year, session):
        data = self.download(year, session) \
            .loadData(year, session)
    
        print(data)

if __name__ == '__main__':
    LvrLand().setTempPath('./files').setColumns('土地區段位置建物區段門牌', 'transaction year month and day').setDataset('build').get(109, 4)

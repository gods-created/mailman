from pandas import read_csv, read_excel

from os.path import basename, exists
from typing import List, Any

class ReadTableService:
    def __init__(
        self,
        path_to_file: str
    ):
        self._path_to_file = path_to_file 

    def _read_csv(self, path_to_file: str) -> List[List[Any]]:
        df = read_csv(path_to_file)
        if df.empty:
            raise ValueError('Uploaded CSV file is empty')
        
        return df.iloc[:].values.tolist()

    def _read_excel(self, path_to_file: str) -> List[List[Any]]:
        df = read_excel(path_to_file)
        if df.empty:
            raise ValueError('Uploaded EXCEL file is empty')
        
        return df.iloc[:].values.tolist()

    def __call__(self) -> List[List[Any]]:
        path_to_file = self._path_to_file 

        if not exists(path_to_file):
            raise FileNotFoundError(f'\'{path_to_file}\' doesn\'t exist')

        filename = basename(path_to_file)
        extension = filename.split('.')[-1]

        match extension:
            case 'csv':
                executor = self._read_csv(path_to_file) 
            case 'xlsx':
                executor = self._read_excel(path_to_file)
            case _:
                raise ValueError('Invalid file extension (only .csv and .xlsx)')

        return executor
        
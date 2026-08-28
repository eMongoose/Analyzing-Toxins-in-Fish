import pandas as pd
from paths import *

csv_files = {
    'OCs_1977-1987.csv' : 'OCs_1.csv',
    'OCs_1988-2000.csv' : 'OCs_2.csv',
    'OCs 2001_2019.csv' : 'OCs_3.csv',
    'OCs_2022_present.csv' : 'OCs_4.csv',
    'Chlorinated_alkanes.csv' : 'OCs_3-5.csv',
    'Dioxins and Furans.csv' : 'OCS_3-25.csv'
}

def renameFile(input, output):
    '''
    Rename a file
    '''
    df = pd.read_csv(input)
    df.to_csv(output)
    
    
def fileConverter():
    for input, output in csv_files.items():
        renameFile(RAW_PATH / input, OUTPUT_PATH / output)
        print(f'currently reading {input} into {output}. Please wait a moment...')


def main():
    fileConverter()
    print('Data conversion has completed.')
    

if __name__ == '__main__':
    main()
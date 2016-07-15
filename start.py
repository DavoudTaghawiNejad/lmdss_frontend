import json
from abce import gui
import subprocess
import pandas as pd
from collections import OrderedDict

from pprint import pprint



fields = OrderedDict([(u'rounds', (1, 500, 1000)),
                      (u'expat_minimum_wage_pmonth', (0, 1000, 10000)),
                      (u'expat_tax_per_head_pmonth', (0, 1000, 10000)),
                      (u'expat_tax_percentage',  (0.0, 0.5, 1.0)),
                      (u'quota1', (0.0, 0.0, 1.0)),
                      (u'quota2', (0.0, 0.14, 1.0)),
                      (u'quota3', (0.0, 0.24, 1.0)),
                      (u'quota4', (0.0, 0.29, 1.0)),
                      (u'quota5', (0.0, 0.29, 1.0)),
                      (u'saudi_minimum_wage_pmonth', (0, 1000, 10000)),
                      (u'saudi_tax_per_head_pmonth', (0, 1000, 10000)),
                      (u'saudi_tax_percentage', (0.0, 0.0, 1.0)),
                      (u'visa_length', (1, 30, 90))])

@gui(fields)
def main(fields):
    fields['time_after_policy'] = fields['rounds']
    with open('industry_6_simulation.json') as data_file:
        data = json.load(data_file)
    data[u'after_policy'].update(fields)
    with open('./result/result/description.txt', 'w') as desc_file:
        json.dump(data, desc_file, indent=4)

    pprint(data)
    subprocess.call(['java',
                     '-Djava.library.path=/usr/local/lib:zmq.jar',
                     '-jar',
                     'lmdss.jar',
                     't',
                     json.dumps(data)])
    subprocess.call(['sh', 'dump.sh'])
    df = pd.read_csv('./result/result/SA.csv')
    cut_off = data[u'assumptions']['setup_period_1'] + data[u'assumptions']['setup_period_2']
    df.drop(range(0, cut_off), axis=0, inplace=True)
    df['round'] = df['day'] - df['day'][cut_off]
    df['index'] = df['day']
    df.set_index('index')
    df['num_expats'] = df['num_expats']
    df['num_saudis'] = df['num_saudis']
    df.drop(u'experamentID', axis=1, inplace=True)
    print(df.columns)
    df = df[[u'num_saudis', u'num_expats', u'wage_bill',
       u'profit', u'price', u'demand', u'production',
       u'wage_saudis', u'wage_expats', u'round', u'index']]

    df.rename(columns={u'num_saudis': 'employment Saudis', u'num_expats': 'employment expats',
                      u'wage_bill': 'total wage bill',
                      u'wage_saudis': 'average wage Saudis',
                      u'wage_expats': 'average wage expats'}, inplace=True)
    df.to_csv('./result/result/SA.csv', row_index='index', index=False)


main(fields)

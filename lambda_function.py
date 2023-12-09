from scrapy import Selector
import urllib3

import pandas as pd
from datetime import datetime
import io


def foo(event,context):
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://rates.am')
    sel = Selector(text=r.data)
    rows = sel.xpath('//*[@id="rb"]//tr[@id[not(.="")]]')
    csv = 'bank,date,usd_sell,usd_buy,eur_sell,eur_buy,rub_sell,rub_buy,gbp_sell,gbp_buy\n'
    date_map = {
        'Հուն': '01',
        'Փետ': '02',
        'Մար': '03',
        'Ապր': '04',
        'Մայ': '05',
        'Հնս': '06',
        'Հլս': '07',
        'Օգս': '08',
        'Սեպ': '09',
        'Հոկ': '10',
        'Նոյ': '11',
        'Դեկ': '12',
    }
    today = datetime.today()
    for row in rows:
        bank = row.xpath('td[2]//text()').extract()[1]
        date = row.xpath('td[5]//text()').extract()[0]
        date_list = date.split(' ')
        new_date = '{0}-{1}-{2} {3}:00'.format(today.year, date_map[date_list[1][:-1]], date_list[0], date_list[2])
        usd_sell = ''.join(row.xpath('td[6]//text()').extract())
        usd_buy = ''.join(row.xpath('td[7]//text()').extract())
        eur_sell = ''.join(row.xpath('td[8]//text()').extract())
        eur_buy = ''.join(row.xpath('td[9]//text()').extract()[0])
        rub_sell = ''.join(row.xpath('td[10]//text()').extract())
        rub_buy = ''.join(row.xpath('td[11]//text()').extract())
        gbp_sell = ''.join(row.xpath('td[12]//text()').extract())
        gbp_buy = ''.join(row.xpath('td[13]//text()').extract())
        csv += '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n'.format(bank, new_date, usd_sell, usd_buy, eur_sell, eur_buy,
                                                                  rub_sell, rub_buy, gbp_sell, gbp_buy)
    df = pd.read_csv(io.StringIO(csv),
                     dtype={'bank': str, 'usd_sell': float, 'usd_buy': float, 'eur_sell': float, 'eur_buy': float,
                            'rub_sell': float, 'rub_buy': float, 'gbp_sell': float, 'gbp_buy': float},
                     parse_dates=['date'])
    print(df.dtypes)
    print(df['usd_buy'].mean())
    print(df.head(18))
    print('updated lambda function')

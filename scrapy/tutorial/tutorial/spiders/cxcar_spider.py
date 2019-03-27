'''
@author: xusheng
'''

import re
import scrapy
from tutorial.items import CarItem


class CXCarSpider(scrapy.Spider):
    name = "cxcar"

    start_urls = [
        'http://car.chexiang.com/list/0-0-0-0-0-0-0-0-0-0-0-0-0-0-19-1.html',
    ]

    def parse(self, response):
#         self._save(response)
        
        # xpath version
#         series_names = response.xpath('//ul[@class="car-series-list"]/li[@class="series-list-item  clearfix"]/div[@class="cont-info"]/p[@class="car-name"]/text()').getall()

        # css version
        series_nodes = response.css('ul.car-series-list li.series-list-item.clearfix')
        for series_node in series_nodes:
            series_name = series_node.css('div.cont-info p.car-name::text').get()
            
            model_nodes = series_node.css('ul.car-model-list li.model-list-item')
            for model_node in model_nodes:
                model_name = model_node.css('a.model-list-item-link div.car-info div.car-model-name h3.name::text').get()
                price = model_node.css('a.model-list-item-link div.car-box p.price span::text').get()
                price_num = self._parse_price(price)
                yield CarItem(series_name=series_name, model_name=model_name, price=price, price_num=price_num)
        
        paging_node = response.css('div.list-pagine-center.page')
        if paging_node.css('a.next.disabled').get() == None:
            next_page = paging_node.css('div.list-pagine-center.page a.next::attr(href)').get()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def _parse_price(self, price):
        price_num = None
        m = re.match(r'^¥(\d*.*\d*)万$', price)
        if m != None:
            price_num = round(float(m.group(1)) * 10000, 2)

        return price_num
    
#     def _save(self, response):
#         filename = 'cxcar_sample_2019.html'
#         with open(filename, 'wb') as f:
#             f.write(response.body)
#         self.log('Saved file %s' % filename)
from scrapy.selector import Selector
import requests
import re








if __name__ == '__main__':
    city_numbers = []
    response = requests.get('https://mobile.gongchang.com/area.php?moduleid=4',
                            headers={'User-Agent':'Mozilla/5.0 (Linux; U; Android 4.4.4; zh-CN; Che1-CL10 Build/Che1-CL10) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/11.0.5.841 U3/0.8.0 Mobile Safari/534.30',
   })
    # province
    provinces = Selector(text=response.text).xpath("//div[@class='list-set']/ul/li").getall()

    for p in provinces:
        province = Selector(text=p).xpath('.//div/a/@href').get('')
        if 'index' in province:
            city_numbers.append(province.split('=')[-1])
        # city
        rsp = requests.get(url='https://mobile.gongchang.com/'+province)
        cities = Selector(text=rsp.text).xpath("//div[@class='list-set']/ul/li").getall()

        for c in cities:
            city = Selector(text=c).xpath('.//div/a/@href').get('')
            city_numbers.append(city.split('=')[-1])
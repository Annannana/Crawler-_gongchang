from scrapy import cmdline

if __name__ == '__main__':
	cmdline.execute("scrapy crawl company -o a.json".split())
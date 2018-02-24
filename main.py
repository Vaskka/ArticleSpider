from scrapy.cmdline import execute

import os

import sys

# os.system("pip install -i https://pypi.douban.com/simple/ pypiwin32")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute(["scrapy", "crawl", "jobbole"])
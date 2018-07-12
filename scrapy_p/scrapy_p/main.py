# -*- coding: utf-8 -*-
__author__ = 'kisan'
from scrapy.cmdline import execute
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#命令行执行
execute(["scrapy", "crawl", "blog_jobbole"])


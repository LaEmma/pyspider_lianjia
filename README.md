# pyspider_lianjia
crawl lianjia rental info( onsale and sold department info)

Mac OS setup instruction:
1. Install macports from website https://www.macports.org/install.php
2. Install phantom js + pyspider
		a. In terminal:
			i. sudo port phantomjs
			ii. pip install pyspider
			iii. pyspider all
		b. then open in safari: localhost:5000


Lianjia:
	use Firefox adds-on "httpfox" to get the following api
	API: http://bj.lianjia.com/chengjiao/getinfo/?page=1&id=101100427559&type=resblock&p=1
	this version extracts data from lianjia website, not from the api above
	result: including rent on sale/rent sold



extract data.zip

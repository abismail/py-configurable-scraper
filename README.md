# py-configurable-scraper
This python script scrapes any website you add a scraping configuration for and stores it in a mongodb (saving to mongodb will be removed)

## Setup

The following dependencies must be installed to run this:
 - This script was written for python 2.7, which you'll already have if you're running Ubuntu. If you don't though, don't panic, I have a link: https://www.python.org/downloads/
 - BeautifulSoup: `sudo apt-get install python-bs4`
  OR
   have a look here: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
 - pymongo client: `sudo apt-get install python-pymongo`
  OR
   have a look here: http://api.mongodb.com/python/current/installation.html

## Usage
For each website you want to scrape you have to specify a url in the `sites-to-scrape` dict object.

And then you're going to give the scraper a `map` to step through, and tell the scraper which data you want extracted.
For example if we want to scrape the website at 'http://www.webtickets.co.za/' for all the shows they're selling tickets, our map will look like this:

```
'webtickets'		: {
		'main_content'	: {
			'div': {
				'properties': { 'id' : 'event_list' }
			}
		},
		'event_card'	: {
			'a': {}
		},
		'paging'		: {
			'type'	: 'post',
			'vars'	: {
				'currentpage': 'page'
			}
		},
		'card_map'		: {
			'name'			: {
				'div'	: {
					'properties' : { 'class' : 'mainContentBlockTextHeading' }
				}
			},
			'image'			: {
				'img'	: {
					'attr' 		: 'src',
					'prepend'	: 'https://www.webtickets.co.za/'
				}
			},
			'link'			: {
				'attr'		: 'href',
				'prepend'	: 'https://www.webtickets.co.za'
			},
			'date'			: {
				'div'	: {
					'properties' : { 'class' : 'mainContentBlockText' },
					'child' 	 : {
						'div' : {
							'index' : 1 #tell bs to use the second find of this yield :: if there's an index AND a child, we first list child, THEN index
						}
					}

				}
			}
		}
	}
```

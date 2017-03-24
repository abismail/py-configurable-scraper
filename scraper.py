# import re, json
# import urllib
import urllib2
from bs4 import BeautifulSoup
# import MySQLdb
# import time, datetime, 
import unicodedata, string
# from fuzzywuzzy import fuzz
# from selenium import webdriver
# to install MongoClient I ran: 'sudo apt-get install python-pymongo' otherwise, see accepted answer at this link: http://stackoverflow.com/questions/17624416/cant-import-mongoclient
from pymongo import MongoClient

# pull site pages
# try an develop templates, per site, to extract data for each site (maybe in a config or something)
read_config = {
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
}

sites_to_scrape = {
	# works:
	#'kirstenbosch'		: 'https://www.sanbi.org/events/kirstenbosch',
	'webtickets'		: 'http://www.webtickets.co.za/'
}

def do_post_request( url, data="" ):
	headers = { 'User-Agent': 'Mozilla/5.0' }

	try:
		request = urllib2.Request(url, data, headers)
	except HTTPError as error:
		print "do_post_request got this error while constructing request object: "
		print error
	# end try
	
	get_type = getattr( request, "get_type", None )
	if True == callable( get_type ):
		response = urllib2.urlopen(request)
		data = response.read()
	else:
		data = request.read()
		# print data
	#end if
	return data
#end def

def do_get_request( url ):
	response = urllib2.urlopen(url)
	data = response.read()
	return data
#end def

def traverse_page( soup, config, movie_cards, key=None ):
	content = None
	main_page = False
	event_cards = ['',]

	for key in config['main_content']:
		if 'properties' in config['main_content'][key]:
			# the current tag is the one we're looking for
			# print "\n inside properties condition"
			if config['main_content'][key]['properties'].keys()[0] == 'id':
				# BS has a problem traversing through nested divs and after looking this issue (lookup using attribute 'id'), many others are having the same problem
				main_page = soup.find( key, id=config['main_content'][key]['properties']['id'] )
			else:
				main_page = soup.find( key, config['main_content'][key]['properties'] )
			# end if
		else:
			# print 'no properties key found'
			main_page = soup.find( key )
		# end if

		# if 'children' in config['main_content'][key]:
		# 	parent_element = soup.find_all( key )
		# 	main_page = traverse_page( soup.find( key, ), config)
		# # end if
	# loop

	if main_page != False:
		# print "\n\nfound main_page: \n" + str( main_page )
		parent_cards = ["",]


		for key in config['event_card']:
			if 'properties' in config['event_card'][key]:
				event_cards = main_page.find_all( key, config['event_card'][key]['properties'] )
				# print "found multiple event cards: "
				# print event_cards
			else:
				print "no properties, just getting all: " + str( key )
				print "from main_page: " + str( main_page )
				event_cards = main_page.find_all( key )
			# end if

			# if 'children' == key:
			# 	# parent_element = main_page.find_all( key )
			# 	# children_cards = []
			# 	# parent_element.find( key )
			# 	# main_page = traverse_page( , config, children_cards )
			# 	# print "found events: "
			# 	# print children_cards

			# 	# parent_cards = event_cards
			# 	# event_cards = ["",]
			# 	# for card in parent_cards:
			# 		# 
			# 	# end if
			# 	print "parent cards have children, not extracting children at this point..."
			# else:
			# 	event_cards = parent_cards
			# # end if
		# loop
	# else:
	# 	event_cards.append( soup.find_all() )
	# end if

	# movies_table = soup.find( 'table', {'class': 'when'} )
	# movies = movies_table.find_all( 'tr' )
	# traverse_page(soup)
	movie_cards = movie_cards + event_cards
	return movie_cards
# end def

def extract_event_data( event, config ):
	result = {}

	for field in config['card_map']:
		if 'attr' in config['card_map'][ field ]:
			prepend = ''
			if 'prepend' in config['card_map'][ field ]:
				prepend = config['card_map'][ field ]['prepend']
			# end if
			result[ field ] = prepend + event[ config['card_map'][ field ]['attr'] ]
			# print "we got " + field + ": " + str( result[ field ] )
		else:
			element = ''
			for key in config['card_map'][ field ]:
				if 'properties' in config['card_map'][ field ][ key ]:
					element = event.find_all( key, config['card_map'][ field ][ key ]['properties'] )
				else:
					element = event.find_all( key )
				# end if
				# print "html: "
				# print element

				if len( element ) > 0:
					if 'index' in config['card_map'][ field ][ key ]:
						element = element[ config['card_map'][ field ][ key ]['index'] ]
					else:
						element = element[0]
					# end if
				else:
					# element will ALWAYS be a list, since find_all returns a list, if it's empty, we'll assume nothing was found for this lookup
					result[ field ] = 'N/A'
					continue
				# end if

				print "got " + str( field ) + " element: "
				print element

				if 'attr' in config['card_map'][ field ][ key ]:
					prepend = ''
					if 'prepend' in config['card_map'][ field ][ key ]:
						prepend = config['card_map'][ field ][ key ]['prepend']
					# end if
					result[ field ] = prepend + element[ config['card_map'][ field ][ key ]['attr'] ]
				# end if

				if 'child' in config['card_map'][ field ][ key ]:
					# TODO: the inside of this block should be made abstract.
					child_element = ''
					child_tag = config['card_map'][ field ][ key ]['child'].keys()[0]

					if 'properties' in config['card_map'][ field ][ key ]['child'][ child_tag ]:
						child_element = element.find_all( child_tag, config['card_map'][ field ][ key ]['child'][ child_tag ]['properties'] )
					else:
						child_element = element.find_all( child_tag )
					# end if

					if 'index' in config['card_map'][ field ][ key ]['child'][ child_tag ]:
						child_element = child_element[ config['card_map'][ field ][ key ]['child'][ child_tag ]['index'] ]
					else:
						child_element = child_element[0]
					# end if

					if 'attr' in config['card_map'][ field ][ key ]['child'][ child_tag ]:
						child_element = child_element[0][ config['card_map'][ field ][ key ]['child'][ child_tag ]['attr'] ]
					# end if

					if child_element != '' and field not in result:
						result[ field ] = child_element.get_text()
					# end if
				else:
					if element != '' and field not in result:
						result[ field ] = element.get_text()
					# end if
				# end if
			# end for
		# end if

		# convert from unicode to ascii for storage
		if not isinstance( result[ field ], str ):
			# decode any non-string values
			result[ field ] = unicodedata.normalize( 'NFKD', result[ field ] ).encode('ascii', 'ignore')
		# end if
	# end for

	return result
# end def

def get_mongodb_connection():
	db_client = MongoClient()
	return db_client.admin # return a connection to the admin db in mongo
# end def

def save_event_data( site, event_data ):
	db_client = get_mongodb_connection()
	result = db_client.events.insert_one( { 'site_name': site, 'events': event_data } )
	return result.inserted_id
# end def

def delete_event_data( selector ):
	db_client = get_mongodb_connection()
	result = db_client.events.remove( selector )
# end def

def get_relavent_data( html, read_config ):
	soup = BeautifulSoup( html, 'html.parser' )
	events = []
	events = traverse_page( soup, read_config, events )

	return events
# end def

def next_page( config, url, page ):
	next_page_html = False

	if 'eval' in config['paging']:
		page = eval( config['paging']['eval'] )
	# end if

	if config['paging']['type'] == 'get':
		get_vars = []

		for var in config['paging']['vars']:
			get_vars.append( var + '=' + str( eval( config['paging']['vars'][ var ] ) ) )
		# end for

		url = url + '?' + '&'.join( get_vars )
		print "doing get on: " + url
		next_page_html = do_get_request( url )
	else:
		form_data = {}

		for var in config['paging']['vars']:
			form_data[ var] = str( eval( config['paging']['vars'][ var ] ) )
		# end for

		print "doing post to: " + url
		print "with data:"
		print form_data

		next_page_html = do_post_request( url, form_data)
	# end if

	return next_page_html
# end def



events = {}
event_data = {}
for site in sites_to_scrape:
	# load site into traversable variable
	site_payload = do_get_request( sites_to_scrape[ site ] )
	
	# extract event cards
	page = 1
	site_data = []
	data = get_relavent_data( site_payload, read_config[ site ] )
	last_payload = None
	while any(data) == True:
		site_data.append( data )

		# page and get the rest of the events
		page += 1
		print "getting page: " + str(page) + "for: " + site
		break
		# site_payload = next_page( read_config[ site ], sites_to_scrape[ site ], page )

		# # check that this isn't the last page we fetched
		# # is_last_payload = False if last_payload == None else set( site_payload ) == set( last_payload )
		
		# if not site_payload:
		# 	break
		# # else:
		# # 	print "\n\nres of list comparison: "
		# # 	print is_last_payload
		# # # end if

		# last_data_set = data[:]
		# data = get_relavent_data( site_payload, read_config[ site ] )

		# # print "\n\nold: \n"
		# # print last_data_set
		# # print "\n\nnew: \n"
		# # print data
		# # exit()
		# for prev_data_set in site_data:
		# 	if set( data ) == set( prev_data_set ): #site_data[ len( site_data ) - 1 ] ):
		# 		print "\n\n\nmatched previous result, breaking...\n\n\n"
		# 		break
		# 	# end if
		# # end for

		# last_payload = site_payload
		# if page > 2:
		# 	print "got page data:"
		# 	print data
	# loop
	# print "we are out"
	# exit()
	events[site] = site_data

	# extract event data from event cards
	
	event_data[ site ] = []
	for page in events[site]:
		for event in page:
			card_data = extract_event_data( event, read_config[ site ] )
			event_data[ site ].append( card_data )
		# end for
	# end for

	# purge database of old data
	delete_event_data( { 'site_name': site } )

	# save event data
	if site in event_data:
		# writing an output file per website for debugging purposes
		insert_id = save_event_data( site, event_data[ site ] )
		if insert_id:
			print "saved data for site: " + str( site ) + " successfully"
			print "insert_id: "
			print insert_id
		# end if
	# end if
# loop

exit()

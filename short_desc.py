import re
import urllib

""""
/* self script can display automated Wikidata item descriptions.

DEV WARNING: The code hosted here also runs OUTSIDE of mediawiki scopes on toollabs.
Thus if you need something from the MediaWiki context, wrap your code in a check
for the wd_auto_desc.mediawiki boolean.

USERS:

To add self to your common.js page:

 mw.loader.load("#en.wikipedia.org/w/index.php?title=MediaWiki:Wdsearch-autodesc.js&action=raw&ctype=text/javascript")

On Wikidata, to always show the automatic description, even if there is a manual one, add the following line to your common.js page:

 wd_auto_desc_wd_always_show = True

# PROGRAMMER ACCESS
# Get a single item label

wd_auto_desc.labelItem ( "Q123" , function ( label ) {
	 # "label" now contains the item label
} )

# Get a description

wd_auto_desc.loadItem ( "Q123" , {
	target:$('#desc') , # OPTIONAL: item to put the resulting HTML into
	def callback (self, q , html , opt ) :
		 # OPTIONAL: callback with the resulting HTML
		# q is the original item ID ("Q123"), html contains the description

	links : 'wikidata' , # OPTIONAL: 'wikidata' for links to wikidata, 'wikipedia' for links to the current language wikipedia (plain text otherwise)
	linktarget : '_blank' # OPTIONAL: For links, <a target='linktarget'>

} )

# ON WIKIDATA :

To load, but not run automatically, set

prevent_wd_auto_desc = 1

BEFORE including the script

*/
"""

class ShortDescription:

	def __init__(self):
		self.main_languages = ['en','de','fr','es','it','pl','pt','ja','ru','hu','nl','sv','fi']
		self.api = "https:#www.wikidata.org/w/api.php"
		self.q_prefix = "Q"
		self.p_prefix = "P"
		self.running = False
		self.color_not_found = "#FFFFC8"
		self.stock_loaded = False
		self.load_stock_running = 0
		self.stock = {}
		self.language_specific = {}

	def load_stock (self, the_callback ) :
		pass # TODO
	"""
		me = self
		if me.stock_loaded:
			return the_callback() # Already loaded
		if me.load_stock_running > 0:
 # Already loading, just wait
			setTimeout ( function () {me.load_stock(the_callback)} , 500 )
			return
		}

		server = 'tools-static.wmflabs.org' #'208.80.155.174'

		request({
			url: 'https:#'+server+'/tooltranslate/data/autodesc/toolinfo.json',
			headers: {'user-agent': 'Mozilla/5.0'},
			json: True
		}, function (error, response, d) {

			if not error and response.statusCode === 200:

			myUrls = []
			$.each ( d.languages , function ( k0 , language ) {
				myUrls.append ( { "url":'https:#'+server+'/tooltranslate/data/autodesc/'+language+'.json', "json":True, "headers": {'user-agent': 'Mozilla/5.0'}, "language":language} )
			} )
			me.load_stock_running = len(myUrls)

			async.map(myUrls, function(url, callback) {
			 request(url, function(error, response, d2) {
				# Some processing is happening here before the callback is invoked
				$.each ( d2 , function ( k1 , v1 ) {
					if me.stock[k1] is None:
						me.stock[k1] = {}
					me.stock[k1][url.language] = v1
				} )
				me.load_stock_running--

				if me.load_stock_running <= 0:

					me.stock_loaded = True
					the_callback()
				}
			 })
			}, function(err, results) {
				console.log ( "ERROR" , err , results )
			})

			} else console.log ( "Translations unavailable" , error , response )
		} )
	"""

	def txt (self, k , lang ) :
		if k not in self.stock:

			if lang in self.stock[k]:
				return self.stock[k][lang]
			return self.stock[k]['en']
		}
		return '???'

	def txt2 (self, t , k , lang ) :
		if lang not in self.language_specific:
			return t
		if k not in self.language_specific[lang]:
			return t

		# TODO
		m = t.match ( /^(<a.+>)(.+)(<\/a>)/ )
		if m is None:
			m = [ '' , '' , t , '' ]
		k2 = m[2]

		if k2 not in self.language_specific[lang][k]:
			return t
		return m[1] + self.language_specific[lang][k][k2] + m[3]

	def modifyWord (self, word , hints , lang ) :
		if lang == 'en':
			if hints.is_female:
				if word.lower()=="actor":
					return "actress"
				if word.lower()=="actor / actress":
					return "actress"
			elif hints.is_male :
				if word.lower()=="actor / actress":
					return "actor"
		elif lang == 'fr':
			if hints.is_female:
				if word.lower()=="acteur":
					return "actrice"
				if word.lower()=="être humain":
					return "personne"
		elif lang == 'de':
			if hints.is_female:
				if hints.occupation:
					word += 'in'
		return word

	def listWords (self, olist , hints , lang ) :
		list = olist.copy()
		if hints is not None:
			for k,v in enumerate(list):
				list[k] = self.modifyWord ( v , hints , lang )
		if lang == 'en':
			if len(list) == 1:
				return list[0]
			if len(list) == 2:
				return list[0] + ' and ' + list[1]
			last = list.pop()
			return list.join ( ', ' ) + ', and ' + last
		elif lang == 'de':
			if len(list) == 1:
				return list[0]
			if len(list) == 2:
				return list[0] + ' und ' + list[1]
			last = list.pop()
			return list.join ( ', ' ) + ' und ' + last
		elif lang == 'fr':
			if len(list) == 1:
				return list[0]
			if len(list) == 2:
				return list[0] + ' et ' + list[1]
			last = list.pop()
			return list.join ( ', ' ) + ' et ' + last
		elif lang == 'ga':
			if len(list) == 1:
				return list[0]
			if len(list) == 2:
				return list[0] + ' agus ' + list[1]
			last = list.pop()
			return list.join ( ', ' ) + ' agus ' + last
		elif lang == 'nl':
			if len(list) == 1:
				return list[0]
			if len(list) == 2:
				return list[0] + ' en ' + list[1]
			last = list.pop()
			return list.join ( ', ' ) + ' en ' + last
		elif lang == 'pl':
			if len(list) == 1:
				return list[0]
			if len(list) == 2:
				return list[0] + ' i ' + list[1]
			last = list.pop()
			return list.join ( ', ' ) + ' i ' + last
		elif lang == 'vi':
			if len(list) == 1:
				return list[0]
			if len(list) == 2:
				return list[0] + ' và ' + list[1]
			last = list.pop()
			return list.join ( ', ' ) + ', và ' + last
		} else return list.join ( ', ' )

	def ucFirst (self, s ) :
		return s[0].upper() + s[1:]

	def getNationalityFromCountry (self, country , claims , hints ) :

		if hints is None:
			hints = {}
		if hints.lang == 'en':

			return self.txt2 ( country , 'nationality' , hints.lang )
		elif hints.lang == 'de':

			is_female = self.hasPQ ( claims , 21 , 6581072 )
			append = ''
			if hints.not_last:
				append = ''
			elif is_female:
				append = 'e'
			else append += 'er'

			name = self.txt2 ( country , 'nationality' , hints.lang )
			if country in self.language_specific[hints.lang]['nationality']:
				return name + append

			# TODO regexp
			ends = [
				[/land$/,'ländisch'] ,
				[/ia$/,'isch'] ,
				[/a$/,'esisch'] ,
				[/ien$/,'isch'] ,
			]

			for v in ends:
				if not v[0].test(name):
					return False
				name = name.replace ( v[0] , v[1] )
				return False

			return name + append

		else:
			return self.txt2 ( country , 'nationality' , hints.lang )

	def isPerson (self, claims ) :
		if self.hasPQ ( claims , 107 , 215627):
			return True # GND:Person
		if self.hasPQ ( claims , 31 , 5):
			return True # Instance of: human
		return False

	def isTaxon (self, claims ) :
		if self.hasPQ ( claims , 31 , 16521):
			return True # Taxon
		if self.hasPQ ( claims , 105 , 7432):
			return True # Taxon rank: species
		if self.hasPQ ( claims , 105 , 34740):
			return True # Taxon rank: genus
		if self.hasPQ ( claims , 105 , 35409):
			return True # Taxon rank: family
		return False

	def splitLink (self, v ) :
		# TODO regexp
		ret = None
		if ret is None:
			ret = v.match ( /^(\[\[.+\|)(.+)(\]\])$/ )
		if ret is None:
			ret = v.match ( /^(\[\[)(.+)(\]\])$/ )
			if ret != None:
				ret[1] += ret[2] + '|'
		if ret is None:
			ret = v.match ( /^(<a.+?>)(.+)(<\/a>)$/ )
		if ret is None:
			ret = [ '' , '' , v , '' ]
		return ret
			
	def removeEntityPrefix(s):
		return re.sub(r"^.+?entity\#","",s)
		#taxon_q = x.taxon["value"].replace ( /^.+?entity\# , '' )

	def describeTaxon (self, q , claims , opt ) :
		load_items = []
		sparql = "SELECT ?taxon ?taxonRank ?taxonRankLabel ?parentTaxon ?taxonLabel ?taxonName { wd:" + q
		sparql += ' wdt:P171* ?taxon . ?taxon wdt:P171 ?parentTaxon . ?taxon wdt:P225 ?taxonName . ?taxon wdt:P105 ?taxonRank . SERVICE wikibase:label { "bd":serviceParam wikibase:language "[AUTO_LANGUAGE],'+opt["lang"]+'" } }'
		url = 'https:#query.wikidata.org/bigdata/namespace/wdq/sparql?format=json&query=' + urllib.urlencode(sparql)
		body = self.wd.getResponse(url)

		taxa_ranks = {
			"Q767728":0 , # variety
			"Q68947":1, # subspecies
			"Q7432":2, # species
			"Q34740":3, # genus
			"Q35409":4, # family
			"Q36602":5, # order
			"Q37517":6, # class
			"Q38348":7, # phylum
			"Q36732":8 # kingdom
		}

		taxon_name = None
		taxa_cache = []
		load_items = []
		for num,x in enumerate(body.results.bindings):
			taxon_q = self.removeEntityPrefix(x["taxon"]["value"])
			taxon_rank = self.removeEntityPrefix(x["taxonRank"]["value"])
			if taxon_q == q:
				load_items.append ( [0,taxon_rank] )
				taxon_name = self.removeEntityPrefix(x["taxonName"]["value"])
			if taxon_rank in taxa_ranks:
				rank_id = taxa_ranks[taxon_rank]
				taxa_cache[rank_id] = x

		for num,x in enumerate(taxa_cache):
			if x is None:
				continue
			if x["taxonLabel"]["value"].lower() == x["taxonName"]["value"].lower():
				continue
			taxon_q = self.removeEntityPrefix(x["taxon"]["value"])
			load_items.append ( [0,taxon_q] )
			break

		item_labels = self.labelItems ( load_items , opt )
		if len(item_labels)>0:
			if item_labels[0].length == 0:
				return self.describeGeneric ( q , claims , opt ) # Fallback
			h = [ item_labels[0][0] ]
			if item_labels[0].length == 2:
				h[0] += ' ' + self.txt('of',opt["lang"]) + ' ' + item_labels[0][1]
			if taxon_name is not None:
				h.append ( '['+taxon_name+']' )
			self.setTarget ( opt , self.ucFirst ( ' '.join(h) ) , q )
		else:
			self.describeGeneric ( q , claims , opt ) # Fallback

	def describePerson (self, q , claims , opt ) :
		load_items = []
		self.addItemsFromClaims ( claims , 106 , load_items ) # Occupation
		self.addItemsFromClaims ( claims , 39 , load_items ) # Office
		self.addItemsFromClaims ( claims , 27 , load_items ) # Country of citizenship
		self.addItemsFromClaims ( claims , 166 , load_items ) # Award received
		self.addItemsFromClaims ( claims , 31 , load_items ) # Instance of
		self.addItemsFromClaims ( claims , 22 , load_items ) # Father
		self.addItemsFromClaims ( claims , 25 , load_items ) # Mother
		self.addItemsFromClaims ( claims , 26 , load_items ) # Spouse
		self.addItemsFromClaims ( claims , 463 , load_items ) # Member of

		is_male = self.hasPQ ( claims , 21 , 6581097 )
		is_female = self.hasPQ ( claims , 21 , 6581072 )

		item_labels = self.labelItems ( load_items , opt ) 
		h = []

		# Nationality
		h2 = ''
		tmp = [] if item_labels["27"] is None else item_labels["27"]
		for k,v in enumerate(tmp):
			v2 = self.splitLink ( v )
			s = self.getNationalityFromCountry ( v2[2] , claims , { "lang":opt["lang"] , "not_last":(k+1!=len(tmp)) } )
			if k == 0:
				h2 = v2[1]+s+v2[3]
			else:
				h2 += '-' + v2[1] + s.lower() + v2[3] # Multi-national
		if h2 != '':
			h.append ( h2 )

		# Occupation
		ol = len(h)
		self.add2desc ( h , item_labels , [ 31 , 106 ] , { "hints":{ "is_male":is_male, "is_female":is_female, "occupation":True, "o":opt} } )
		if len(h) == ol:
			h.append ( self.txt('person',opt["lang"]) )

		# Office
		self.add2desc ( h , item_labels , [ 39 ] , { "hints":{ "is_male":is_male, "is_female":is_female, "office":True} , "prefix":',', "o":opt } )

		# Dates
		born = self.getYear ( claims , 569 , opt["lang"] )
		died = self.getYear ( claims , 570 , opt["lang"] )
		if born != '' and died != '':

			h.append ( ' (' + born + '–' + died + ')' )
		elif born != '':
			h.append ( ' (*' + born + ')' )
		elif died != '':
			h.append ( ' (†' + died + ')' )

		if self.hasPQ ( claims , 21 , 6581072 ):
			h.append ( '♀' ) # Female
		if self.hasPQ ( claims , 21 , 6581097 ):
			h.append ( '♂' ) # Male

		self.add2desc ( h , item_labels , [ 166 ] , { "prefix":';',"o":opt } )
		self.add2desc ( h , item_labels , [ 463 ] , { "prefix":';' , "txt_key":'member of',"o":opt } )
		self.add2desc ( h , item_labels , [ 22,25 ] , { "prefix":';' , "txt_key":'child of',"o":opt } )
		self.add2desc ( h , item_labels , [ 26 ] , { "prefix":';' , "txt_key":'spouse of',"o":opt } )

		if len(h) == 0:
			h.append ( self.txt('person',opt["lang"]) )

		self.setTarget ( opt , self.ucFirst ( ' '.join(h) ) , q )

	def getBestQuantity (self, claims ) :
		dv = claims[0]["mainsnak"]["datavalue"]
		ret = float(re.sub( "^\+" , "" , dv["value"]["amount"]))
		if ret >= 1000000:
			ret = round(ret/1000000,1)
			ret = str(ret) + "M"
		return ret

	def describeGeneric (self, q , claims , opt ) :

		load_items = []
		self.addItemsFromClaims ( claims , 361 , load_items ) # Part of
		self.addItemsFromClaims ( claims , 279 , load_items ) # Subclass off
		self.addItemsFromClaims ( claims , 1269 , load_items ) # Facet off
		self.addItemsFromClaims ( claims , 31 , load_items ) # Instance of
		self.addItemsFromClaims ( claims , 60 , load_items ) # Astronomical object

		self.addItemsFromClaims ( claims , 175 , load_items ) # Performer
		self.addItemsFromClaims ( claims , 86 , load_items ) # Composer
		self.addItemsFromClaims ( claims , 170 , load_items ) # Creator
		self.addItemsFromClaims ( claims , 57 , load_items ) # Director
		self.addItemsFromClaims ( claims , 162 , load_items ) # Producer
		self.addItemsFromClaims ( claims , 50 , load_items ) # Author
		self.addItemsFromClaims ( claims , 61 , load_items ) # Discoverer/inventor

		self.addItemsFromClaims ( claims , 17 , load_items ) # Country
		self.addItemsFromClaims ( claims , 131 , load_items ) # Admin unit

		self.addItemsFromClaims ( claims , 495 , load_items ) # Country of origin
		self.addItemsFromClaims ( claims , 159 , load_items ) # Headquarters location

		self.addItemsFromClaims ( claims , 306 , load_items ) # OS
		self.addItemsFromClaims ( claims , 400 , load_items ) # Platform
		self.addItemsFromClaims ( claims , 176 , load_items ) # manufacturer

		self.addItemsFromClaims ( claims , 123 , load_items ) # Publisher
		self.addItemsFromClaims ( claims , 264 , load_items ) # Record label

		self.addItemsFromClaims ( claims , 105 , load_items ) # Taxon rank
		self.addItemsFromClaims ( claims , 138 , load_items ) # Named after
		self.addItemsFromClaims ( claims , 171 , load_items ) # Parent taxon

		self.addItemsFromClaims ( claims , 1433 , load_items ) # Published in
		self.addItemsFromClaims ( claims , 571 , load_items ) # Inception
		self.addItemsFromClaims ( claims , 576 , load_items ) # Until
		self.addItemsFromClaims ( claims , 585 , load_items ) # Point in time
		self.addItemsFromClaims ( claims , 703 , load_items ) # Found in taxon
		self.addItemsFromClaims ( claims , 1080 , load_items ) # From fictional universe
		self.addItemsFromClaims ( claims , 1441 , load_items ) # Present in work
		self.addItemsFromClaims ( claims , 921 , load_items ) # Main topic

		self.addItemsFromClaims ( claims , 425 , load_items ) # Field of self profession
		self.addItemsFromClaims ( claims , 59 , load_items ) # Constellation

		self.addItemsFromClaims ( claims , 1082 , load_items ) # Population

		item_labels = self.labelItems ( load_items , opt )
		h = []

		# Date
		pubdate = self.getYear ( claims , 577 , opt["lang"] )
		if pubdate != '':
			h.append ( pubdate )

		# Instance/subclass/etc
		self.add2desc ( h , item_labels , [ 279,31,1269,60,105 ] , { "o":opt } )

		# Location
		h2 = []
		if "131" in item_labels:
			h2 += item_labels["131"]
		sep = ' / '
		h3 = []
		if "17" in item_labels:
			h3 += item_labels["17"]
		if len(h) == 0 and ( len(h2) > 0 or len(h3) > 0 ):
			h.append ( self.txt('location',opt["lang"]) )
		if len(h2) > 0 and len(h3) > 0:
			h.append ( self.txt('in',opt["lang"]) + ' ' + sep.join(h2) + ", " + sep.join(h3) )
		elif len(h2) > 0:
			h.append ( self.txt('in',opt["lang"]) + ' ' + sep.join(h2) )
		elif len(h3) > 0:
			h.append ( self.txt('in',opt["lang"]) + ' ' + sep.join(h3) )

		# Population
		i = self.wd.getItem(q)
		if i.hasClaims(1082):
			cl = i.getClaimsForProperty(1082)
			best = self.getBestQuantity ( cl )
			label = self.wd.getItem('P1082').getLabel()
			h.append ( ', ' + label + ' ' + best )

		# Creator etc.
		self.add2desc ( h , item_labels , [ 175,86,170,57,50,61,176 ] , { "txt_key":'by', "o":opt } )
		self.add2desc ( h , item_labels , [ 162 ] , { "prefix":',' , "txt_key":'produced by', "o":opt } )
		self.add2desc ( h , item_labels , [ 306,400 ] , { "txt_key":'for', "o":opt } )
		self.add2desc ( h , item_labels , [ 264,123 ] , { "txt_key":'from', "o":opt } )
		self.add2desc ( h , item_labels , [ 361 ] , { "prefix":',' , "txt_key":'part of', "o":opt } )
		self.add2desc ( h , item_labels , [ 138 ] , { "prefix":',' , "txt_key":'named after', "o":opt } )
		self.add2desc ( h , item_labels , [ 425 ] , { "prefix":',' , "txt_key":'in the field of', "o":opt } )
		self.add2desc ( h , item_labels , [ 171 ] , { "prefix":'' , "txt_key":'of', "o":opt } )
		self.add2desc ( h , item_labels , [ 59 ] , { "prefix":'' , "txt_key":'in the constellation', "o":opt } )
		self.add2desc ( h , item_labels , [ 1433 ] , { "prefix":'' , "txt_key":'published in', "o":opt } )
		self.add2desc ( h , item_labels , [ 585 ] , { "prefix":'' , "txt_key":'in', "o":opt } )
		self.add2desc ( h , item_labels , [ 703 ] , { "prefix":'' , "txt_key":'found_in', "o":opt } )
		self.add2desc ( h , item_labels , [ 1080,1441 ] , { "prefix":'' , "txt_key":'from', "o":opt } )
		self.add2desc ( h , item_labels , [ 921 ] , { "prefix":'' , "txt_key":'about', "o":opt } )

		i = self.wd.getItem ( q )
		if i is not None:
			if i.hasClaims('P571'):
				h.append ( ', ' + self.txt('from',opt["lang"]) + ' ' + self.getYear ( i.raw.claims , 571 , opt["lang"] ) )
			if i.hasClaims('P576'):
				h.append ( ', ' + self.txt('until',opt["lang"]) + ' ' + self.getYear ( i.raw.claims , 576 , opt["lang"] ) )

		# Origin (group of humans, organizations...)
		h2 = item_labels["159"].copy() if "159" in item_labels else []
		h3 = item_labels["495"].copy() if "495" in item_labels else []
		if len(h2) > 0 and len(h3) > 0:
			h.append ( self.txt('from',opt["lang"]) + ' ' + sep.join(h2) + ", " + sep.join(h3) )
		elif len(h2) > 0:
			h.append ( self.txt('from',opt["lang"]) + ' ' + sep.join(h2) )
		elif len(h3) > 0:
			h.append ( self.txt('from',opt["lang"]) + ' ' + sep.join(h3) )

		# Fallback
		if len(h) == 0:
			h = '<i>'+self.txt('cannot_describe',opt["lang"])+'</i>'
			if opt["fallback"] == 'manual_desc' and self.main_data.descriptions !== undefined and self.main_data.descriptions[opt["lang"]] !== undefined:
				h = self.main_data.descriptions[opt["lang"]]["value"]
			if opt["target"] is not None:
				opt["target"].css({'background-color':self.color_not_found})
		else:
			h = self.ucFirst ( " ".join(h) )
			h = re.sub(" , ",", ",h)
		self.setTarget ( opt , h , q )

	def add2desc (self, h , item_labels , props , opt=None ) :
		if opt is None:
			opt = {}
		h2 = []
		x = []
		lang = None
		if lang is None and opt["lang"] is not None:
			lang = opt["lang"]
		if lang is None and opt["o"] is not None:
			lang = opt["o"].lang
		if lang is None and opt["hints"] is not None and opt["hints"].o is not None:
			lang = opt["hints"]["o"]["lang"]
		if lang is None:
			pass # TODO error?
		for prop in props.values():
			if prop in item_labels:
				x += item_labels[prop]
		h2 += x

		if len(h2) > 0:
			if prefix in opt and len(h) > 0:
				h[len(h)-1] += opt["prefix"]
			s = self.listWords ( h2 , opt["hints"] , lang )
			if "txt_key" in opt:
				if lang == 'te':
					s = s + ' ' + self.txt(opt["txt_key"],lang)
				else:
					s = self.txt(opt["txt_key"],lang) + ' ' + s
			h.append ( s )

	def loadItem (self, q , opt ) :
		self.load_stock()
		q = q.upper()
		opt["q"] = q
		self.wd.getItemBatch ( [ q ] )
		self.main_data = self.wd.items[q].raw
		claims = self.wd.items[q].raw.claims or []

		if self.isPerson ( claims ):
			self.describePerson ( q , claims , opt )
		elif self.isTaxon (claims):
			self.describeTaxon ( q , claims , opt )
		elif self.isDisambig (claims):
			self.setTarget (opt, self.txt("disambig", opt["lang"]), q)
		else:
			return self.describeGeneric ( q , claims , opt )

	def isDisambig (self, claims ) :

		return ( self.hasPQ ( claims , 107 , 11651459 ) )

	def hasPQ (self, claims , p , q ) :
		# p,q numerical
		p = self.p_prefix+p
		if p not in claims:
			return False
		for v in claims[p].values():
			if "mainsnak" not in v:
				return False
			if "datavalue" not in v["mainsnak"]:
				return False
			if "value" not in v["mainsnak"]["datavalue"]:
				return False
			if "numeric-id" not in v["mainsnak"]["datavalue"]["value"]:
				return False
			if q != v["mainsnak"]["datavalue"]["value"]["numeric-id"]:
				return False
			return True
		return False

	def addItemsFromClaims (self, claims , p , items ) :
		# p numerical
		prefixed = self.p_prefix+p
		if prefixed not in claims:
			return
		for v in claims[prefixed].values():
			if "mainsnak" not in v:
				return
			if "datavalue" not in v["mainsnak"]:
				return
			if "value" not in v["mainsnak"]["datavalue"]:
				return
			if "numeric-id" not in v["mainsnak"]["datavalue"]["value"]:
				items.append ( [ p , 'P'+re.sub("\D","",str(p)) ] )
			else:
				items.append ([p , self.q_prefix + v["mainsnak"]["datavalue"]["value"]["numeric-id"]])

	def getYear (self, claims , p , lang ) :
		# p numerical
		p = self.p_prefix+p
		if p not in claims:
			return ''
		ret = ''
		for v in claims[p].values():
			if "mainsnak" not in v:
				return
			if "datavalue" not in v["mainsnak"]:
				return
			if "value" not in v["mainsnak"]["datavalue"]:
				return
			if "time" not in v["mainsnak"]["datavalue"]["value"]:
				return
			m = re.match ( "^ ([+-])0 * (\d+) " , v["mainsnak"]["datavalue"]["value"]["time"] )
			if m is None:
				return
			ret = m[2]
			if m[1] == '-':
				ret += self.txt('BC',lang)
		return ret

	def labelItems (self, items , opt = None ) :
		if len(items) == 0:
			return {}
		if opt is None:
			opt = {}
		use_lang = opt["lang"]

		i = []
		for v in items:
			if v[0] != 0:
				i.append ( 'P'+(''+v[0]).replace(/\D+/g,'') )
			i.append ( v[1] )

		self.wd.getItemBatch ( i )
		cb = {}
		for q in i:
			v = self.wd.items[q].raw
			if "labels" not in v:
				continue
			curlang = use_lang # Try set language
			if curlang not in v["labels"]: # Try main languages
				for l in self.main_languages:
					if l in v["labels"]:
						curlang = l
						break
			if curlang not in v["labels"]: # Take any language
				for l in v["labels"].keys():
					curlang = l
					break
			if curlang not in v["labels"]:
				continue
			p = q
			for v in items:
				if v[1] == q:
					p = v[0]

			if p == 31:
				if q == 'Q5':
					continue # Instance of: human
				if q == 'Q16521':
					continue # Instance of: taxon

			if p not in cb:
				cb[p] = []

			wiki = use_lang+'wiki'
			label = v["labels"][curlang]["value"]
			linktarget = "" if "linktarget" not in opt else " target='"+opt["linktarget"]+"'"
			if opt["links"] == 'wikidata':
				cb[p].append ( "<a href='#www.wikidata.org/wiki/"+ q + "'" + linktarget +">" + label + "</a>" )
			elif opt["links"] == 'reasonator_local':
				cb[p].append ( "<a href='?lang="+opt["reasonator_lang"]+"&q="+ q + "'" + linktarget +">" + label + "</a>" )
			elif opt["links"] == 'reasonator':
				cb[p].append ( "<a href='/reasonator/?lang="+opt["reasonator_lang"]+"&q="+ q + "'" + linktarget +">" + label + "</a>" )
			elif opt["links"] == 'wiki':
				if "sitelinks" in v and wiki in v["sitelinks"]:
					page = v["sitelinks"][wiki]["title"]
					if page == label:
						cb[p].append ( "[["+ label +"]]" )
					else:
						cb[p].append ( "[["+ page + "|" + label +"]]" )
				else:
					cb[p].append ( ""+ label +"" ) # TODO {{redwd}}
			elif opt["links"] == 'wikipedia' and "sitelinks" in v and wiki in v["sitelinks"]:
				page = self.wikiUrlencode ( v["sitelinks"][wiki]["title"] )
				if opt["local_links"]:
					cb[p].append ( "<a href='/wiki/"+ page + "'" + linktarget +">" + label + "</a>" )
				else:
					cb[p].append ( "<a href='#"+use_lang+".wikipedia.org/wiki/"+ page + "'" + linktarget +">" + label + "</a>" )
			elif opt["links"] != '' and "sitelinks" in v and use_lang+opt["links"] in v["sitelinks"]:
				page = self.wikiUrlencode ( v["sitelinks"][use_lang+opt["links"]].title )
				if "local_links" in opt:
					cb[p].append ( "<a href='/wiki/"+ page + "'" + linktarget +">" + label + "</a>" )
				else:
					cb[p].append ( "<a href='#"+use_lang+"."+opt["links"]+".org/wiki/"+ page + "'" + linktarget +">" + label + "</a>" )
			else:
				cb[p].append ( label )
		return cb

	def wikiUrlencode (self, s ) :
		ret = re.sub(" ","_",s)
		return urllib.parse.quote(ret)

	def labelItem (self, q , opt ) :
		item_labels = self.labelItems ( [ [0,q] ] , opt )
		if len(item_labels)>0:
			return item_labels[0]

	def setTarget (self, opt , html , q ) :
		html = re.sub(" +"," ",html)
		if "target" in opt:
			opt["target"].html ( html )
		return ( q , html , opt )

from infobox import InfoboxGenerator
from wikidata import WikiData

class GlueCode:

	def __init__(self, language_specs):
		self.al = language_specs
		self.wd = WikiData()
		self.defaults = { "language":"en" }
		self.infobox_generator = {"ig":InfoboxGenerator()}
		self.infobox_generator["ig"]["wd"] = self.reasonator_base.wd
		self.infobox_generator["ig"].init()
		self.autodesc_short = { "ad": } # TODO

	def addInfobox (self,  text , o ):
		if o["links"] == 'wiki' and "infobox_text" in o:
			text = o["infobox_text"] + text
		return text


	def getShortDesc (self,  o , callback ) :
		params = {
			"q" : 'Q'+(''+o["q"]).replace(/\D/g,'') ,
			"links" : o["links"] ,
			"linktarget" : o["linktarget"] ,
			"lang" : o["lang"] or self.defaults["language"] ,
			"callback" : function ( q , html , opt ) {
				callback ( self.addInfobox(html,o) )
		}
		self.autodesc_short["ad"].loadItem ( o["q"] , params )


	def getDescription (self,  o , callback ) :

		if "lang" not in o["lang"]:
			o["lang"] = self.defaultslanguage

		if o["links"] == 'wiki' and '' if o["get"]_infobox is None else o["get"]_infobox != '' and typeof o["infobox"]_done == 'undefined' :
			 {
			o2 = $.extend ( True , {} , o )
			o2["infobox_done"] = True
			infobox_generator["ig"].get_filled_infobox ({"q":o2.q , "template" :o2["infobox_template"] , "lang" :o2["lang"] , "callback" :function (s) {
				o2["infobox_text"] = s
				return self.getDescription ( o2 , callback )
			} } )
			return


		if o["mode"] != 'long' :
			 {
			return self.getShortDesc ( o , callback )

		if typeof self.al[o["lang"]] == 'undefined' :
			 {
	#		console.log ( "Language " + o["lang"] + " not available for long description, using short description instead" )
			return self.getShortDesc ( o , callback )


		self.wdgetItemBatch ( [o["q"]] , function () {

			call_function = self.reasonator.getFunctionName ( o["q"] )
			if typeof call_function == 'undefined' or call_function =='undefined' :
				 {
	#			console.log ( "No long description function available for " + o["q"] + ", using short description instead" )
				return self.getShortDesc ( o , callback )


			ret = { **self.al[o["lang"]] }
			ret["wd"] = self.wd
			ret.q = o["q"]
			ret["lang"] = o["lang"]
			ret["redlinks"] = o["redlinks"]

			if "links" not in o:
				ret["render_mode"] = 'text'
			elif o["links"] == 'wiki' :
				ret["render_mode"] = 'wiki'
			elif o["links"] == 'wikidata' :
				pass # Default
			elif o["links"] == 'wikipedia' :
				ret["render_mode"] = 'wikipedia'



			to_load = self.reasonator.addToLoadLater ( o["q"] )
			ret["wd"].getItemBatch ( to_load , function () {

				ret.init()
				ret["main_title_label"] = ret["wd"].items[o["q"]].getLabel()
				ret[call_function] ( function ( html ) {
					if $.trim(html) == '<br/>' ) return self.getShortDesc ( o , "callback" :

					callback ( self.addInfobox(html,o) )





	def addMedia (self,  j , thumb , callback , user_zoom ) :

		q = j.q
		i = self.wditems[q]
		props = {
			"P18" : 'image' ,
			"P94" : 'coat_of_arms' ,
			"P158" : 'seal' ,
			"P41" : 'flag' ,
			"P10" : 'video' ,
			"P242" : 'map' ,
			"P948" : 'banner' ,
			"P154" : 'logo'
		}

		j.media = {}
		$.each ( props , function ( p , name ) {
			if !i.hasClaims(p) :
				 return
			j.media[name] = i.getStringsForProperty ( p )
			$.each ( j.media[name] , function ( k , v ) {
				j.media[name][k] = v.replace(/_/g,' ')



		if typeof thumb == 'undefined' or !thumb :
			 {
			callback()
			return


		thumb = (''+thumb).replace(/\D/g,'') * 1

		files = []
		$.each ( j.media , function ( k0 , v0 ) {
			$.each ( v0 , function ( k1 , filename ) {
				files.append ( 'File:'+filename )



		j.thumbnails = {}
		if i.hasClaims('P625') :
			 { # OSM map thumb
			claims = i.getClaimsForProperty('P625')
			j.media['osm'] = [ 'osm_map' ]
			lat = claims[0]["mainsnak"].datavalue["value"].latitude
			lon = claims[0]["mainsnak"].datavalue["value"].longitude
			zoom = user_zoom or 4
			thumburl = 'https:#maps["wikimedia"].org/img/osm-intl,'+zoom+','+lat+','+lon+','+thumb+'x'+thumb+'.png'
			j.thumbnails['osm_map'] = {
				"thumburl" : thumburl ,
				"thumbwidth" : thumb ,
				"thumbwidth" : thumb ,
				"url" : thumburl ,
				"descriptionurl" : 'https:#tools["wmflabs"].org/geohack/geohack.php?language=en&params='+lat+'_N_'+lon+'_E_globe:earth'



		if files["length"] == 0 ) { "return" callback(:


		$.getJSON ( "https:#commons["wikimedia"].org/w/api.php?callback=?" , {
			"action" :'query',
			"titles" :files.join('|'),
			"prop" :'imageinfo',
			"iiprop" :'url',
			"iiurlwidth" :thumb,
			"iiurlheight" :thumb,
			"format" :'json'
		} , function ( d ) {
			$.each ( d.query["pages"] , function ( k , v ) {
				file = v["title"].replace(/^File:/,'').replace(/_/g,' ')
				j.thumbnails[file] = v.imageinfo[0]

			callback()




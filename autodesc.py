from infobox import InfoboxGenerator
from wikidata import WikiData
from short_desc import ShortDescription
import re


class AutoDesc:

	def __init__(self, language_specs):
		self.al = language_specs
		self.defaults = {"language": "en"}
		self.wd = WikiData()
		self.infobox_generator = InfoboxGenerator(self.wd)
		self.autodesc_short = ShortDescription(self.wd)
		self.media_props = {
			"P18": 'image',
			"P94": 'coat_of_arms',
			"P158": 'seal',
			"P41": 'flag',
			"P10": 'video',
			"P242": 'map',
			"P948": 'banner',
			"P154": 'logo'
		}

	def addInfobox(self, text, o):
		if o["links"] == 'wiki' and "infobox_text" in o:
			text = o["infobox_text"] + text
		return text

	def getShortDesc(self, o):
		params = {
			"q": "Q" + re.sub(r"\D", "", str(o["q"])),
			"links": o["links"],
			"linktarget": o["linktarget"],
			"lang": o["lang"] or self.defaults["language"],
			"callback": lambda lst: self.addInfobox(lst[1], lst[2])  # function ( q , html , opt )
		}
		self.autodesc_short.loadItem(o["q"], params)

	def setInfoboxDescription(self, o2, s):
		o2["infobox_text"] = s
		return self.getDescription(o2)

	def getDescription(self, o):
		if "lang" not in o["lang"]:
			o["lang"] = self.defaults["language"]

		tmp1 = '' if o["get_infobox"] is None else o["get_infobox"]
		if o["links"] == 'wiki' and tmp1 != '' and "infobox_done" not in o:
			o2 = o.copy()
			o2["infobox_done"] = True
			self.infobox_generator.get_filled_infobox({
				"q": o2.q,
				"template": o2["infobox_template"],
				"lang": o2["lang"],
				"callback": lambda s: self.setInfoboxDescription(o2, s)
			})
			return

		if o["mode"] != 'long':
			return self.getShortDesc(o)
		if o["lang"] not in self.al:
			return self.getShortDesc(o)

		self.wd.getItemBatch([o["q"]])

		call_function = self.reasonator.getFunctionName(o["q"])
		if call_function is None:
			return self.getShortDesc(o)

		ret = self.al[o["lang"]].copy()
		ret["wd"] = self.wd
		ret.q = o["q"]
		ret["lang"] = o["lang"]
		ret["redlinks"] = o["redlinks"]

		if "links" not in o:
			ret["render_mode"] = 'text'
		elif o["links"] == 'wiki':
			ret["render_mode"] = 'wiki'
		elif o["links"] == 'wikidata':
			pass  # Default
		elif o["links"] == 'wikipedia':
			ret["render_mode"] = 'wikipedia'

		to_load = self.reasonator.addToLoadLater(o["q"])
		ret["wd"].getItemBatch(to_load)

		ret.init()
		ret["main_title_label"] = ret["wd"].items[o["q"]].getLabel()
		# TODO what was this again?
		"""
		ret[call_function] ( function ( html ) {
			if $.trim(html) == '<br/>' ):
				return self.getShortDesc ( o , "callback" :
			self.addInfobox(html,o)
		"""

	def addMedia(self, j, thumb, callback, user_zoom):
		q = j.q
		i = self.wditems[q]

		j.media = {}
		for p, name in self.media_props.items():
			if not i.hasClaims(p):
				continue
			j.media[name] = i.getStringsForProperty(p)
			for k, v in enumerate(j.media[name]):
				j.media[name][k] = re.sub(r"_", " ", v)

		if thumb is None or not thumb:
			return

		thumb = int(re.sub(r"\D", "", str(thumb)))

		files = []
		for v0 in j.media.values():
			for filename in v0.values():
				files.append('File:' + filename)

		j.thumbnails = {}
		if i.hasClaims('P625'):  # OSM map thumb
			claims = i.getClaimsForProperty('P625')
			j.media['osm'] = ['osm_map']
			lat = claims[0]["mainsnak"].datavalue["value"].latitude
			lon = claims[0]["mainsnak"].datavalue["value"].longitude
			zoom = user_zoom or 4
			thumburl = 'https:#maps["wikimedia"].org/img/osm-intl,' + zoom + ',' + lat + ',' + lon + ',' + thumb + 'x' + thumb + '.png'
			j.thumbnails['osm_map'] = {
				"thumburl": thumburl,
				"thumbwidth": thumb,
				"thumbwidth": thumb,
				"url": thumburl,
				"descriptionurl": 'https:#tools["wmflabs"].org/geohack/geohack.php?language=en&params=' + lat + '_N_' + lon + '_E_globe:earth'
			}

		if len(files) == 0:
			return

		url = "https://commons.wikimedia.org/w/api.php"
		params = {
			"action": 'query',
			"titles": files.join('|'),
			"prop": 'imageinfo',
			"iiprop": 'url',
			"iiurlwidth": thumb,
			"iiurlheight": thumb,
			"format": 'json'
		}
		d = self.wd.getJsonFromUrl(url, params)
		for v in d['query']['pages'].values():
			file = re.sub(r"^File:", "", v["title"])
			file = re.sub(r"_", " ", file)
			j.thumbnails[file] = v["imageinfo"][0]

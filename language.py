import re
from wikidata import *

# ________________________________________________________________________________________________________________________________________________________________
# BASE CLASS FOR LANGUAGE RENDERING
class LanguageRoot:

	def __init__(self, wd=None):
		self.wd = wd
		self.q = None
		self.main_title_label = None
		self.relations = None
		self.render_mode = None
		self.lang = None
		self.reasonator = None
		self.wd_auto_desc = None
		self.autodesc_short = None
		self.redlinks = None

	# INITIALISE
	def init(self):
		self.show_people_dates = False
		self.lang = self.getMainLang()
		if self.wd is None:
			self.wd = WikiData()
		self.h = {}
		self.wd.getItemBatch([self.getMainQ()])
		self.i = self.wd.items[self.getMainQ()]
		self.is_dead = self.i.hasClaims('P570')

	def getQlink(self, q, options):
		if options is None:
			options = {}
		if self.render_mode is not None:
			options["render_mode"] = self.render_mode
		if self.lang is not None:
			options["lang"] = self.lang
		if self.redlinks is not None:
			options["redlinks"] = self.redlinks
		return self.reasonator.getQlink(q, options)

	def getMainLang(self):
		return "en" if self.lang is None else self.lang

	def getMainQ(self):
		return self.wd.sanitizeQ(self.q)

	def getRelations(self):
		return self.reasonator.main_type_object["relations"] if self.relations is None else self.relations

	def getParent(self, p):
		rel = self.getRelations()
		if rel is None:
			return
		if "parents" not in rel:
			return
		if p not in rel["parents"]:
			return
		for k in rel["parents"][p].keys():
			return k

	def pad(self, a, b):
		return self.reasonator.pad(a, b)

	def getSelfURL(self, o):
		return self.reasonator.getSelfURL(o)

	def mainTitleLabel(self):
		return self.main_title_label

	def generateRelations(self):
		if self.reasonator["generateRelations"] is None:
			return
		self.relations = self.reasonator.generateRelations(self.getMainQ())

	def getNewline(self):
		if self.render_mode == 'text':
			return "\n"
		if self.render_mode == 'wiki':
			return "\n\n"
		return '<br/>'  # Default

	def getBold(self, o):
		if self.render_mode == 'text':
			o["after"] = ' ' + '' if o["after"] is None else o["after"]
		elif self.render_mode == 'wiki':
			o["before"] = ('' if o["after"] is None else o["before"]) + "'''"
			o["after"] = "''' " + '' if o["after"] is None else o["after"]
		else:  # Default
			o["before"] = ('' if o["after"] is None else o["before"]) + '<b>'
			o["after"] = '</b> ' + '' if o["after"] is None else o["after"]
		return o

	def getNationalityFromCountry(self, country, claims, hints):
		if self.wd_auto_desc is not None:
			return self.wd_auto_desc.getNationalityFromCountry(country, claims, hints)  # Real self.reasonator
		if hints is None:
			hints = {}
		hints["lang"] = self.getMainLang()
		return self.autodesc_short["ad"].getNationalityFromCountry(country, claims, hints)

	def setup(self):
		pass  # For child classes to implement

	def addFirstSentence(self):
		pass  # For child classes to implement

	def addBirthText(self):
		pass  # For child classes to implement

	def addDeathText(self):
		pass  # For child classes to implement

	def run_person(self):
		self.setup()
		self.generateRelations()
		self.addFirstSentence()
		self.addBirthText()
		self.addWorkText()
		self.addFamilyText()
		self.addDeathText()
		self.renderHTML()

	def renderDate(self, claim, o):

		if o is None:
			o = {}
		ret = {"after": ' '}

		# 		var d = (claim.time===undefined) ? (claim.datavalue===undefined?this.i.getClaimDate(claim):claim.datavalue.value) : claim ;
		if "time" not in claim:
			d = claim["datavalue"].value if "datavalue" in claim else self.i.getClaimDate(claim)
		else:
			d = claim

		if d is None:
			return '???'

		pre = 1 if d["time"].substr(0, 1) == '+' else -1
		dp = re.split(r"[-T:Z]", d["time"][1:])
		year = dp[0] * 1
		month = self.pad(dp[1], 2)
		day = self.pad(dp[2], 2)

		trans = self.renderDateByPrecision(pre, year, month, day, d.precision, o["no_prefix"])
		ret["label"] = trans.label
		ret["before"] = trans.before

		if o["just_year"]:
			return {"label": year}

		iso = d.time  # Fallback
		label = d.time  # Fallback

		ret["url"] = self.getSelfURL({"date": trans["iso"]})

		return ret

	def addPerson(self, pq, after):
		self.h.append({"q": pq})
		born = self.wd.items[pq]["raw"].claims['P569']
		died = self.wd.items[pq]["raw"].claims['P570']
		if self.show_people_dates and (born is not None or died is not None):
			self.h.append({"label": ' ('})
			if born is not None:
				self.h.append(self.renderDate(born[0], {"just_year": True}))
			if born is not None and died is not None:
				self.h.append({"label": '&ndash;'})
			if died is not None:
				self.h.append(self.renderDate(died[0], {"just_year": True}))

			self.h.append({"label": ')'})
		if after is not None and after != '':
			self.h.append({"label": after})

	def addPlace(self, o):
		if "before" in o:
			self.h.append({"label": o["before"]})
		self.h.append({"q": o["q"]})  # TODO country, city etc.
		if "after" in o:
			self.h.append({"label": o["after"]})

	def getSepAfter(self, arr, pos):
		if pos + 1 == arr["length"]:
			return ' '
		if pos == 0 and arr["length"] == 2:
			return ' and '
		if arr["length"] == pos + 2:
			return ', and '
		return ', '

	def getQualifierItem(self, qualifiers, prop):
		if qualifiers[prop] is None:
			return
		if qualifiers[prop][0].datavalue is None:
			return
		if qualifiers[prop][0].datavalue["value"] is None:
			return
		return 'Q' + qualifiers[prop][0]["datavalue"].value['numeric-id']

	def getDatesFromQualifier(self, qualifiers):
		ret = {}
		if qualifiers is None:
			return ret
		if "P581" in qualifiers:
			ret["from"] = qualifiers["P581"][0]
			ret["to"] = qualifiers["P581"][0]
			ret["pit"] = True  # Point In Time
		else:
			if "P580" in qualifiers:
				ret["from"] = qualifiers["P580"][0]
			if "P582" in qualifiers:
				ret["to"] = qualifiers["P582"][0]
		return ret

	@staticmethod
	def sortByDate(element):
		if "from" in element["dates"]:
			return "F:" + element["dates"]["from"]["time"]
		if "to" in element["dates"]:
			return "T:" + element["dates"]["to"]["time"]
		return ""

	"""
		def sortByDate(self, x ):
			return x.sort ( function ( a , b ) {
				if "from" in a.dates and "from" in b.dates:
					if a["dates"]["from"]["time"] == b["dates"]["from"]["time"]:
						return 0
					else:
						( a["dates"].from["time"] < b["dates"].from["time"] ? -1 : 1 )
				elif a.dates["to"] is not None and b.dates["to"] is not None :
					return a["dates"].to["time"] == b["dates"].to["time"] ? 0 : ( a["dates"].to["time"] < b["dates"].to["time"] ? -1 : 1 )
	
				return 0 if a.q == b.q else ( -1 if a.q < b.q else 1 )
	"""

	def getRelatedItemsWithQualifiers(self, o):
		if o is None:
			o = {}
		ret = []
		props = [] if o["properties"] is None else o["properties"]
		for prop in props:
			claims = [] if self.i.raw.claims[prop] is None else self.i.raw["claims"][prop]
			for claim in claims:
				eq = self.i.getClaimTargetItemID(claim)
				if eq is None:
					continue
				em = {"q": eq}
				if o["dates"]:
					em["dates"] = self.getDatesFromQualifier(claim.qualifiers)

				qualifiers = o["qualifiers"] if "qualifiers" in o else {}
				for (k, v) in qualifiers.items():
					tmp = []
					for prop2 in v:
						if claim["qualifiers"] is None:
							continue
						tmp = tmp.concat(self.getQualifierItem(claim["qualifiers"], prop2))
					em[k] = tmp
				ret.append(em)

		if o["sort"] == 'date':
			ret.sort(key=self.sortByDate)
		# ret = self.sortByDate ( ret )

		return ret

	def getRelationsList(self, k1, props, use_birth_death):
		ret = []
		for prop in props:
			relations = self.getRelations()
			if k1 not in relations:
				continue
			if prop not in relations[k1]:
				continue
			for (q2, v) in relations[k1][prop].items():
				for v2 in v:
					if self.wd.items[q2] is None:
						continue
					sp = {"q": q2, "dates": {}}
					if use_birth_death:
						if self.wd.items[q2].hasClaims('P569'):
							sp["dates"]["from"] = self.wd.items[q2].getClaimDate(
								self.wd.items[q2]["raw"].claims['P569'][0])
						if self.wd.items[q2].hasClaims('P570'):
							sp["dates"]["to"] = self.wd.items[q2].getClaimDate(
								self.wd.items[q2]["raw"].claims['P570'][0])
					else:
						sp["dates"] = self.getDatesFromQualifier(v2["qualifiers"])
					ret.append(sp)
		ret.sort(key=self.sortByDate)
		# ret = self.sortByDate ( ret )
		return ret

	def listNationalities(self):
		countries = self.i.raw.claims['P27']
		ctmp = [] if countries is None else countries
		for (k, claim) in ctmp.items():
			country = self.i.getClaimTargetItemID(claim)
			if country is None:
				continue
			country_name = self.wd.items[country].getLabel(self.lang)
			not_last = k + 1 != countries.length
			s = self.getNationalityFromCountry(country_name, self.wd.items[self.getMainQ()].raw["claims"],
											   {"not_last": not_last})
			self.h.append({"label": s, "q": country, "after": ('-' if not_last else ' ')})

	def listOccupations(self):
		occupations = self.i.raw.claims['P106']
		occupation_claims = [] if occupations is None else occupations
		for (k, claim) in occupation_claims.items():
			occupation = self.i.getClaimTargetItemID(claim)
			if occupation is None:
				continue
			not_last = k + 1 != occupations.length
			self.h.append({"q": occupation, "after": self.getSepAfter(occupations, k)})

	def simpleList(self, d, start, end):
		self.listSentence({
			"data": d,
			"start": lambda lst: lst[0].h.push({"label": start}),
			"item_start": lambda lst: (lst[1](), lst[0].h.append({"label": ' '})),
			"item_end": lambda lst: lst[0].h.push({"label": lst[2]}),
			"end": lambda lst: lst[0].h.push({"label": end})
		})

	"""
	start:self
	item_start:self,callback
	item_start:self,num,sep
	date_from:self,callback
	date_to:self,callback
	start:end
	"""

	# TODO actually call subroutines
	def listSentence(self, o):
		if o["data"] is None:
			o["data"] = []
		if o["data"]["length"] == 0:
			return
		# if o["start"] ) o["start"](: # TODO

		for (k, v) in o["data"].items():
			# if undefined !== o["item"]_start ) o["item"]_start ( function(){ self.h.push ( { "q":v["q"] })} :

			dates = v["dates"]
			show_date = False
			# $.each ( [] if o["qualifiers"] is None else o["qualifiers"] , function ( qual , cb ) { "if" ( v[qual] is not None ) show_date = True } )
			if dates is not None and (dates["from"] is not None or dates["to"] is not None):
				show_date = True
			if show_date:
				# if undefined !== o["date"]_start ) o["date"]_start(: #TODO

				# if dates["from"] is not None and undefined !== o["date"]_from ) o["date"]_from ( function(o2){ self.h.push ( self.renderDate ( dates["from"] , o2 ) )} :

				# if dates["to"] is not None and undefined !== o["date"]_to ) o["date"]_to ( function(o2){ self.h.push ( self.renderDate ( dates["to"] , o2 ) )} :

				qualifiers = [] if o["qualifiers"] is None else o["qualifiers"]
				for (qual, cb) in qualifiers.items():
					if v[qual] is None:
						continue
					if v[qual].length == 0:
						continue
					if v[qual][0] is None:
						continue
					cb(v[qual])
			# if undefined !== o["date"]_end ) o["date"]_end(:

			sep = self.getSepAfter(o["data"], k)

	# if undefined !== o["item"]_end ) o["item"]_end ( k , "sep" :

	# if undefined !== o["end"] ) o["end"](: #TODO

	def addWorkText(self):
		alma = self.getRelatedItemsWithQualifiers({"dates": True, "sort": 'date', "properties": ['P69']})
		field = self.getRelatedItemsWithQualifiers({"properties": ['P136', 'P101']})
		position = self.getRelatedItemsWithQualifiers(
			{"dates": True, "sort": 'date', "properties": ['P39'], "qualifiers": {'of': ['P642']}})
		member = self.getRelatedItemsWithQualifiers({"dates": True, "sort": 'date', "properties": ['P463']})
		employers = self.getRelatedItemsWithQualifiers(
			{"dates": True, "sort": 'date', "properties": ['P108'], "qualifiers": {'job': ['P794']}})
		self.alma(alma)
		self.field(field)
		self.position(position)
		self.member(member)
		self.employers(employers)
		self.h.append({"label": self.getNewline()})

	def addFamilyText(self):
		spouses = self.getRelationsList('other', [26], False)
		children = self.getRelationsList('children', [40], True)
		self.spouses(spouses)
		self.children(children)
		self.h.append({"label": self.getNewline()})

	def renderHTML(self) -> str:
		qs = []
		for v in self.h:
			if "q" in v:
				qs.append(v["q"])
		self.wd.getItemBatch(qs)
		h2 = ''

		for v in self.h:
			if v is None:
				continue  # Paranoia
			main = v["label"]
			if main is None:
				if v["q"] not in self.wd.items:
					main = v["q"]
				else:
					main = self.wd.items[v["q"]].getLabel(self.lang)
			if "url" in v:
				main = "<a href='" + v["url"] + "'>" + main + "</a>"
			else:
				if "q" in v["q"]:
					main = self.getQlink(v["q"], {"label": v["label"]})
			h2 += '' if v["before"] is None else v["before"]
			h2 += main
			h2 += '' if v["after"] is None else v["after"]

		h2 = re.sub(r" +", ' ', h2)  # Excessive spaces
		h2 = re.sub(r" \n", '\n', h2)  # Space before newline
		h2 = re.sub(r"\s\.", '.', h2)  # Space before punctuation
		h2 = re.sub(r"\s,", ',', h2)  # Space before punctuation
		h2 = re.sub(r"\.+", '.', h2)  # Multiple end dots
		h2 = re.sub(r"(<br/>\s*)+", '<br/>\n', h2)  # Multiple new lines
		return h2

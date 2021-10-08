import re
import urllib
import json


class WikiDataItem:
	# Constructor
	def __init__(self, init_wd, init_raw):
		self.wd = init_wd
		self.raw = init_raw
		self.placeholder = init_raw is None

	# Methods
	def isPlaceholder(self):
		return self.placeholder

	def isItem(self):
		return False if self.raw is None else self.raw.ns == 0

	def isProperty(self):
		return False if self.raw is None else self.raw.ns == 128

	def getID(self):
		if self.raw is not None:
			return self.raw.id

	def getURL(self):
		return "" if self.raw is None else f"https://www.wikidata.org/wiki/{self.raw.title}"

	def getPropertyList(self):
		return [] if self.raw.claims is None else self.raw.claims.keys()

	def getLink(self, o):
		if o is None:
			o = {}
		h = "<a "
		for v in ["target", "class"]:
			if v in o:
				h += f"{v}='{o[v]}' "

		url = self.getURL()

		if o["add_q"]:
			h += "q="" + self.raw.title + "" "
		if o["desc"] is not None:
			h += "title="" + self.getDesc() + "" "
		else:
			h += f"title='{self.raw.title}' "
		h += f"href='{url}'>"
		if "title" in o:
			h += o["title"]
		else:
			if o["ucfirst"]:
				h += self.getLabel().upper()
			else:
				h += self.getLabel()
		h += "</a>"
		return h

	def getAliases(self, include_labels):
		aliases = {}
		raw_aliases = {} if self.raw["aliases"] is None else self.raw["aliases"]
		for (lang, v1) in raw_aliases.items():
			for v2 in v1.values():
				aliases[v2.value] = 1

		if include_labels:
			raw_labels = {} if self.raw.labels is None else self.raw.labels
			for (lang, v1) in raw_labels.items():
				aliases[v1["value"]] = 1

		return list(aliases.keys())

	def getAliasesForLanguage(self, lang, include_labels):
		aliases = {}
		raw_aliases = self.raw["aliases"] if "aliases" in self.raw else {}
		v1 = raw_aliases[lang] if lang in raw_aliases else {}
		for v2 in v1.values():
			aliases[v2.value] = 1

		if include_labels:
			raw_labels = self.raw["labels"] if "labels" in self.raw else {}
			v1 = raw_labels[lang] if lang in raw_labels else {}
			if v1 is not None:
				aliases[v1["value"]] = 1

		return aliases.keys()

	def getStringsForProperty(self, p):
		return self.getMultimediaFilesForProperty(p)

	def getMultimediaFilesForProperty(self, p):
		ret = []
		claims = self.getClaimsForProperty(p)
		for (dummy, c) in claims.items():
			s = self.getClaimTargetString(c)
			if s is not None:
				ret.append(s)
		return ret

	def getClaimsForProperty(self, p):
		p = self.wd.convertToStringArray(p, "P")[0]
		if self.raw is None or self.raw.claims is None:
			return []
		ret = self.raw["claims"][self.wd.getUnifiedID(p)]
		return [] if ret is None else ret

	def hasClaims(self, p):
		return len(self.getClaimsForProperty(p)) > 0

	def getClaimLabelsForProperty(self, p):
		ret = []
		claims = self.getClaimsForProperty(p)
		for c in claims.values():
			q = self.getClaimTargetItemID(c)
			if q is None or self.wd.items[q] is None:
				continue
			ret.append(self.wd.items[q].getLabel())
		return ret

	def getClaimItemsForProperty(self, p, return_all):
		ret = []
		claims = self.getClaimsForProperty(p)
		for c in claims.values():
			q = self.getClaimTargetItemID(c)
			if q is None:
				continue
			if q in self.wd.items and not return_all:
				continue
			ret.append(q)
		return ret

	def getSnakObject(self, s):
		o = {}
		if s is None:
			return o

		if s["datavalue"] is not None:
			if s["datavalue"]["type"] == "wikibase-entityid":
				o["type"] = "item"
				o["q"] = "Q" + s["datavalue"]["value"]["numeric-id"]
				o["key"] = o["q"]
			elif s["datavalue"]["type"] == "string":
				o["type"] = "string"
				o["s"] = s["datavalue"]["value"]
				o["key"] = o["s"]
			elif s["datavalue"]["type"] == "time":
				o["type"] = "time"
				o.update(s["datavalue"]["value"])
				o["key"] = o["time"]  # TODO FIXME
			elif s["datavalue"]["type"] == "globecoordinate":
				o["type"] = "globecoordinate"
				o.update(s["datavalue"]["value"])
				o["key"] = o["latitude"] + "/" + o["longitude"]  # TODO FIXME
			elif s["datavalue"]["type"] == "quantity":
				o["type"] = "quantity"
				o.update(s["datavalue"]["value"])
				o["key"] = o["amount"]  # TODO FIXME
			elif s["datavalue"]["type"] == "monolingualtext":
				o["type"] = "monolingualtext"
				o.update(s["datavalue"]["value"])

		return o

	def getClaimObjectsForProperty(self, p):
		ret = []
		claims = self.getClaimsForProperty(p)
		for c in claims.values():
			o = self.getSnakObject(c.mainsnak)
			if o["type"] is None:
				return
			o["rank"] = c.rank
			o["qualifiers"] = {}
			qualifiers = {} if c.qualifiers is None else c.qualifiers
			for (qp, qv) in qualifiers.items():
				o["qualifiers"][qp] = []
				for v in qv.values():
					o["qualifiers"][qp].append(self.getSnakObject(v))
			ret.append(o)
		return ret

	def getDesc(self, language):
		desc = ""
		if language is None:
			for lang in self.wd.main_languages:
				l = self.getDesc(lang)
				if l == desc:
					continue
				desc = l
				break
		else:
			if self.raw is not None and "descriptions" in self.raw:
				if language in self.raw["descriptions"] and "value" in self.raw["descriptions"][language]:
					desc = self.raw["descriptions"][language]["value"]
		return desc

	def getLabelDefaultLanguage(self):
		default_label = self.getID()  # Fallback
		ret = ""
		for lang in self.wd.main_languages:
			l = self.getLabel(lang)
			if l == default_label:
				return
			ret = lang
			break
		return ret

	def getLabel(self, language):
		label = self.getID()  # Fallback
		if language is None:
			found = False
			for lang in self.wd.main_languages:
				l = self.getLabel(lang)
				if l == label:
					continue
				label = l
				found = True
				break

			# Fallback; pick first language
			if not found and self.raw is not None:
				labels = {} if "labels" not in self.raw else self.raw["labels"]
				for v in labels.values():
					label = v.value
					break
		else:
			if self.raw is not None and "labels" in self.raw:
				if language in self.raw["labels"] and "value" in self.raw["labels"][language]:
					label = self.raw["labels"][language]["value"]

		return label

	def getWikiLinks(self):
		if self.raw is None:
			return {}
		return {} if self.raw.sitelinks is None else self.raw.sitelinks

	def getClaimRank(self, claim):
		if claim is None:
			return
		return "normal" if claim.rank is None else claim.rank

	def getClaimTargetItemID(self, claim):
		if claim is None:
			return
		if "mainsnak" not in claim:
			return
		if "datavalue" not in claim["mainsnak"]:
			return
		if "value" not in claim["mainsnak"]["datavalue"]:
			return
		if claim["mainsnak"]["datavalue"]["value"]["entity-type"] != "item":
			return
		if "numeric-id" not in claim["mainsnak"]["datavalue"]["value"]:
			return
		return "Q" + claim["mainsnak"]["datavalue"]["value"]["numeric-id"]

	def getClaimTargetString(self, claim):
		return self.getClaimValueWithType(claim, "string")

	def getClaimDate(self, claim):
		return self.getClaimValueWithType(claim, "time")

	def getClaimValueWithType(self, claim, type):
		if claim is None:
			return
		if "mainsnak" not in claim:
			return
		if "datavalue" not in claim["mainsnak"]:
			return
		if "value" not in claim["mainsnak"]["datavalue"]:
			return
		if "type" not in claim["mainsnak"]["datavalue"]:
			return
		if claim["mainsnak"]["datavalue"]["type"] != type:
			return
		return claim["mainsnak"]["datavalue"]["value"]

	def hasClaimItemLink(self, p, q):
		q = self.wd.convertToStringArray(q, "Q")[0]
		claims = self.getClaimsForProperty(p)
		for c in claims.values():
			id = self.getClaimTargetItemID(c)
			if id is None or id != q:
				continue
			return True
		return False

	def followChain(self, o):
		id = self.getID()
		if self.wd is None:
			# console.log ( "ERROR : followChain for " + id + " has no wd object set!" )
			return

		if o["hadthat"] is None:
			o["hadthat"] = {}
			o["longest"] = []
			o["current"] = []
			o["props"] = self.wd.convertToStringArray(o["props"], "P")

		if o["hadthat"][id] is not None:
			return
		o["hadthat"][id] = 1
		o["current"]["append"](id)
		if o["current"]["length"] > o["longest"]["length"]:
			o["longest"] = {**o["current"]}

		tried_item = {}
		for p in o["props"].values():
			items = self.getClaimItemsForProperty(p)
			for q in items.values():
				if q in o["current"]:
					continue  # Already on that:
				if tried_item[q]:
					continue  # Only once my dear
				tried_item[q] = True
				self.wd.getItem(q).followChain(o)

		del o["hadthat"][self.getID()]
		o["current"]["pop"]()
		if o["current"]["length"] == 0:
			return o["longest"]


class WikiData:
	# Constructor
	def __init__(self):
		self.restrict_to_langs = None
		self.api = "https://www.wikidata.org/w/api.php?callback=?"
		self.max_get_entities = 50
		self.max_get_entities_smaller = 25
		self.language = "en"  # Default
		self.main_languages = ["en", "de", "fr", "nl", "es", "it", "pl", "pt", "ja", "ru", "hu", "sv", "fi", "da", "cs",
							   "sk", "et", "tr"]
		self.items = {}
		self.default_props = "info|aliases|labels|descriptions|claims|sitelinks|datatype"

	# Methods
	def clear(self):
		self.items = {}

	def countItemsLoaded(self):
		ret = 0
		for v in self.items.values():
			if not v.isPlaceholder() and v.isItem():
				ret += 1
		return ret

	def getUnifiedID(self, name, type=None):
		ret = re.sub(r"\s", "", str(name)).upper()
		if ret.isnumeric() and type is not None:
			ret = type.upper() + ret
		return ret

	def getItem(self, q):
		return self.items[self.getUnifiedID(q)]

	def convertToStringArray(self, o, type):
		ret = []
		if o is None:
			return ret
		if type(o) is dict:
			for v in o.values:
				ret.append(self.getUnifiedID(v, type))
		elif type(o) is list:
			for v in o:
				ret.append(self.getUnifiedID(v, type))
		else:
			ret = [self.getUnifiedID(o, type)]
		return ret

	def getLinksForItems(self, ql, o, fallback):
		if fallback is None:
			fallback = ""
		a = []
		sar = self.convertToStringArray(ql, "Q")
		for q in sar:
			if self.items[q] is None:
				continue
			a.append(self.items[q].getLink(o))

		if len(a) == 0:
			return fallback
		return "; ".join(a)

	def getItemBatch(self, item_list, props=None):
		if props is None:
			props = self.default_props
		ids = [[]]

		# Batch item lists
		max_per_batch = self.max_get_entities
		hadthat = {}
		for q in item_list:
			q = str(q)
			if q.numeric():
				q = "Q" + q
			if q in self.items or q in hadthat:
				continue  # Have that one
			hadthat[q] = 1
			if len(ids[len(ids) - 1]) >= max_per_batch:
				ids.append([])
			ids[len(ids) - 1].append(q)

		if len(ids[0]) == 0:
			return ids

		if len(ids) > 1:
			last = len(ids) - 1
			while len(ids[last]) + last <= max_per_batch and len(ids[last]) + last <= len(ids[0]):
				for i in range(last):
					ids[last].append(ids[i].pop())

		for id_list in ids:
			api_params = {
				"action": "wbgetentities",
				"ids": "|".join(id_list),
				"props": props,
				"format": "json"
			}

			data = self.getResponse(self.api, api_params)
			entities = data["entities"] if "entities" in data else {}
			for (k, v) in entities.items():
				q = self.getUnifiedID(k)
				self.items[q] = WikiDataItem(self, v)
		return ids

	def getResponse(self, url, params=None):
		open_url = urllib.request.urlopen(url, data=params)
		if open_url.getcode() == 200:
			data = open_url.read()
			json_data = json.loads(data)
		else:
			print("Error receiving data", open_url.getcode())
		return json_data

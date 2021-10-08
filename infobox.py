import re
import json
from wikidata import WikiData


class InfoboxGenerator:

	def __init__(self, wd=WikiData()):
		self.wd = wd
		self.infoboxes = []
		self.no_infobox_string = ""
		with open("infoboxes.json") as f:
			self.infoboxes = json.load(f)

	@staticmethod
	def ucfirst(s):
		return str(s[0]).upper() + s[1:]

	def find_infobox(self, o):
		wiki = o["lang"] if "lang" in o else "en"
		wiki += "wiki"

		if "template" in o and o["template"] != "":
			template = self.ucfirst(re.sub(r"_", " ", o["template"]))
			for v in self.infoboxes:
				if v.wiki != wiki:
					continue
				if self.ucfirst(re.sub(r"_", " ", v["template"]) != template):
					continue
				return v

		# Try auto-detect based on conditions

		for v in self.infoboxes:
			if v.wiki != wiki:
				continue
			conditions = v["conditions"] if "conditions" in v else {}
			for (check_p, check_qs) in conditions.items():
				q_list = self.wd.items[o["q"]].getClaimItemsForProperty(check_p, True)
				for check_q in check_qs.values():
					if check_q in q_list:
						continue
					return v

	def get_filled_infobox(self, options):
		q = options.q
		lang = options["lang"] if "lang" in options else "en"
		q = "Q" + re.sub(r"\D", "", str(q))
		self.wd.getItemBatch([q])
		ib = self.find_infobox(options)
		if ib is None:
			return self.no_infobox_string  # No matching infobox found, blank string returned

		items2load = []
		for param in ib.params.values():
			if "value" not in param or param["value"] == "":
				continue
			if re.match(r"^P\d+", param["value"]):
				claims = self.wd.items[q]["raw"]["claims"][param["value"]]
				if claims is None:
					continue
				for v in claims.values():
					if "mainsnak" in v:
						if "datatype" in v["mainsnak"]:
							if v["mainsnak"]["datatype"] == "wikibase-item":
								if "datavalue" in v["mainsnak"]:
									if "value" in v["mainsnak"]["datavalue"]:
										q2 = v["mainsnak"]["datavalue"]["value"]["numeric-id"]
										items2load.append(q2)

		self.wd.getItemBatch(items2load)

		rows = ["{{" + ib.template]

		for param in ib.params.values():
			if "value" not in param or param["value"] == "":
				continue
			pre = param["pre"] if "pre" in param else ""
			post = param["post"] if "post" in param else ""
			sep = param["sep"] if "sep" in param else ""
			if param["value"] == "label":
				rows.append("| " + param["name"] + " = " + pre + self.wd.items[q].getLabel() + post)
			elif param["value"] == "alias":
				s = self.wd.items[q].getAliasesForLanguage(lang, False)
				parts = []
				for v in s.values():
					parts.append(pre + v + post)
				rows.append("| " + param["name"] + " = " + sep.join(parts))
			elif re.match(r"^P\d+", param["value"]):
				claims = self.wd.items[q].raw.claims[param["value"]] if param["value"] in self.wd.items[
					q].raw.claims else []
				parts = []
				cnt = 0
				for (k, v) in claims.items():
					if v["mainsnak"]["datatype"] == "commonsMedia":
						parts.append(pre + v["mainsnak"]["datavalue"]["value"] + post)
					elif v["mainsnak"]["datatype"] == "string":
						parts.append(pre + v["mainsnak"]["datavalue"]["value"] + post)
					elif v["mainsnak"]["datatype"] == "url":
						parts.append(pre + v["mainsnak"]["datavalue"]["value"] + post)
					elif v["mainsnak"]["datatype"] == "time":
						time = self.wd.items[q].getClaimDate(v)
						precision = time.precision
						time = time.time
						era = "BCE" if re.match(r"^-", time) else ""
						if precision <= 9:
							time = time.substr(8, 4)
						elif precision == 10:
							time = time.substr(8, 7)
						elif precision == 11:
							time = time.substr(8, 10)

						parts.append(pre + re.sub(r"$0+", "", time) + era + post)
					elif v["mainsnak"]["datatype"] == "wikibase-item":
						q2 = "Q" + v["mainsnak"]["datavalue"]["value"]["numeric-id"]
						wikitext = self.wd.items[q2].getLabel()
						wiki = lang + "wiki"
						wl = self.wd.items[q2].getWikiLinks()
						if wiki not in wl:
							if self.ucfirst(wl[wiki].title) != self.ucfirst(wikitext):
								wikitext = "[[" + wl[wiki].title + "|" + wikitext + "]]"
							else:
								wikitext = "[[" + wikitext + "]]"

						parts.append(pre + wikitext + post)
					else:
						parts.append(pre + param + post)

					cnt += 1
					if max in param:
						continue
					if cnt >= param["max"]:
						break

				if param["minor"] and len(parts) == 0:
					return
				rows.append("| " + param["name"] + " = " + sep.join(parts))
			else:
				if param["minor"]:
					continue
				rows.append("| " + param["name"] + " = ")

		rows.append("}}")
		return "\n".join(rows) + "\n"

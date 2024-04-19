import json
import re

from wikidata import WikiData


class InfoboxGenerator:

    def __init__(self, wd=None):
        self.wd = wd if wd is not None else WikiData()
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

        if "template" in o and o["infobox_template"] != "":
            template = self.ucfirst(re.sub(r"_", " ", o["infobox_template"]))
            for v in self.infoboxes:
                if v["wiki"] != wiki:
                    continue
                if self.ucfirst(re.sub(r"_", " ", v["infobox_template"]) != template):
                    continue
                return v

        # Try auto-detect based on conditions

        for v in self.infoboxes:
            if v["wiki"] != wiki:
                continue
            conditions = v["conditions"] if "conditions" in v else {}
            for check_p, check_qs in conditions.items():
                q_list = self.wd.items[o["q"]].getClaimItemsForProperty(check_p, True)
                for check_q in check_qs:
                    if check_q not in q_list:
                        continue
                    return v

    def get_filled_infobox(self, options):
        q = options["q"]
        lang = options["lang"] if "lang" in options else "en"
        q = self.wd.sanitizeQ(q)
        self.wd.getItemBatch([q])
        item = self.wd.getItem(q)
        if item is None:
            return ""
        ib = self.find_infobox(options)
        if ib is None:
            return (
                self.no_infobox_string
            )  # No matching infobox found, blank string returned

        items2load = []
        for param in ib["params"]:
            if "value" not in param or param["value"] == "":
                continue
            if re.match(r"^P\d+", param["value"]):
                if param["value"] not in item.raw["claims"]:
                    continue
                claims = item.raw["claims"][param["value"]]
                if claims is None:
                    continue
                for v in claims:
                    if "mainsnak" in v:
                        if "datatype" in v["mainsnak"]:
                            if v["mainsnak"]["datatype"] == "wikibase-item":
                                if "datavalue" in v["mainsnak"]:
                                    if "value" in v["mainsnak"]["datavalue"]:
                                        q2 = str(
                                            v["mainsnak"]["datavalue"]["value"][
                                                "numeric-id"
                                            ]
                                        )
                                        items2load.append(str(q2))

        self.wd.getItemBatch(items2load)

        rows = ["{{" + ib["template"]]

        for param in ib["params"]:
            if "value" not in param or param["value"] == "":
                continue
            pre = param["pre"] if "pre" in param else ""
            post = param["post"] if "post" in param else ""
            sep = param["sep"] if "sep" in param else ", "
            if param["value"] == "label":
                rows.append("| " + param["name"] + " = " + pre + item.getLabel() + post)
            elif param["value"] == "alias":
                s = item.getAliasesForLanguage(lang, False)
                parts = []
                for v in s:
                    parts.append(pre + v + post)
                rows.append("| " + param["name"] + " = " + sep.join(parts))
            elif re.match(r"^P\d+", param["value"]):
                claims = (
                    item.raw["claims"][param["value"]]
                    if param["value"] in self.wd.items[q].raw["claims"]
                    else []
                )
                parts = []
                cnt = 0
                for v in claims:
                    if v["mainsnak"]["datatype"] == "commonsMedia":
                        parts.append(pre + v["mainsnak"]["datavalue"]["value"] + post)
                    elif v["mainsnak"]["datatype"] == "string":
                        parts.append(pre + v["mainsnak"]["datavalue"]["value"] + post)
                    elif v["mainsnak"]["datatype"] == "url":
                        parts.append(pre + v["mainsnak"]["datavalue"]["value"] + post)
                    elif v["mainsnak"]["datatype"] == "time":
                        time_object = item.getClaimDate(v)
                        precision = time_object["precision"]
                        time = time_object["time"]
                        era = "BCE" if re.match(r"^-", time) else ""
                        if precision <= 9:
                            time = time[8 : 8 + 4]
                        elif precision == 10:
                            time = time[8 : 8 + 7]
                        elif precision == 11:
                            time = time[8 : 8 + 10]

                        parts.append(pre + re.sub(r"$0+", "", time) + era + post)
                    elif v["mainsnak"]["datatype"] == "wikibase-item":
                        q2 = "Q" + str(
                            v["mainsnak"]["datavalue"]["value"]["numeric-id"]
                        )
                        wikitext = self.wd.items[q2].getLabel()
                        wiki = lang + "wiki"
                        wl = self.wd.items[q2].getWikiLinks()
                        if wiki in wl:
                            if self.ucfirst(wl[wiki]["title"]) != self.ucfirst(
                                wikitext
                            ):
                                wikitext = (
                                    "[[" + wl[wiki]["title"] + "|" + wikitext + "]]"
                                )
                            else:
                                wikitext = "[[" + wikitext + "]]"

                        parts.append(pre + wikitext + post)
                    else:
                        parts.append(pre + param + post)

                    cnt += 1
                    if "max" not in param:
                        continue
                    if cnt >= param["max"]:
                        break

                if "minor" in param and param["minor"] and len(parts) == 0:
                    continue
                rows.append("| " + param["name"] + " = " + sep.join(parts))
            else:
                if "minor" in param and param["minor"]:
                    continue
                rows.append("| " + param["name"] + " = ")

        rows.append("}}")
        return "\n".join(rows) + "\n"

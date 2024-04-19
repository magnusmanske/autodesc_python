from language import LanguageRoot

# ________________________________________________________________________________________________________________________________________________________________


# FRENCH
class LanguageClassFr(LanguageRoot):

    def setup(self):
        self.init()
        self.month_label = [
            "",
            "janvier",
            "fÃ©vrier",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "aoÃ»t",
            "septembre",
            "octobre",
            "novembre",
            "dÃ©cembre",
        ]  # First one needs to be empty!!
        self.i.s_male = not self.i.hasClaimItemLink("P21", "Q6581072")
        self.s_he = "Il" if self.i.s_male else "Elle"
        self.h["is_er"] = "Son"

    def getSepAfter(self, arr, pos):
        if pos + 1 == arr["length"]:
            return " "
        if pos == 0 and arr["length"] == 2:
            return " et "  # 2 items
        if arr["length"] == pos + 2:
            return " et "  # 3+ items
        return ", "

    def renderDateByPrecision(self, pre, year, month, day, precision, jusque):
        ret = {}
        if precision <= 9:
            ret["iso"] = year * pre
            ret["label"] = year
            ret["before"] = "en "
            if jusque:
                ret["before"] = "jusqu'en "
        elif precision == 10:
            ret["iso"] = year * pre + "-" + month
            ret["label"] = self.month_label[month * 1] + " " + year
            ret["before"] = "en "
            if jusque:
                ret["before"] = "jusqu'en "
        elif precision == 11:
            ret["iso"] = year * pre + "-" + month + "-" + day
            ret["label"] = (day * 1) + " " + self.month_label[month * 1] + " " + year
            ret["before"] = "le "
            if jusque:
                ret["before"] = "jusqu'au "

        if pre == -1:
            ret["after"] = " <small>av. J.-C.</small>" + ret.after
        return ret

    def employers(self, d):
        self.listSentence(
            {
                "data": d,
                "start": lambda lst: lst[0].h.append(
                    {"label": lst[0].s_he + " a travaillÃ© pour "}
                ),
                "item_start": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_from": lambda lst: (
                    lst[0].h.append({"label": "depuis "}),
                    lst[1](),
                ),
                "date_to": lambda lst: (
                    lst[0].h.append({"label": "jusque "}),
                    lst[1]({"jusque": True}),
                ),
                # TODO FIXME "qualifiers" : { "job":function(qv){ self.h["append"] ( { "before":'en tant que ' , "q" :qv[0] , "after" :' ' } )} } ,
                "item_end": lambda lst: {
                    lst[0].h.append(
                        {"label": lst[2] + "pour " if lst[1] + 1 < d.length else ""}
                    )
                },
                "end": lambda lst: lst[0].h.append({"label": ". "}),
            }
        )

    def position(self, d):
        self.listSentence(
            {
                "data": d,
                "start": lambda lst: lst[0].h.append(
                    {
                        "label": (
                            lst[0].s_he + " Ã©tait" + ""
                            if self.i.s_dead
                            else "/est" + " "
                        )
                    }
                ),
                "item_start": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_from": lambda lst: (
                    lst[0].h.append({"label": "depuis "}),
                    lst[1](),
                ),
                "date_to": lambda lst: (
                    lst[0].h.append({"label": "jusque "}),
                    lst[1]({"jusque": True}),
                ),
                # TODO FIXME "qualifiers" : { "of":function(qv){ self.h["append"] ( { "before":'pour ' , "q" :qv[0] , "after" :' ' } )} } ,
                "item_end": lambda lst: {lst[0].h.append({"label": lst[2]})},
                "end": lambda lst: lst[0].h.append({"label": ". "}),
            }
        )

    def member(self, d):
        self.listSentence(
            {
                "data": d,
                "start": lambda lst: lst[0].h.append(
                    {
                        "label": (
                            lst[0].s_he + " Ã©tait" + ""
                            if self.i.s_dead
                            else "/est" + " membre de "
                        )
                    }
                ),
                "item_start": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_from": lambda lst: (
                    lst[0].h.append({"label": "depuis "}),
                    lst[1](),
                ),
                "date_to": lambda lst: (
                    lst[0].h.append({"label": "jusque "}),
                    lst[1]({"jusque": True}),
                ),
                # 					"qualifiers" : { "job":function(qv){ self.h["append"] ( { "before":'en tant que ' , "q" :qv[0] , "after" :' ' } )} } ,
                "item_end": lambda lst: {lst[0].h.append({"label": lst[2]})},
                "end": lambda lst: lst[0].h.append({"label": ". "}),
            }
        )

    def alma(self, d):
        self.listSentence(
            {
                "data": d,
                "start": lambda lst: lst[0].h.append(
                    {"label": lst[0].s_he + " a Ã©tudiÃ© Ã "}
                ),
                "item_start": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_from": lambda lst: (
                    lst[0].h.append({"label": "depuis "}),
                    lst[1](),
                ),
                "date_to": lambda lst: (
                    lst[0].h.append({"label": "jusque "}),
                    lst[1]({"jusque": True}),
                ),
                "item_end": lambda lst: {lst[0].h.append({"label": lst[2]})},
                "end": lambda lst: lst[0].h.append({"label": ". "}),
            }
        )

    def field(self, d):
        self.simpleList(
            d,
            (
                self.h["is_er"] + " domaine de travail " + "comprend"
                if self.i.s_dead
                else "comprenait" + " "
            ),
            ". ",
        )

    def cause_of_death(self, d):
        self.simpleList(d, "de ", " ")

    def killer(self, d):
        self.simpleList(d, "par ", " ")

    def sig_event(self, d):
        self.simpleList(d, self.s_he + " a jouÃ© un rÃ´le important dans ", ".")

    def spouses(self, d):
        self.listSentence(
            {
                "data": d,
                "start": lambda lst: lst[0].h.append(
                    {"label": lst[0].s_he + " a Ã©pousÃ© "}
                ),
                "item_start": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_from": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_to": lambda lst: (
                    lst[0].h.append({"label": "(mariÃ©s "}),
                    lst[1]({"jusque": True}),
                    self.h["append"]({"label": ")"}),
                ),
                "item_end": lambda lst: {lst[0].h.append({"label": lst[2]})},
                "end": lambda lst: lst[0].h.append({"label": ". "}),
            }
        )

    def children(self, d):
        self.listSentence(
            {
                "data": d,
                "start": lambda lst: lst[0].h.append(
                    {
                        "label": (
                            "Il est le pÃ¨re de "
                            if lst[0].i.s_male
                            else "Elle est la mÃ¨re de "
                        )
                    }
                ),
                "item_start": lambda lst: lst[1](),
                "item_end": lambda lst: {lst[0].h.append({"label": lst[2]})},
                "end": lambda lst: lst[0].h.append({"label": ". "}),
            }
        )

    def addFirstSentence(self):
        self.h["append"](self.getBold({"label": self.mainTitleLabel()}))
        self.h["append"](
            {
                "label": "Ã©tait" if self.i.s_dead else "est",
                "after": " un " if self.i.s_male else " une ",
            }
        )
        self.listOccupations()
        self.listNationalities()
        self.h["append"]({"label": ". "})
        if self.h["length"] == 3:
            self.h = []  # No information, skip it.
        sig_event = self.getRelatedItemsWithQualifiers({"properties": ["P793"]})
        self.sig_event(sig_event)
        self.h["append"]({"label": self.getNewline()})

    def addBirthText(self):
        birthdate = self.i.raw.claims["P569"]
        birthplace = self.i.raw.claims["P19"]
        birthname = self.i.raw.claims["P513"]
        if birthdate is not None or birthplace is not None or birthname is not None:
            self.h["append"](
                {
                    "label": self.s_he,
                    "after": " est nÃ© " if self.i.s_male else " est nÃ©e ",
                }
            )
            if birthname is not None:
                self.h["append"](
                    {
                        "label": self.i.getClaimTargetString(birthname[0]),
                        "before": "<i>",
                        "after": "</i> ",
                    }
                )
            if birthdate is not None:
                self.h["append"](self.renderDate(birthdate[0]))
            if birthplace is not None:
                self.addPlace(
                    {
                        "q": self.i.getClaimTargetItemID(birthplace[0]),
                        "before": "Ã ",
                        "after": " ",
                    }
                )
            father = self.getParent(22)
            mother = self.getParent(25)
            if father is not None or mother is not None:
                self.h["append"](
                    {
                        "label": (
                            ". Il est le fils de "
                            if self.i.s_male
                            else ". Elle est la fille de "
                        )
                    }
                )
                if father is not None:
                    self.addPerson(father, " ")
                if father is not None and mother is not None:
                    self.h["append"]({"label": "et "})
                if mother is not None:
                    self.addPerson(mother, " ")
            self.h["append"]({"label": ". "})
            self.h["append"]({"label": self.getNewline()})

    def addDeathText(self):
        deathdate = self.i.raw.claims["P570"]
        deathplace = self.i.raw.claims["P20"]
        deathcause = self.i.hasClaims("P509")
        killer = self.i.hasClaims("P157")
        if deathdate is not None or deathplace is not None or deathcause or killer:
            self.h["append"](
                {
                    "label": self.s_he,
                    "after": " est mort " if self.i.s_male else " est morte ",
                }
            )
            if deathcause is not None:
                self.cause_of_death(
                    self.getRelatedItemsWithQualifiers({"properties": ["P509"]})
                )
            if killer is not None:
                self.killer(
                    self.getRelatedItemsWithQualifiers({"properties": ["P157"]})
                )
            if deathdate is not None:
                self.h["append"](self.renderDate(deathdate[0]))
            if deathplace is not None:
                self.addPlace(
                    {
                        "q": self.i.getClaimTargetItemID(deathplace[0]),
                        "before": "Ã ",
                        "after": " ",
                    }
                )
            self.h["append"]({"label": ". "})

        burialplace = self.i.raw.claims["P119"]
        if burialplace is not None:
            self.addPlace(
                {
                    "q": self.i.getClaimTargetItemID(burialplace[0]),
                    "before": (
                        self.s_he + " fut inhumÃ© Ã "
                        if self.i.s_male
                        else " fut inhumÃ©e Ã "
                    ),
                    "after": ". ",
                }
            )

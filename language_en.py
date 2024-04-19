from language import LanguageRoot

# ________________________________________________________________________________________________________________________________________________________________


class LanguageClassEn(LanguageRoot):

    def setup(self):
        self.init()
        self.month_label = [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]  # First one needs to be empty!!
        self.i.s_male = not self.i.hasClaimItemLink("P21", "Q6581072")
        self.s_he = "He" if self.i.s_male else "She"
        self.h["is_er"] = "His" if self.i.s_male else "Her"

    def renderDateByPrecision(self, pre, year, month, day, precision, no_prefix):
        ret = {}
        if precision <= 9:
            ret["iso"] = year * pre
            ret["label"] = year
            if not no_prefix:
                ret["before"] = "in "
        elif precision == 10:
            ret["iso"] = year * pre + "-" + month
            ret["label"] = self.month_label[month * 1] + " " + year
            if not no_prefix:
                ret["before"] = "in "
        elif precision == 11:
            ret["iso"] = year * pre + "-" + month + "-" + day
            ret["label"] = self.month_label[month * 1] + " " + (day * 1) + ", " + year
            if not no_prefix:
                ret["before"] = "on "

        if pre == -1:
            ret["after"] = " <small>B[C].E.</small>" + ret.after
        return ret

    def employers(self, d):
        self.listSentence(
            {
                "data": d,
                "start": lambda lst: lst[0].h.append(
                    {"label": lst[0].s_he + " worked for "}
                ),
                "item_start": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_from": lambda lst: (
                    lst[0].h.append({"label": "from "}),
                    lst[1]({"no_prefix": True}),
                ),
                "date_to": lambda lst: (
                    lst[0].h.append({"label": "until "}),
                    lst[1]({"no_prefix": True}),
                ),
                # TODO FIXME "qualifiers" : { "job":function(qv){ self.h["append"] ( { "before":'as ' , "q" :qv[0] , "after" :' ' } )} } ,
                "item_end": lambda lst: {
                    lst[0].h.append(
                        {"label": lst[2] + "for " if lst[1] + 1 < d.length else ""}
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
                            lst[0].s_he + " was" + "" if self.i.s_dead else "/is" + " "
                        )
                    }
                ),
                "item_start": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_from": lambda lst: (
                    lst[0].h.append({"label": "from "}),
                    lst[1]({"no_prefix": True}),
                ),
                "date_to": lambda lst: (
                    lst[0].h.append({"label": "until "}),
                    lst[1]({"no_prefix": True}),
                ),
                # TODO FIXME "qualifiers" : { "of":function(qv){ self.h["append"] ( { "before":'for ' , "q" :qv[0] , "after" :' ' } )} } ,
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
                            lst[0].s_he + " was" + ""
                            if self.i.s_dead
                            else "/is" + " a member of "
                        )
                    }
                ),
                "item_start": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_from": lambda lst: (
                    lst[0].h.append({"label": "from "}),
                    lst[1]({"no_prefix": True}),
                ),
                "date_to": lambda lst: (
                    lst[0].h.append({"label": "until "}),
                    lst[1]({"no_prefix": True}),
                ),
                # 					"qualifiers" : { "job":function(qv){ self.h["append"] ( { "before":'as ' , "q" :qv[0] , "after" :' ' } )} } ,
                "item_end": lambda lst: {lst[0].h.append({"label": lst[2]})},
                "end": lambda lst: lst[0].h.append({"label": ". "}),
            }
        )

    def alma(self, d):
        self.listSentence(
            {
                "data": d,
                "start": lambda lst: lst[0].h.append(
                    {"label": lst[0].s_he + " studied at "}
                ),
                "item_start": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_from": lambda lst: (
                    lst[0].h.append({"label": "from "}),
                    lst[1]({"no_prefix": True}),
                ),
                "date_to": lambda lst: (
                    lst[0].h.append({"label": "until "}),
                    lst[1]({"no_prefix": True}),
                ),
                "item_end": lambda lst: {lst[0].h.append({"label": lst[2]})},
                "end": lambda lst: lst[0].h.append({"label": ". "}),
            }
        )

    def field(self, d):

        self.simpleList(
            d,
            (
                self.h["is_er"] + " field of work include" + "d"
                if self.i.s_dead
                else "s" + " "
            ),
            ". ",
        )

    def cause_of_death(self, d):
        self.simpleList(d, "of ", " ")

    def killer(self, d):
        self.simpleList(d, "by ", " ")

    def sig_event(self, d):
        self.simpleList(d, self.s_he + " played a role in ", ".")

    def spouses(self, d):
        self.listSentence(
            {
                "data": d,
                "start": lambda lst: lst[0].h.append(
                    {"label": lst[0].s_he + " married "}
                ),
                "item_start": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_from": lambda lst: (lst[1](), lst[0].h.append({"label": " "})),
                "date_to": lambda lst: (
                    lst[0].h.append({"label": "(married until "}),
                    lst[1](),
                    self.h["append"]({"label": ") "}),
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
                    {"label": lst[0].h.is_er + " children include "}
                ),
                "item_start": lambda lst: lst[1](),
                "item_end": lambda lst: {lst[0].h.append({"label": lst[2]})},
                "end": lambda lst: lst[0].h.append({"label": ". "}),
            }
        )

    def addFirstSentence(self):
        self.h["append"](self.getBold({"label": self.mainTitleLabel()}))
        self.h["append"]({"label": "was" if self.i.s_dead else "is", "after": " a "})
        self.listNationalities()
        self.listOccupations()
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
            self.h["append"]({"label": self.s_he, "after": " was born "})
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
                        "before": "in ",
                        "after": " ",
                    }
                )
            father = self.getParent(22)
            mother = self.getParent(25)
            if father is not None or mother is not None:
                self.h["append"]({"label": "to "})
                if father is not None:
                    self.addPerson(father, " ")
                if father is not None and mother is not None:
                    self.h["append"]({"label": "and "})
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
            self.h["append"]({"label": self.s_he, "after": " died "})
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
                        "before": "in ",
                        "after": " ",
                    }
                )
            self.h["append"]({"label": ". "})

        burialplace = self.i.raw.claims["P119"]
        if burialplace is not None:
            self.addPlace(
                {
                    "q": self.i.getClaimTargetItemID(burialplace[0]),
                    "before": self.s_he + " was buried at ",
                    "after": ". ",
                }
            )

from language_en import LanguageClassEn
from language_fr import LanguageClassFr
from language_nl import LanguageClassNl
from short_desc import ShortDescription


class LongDescription:
    def loadItem(self, q, params):
        language = "en" if "lang" not in params else params["lang"]

        if language == "en":
            ld = LanguageClassEn()
        elif params["lang"] == "nl":
            ld = LanguageClassNl()
        elif params["lang"] == "fr":
            ld = LanguageClassFr()
        else:
            return ShortDescription(q, params)
        ld.q = q
        ld.lang = params["lang"]
        ld.setup()
        html = ld.run_person()  # TODO which function?
        return html

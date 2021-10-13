from short_desc import ShortDescription
from language_en import *
from language_fr import *
from language_nl import *


class LongDescription:
	def loadItem(self, q, params):
		if "lang" not in params:
			params["lang"] = "en"

		if params["lang"] == "en":
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

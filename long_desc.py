from short_desc import ShortDescription
from languages import *

class LongDescription:
	def loadItem(self, q, props):
		if "lang" not in props:
			props["lang"] = "en"

		if props["lang"] == "en":
			ld = LanguageClassEn()
		elif props["lang"] == "nl":
			ld = LanguageClassNl()
		elif props["lang"] == "fr":
			ld = LanguageClassFr()
		else:
			return ShortDescription(q, props)
		return "So far so good..."


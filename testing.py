#!/usr/bin/env python3

from wikidata import WikiData
from short_desc import ShortDescription

def test_wikidata():
	q = "Q12345"
	wd = WikiData()
	wd.getItemBatch([q])
	i = wd.getItem(q)
	imdb = i.getStringsForProperty("P345")
	assert (imdb == ["ch0000709"])
	assert (i.hasClaimItemLink("P31", "Q30061417"))
	sitelinks = i.getWikiLinks()
	assert("dewiki" in sitelinks)
	assert(sitelinks["dewiki"]["title"]=="Graf Zahl")
	followers = i.getClaimObjectsForProperty("P8687")
	followers_2021 = list(filter(lambda f: f["qualifiers"]["P585"][0]["time"]=="+2021-01-04T00:00:00Z", followers))
	assert(followers_2021[0]["amount"]=="+149471")

def test_short_description():
	sd = ShortDescription()
	assert(sd.stock["produced by"]["de"]=="produziert von")

	desc = sd.loadItem("Q12345",{})
	assert(desc[1]=="<a href='https://www.wikidata.org/wiki/Q30061417'>vampire in a work of fiction</a> and <a href='https://www.wikidata.org/wiki/Q15773317'>television character</a> by <a href='https://www.wikidata.org/wiki/Q7052825'>Norman Stiles</a> from <a href='https://www.wikidata.org/wiki/Q155629'>Sesame Street</a>")

	desc = sd.loadItem("Q1035",{"lang":"de","links":"text"})
	assert(desc[1]=="Geologe, Forschungsreisender, Reiseschriftsteller, Verhaltensforscher, Entomologe, Botaniker, Karzinologe, Imker, Naturwissenschaftler und Philosoph ♂; Royal Medal, Copley Medal, Pour le Mérite für Wissenschaften und Künste, Pour le Mérite, Fellow of the Linnean Society of London, Fellow of the Royal Geographical Society, Fellow of the Royal Society, Baly Medal, Fellow of the Geological Society, Bressa Prize, Ehrendoktor der Universität Leiden und Wollaston-Medaille; Mitglied von Royal Society, Deutsche Akademie der Naturforscher Leopoldina, Königlich Schwedische Akademie der Wissenschaften, American Philosophical Society, Ungarische Akademie der Wissenschaften, Schlesische Gesellschaft für vaterländische Kultur, American Academy of Arts and Sciences, Königlich Niederländische Akademie der Wissenschaften, Accademia Nazionale dei Lincei, Zoological Society of London, Académie des sciences, Russische Akademie der Wissenschaften, Preußische Akademie der Wissenschaften, Royal Geographical Society, Bayerische Akademie der Wissenschaften und Accademia delle Scienze Turin; Kind von Robert Darwin und Susannah Darwin; verheiratet mit Emma Darwin")

	desc = sd.loadItem("Q4504",{"links":"wiki"})
	print (desc)

test_wikidata()
test_short_description()

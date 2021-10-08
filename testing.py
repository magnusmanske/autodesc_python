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
	print (desc)

#test_wikidata()
test_short_description()

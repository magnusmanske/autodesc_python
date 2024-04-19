#!/usr/bin/env python3

from infobox import InfoboxGenerator
from long_desc import LongDescription
from media import MediaGenerator
from short_desc import ShortDescription
from wikidata import WikiData


def test_wikidata():
    q = "Q12345"
    wd = WikiData()
    wd.getItemBatch([q])
    i = wd.getItem(q)
    imdb = i.getStringsForProperty("P345")
    assert imdb == ["ch0000709"]
    assert i.hasClaimItemLink("P31", "Q30061417")
    sitelinks = i.getWikiLinks()
    assert "dewiki" in sitelinks
    assert sitelinks["dewiki"]["title"] == "Graf Zahl"
    followers = i.getClaimObjectsForProperty("P8687")
    followers_2021 = list(
        filter(
            lambda f: f["qualifiers"]["P585"][0]["time"] == "+2021-01-04T00:00:00Z",
            followers,
        )
    )
    assert followers_2021[0]["amount"] == "+149471"


def test_short_description():
    sd = ShortDescription()
    assert sd.stock["produced by"]["de"] == "produziert von"

    sd = ShortDescription()
    desc = sd.loadItem("Q12345", {})
    assert (
        desc[1]
        == "<a href='https://www.wikidata.org/wiki/Q30061417'>vampire in a work of fiction</a> and <a href='https://www.wikidata.org/wiki/Q15773317'>television character</a> by <a href='https://www.wikidata.org/wiki/Q7052825'>Norman Stiles</a> from <a href='https://www.wikidata.org/wiki/Q155629'>Sesame Street</a>"
    )

    sd = ShortDescription()
    desc = sd.loadItem("Q1035", {"lang": "de", "links": "text"})
    assert (
        desc[1]
        == "Geologe, Forschungsreisender, Reiseschriftsteller, Verhaltensforscher, Entomologe, Botaniker, Karzinologe, Imker, Naturwissenschaftler und Philosoph (1809–1882) ♂; Royal Medal, Copley Medal, Pour le Mérite für Wissenschaften und Künste, Pour le Mérite, Fellow of the Linnean Society of London, Fellow of the Royal Geographical Society, Fellow of the Royal Society, Baly Medal, Fellow of the Geological Society, Bressa Prize, Ehrendoktor der Universität Leiden und Wollaston-Medaille; Mitglied von Royal Society, Deutsche Akademie der Naturforscher Leopoldina, Königlich Schwedische Akademie der Wissenschaften, American Philosophical Society, Ungarische Akademie der Wissenschaften, Schlesische Gesellschaft für vaterländische Kultur, American Academy of Arts and Sciences, Königlich Niederländische Akademie der Wissenschaften, Accademia Nazionale dei Lincei, Zoological Society of London, Académie des sciences, Russische Akademie der Wissenschaften, Preußische Akademie der Wissenschaften, Royal Geographical Society, Bayerische Akademie der Wissenschaften und Accademia delle Scienze Turin; Kind von Robert Darwin und Susannah Darwin; verheiratet mit Emma Darwin"
    )

    sd = ShortDescription()
    desc = sd.loadItem("Q4504", {"links": "wiki"})
    assert (
        desc[1]
        == "[[Species|species]], named after [[Komodo (island)|Komodo]] of [[Monitor lizard|Varanus]]"
    )


def test_infobox_generator():
    args = {"q": "Q311243", "lang": "en"}
    ig = InfoboxGenerator()
    infobox = ig.get_filled_infobox(args)
    assert (
        infobox
        == """{{Infobox artwork
| title = Traveler Over The Mist Sea
| image_file = Caspar David Friedrich - Wanderer above the sea of fog.jpg, Ueber-die-sammlung-19-jahrhundert-caspar-david-friedrich-wanderer-ueber-dem-nebelmeer.jpg
| artist = [[Caspar David Friedrich]]
| completion_date = -00T
| type = [[Landscape painting|landscape art]], [[figure painting]]
| material = [[oil paint]], canvas
| subject = [[strolling]]
| museum = [[Hamburger Kunsthalle|Kunsthalle Hamburg]]
| accession = 5161, 1847
}}
"""
    )


def test_long_description():
    ld = LongDescription()
    desc = ld.loadItem("Q80", {"lang": "en", "links": "text"})
    print(desc)


def test_media_generator():
    thumb = "80"
    mg = MediaGenerator()
    media = mg.generateMedia("Q0")
    assert media == {"thumbnails": {}}

    mg = MediaGenerator()
    media = mg.generateMedia("Q350", thumb)
    assert "image" in media
    assert "coat_of_arms" in media
    assert "banner" in media
    assert "osm_map" in media["thumbnails"]


# test_wikidata()
# test_short_description()
# test_infobox_generator()
# test_long_description()
# test_media_generator()

sd = ShortDescription()
desc = sd.loadItem("Q1012569", {"links": "text","lang":"de"})
print(desc)

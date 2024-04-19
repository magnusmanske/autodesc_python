import re

from wikidata import WikiData


class MediaGenerator:
    commons_api = "https://commons.wikimedia.org/w/api.php"

    media_props = {
        "P18": "image",
        "P94": "coat_of_arms",
        "P158": "seal",
        "P41": "flag",
        "P10": "video",
        "P242": "map",
        "P948": "banner",
        "P154": "logo",
    }

    def __init__(self, wd=None):
        self.wd = wd if wd is not None else WikiData()

    def generateMedia(self, q, thumb="", user_zoom=4):
        ret = {"thumbnails": {}}
        q = q.upper()
        self.wd.getItemBatch([q])
        if not self.wd.hasItem(q):
            return ret

        i = self.wd.getItem(q)

        files = []
        for prop_id, prop_label in self.media_props.items():
            if i.hasClaims(prop_id):
                ret[prop_label] = i.getStringsForProperty(prop_id)
                ret[prop_label] = list(
                    map(lambda fn: fn.replace("_", " "), ret[prop_label])
                )
                files += list(map(lambda fn: f"File:{fn}", ret[prop_label]))

        if i.hasClaims("P625"):
            claims = i.getClaimsForProperty("P625")
            ret["osm"] = ["osm_map"]
            lat = claims[0]["mainsnak"]["datavalue"]["value"]["latitude"]
            lon = claims[0]["mainsnak"]["datavalue"]["value"]["longitude"]
            zoom = user_zoom
            thumburl = f"https://maps.wikimedia.org/img/osm-intl,{zoom},{lat},{lon},{thumb}x{thumb}.png"
            ret["thumbnails"]["osm_map"] = {
                "thumburl": thumburl,
                "thumbwidth": thumb,
                # "thumbheight" : thumb ,
                "url": thumburl,
                "descriptionurl": f"https://tools.wmflabs.org/geohack/geohack.php?language=en&params={lat}_N_{lon}_E_globe:earth",
            }

        if not files:
            return ret

        try:
            thumb = int(thumb)
        except Exception as _e:
            return ret
        if thumb <= 0:
            return ret

        api_params = {
            "action": "query",
            "titles": "|".join(files),
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": thumb,
            "iiurlheight": thumb,
            "format": "json",
        }

        data = self.wd.getJsonFromUrl(self.commons_api, api_params)
        for v in data["query"]["pages"].values():
            file = re.sub(r"^File:", "", v["title"]).replace("_", " ")
            ret["thumbnails"][file] = v["imageinfo"][0]

        return ret

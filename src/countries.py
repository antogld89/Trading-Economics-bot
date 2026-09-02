"""Whitelist of countries relevant to FX trading.

Values must match the lowercase `data-country` attribute used by
tradingeconomics.com/calendar?g=world. Easy to extend: just add/remove
strings below, no other code needs to change.
"""

FX_RELEVANT_COUNTRIES = {
    # G10 / majors
    "united states", "euro area", "germany", "france", "italy", "spain",
    "netherlands", "belgium", "austria", "finland", "greece", "portugal",
    "ireland", "united kingdom", "japan", "switzerland", "canada",
    "australia", "new zealand",
    # Major EM / Asia
    "china", "india", "brazil", "mexico", "south africa", "turkey",
    "russia", "south korea", "indonesia", "saudi arabia",
    "united arab emirates", "singapore", "hong kong", "taiwan",
    "thailand", "malaysia", "philippines", "vietnam", "pakistan",
    "bangladesh", "sri lanka", "mongolia", "kazakhstan", "uzbekistan",
    "georgia", "azerbaijan",
    # Europe (non-euro or smaller)
    "norway", "sweden", "denmark", "poland", "hungary", "czech republic",
    "romania", "bulgaria", "croatia", "slovakia", "slovenia", "serbia",
    "iceland", "ukraine",
    # Middle East / Africa
    "israel", "oman", "egypt", "ghana", "tunisia",
    # Americas
    "chile", "colombia", "peru", "argentina", "uruguay",
}

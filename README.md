# EMBER - Wood-Fire Kitchen & Bar

Telegram Mini App for a restaurant: full menu, cart and the Surprise Plate roulette (random dish within a budget, 20% off).

- Menu: 17 dishes across 6 categories, photos from TheMealDB / TheCocktailDB (stored locally in `img/`)
- Surprise Plate: pick $15 / $25 / $40, spin, land a random dish, get it at 20% off
- Order flow: cart -> deep link to Telegram bot (@openyanixvxclawbot), no backend required
- Table booking: pre-filled Telegram message

Static single-file app (index.html + img/), works on GitHub Pages. No build step.

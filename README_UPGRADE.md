# resQthali upgrade notes

## Existing site features retained

The original homepage, participant workflows, NGO and donor dashboards, verification flows, matching and route views, notifications, certificates, profile uploads, assistant chat, and both original image assets are retained.

## Visual and layout refinements

The homepage hero continues to use the included `static/resqthali-child.jpeg` image with a text-safe warm overlay. The shared visual layer includes food particles, reveal and hover motion, button feedback, a scroll-progress indicator, and reduced-motion support. Responsive grid constraints and media/code overflow safeguards keep content inside the viewport. A malformed orphaned card-style declaration was corrected so card borders, spacing, and shadows apply as intended.

The About page uses the separate `static/about-hunger.jpeg` image in its story card; the homepage background remains unchanged. The chat button and panel are fixed to the viewport with safe right insets and width limits so they stay visible on narrow screens.

## Regression tests

Run the built-in tests from the project root:

```bash
python3 -m unittest discover -s tests -v
```

The regression suite covers existing public pages, login/role access, the NGO-control-room, chat, location, and matching APIs, image delivery, and homepage visual/overflow requirements.

## Running

```bash
pip install -r requirements.txt
python app.py
```

### Optional Google Directions API

The current routing button uses the public Google Maps Directions URL format, which is a simple, key-free way to hand the user off to Google Maps for navigation.

If you later want the server to calculate Google travel times, traffic-aware routes, or multi-stop optimization, use the `googlemaps` Python package and a server-side `GOOGLE_MAPS_API_KEY` environment variable. Do not hard-code the key into templates or JavaScript.

The current `est_time_mins` field remains a simple estimate based on 30 km/h average city travel and should not be presented as live Google traffic data.

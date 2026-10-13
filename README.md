# RobotYOUNG Academy

Responsive, green-and-white technology-school website for **RobotYOUNG
Academy**. Includes seven program summaries with expandable details, academy
information, photographed student activities, a news blog with story pages,
franchise enquiries, and contact options.

## Local preview

Python 3 is required; no third-party packages are needed. Run commands from
the repository root. No build step is required to preview the checked-in pages:

```bash
python3 scripts/preview.py
```

Then open <http://localhost:8000> on the host machine. The preview server allows
128 queued connections instead of the standard server's five, preventing
intermittent image-request failures through the preview tunnel when galleries
load concurrently. It is not a production server.

## Structure

The deployable website lives in `public/`, with browser styles in
`public/assets/css/` and JavaScript in `public/assets/js/`. Editable academy
content lives in `src/`; Python development tools live in `scripts/`.
Generated pages should not be edited directly, because rebuilding overwrites them.
See [the project and page guide](docs/PROJECT-STRUCTURE.md) for the full tree and
details of every page.

### Where to edit

| Change | File or folder |
| --- | --- |
| Academy content, contact details, shared header/footer | `src/site-template.html` |
| News/blog copy | `src/content/news.json` |
| Gallery and robot entries, order, and captions | `src/content/gallery.json`, `src/content/robots.json` |
| Page generation | `scripts/build_pages.py` |
| Styling | `public/assets/css/styles.css` |
| Browser interactions | `public/assets/js/script.js` |
| Gallery photographs | `public/assets/gallery/previews/` |
| Robot images | `public/assets/robots/` |
| Project documentation | `docs/PROJECT-STRUCTURE.md` |

HTML asset URLs are relative to the website root: `assets/css/styles.css`
and `assets/js/script.js`. CSS URLs are relative to the stylesheet itself;
the font reference is `../fonts/nunito-latin.woff2`. Do not add `public/` to
browser URLs or change the gallery fetch URL to be relative to `assets/js/`.

```text
rya-portfolio/
├── README.md
├── docs/               # Project and page documentation
├── src/                # Editable HTML template and JSON content sources
├── scripts/            # Python build and preview tools
└── public/             # Deploy this directory as the website root
    ├── *.html          # Generated public pages
    └── assets/
        ├── css/        # styles.css
        ├── js/         # script.js
        ├── fonts/
        ├── gallery/
        ├── robots/
        ├── image-catalog.json
        └── rya-logo-*
```

### JSON content sources

Edit `src/content/gallery.json`, `src/content/robots.json`, and
`src/content/news.json`. They are prefilled with the existing content.
See the [JSON editing guide](docs/PROJECT-STRUCTURE.md#json-content-editing-guide)
for complete examples, field definitions, and troubleshooting.

For a gallery photo or robot, upload the image to the corresponding folder in
`public/assets/`, then add an entry to the JSON array:

```json
{
  "src": "assets/gallery/previews/classroom.webp",
  "caption": "Building together"
}
```

Gallery and robot entries contain only `src` and `caption`. `src` is relative
to `public/` (do not include `public/` in it). `caption` controls the visible
text and is also used as the image's accessibility text. There are no separate
alt or subtitle fields. All visible captions live in these JSON sources.
Do not edit `public/assets/image-catalog.json` directly: it is generated, and
the preview server bypasses it in favor of the source JSON.
Array order controls display order; remove an entry to hide it from the live
gallery. Uploading an image alone no longer adds it automatically. The existing
same-page image exclusions still apply, including the duplicate smart-car photo.
The HTML galleries remain as a fallback if JavaScript or catalog loading fails;
edit the template separately if you need to update that fallback.

For news, duplicate an object in `src/content/news.json` and edit its fields:
`slug`, `category`, `title`, `image`, `alt`, `summary`, `sections`, `ctaTarget`,
and `ctaLabel`. Each section has `heading` and `text`. Text is plain text, not
HTML. The image is a filename inside `public/assets/gallery/previews/`.
Use a unique lowercase hyphen-separated slug; it becomes the article filename.
Do not use existing navigation page names as slugs. `ctaTarget` is a page name
without `.html`: `index`, `about`, `programs`, `projects`, `gallery`, `news`, or
`contact`. The first story is featured on the homepage and news page, so keep at
least one story. Removing a story removes it from listings; delete its old
generated `public/<slug>.html` separately if it should no longer be accessible.

After editing, run both build commands in **Before publishing** below. The
preview server reads gallery/robot JSON on refresh; news changes require a page
rebuild. Publish the regenerated `public/` directory, not the source JSON files.
Builds check image paths and news slugs and escape blog text for safe HTML.

The page names and asset paths below are relative to `public/`; `src/` and
`scripts/` paths are relative to the repository root:

- `index.html` — academy homepage with links to the dedicated sections
- `about.html`, `programs.html`, `projects.html`, `gallery.html`,
  `news.html`, `contact.html` — separate navigation pages; contact includes
  franchise information and the shared enquiry form
- `franchise.html` — redirects old bookmarks to the combined contact page
- `beyond-the-classroom.html`, `next-learning-adventure.html`,
  `stay-curious.html` — individual blog posts
- `src/site-template.html` — shared header/footer and academy section content source
- `scripts/build_pages.py` — generates the static pages; edit the template for academy
  content and `src/content/news.json` for blog posts, then run `python3 scripts/build_pages.py`.
  Generated HTML is checked in, so no build step is needed to preview or host it.
- `scripts/build_galleries.py` — rebuilds the image catalog for static hosting
- `scripts/preview.py` — serves the website locally with a live image catalog
- `assets/css/styles.css` — responsive visual system and layout
- `assets/js/script.js` — mobile navigation, program enquiry selection, and email draft
  preparation
- `assets/rya-logo-horizontal.png` and `assets/rya-logo-square.jpg` — supplied
  academy logos; square version cropped to remove outer whitespace
- `assets/gallery/academy-*.jpg` — six supplied graduation and community photos,
  resized to 1600px for the website; original uploads are retained locally.
- `assets/gallery/IMG_*.jpg`, `DSC*.jpg`, `DJI_*.jpg` and `PXL_*.jpg` — 43
  additional photos downloaded on 8 October 2026, 14:03–14:10, shown in the
  expandable gallery with individual captions and descriptive alt text.
- `assets/gallery/PHOTO-NOTES.md` — filename-to-alt-text reference for all 49
  gallery photos. Original Downloads files are unchanged.
- `assets/gallery/previews/` — compressed WebP previews (maximum 800px) for
  gallery and classroom-led homepage display. Images are display-only, with
  individual captions and alt text; they do not open full-size files on click.
- `assets/robots/` — optimized robot images and source-filename reference notes.
  The homepage uses photography and robot imagery instead of decorative icons,
  emoji and CSS illustrations; menu and disclosure controls remain functional.

## Enquiries

The form opens a prefilled Gmail draft in the browser. Visitors must sign in
if needed and press Send. It does not send, store, or register an enquiry.
WhatsApp, telephone, email, and Google
Maps links provide alternative contact routes. No backend or CMS is configured.

## Before publishing

After content and image changes, run these commands from the project root:

```bash
python3 scripts/build_pages.py
python3 scripts/build_galleries.py
```

Configure static hosting to serve `public/` as its document root, or upload
the contents of `public/` to the host's website root. Do not publish the repository
root or add `/public/` to visitor URLs. The `src/`, `scripts/`, documentation,
and development metadata are not required on the production host.

For a production-like local check without the live catalog endpoint, run:

```bash
python3 -m http.server 8001 --bind 127.0.0.1 --directory public
```

Open `http://localhost:8001` on the host machine. Check navigation, images,
program disclosures, gallery expansion, and the contact form's Gmail draft.
Check the mobile menu at a narrow viewport. Stop this test server with Ctrl+C.

The current implementation has separate static pages and a blog, but no news
CMS or publishing dashboard. Blog copy is adapted from the existing academy
information, not dated event announcements. The academy introduction, mission and vision use the supplied
academy statement. The supplied requirements PDF describes the broader website,
ERP, inventory and franchise platform; those systems are not implemented here.
Project facts come from the local RYA website-copy and Facebook-facts notes;
review them before publication. Program descriptions are introductory, not
finalized curricula.

Still needed: classroom photos/videos, confirmed fees, durations and schedules,
future event dates, team/organization details, awards, approved testimonials,
partner assets, social URLs and franchise packages. These are not fabricated in
the design. Full course pages, online registration, franchise applications, news
CMS and embedded Google Maps remain future work.

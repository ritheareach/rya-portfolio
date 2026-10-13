# RobotYOUNG Academy

Responsive, green-and-white technology-school website for **RobotYOUNG
Academy**. Includes seven program summaries with expandable details, academy
information, photographed student activities, a news blog with story pages,
franchise enquiries, and contact options.

## Local preview

No build step is required:

```bash
python3 preview.py
```

Then open <http://localhost:8000> on the host machine. The preview server allows
128 queued connections instead of the standard server's five, preventing
intermittent image-request failures through the preview tunnel when galleries
load concurrently. It is not a production server.

## Structure

### Automatic galleries

Add optimized images to `assets/gallery/previews/` or `assets/robots/`. The
preview server scans those folders on each page refresh. Images already featured
elsewhere are excluded from the expandable galleries, and counts update
automatically. Existing captions and alt text are preserved. For new images, add
descriptions to `assets/gallery/PHOTO-NOTES.md` or `assets/robots/README.md`;
otherwise a readable filename is used as a label. Use descriptive filenames
rather than camera-generated names for new uploads.

Before publishing to static hosting, run `python3 build_galleries.py` to refresh
`assets/image-catalog.json`. Static hosting cannot scan new folders at runtime;
rebuild and republish the catalog whenever images change. The HTML galleries
remain as a fallback if the catalog cannot load.

- `index.html` — academy homepage with links to the dedicated sections
- `about.html`, `programs.html`, `projects.html`, `gallery.html`,
  `news.html`, `contact.html` — separate navigation pages; contact includes
  franchise information and the shared enquiry form
- `franchise.html` — redirects old bookmarks to the combined contact page
- `beyond-the-classroom.html`, `next-learning-adventure.html`,
  `stay-curious.html` — individual blog posts
- `site-template.html` — shared header/footer and academy section content source
- `build_pages.py` — generates the static pages; edit the template for academy
  content and the `stories` list for blog posts, then run `python3 build_pages.py`.
  Generated HTML is checked in, so no build step is needed to preview or host it.
- `styles.css` — responsive visual system and layout
- `script.js` — mobile navigation, program enquiry selection, and email draft
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

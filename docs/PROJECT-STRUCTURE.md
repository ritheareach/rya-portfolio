# RobotYOUNG Academy — Project Structure and Page Guide

This document describes the current implementation, based on the project files. It covers the directory structure, page content, shared functionality, and editing workflow.

[Return to the setup README](../README.md).

## 1. Project overview

RobotYOUNG Academy is a responsive, static website presenting a STEM learning academy in Phnom Penh, Cambodia. Visitors can explore programs, student projects, academy photographs, stories, and contact or franchise enquiry options.

| Area | Implementation |
| --- | --- |
| Frontend | HTML, shared CSS, and vanilla JavaScript |
| Page generation | Python standard-library script (`scripts/build_pages.py`) |
| Image catalog | Python standard-library script (`scripts/build_galleries.py`) |
| Editable collections | JSON sources for gallery photos, robot images, and news stories in `src/content/` |
| Local preview | Python HTTP server (`scripts/preview.py`) |
| Typography | Locally hosted Nunito font |
| Hosting model | Static files; no production application server required |
| Enquiries | Prefilled Gmail draft; visitor must send it manually |
| Database, authentication, CMS | Not implemented |

Generated HTML is checked into the project. No build step is required just to preview the existing site.

## 2. Project tree

The current layout separates documentation, editable HTML source, Python
tooling, and the deployable website. All 11 public HTML pages live directly
inside `public/`; CSS and browser JavaScript live in separate asset folders.

Repeated image files are grouped below rather than listed individually.
`.git/` and `.amp/` are development metadata, not website content. Generated
Python `__pycache__/` folders are ignored and omitted from the tree.

```text
rya-portfolio/
├── README.md                       # Setup, scope, and publishing notes
├── docs/
│   └── PROJECT-STRUCTURE.md        # This project and page guide
├── src/
│   ├── content/
│   │   ├── gallery.json            # Photo paths and captions, in display order
│   │   ├── robots.json             # Robot paths and captions, in display order
│   │   └── news.json               # Story metadata, body sections, and links
│   └── site-template.html          # Editable layout and academy content source
├── scripts/
│   ├── build_pages.py              # Generates public HTML pages
│   ├── build_galleries.py          # Generates the static image catalog
│   └── preview.py                  # Local server with live image catalog
├── public/                         # Website document root for hosting
│   ├── index.html                  # Homepage
│   ├── about.html                  # Academy introduction and learning approach
│   ├── programs.html               # Programs, robotics levels, training courses
│   ├── projects.html               # Student projects and robot showcase
│   ├── gallery.html                # Academy photo gallery
│   ├── news.html                   # Story listing
│   ├── beyond-the-classroom.html   # Academy-highlight story
│   ├── next-learning-adventure.html # Programs and camp story
│   ├── stay-curious.html           # Community story
│   ├── contact.html                # Contact and franchise enquiries
│   ├── franchise.html              # Legacy redirect to contact.html#franchise
│   └── assets/
│       ├── css/
│       │   └── styles.css          # Shared visual styles and responsive layout
│       ├── js/
│       │   └── script.js           # Shared browser interactions
│       ├── rya-logo-horizontal.png # Horizontal academy logo
│       ├── rya-logo-square.jpg     # Square academy logo
│       ├── image-catalog.json      # Gallery and robot image entries
│       ├── fonts/
│       │   ├── nunito-latin.woff2  # Local font file
│       │   └── OFL-Nunito.txt      # Font license
│       ├── gallery/
│       │   ├── PHOTO-NOTES.md      # Photo descriptions and source references
│       │   ├── *.jpg              # Academy and activity photographs
│       │   └── previews/
│       │       └── *.webp          # Optimized display images
│       └── robots/
│           ├── README.md           # Robot image descriptions and references
│           └── *.webp             # Optimized robot images and hero cutout
├── .gitignore                      # Ignore rules
├── .git/                           # Version-control metadata
└── .amp/                           # Agent workspace metadata/artifacts
```

### Folder responsibilities

| Repository folder | Responsibility | Editing and publishing |
| --- | --- | --- |
| `docs/` | Project structure and page documentation | Edit directly; not part of the hosted site |
| `src/` | Shared HTML layout and academy content | Edit the template, then rebuild public pages |
| `src/content/` | Editable gallery, robot, and news JSON sources | Edit collections here; rebuild the catalog or pages before publishing |
| `scripts/` | Python page generation, catalog generation, and local preview | Development tools; not required on the production host |
| `public/` | Complete website document root | Publish this folder's contents; HTML pages are generated |
| `public/assets/css/` | Shared website stylesheet | Edit directly; included in deployment |
| `public/assets/js/` | Browser interactions | Edit directly; distinct from Python tooling in `scripts/` |
| `public/assets/fonts/` | Local font and license | Included in deployment |
| `public/assets/gallery/` | Academy photographs, preview images, and reference notes | Add optimized images in `previews/`, update `src/content/gallery.json`, and rebuild the catalog |
| `public/assets/robots/` | Robot imagery and reference notes | Add optimized images, update `src/content/robots.json`, and rebuild the catalog |

There are no public HTML pages, `styles.css`, `script.js`, or `assets/` folder
at the repository root. Do not recreate those old paths when updating the site.

## 3. Architecture and content ownership

Public pages and assets live in `public/`, which is the document root for
preview and static hosting. Visitor page URLs remain unchanged. Below, page
names and `assets/` paths are relative to `public/`, while short CSS and
JavaScript names refer to `public/assets/css/styles.css` and
`public/assets/js/script.js` respectively.
Editable academy content is separated into `src/`, and development tools into
`scripts/`. Below, short script names refer to files in `scripts/`, and
`site-template.html` refers to `src/site-template.html`.

### Page generation

`build_pages.py` reads `site-template.html`, separates its shared header, main sections, and footer, then assembles the public pages. It also:

- Assigns page-specific browser titles and active navigation states.
- Converts known template section links into links to the corresponding pages.
- Builds the homepage from the hero section, an academy page-link grid, and a featured story.
- Builds `news.html` and story pages from `src/content/news.json`.
- Writes the legacy `franchise.html` redirect.

**Edit the source, not only the generated page:** manual changes to generated HTML can be overwritten the next time `build_pages.py` runs.

| Content | Source to edit |
| --- | --- |
| Header, footer, hero, academy sections, contact information | `src/site-template.html` |
| Page section assignments and generated page headings | `pages` mapping in `scripts/build_pages.py` |
| Story titles, summaries, body text, images, and related calls to action | `src/content/news.json` |
| Homepage exploration grid and news listing layout | Generation code in `scripts/build_pages.py` |
| Colors, typography, spacing, layouts, and responsive rules | `public/assets/css/styles.css` |
| Menu, enquiry selection, Gmail draft, gallery updates | `public/assets/js/script.js` |
| Gallery/robot order, image paths, and captions | `src/content/gallery.json` and `src/content/robots.json` |

`site-template.html` is a source document, not a primary visitor destination. Some template content is not selected into the public pages; its presence alone does not mean visitors see it.

### Shared layout and behavior

All regular public pages share the academy header, navigation, footer, stylesheet, and JavaScript. The minimal franchise redirect does not use that full layout.

### Asset path rules

Repository paths and browser URLs are different: `public/` is the hosting
directory, not part of the public URL.

| Resource | Repository location | Browser reference |
| --- | --- | --- |
| Homepage | `public/index.html` | `/` or `index.html` |
| Stylesheet | `public/assets/css/styles.css` | `assets/css/styles.css` in HTML |
| Browser script | `public/assets/js/script.js` | `assets/js/script.js` in HTML |
| Nunito font | `public/assets/fonts/nunito-latin.woff2` | `../fonts/nunito-latin.woff2` in CSS |
| Image catalog | `public/assets/image-catalog.json` | `assets/image-catalog.json` in JavaScript |

CSS paths resolve relative to the stylesheet. The JavaScript gallery fetch
resolves relative to the page, not the script's `assets/js/` directory.
The template's asset references target generated pages in `public/`; preview
the generated website rather than opening `src/site-template.html` directly.

### Navigation and interactions

- **Navigation:** Home, About us, Programs, Projects, Gallery, News, and Contact & Franchise.
- **Mobile menu:** opens with the menu button and closes when a navigation link is selected or Escape is pressed.
- **Accessibility features:** skip-to-content link, active-page navigation indicators, image alt text, labeled form fields, and native disclosure controls.
- **Footer:** academy message, Explore and Connect links, and a copyright year updated by JavaScript.
- **Visual system:** green-and-white academy branding, pastel accents, Nunito typography, photography, and responsive layouts.

## 4. Page-by-page details

### 4.1 Homepage — `index.html`

**Purpose:** introduce the academy and direct visitors to the main information pages.

**Content:**

- Hero headline: “Build skills. Create the future.”
- Introduction to hands-on STEM, innovation, critical thinking, and problem-solving.
- Robotics, coding, AI & IoT, and drones highlighted alongside classroom and robot imagery.
- “Explore the academy” links to About, Programs, Projects, Gallery, and Contact.
- Featured academy story: “Learning doesn’t stop at the classroom door.”

**Visitor actions:** explore programs, contact the academy, visit dedicated sections, read the featured story, or open all news and stories.

**Source:** template section `top`, plus homepage markup generated in `build_pages.py`.

### 4.2 About — `about.html`

**Purpose:** explain the academy’s identity, mission, vision, and learning approach.

**Content:**

- Academy introduction and the “Think it. Build it. Try again.” message.
- Mission: equip students with knowledge, skills, and confidence to lead in STEM and make a positive impact.
- Vision: students contributing to a sustainable, equitable, technologically advanced society through STEM innovation.
- Five learning-approach themes: Learn by Doing, Friendly Learning Environment, Future Skills, Project-Based Learning, and Encouraging Young Innovators.

**Visitor actions:** explore programs or contact the academy.

**Source:** template sections `about` and `learning-approach`.

### 4.3 Programs — `programs.html`

**Purpose:** present the available learning areas and the robotics progression.

**Program summaries:**

1. Robotics
2. Coding
3. AI & IoT
4. Drone
5. STEM Playground
6. Summer Camp
7. Mechanical Design

Program cards contain expandable introductory details and enquiry links. A separate prompt helps visitors who are unsure where to start.

**Robotics learning path:** four expandable levels, each with four modules.

| Level | Name | Module coverage |
| --- | --- | --- |
| 1 | Basic Robotics | Micro:bit and sensors; differential-drive robot design/programming; SuperBit and mecanum wheels; multidirectional control and wireless communication |
| 2 | Intermediate Robotics | Arduino fundamentals; control systems; robotics design/development; wireless robotics control |
| 3 | Advanced Robotics | Robotic arms; mini production lines and automation; quadruped motion control; quadruped wireless communication |
| 4 | Advanced Plus Robotics | Mechanical design; prototyping; robotics engineering projects; final project presentation and defense |

Module identifiers run from `RYA-L1A` through `RYA-L4D`.

**Specialist training:** an expandable list of ten courses (`RYA-T01`–`RYA-T10`): Arduino, ESP32, STM32, IoT, Mechanical Design and CAD, FPV Drone Technology, PCB Design and Prototyping, AI Fundamentals, Embedded Systems Development, and Robotics Integration and Automation.

**Visitor actions:** expand program or curriculum details and enquire about a program or training course. Program enquiry links carry the selected interest to the contact form using session storage.

**Limits:** this is not online enrollment or a set of dedicated course-detail pages. Confirmed fees, durations, schedules, and availability must be obtained from the academy.

**Source:** template sections `programs` and `curriculum`.

### 4.4 Projects — `projects.html`

**Purpose:** show practical student learning and examples of robots.

**Content:**

- “Little makers. Real projects.” introduction.
- Three photographed project themes: hands-on electronics, coding and robot building, and a community robotics showcase.
- Robot showcase headed “Robots that spark big questions.”
- Featured robot images and an expandable archive of additional robot images.

**Visitor actions:** browse project examples and expand the robot collection. Images are display-only rather than links to full-size files.

**Gallery behavior:** JavaScript refreshes the robot collection from `assets/image-catalog.json`; existing HTML remains usable if catalog loading fails.

**Source:** template sections `projects` and `robots` provide layout and fallback figures; `src/content/robots.json` controls the refreshed robot images and captions.

### 4.5 Gallery — `gallery.html`

**Purpose:** present academy life, student activities, and community photographs.

**Content:** a featured photo grid with captions (also used as image alt text), followed by an expandable archive of additional academy photos.

**Visitor actions:** browse images and expand the archive. There is no full-size image viewer or lightbox.

**Gallery behavior:** the image catalog supplies the collection and JavaScript updates the “Explore … more academy photos” count. Images featured elsewhere on the same page are excluded from the refreshed collection. Static HTML is retained as a fallback.

**Source:** `src/content/gallery.json` controls refreshed photos and captions; template section `gallery` provides layout and fallback figures. Optimized images live in `assets/gallery/previews/`.

### 4.6 News and stories — `news.html`

**Purpose:** provide an index of academy stories.

**Content:**

- Heading: “Small discoveries. Big possibilities.”
- One featured story in the Academy highlight category.
- Two additional cards in the Courses & camps and Community categories.
- Each card has a photograph, category, title, summary, and story link.

**Visitor actions:** open one of the three story pages.

**Limits:** stories are static editorial content, not dated event announcements. There is no CMS, search, category filtering, or pagination.

**Source:** `src/content/news.json` and news-generation code in `build_pages.py`, not the template’s `news` section.

### 4.7 Academy-highlight story — `beyond-the-classroom.html`

**Title:** “Learning doesn’t stop at the classroom door.”

**Category:** Academy highlight.

**Content:** classroom robot-building photograph; introduction connecting hands-on projects with Cambodia Robotics Olympiad participation; sections “Ideas become something you can build” and “A wider community of makers.”

**Visitor actions:** return to all stories, explore student projects, or open either other story through “Keep exploring.”

### 4.8 Programs and camp story — `next-learning-adventure.html`

**Title:** “Plan their next learning adventure.”

**Category:** Courses & camps.

**Content:** photograph of a learner programming beside wheeled robots; introduction to finding a suitable learning path; sections “Start with their curiosity” and “Talk to us about availability.” The story advises asking the academy about class openings and the next Summer Camp rather than publishing unconfirmed dates.

**Visitor actions:** return to all stories, discover programs, or read another story.

### 4.9 Community story — `stay-curious.html`

**Title:** “Stay curious. Stay connected.”

**Category:** Community.

**Content:** robotics exhibition photograph; introduction to workshops, STEM activities, and the robotics community; sections “Make room for discovery” and “Keep in touch with the academy.”

**Visitor actions:** return to all stories, contact the academy about upcoming activities, or read another story.

**Shared story layout:** all three stories include an academy byline, lead paragraph, main image, two body sections, a relevant call to action, and links to the other stories. Their source is `src/content/news.json`.

### 4.10 Contact and franchise — `contact.html`

**Purpose:** provide direct contact routes and one shared enquiry form for learning and franchise interests.

**Content:**

- Franchise introduction: “Grow with RobotYOUNG,” with a “Discuss a franchise” action.
- Contact introduction: “Let’s find their starting point.”
- Telephone: `+855 15 999 187`.
- Email: `robotyoungacademy@gmail.com`.
- Telegram contact and group links, Facebook link, and WhatsApp alternative.
- Location: RobotYOUNG Academy, Koh Pich City, Phnom Penh, Cambodia.
- External Google Maps link; no embedded map.

**Form fields:** name, email address, interest, and message. Interest options include help choosing a program, the seven programs, Training Courses, Events & workshops, and Franchise enquiry.

**Submission behavior:** the browser prepares a Gmail compose URL containing the selected interest in the subject and the visitor’s name, email, interest, and message in the body. The visitor must sign in if necessary and press Send. The website itself does not send, store, or register the enquiry.

**Source:** template sections `franchise` and `contact`.

### 4.11 Legacy franchise link — `franchise.html`

**Purpose:** preserve older bookmarks without maintaining a second franchise page.

**Behavior:** immediately redirects through an HTML meta refresh to `contact.html#franchise`. A visible “Continue to contact & franchise enquiries” link provides a fallback.

**Source:** redirect-generation code in `build_pages.py`.

## 5. Image and gallery pipeline

1. Optimized academy images live in `assets/gallery/previews/`; optimized robot images live in `assets/robots/`.
2. `build_galleries.py` reads `src/content/gallery.json` and `src/content/robots.json` and builds the public catalog, checking that referenced images exist.
3. Entries contain only `src` and `caption`. The caption supplies both visible text and image accessibility text, even for existing figures. Array order controls display order. Uploads must be added to the JSON explicitly; Markdown image notes are reference documents, not active content sources.
4. `script.js` loads the catalog, reuses existing figures where possible, creates figures for new images, and updates featured and expandable grids.
5. `preview.py` reads the source JSON in memory when `/assets/image-catalog.json` is requested, so gallery edits appear on refresh without rewriting the static catalog.
6. Static hosting uses the checked-in JSON file. Rebuild and republish it whenever images change.

Images are made non-draggable in the browser; this is an interaction choice, not image-copy protection.

### JSON content editing guide

The three source files contain JSON arrays. Use double-quoted keys and text,
separate entries with commas, and do not add comments or trailing commas.
Image files are stored separately; JSON contains their paths, not image data.
There is no CSV importer, database, or admin dashboard.

#### Gallery photos and robots

Edit `src/content/gallery.json` for academy photos and
`src/content/robots.json` for the robot showcase. Both use exactly the same
two-field format. For example, a robot collection can contain:

```json
[
  {
    "src": "assets/robots/010-robot-02.webp",
    "caption": "Mini Dynamo One"
  }
]
```

| Field | Meaning |
| --- | --- |
| `src` | Image path relative to `public/`; the file must exist inside `public/assets/` |
| `caption` | Plain-text caption shown below the image; also used as its HTML `alt` text |

Do not add separate `alt`, `title`, or `description` fields. There are no
subtitle rows. Choose captions that identify the image for both visible and
screen-reader use.

- **Add:** place an optimized image in `public/assets/gallery/previews/` or
  `public/assets/robots/`, then append its `src` and `caption` object to the
  corresponding source array. Uploading a file alone does not add it.
- **Edit:** change `caption` to rename a card, or `src` to use another image.
- **Reorder:** move objects within the array. The first entries fill the
  featured grid; remaining entries appear in the expandable archive. The
  number of featured slots comes from the template, not another JSON field.
- **Remove:** delete the object to remove it from the refreshed collection.
  This does not delete the image file or the template's fallback figure.

Images already used outside the gallery on the same page are excluded.
`assets/robots/005-robot-23.webp` is also excluded because it duplicates the
hero robot. Archive counts reflect displayed entries after these exclusions.
An empty image array hides the archive and leaves the featured grid empty.

JavaScript replaces captions even on existing template figures. If JavaScript
is disabled or the catalog fails to load, the original HTML figures remain;
JSON edits do not update that fallback. To change the fallback too, edit
`src/site-template.html` and rebuild pages.

#### News and blog posts

Edit `src/content/news.json`. News retains its own richer format; the
two-field image format does not apply to articles. This shortened version of
an existing story illustrates every required field:

```json
[
  {
    "slug": "beyond-the-classroom",
    "category": "Academy highlight",
    "title": "Learning doesn’t stop at the classroom door.",
    "image": "050-IMG_20260718_094400.webp",
    "alt": "Students working on robots together in the classroom",
    "summary": "Our learners take their ideas into the wider robotics community.",
    "sections": [
      {
        "heading": "Ideas become something you can build",
        "text": "Learners turn ideas into builds they can test and improve."
      }
    ],
    "ctaTarget": "projects",
    "ctaLabel": "Explore student projects"
  }
]
```

| Field | Meaning |
| --- | --- |
| `slug` | Unique lowercase letters/numbers separated by hyphens; generates `public/<slug>.html` |
| `category`, `title`, `summary` | Category label, article heading, and introduction/listing summary |
| `image` | Existing filename in `public/assets/gallery/previews/`, without a directory prefix |
| `alt` | Accessibility description for the article image |
| `sections` | Array of body sections, each with plain-text `heading` and `text` |
| `ctaTarget` | Destination page name without `.html`: `index`, `about`, `programs`, `projects`, `gallery`, `news`, or `contact` |
| `ctaLabel` | Visible call-to-action text |

Duplicate an existing object to add a story, assign a new slug, and edit its
content. The first object is featured on the homepage and news listing; keep
at least one story. Body text is escaped for HTML, so HTML tags are displayed
as text rather than interpreted as markup. JSON can contain Khmer and other
Unicode text directly.

The builder rejects duplicate or invalid slugs and reserved names (`index`,
`news`, `franchise`, and the navigation page names). It also checks the image
filename and CTA destination. Removing or renaming a story updates listings
and related-story links on rebuild, but does not delete its old generated
page. Delete the obsolete `public/<old-slug>.html` separately if it should no
longer be accessible, and ensure your hosting deployment removes it too.

#### Preview and publishing behavior

| Change | Live preview with `scripts/preview.py` | Static hosting or plain HTTP server |
| --- | --- | --- |
| Gallery/robot entry, order, or caption | Save source JSON and refresh the browser | Run `python3 scripts/build_galleries.py`, then publish the updated catalog and any new images |
| News story | Run `python3 scripts/build_pages.py`, then refresh | Run the same build, then publish generated pages and any new images |
| Template or fallback figures | Run `python3 scripts/build_pages.py`, then refresh | Run the same build, then publish generated pages |

**Do not edit `public/assets/image-catalog.json` directly.** It is generated
output and is overwritten by the catalog build. The live preview endpoint
reads the source files instead, so edits to that output file will not appear
there. Markdown photo notes remain references, not content sources.

If a change is missing, check that you edited the correct source file, saved
valid JSON, and refreshed or rebuilt as shown above. For a missing image,
check its exact filename and whether an exclusion applies. Read the terminal
error if a build fails. Restart the preview server after changing Python
scripts, since its imported code does not reload automatically. If browser
JavaScript changed, use a hard refresh to avoid an old cached script.

## 6. Editing, preview, and publishing

Python 3 is required; the build and preview tools use only the standard
library. Run the commands below from the repository root.

### Preview the current site

```bash
python3 scripts/preview.py
```

Open `http://localhost:8000` on the machine running the server. The server binds to `127.0.0.1:8000`, serves only `public/`, and uses an enlarged request queue for concurrent gallery requests. It is for development, not production. Stop it with Ctrl+C before starting another server on the same port.

### Update content and prepare static files

```bash
# After editing src/site-template.html or src/content/news.json:
python3 scripts/build_pages.py

# After editing src/content/gallery.json or src/content/robots.json:
python3 scripts/build_galleries.py
```

When updating content and imagery, run both commands. Catalog generation reads the JSON sources, not homepage image descriptions. See the README's JSON content guide for fields and examples.

Page generation writes the navigation pages and one page per news story into
`public/` (11 HTML files with the current three stories). It does not overwrite
`public/assets/css/styles.css` or `public/assets/js/script.js`, which are edited
directly. Catalog generation writes `public/assets/image-catalog.json` and
does not modify the image files.

Before publishing, review the generated pages and links, image descriptions, mobile navigation, disclosure controls, and Gmail draft behavior. Configure hosting to serve `public/` as the document root, or upload its contents to the host's website root. Do not include `/public/` in visitor URLs. The `src/` and `scripts/` folders, documentation, and development metadata are not needed by the hosted browser experience.

### Verify the static hosting layout locally

After generating the pages and catalog, run a plain static server:

```bash
python3 -m http.server 8001 --bind 127.0.0.1 --directory public
```

Open `http://localhost:8001` on the host machine. Unlike `scripts/preview.py`,
this serves the generated catalog from disk instead of reading source JSON on each
catalog request. Check all navigation pages and stories, the franchise redirect,
CSS and font loading, program disclosures, gallery expansion, and mobile menu.
Check that a program enquiry preselects the contact form's interest and that
form submission opens the expected Gmail draft; nothing should send automatically.
Stop the static test server with Ctrl+C.

## 7. Current scope and future work

**Implemented:** responsive public pages, program disclosures, curriculum listings, project imagery, JSON-managed gallery and robot collections, JSON-generated news and story pages, expandable galleries, shared navigation, contact links, Gmail draft preparation, and the legacy franchise redirect.

**Not implemented:** backend enquiry processing, online registration, student accounts, payments, ERP, inventory management, franchise applications, a franchise management platform, a news CMS, dedicated course-detail pages, or an embedded Google Map.

Content still requiring confirmation or supply includes fees, course durations and schedules, future event dates, team details, awards, approved testimonials, partner assets, and franchise packages. Existing program descriptions are introductory; this document describes the website implementation, not a finalized academic or business offering.

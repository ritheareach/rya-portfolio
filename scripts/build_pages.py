"""Build the academy's static pages from the shared content template."""
from pathlib import Path
from html import escape
from datetime import date
from urllib.parse import urlsplit, parse_qs, urlencode
import json
import re
from build_images import build_images
from build_galleries import build_catalog

build_images()
build_catalog()

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
PUBLIC.mkdir(exist_ok=True)
source = (ROOT / "src" / "site-template.html").read_text()
header, rest = source.split('    <main id="main">', 1)
body, footer = rest.split('    </main>', 1)
sections = re.findall(r'<section\b.*?</section>', body, re.S)
pages = {
    "about": ("About the academy", ["about", "learning-approach"]),
    "programs": ("Our programs", ["programs", "curriculum"]),
    "projects": ("Student projects", ["projects", "robots"]),
    "gallery": ("Life at the academy", ["gallery"]),
    "contact": ("Contact & franchise enquiries", ["franchise", "contact"]),
}
owners = {section: page for page, (_, ids) in pages.items() for section in ids}
owners.update(top="index", news="news")

def publish(name, title, content, active=None):
    document = header + '<main id="main">' + content + '</main>' + footer
    document = re.sub(r'<title>.*?</title>', f'<title>{title} — RobotYOUNG Academy</title>', document)
    document = re.sub(r'href="#([\w-]+)"', lambda m: (m[0] if name == "contact" and m[1] in ("contact", "franchise") else f'href="{owners[m[1]]}.html#{m[1]}"' if m[1] == "franchise" else f'href="{owners[m[1]]}.html"') if m[1] in owners else m[0], document)
    if active:
        document = document.replace(f'<a href="{active}.html">', f'<a href="{active}.html" aria-current="page">', 1)
        if active == "contact":
            document = document.replace('class="button button-small"', 'aria-current="page" class="button button-small"', 1)
    (PUBLIC / f"{name}.html").write_text(document)

for name, (title, ids) in pages.items():
    content = ''.join(s for s in sections if any(f'id="{i}"' in s for i in ids))
    intro = f'<div class="page-heading shell"><p class="eyebrow">ROBOTYOUNG ACADEMY</p><h1>{title}</h1></div>'
    publish(name, title, intro + content, name)

# Preserve old franchise bookmarks without maintaining a second enquiry page.
(PUBLIC / "franchise.html").write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0;url=contact.html#franchise"><title>Franchise enquiries — RobotYOUNG Academy</title></head><body><a href="contact.html#franchise">Continue to contact &amp; franchise enquiries</a></body></html>')

def photo_gallery(photos):
    if not photos:
        return ''
    content = '<div class="post-gallery">'
    for photo in photos:
        filename = photo["image"]
        if Path(filename).name != filename or not (PUBLIC / "assets/gallery" / filename).is_file():
            raise ValueError(f"News image not found in gallery: {filename}")
        content += f'<figure><img src="assets/gallery/{escape(filename)}" alt="{escape(photo["alt"])}" loading="lazy" />'
        if photo.get("caption"):
            content += f'<figcaption>{escape(photo["caption"])}</figcaption>'
        content += '</figure>'
    return content + '</div>'


def video_blocks(videos, source_url=None):
    content = ''
    for video in videos:
        link = video['url']
        url = urlsplit(link)
        local = not url.scheme and not url.netloc
        if local:
            path = Path(link)
            if not link.startswith('assets/videos/') or '..' in path.parts or not (PUBLIC / path).is_file():
                raise ValueError(f'Local video must exist under assets/videos/: {link}')
        elif url.scheme != 'https' or not url.hostname or url.username or url.password:
            raise ValueError(f'Video URL must use HTTPS: {link}')
        host = url.hostname or ''
        path = url.path.rstrip('/')
        query = parse_qs(url.query)
        embed = video.get('embedUrl', '')
        portrait = False
        if not embed and host in {'youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be', 'www.youtube-nocookie.com'}:
            identifier = query.get('v', [''])[0] if path == '/watch' else path.split('/')[-1]
            if re.fullmatch(r'[A-Za-z0-9_-]{11}', identifier):
                embed = f'https://www.youtube-nocookie.com/embed/{identifier}'
                portrait = path.startswith('/shorts/')
        elif not embed and host in {'vimeo.com', 'www.vimeo.com', 'player.vimeo.com'}:
            identifier = path.split('/')[-1]
            if identifier.isdigit():
                embed = f'https://player.vimeo.com/video/{identifier}'
                if query.get('h'):
                    embed += '?' + urlencode({'h': query['h'][0]})
        elif not embed and host in {'facebook.com', 'www.facebook.com', 'm.facebook.com', 'fb.watch'}:
            if '/videos/' in path or path.startswith(('/reel/', '/watch')) or path == '/video.php' or host == 'fb.watch':
                embed = 'https://www.facebook.com/plugins/video.php?' + urlencode({'href': link, 'show_text': 'false'})
                portrait = path.startswith('/reel/')
        elif not embed and host in {'tiktok.com', 'www.tiktok.com'}:
            match = re.search(r'/video/(\d+)$', path)
            if match:
                embed = f'https://www.tiktok.com/player/v1/{match[1]}'
                portrait = True
        elif not embed and host in {'instagram.com', 'www.instagram.com'}:
            if re.fullmatch(r'/(?:p|reel|tv)/[A-Za-z0-9_-]+', path):
                embed = f'https://www.instagram.com{path}/embed/'
                portrait = True
        elif not embed and host in {'dailymotion.com', 'www.dailymotion.com', 'dai.ly'}:
            identifier = path.split('/')[-1]
            if re.fullmatch(r'[A-Za-z0-9]+', identifier) and (host == 'dai.ly' or path.startswith('/video/')):
                embed = f'https://www.dailymotion.com/embed/video/{identifier}'
        ratio = video.get('ratio', 'portrait' if portrait else 'landscape')
        if ratio not in {'landscape', 'portrait', 'square'}:
            raise ValueError(f'Unknown video ratio: {ratio}')
        title = escape(video['title'])
        content += f'<figure class="post-video post-video-{ratio}">'
        if Path(url.path).suffix.lower() in {'.mp4', '.webm', '.ogg'} and not embed:
            content += f'<video controls playsinline preload="metadata" aria-label="{title}" src="{escape(link)}"></video>'
        elif embed:
            parsed = urlsplit(embed)
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError('embedUrl must be an HTTPS player URL')
            content += f'<iframe src="{escape(embed)}" title="{title}" loading="lazy" allow="fullscreen; picture-in-picture; encrypted-media" allowfullscreen sandbox="allow-scripts allow-same-origin allow-presentation"></iframe>'
        content += f'<figcaption>{title}'
        if video.get('caption'):
            content += f' — {escape(video["caption"])}'
        content += '</figcaption>'
        if link != source_url:
            content += f'<a class="secondary-link" href="{escape(link)}" target="_blank" rel="noopener noreferrer">Watch original video ↗</a>'
        content += '</figure>'
    return content


stories = []
records = json.loads((ROOT / "src/content/news.json").read_text())
if not records:
    raise ValueError("news.json needs at least one story for the homepage highlight")
slugs = set()
for record in records:
    slug = record["slug"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in slugs or slug in {*pages, "index", "news", "franchise"}:
        raise ValueError(f"Invalid, duplicate, or reserved news slug: {slug}")
    slugs.add(slug)
    if record["ctaTarget"] not in {"index", "news", *pages}:
        raise ValueError(f"Unknown CTA page: {record['ctaTarget']}")
    image = record["image"]
    if Path(image).name != image or not (PUBLIC / "assets/gallery" / image).is_file():
        raise ValueError(f"News image not found in gallery: {image}")
    article_images = photo_gallery(record.get("images", []))
    published_date = record["publishedDate"]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", published_date):
        raise ValueError(f"News publishedDate must use YYYY-MM-DD: {slug}")
    published = date.fromisoformat(published_date)
    date_label = f"{published.day} {published.strftime('%B')} {published.year}"
    source_details = ''
    if record.get("sourceUrl"):
        url = urlsplit(record["sourceUrl"])
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError(f"News sourceUrl must be an HTTPS URL: {slug}")
        source_link = f'<a class="secondary-link" href="{escape(record["sourceUrl"])}">View original source ↗</a>'
        source_details = f'<aside class="post-source" aria-label="Article source">{source_link}</aside>'
    stories.append((f"{published_date}-{slug}", *(escape(record[key]) for key in ("category", "title", "image", "alt", "summary")),
                    [(escape(section["heading"]), escape(section["text"]), photo_gallery(section.get("images", [])) + video_blocks(section.get("videos", []), record.get("sourceUrl")))
                     for section in record["sections"]],
                    record["ctaTarget"], escape(record["ctaLabel"]), published_date, date_label, slug,
                    escape(record.get("author", "RobotYOUNG Academy")), article_images, source_details, video_blocks(record.get("videos", []), record.get("sourceUrl"))))

# Equal publication dates retain source order.
stories.sort(key=lambda story: story[9], reverse=True)

def card(story, featured=False):
    slug, category, title, image, alt, summary, *_ = story
    published_date, date_label = story[9:11]
    return f'<article class="blog-card {"blog-featured" if featured else ""}"><a class="blog-image" href="{slug}.html" tabindex="-1" aria-hidden="true"><img src="assets/gallery/{image}" alt="{alt}" /></a><div class="blog-card-copy"><p class="eyebrow">{category}</p><p class="post-byline">Published <time datetime="{published_date}">{date_label}</time></p><h2><a href="{slug}.html">{title}</a></h2><p>{summary}</p><a class="secondary-link" href="{slug}.html">Read the story <span aria-hidden="true">↗</span></a></div></article>'

news = '<section class="shell blog-index"><div class="blog-heading"><p class="eyebrow">NEWS &amp; STORIES</p><h1>Small discoveries.<br /><span>Big possibilities.</span></h1><p>Ideas, learning adventures and life in our academy community.</p></div>'
news += card(stories[0], True) + '<div class="blog-grid">' + ''.join(card(s) for s in stories[1:5]) + '</div>'
if len(stories) > 5:
    news += '<section class="news-more" aria-labelledby="more-stories-title"><div class="news-more-heading"><h2 id="more-stories-title">More stories</h2><div class="news-slider-controls" hidden><button class="button button-small" type="button" aria-label="Previous stories" aria-controls="more-stories">←</button><button class="button button-small" type="button" aria-label="Next stories" aria-controls="more-stories">→</button></div></div><div class="news-slider" id="more-stories" tabindex="0" role="region" aria-label="More stories; scroll to browse">'
    news += ''.join(card(s) for s in stories[5:]) + '</div></section>'
news += '</section>'
publish("news", "News & stories", news, "news")
for slug, category, title, image, alt, summary, paragraphs, target, label, published_date, date_label, original_slug, author, article_images, source_details, article_videos in stories:
    content = f'<article class="blog-post shell"><a class="secondary-link" href="news.html">← All stories</a><header class="post-heading"><p class="eyebrow">{category}</p><h1>{title}</h1><p class="post-lede">{summary}</p><p class="post-byline">By {author} · Published <time datetime="{published_date}">{date_label}</time></p></header><img class="post-image" src="assets/gallery/{image}" alt="{alt}" /><div class="post-body">'
    for index, (heading, text, section_images) in enumerate(paragraphs):
        if heading:
            content += f'<h2>{heading}</h2>'
        content += '<p>' + text.replace('\n', '<br />') + '</p>' + section_images
        if index == 0:
            content += article_images
    if not paragraphs:
        content += article_images
    content += article_videos + source_details
    content += f'<a class="button" href="{target}.html">{label} ↗</a></div><aside class="post-next"><h2>Keep exploring</h2>'
    content += ''.join(f'<a class="secondary-link" href="{other[0]}.html">{other[2]} →</a>' for other in stories if other[0] != slug) + '</aside></article>'
    publish(slug, title, content, "news")
    # Keep undated bookmarks working without duplicating article content.
    (PUBLIC / f"{original_slug}.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0;url={slug}.html"><link rel="canonical" href="{slug}.html"><title>{title} — RobotYOUNG Academy</title></head><body><a href="{slug}.html">Continue to the article</a></body></html>')

home = next(s for s in sections if 'id="top"' in s)
home += '<section class="section shell"><div class="section-heading"><div><p class="eyebrow">EXPLORE THE ACADEMY</p><h2>A starting point<br /><span>for every curious mind.</span></h2></div></div><div class="home-links">'
for name, (title, _) in pages.items():
    home += f'<a href="{name}.html"><h3>{title}</h3><span>Explore →</span></a>'
home += '</div></section><section class="shell home-news"><p class="eyebrow">FROM THE ACADEMY</p>' + card(stories[0], True) + '<a class="secondary-link" href="news.html">All news &amp; stories →</a></section>'
publish("index", "Build skills. Create the future.", home, "index")

"""Build the academy's static pages from the shared content template."""
from pathlib import Path
import re

ROOT = Path(__file__).parent
source = (ROOT / "site-template.html").read_text()
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
    (ROOT / f"{name}.html").write_text(document)

for name, (title, ids) in pages.items():
    content = ''.join(s for s in sections if any(f'id="{i}"' in s for i in ids))
    intro = f'<div class="page-heading shell"><p class="eyebrow">ROBOTYOUNG ACADEMY</p><h1>{title}</h1></div>'
    publish(name, title, intro + content, name)

# Preserve old franchise bookmarks without maintaining a second enquiry page.
(ROOT / "franchise.html").write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0;url=contact.html#franchise"><title>Franchise enquiries — RobotYOUNG Academy</title></head><body><a href="contact.html#franchise">Continue to contact &amp; franchise enquiries</a></body></html>')

stories = [
    ("beyond-the-classroom", "Academy highlight", "Learning doesn’t stop at the classroom door.", "050-IMG_20260718_094400.webp", "Students working on robots together in the classroom", "From hands-on projects to Cambodia Robotics Olympiad participation, our learners take their ideas into the wider robotics community.", [
        ("Ideas become something you can build", "Robotics brings science, technology, engineering and mathematics together. At RobotYOUNG Academy, learners explore these subjects through hands-on projects, turning ideas into builds they can test and improve."),
        ("A wider community of makers", "Learning reaches beyond classroom activities through student projects and Cambodia Robotics Olympiad participation. Explore the academy’s project page for a closer look at what young makers are working on.")], "projects", "Explore student projects"),
    ("next-learning-adventure", "Courses & camps", "Plan their next learning adventure.", "033-IMG_5959.webp", "A learner programming beside wheeled robots", "A starting point for curious minds: discover programs, ask questions and find a learning path that fits your child.", [
        ("Start with their curiosity", "The academy offers learning opportunities in robotics, coding, AI and IoT, drones and more. Browse the program summaries and learning path to see where your child’s interests could lead."),
        ("Talk to us about availability", "Ask the academy about current class openings and the next Summer Camp. Dates and availability are confirmed directly by the academy, so get in touch before making your plans.")], "programs", "Discover our programs"),
    ("stay-curious", "Community", "Stay curious. Stay connected.", "045-IMG_8719.webp", "An exhibitor sharing robot models with visitors", "Workshops, STEM activities and the robotics community: there is always another question worth exploring.", [
        ("Make room for discovery", "Building, experimenting and sharing ideas are part of the academy’s hands-on approach. Workshops and STEM activities offer opportunities to connect those interests with other curious learners."),
        ("Keep in touch with the academy", "Contact RobotYOUNG Academy for workshop announcements, STEM activities and competition updates. The team can confirm what is coming up and help you find a suitable opportunity.")], "contact", "Ask about upcoming activities"),
]

def card(story, featured=False):
    slug, category, title, image, alt, summary, *_ = story
    return f'<article class="blog-card {"blog-featured" if featured else ""}"><a class="blog-image" href="{slug}.html" tabindex="-1" aria-hidden="true"><img src="assets/gallery/previews/{image}" alt="{alt}" /></a><div class="blog-card-copy"><p class="eyebrow">{category}</p><h2><a href="{slug}.html">{title}</a></h2><p>{summary}</p><a class="secondary-link" href="{slug}.html">Read the story <span aria-hidden="true">↗</span></a></div></article>'

news = '<section class="shell blog-index"><div class="blog-heading"><p class="eyebrow">NEWS &amp; STORIES</p><h1>Small discoveries.<br /><span>Big possibilities.</span></h1><p>Ideas, learning adventures and life in our academy community.</p></div>'
news += card(stories[0], True) + '<div class="blog-grid">' + ''.join(card(s) for s in stories[1:]) + '</div></section>'
publish("news", "News & stories", news, "news")
for slug, category, title, image, alt, summary, paragraphs, target, label in stories:
    content = f'<article class="blog-post shell"><a class="secondary-link" href="news.html">← All stories</a><header class="post-heading"><p class="eyebrow">{category}</p><h1>{title}</h1><p class="post-lede">{summary}</p><p class="post-byline">By RobotYOUNG Academy · Academy stories</p></header><img class="post-image" src="assets/gallery/previews/{image}" alt="{alt}" /><div class="post-body">'
    content += ''.join(f'<h2>{heading}</h2><p>{text}</p>' for heading, text in paragraphs)
    content += f'<a class="button" href="{target}.html">{label} ↗</a></div><aside class="post-next"><h2>Keep exploring</h2>'
    content += ''.join(f'<a class="secondary-link" href="{other[0]}.html">{other[2]} →</a>' for other in stories if other[0] != slug) + '</aside></article>'
    publish(slug, title, content, "news")

home = next(s for s in sections if 'id="top"' in s)
home += '<section class="section shell"><div class="section-heading"><div><p class="eyebrow">EXPLORE THE ACADEMY</p><h2>A starting point<br /><span>for every curious mind.</span></h2></div></div><div class="home-links">'
for name, (title, _) in pages.items():
    home += f'<a href="{name}.html"><h3>{title}</h3><span>Explore →</span></a>'
home += '</div></section><section class="shell home-news"><p class="eyebrow">FROM THE ACADEMY</p>' + card(stories[0], True) + '<a class="secondary-link" href="news.html">All news &amp; stories →</a></section>'
publish("index", "Build skills. Create the future.", home, "index")

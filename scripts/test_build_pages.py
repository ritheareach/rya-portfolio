"""Run with python3 -m unittest discover -s scripts -p 'test_*.py'."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


class NewsDateTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        source = Path(__file__).resolve().parent.parent
        shutil.copytree(source / "scripts", self.root / "scripts")
        (self.root / "src/content").mkdir(parents=True)
        shutil.copy(source / "src/site-template.html", self.root / "src/site-template.html")
        for folder in ("gallery", "robots"):
            (self.root / "public/assets" / folder).mkdir(parents=True)
            (self.root / "src/content" / f"{folder}.json").write_text("[]")
        (self.root / "public/assets/gallery/photo.webp").touch()
        self.story = {
            "category": "Learning", "title": "A story", "image": "photo.webp",
            "alt": "Learners", "summary": "Explore", "sections": [],
            "ctaTarget": "programs", "ctaLabel": "Programs",
        }

    def build(self, records):
        (self.root / "src/content/news.json").write_text(json.dumps(records))
        return subprocess.run([sys.executable, str(self.root / "scripts/build_pages.py")],
                              capture_output=True, text=True)

    def test_dated_articles_sort_newest_first_and_preserve_old_links(self):
        records = [dict(self.story, slug=slug, publishedDate=published)
                   for slug, published in (("old", "2025-12-31"),
                                           ("new", "2026-01-02"),
                                           ("same-day", "2026-01-02"))]
        result = self.build(records)
        self.assertEqual(result.returncode, 0, result.stderr)
        public = self.root / "public"
        news = (public / "news.html").read_text()
        self.assertLess(news.index('href="2026-01-02-new.html"'),
                        news.index('href="2026-01-02-same-day.html"'))
        self.assertLess(news.index('href="2026-01-02-same-day.html"'),
                        news.index('href="2025-12-31-old.html"'))
        self.assertIn('href="2026-01-02-new.html"', (public / "index.html").read_text())
        for record in records:
            filename = f"{record['publishedDate']}-{record['slug']}.html"
            article = (public / filename).read_text()
            self.assertIn(f'<time datetime="{record["publishedDate"]}">', article)
            self.assertIn(f'url={filename}', (public / f'{record["slug"]}.html').read_text())
        article = (public / "2026-01-02-new.html").read_text()
        self.assertIn('>2 January 2026</time>', article)
        self.assertIn('href="2025-12-31-old.html"', article)
        self.assertNotIn('href="old.html"', article)

    def test_authors_are_optional_and_rendered_as_plain_text(self):
        records = [
            dict(self.story, slug="default-author", publishedDate="2026-10-14"),
            dict(self.story, slug="custom-author", publishedDate="2026-10-14",
                 author="Dara & <Team>"),
        ]
        result = self.build(records)
        self.assertEqual(result.returncode, 0, result.stderr)
        public = self.root / "public"
        default = (public / "2026-10-14-default-author.html").read_text()
        custom = (public / "2026-10-14-custom-author.html").read_text()
        self.assertIn("By RobotYOUNG Academy · Published", default)
        self.assertIn("By Dara &amp; &lt;Team&gt; · Published", custom)
        self.assertNotIn("By RobotYOUNG Academy", custom)

    def test_article_supports_multiple_photos_without_changing_listing(self):
        (self.root / "public/assets/gallery/second.webp").touch()
        record = dict(self.story, slug="photos", publishedDate="2026-10-14", images=[
            {"image": "second.webp", "alt": 'Tools & "parts"', "caption": "Build <together>"},
            {"image": "photo.webp", "alt": "Learners"},
        ], sections=[{"heading": "First section", "text": "Start here."},
                     {"heading": "Second section", "text": "Keep exploring."}])
        result = self.build([record])
        self.assertEqual(result.returncode, 0, result.stderr)
        public = self.root / "public"
        article = (public / "2026-10-14-photos.html").read_text()
        self.assertIn('src="assets/gallery/second.webp" alt="Tools &amp; &quot;parts&quot;"', article)
        self.assertIn('<figcaption>Build &lt;together&gt;</figcaption>', article)
        self.assertLess(article.index('src="assets/gallery/second.webp"'),
                        article.rindex('src="assets/gallery/photo.webp"'))
        self.assertEqual(article.count("<figcaption>"), 1)
        self.assertLess(article.index("Start here."), article.index('class="post-gallery"'))
        self.assertLess(article.index('class="post-gallery"'), article.index("Second section"))
        self.assertNotIn("second.webp", (public / "news.html").read_text())
        record["images"][0]["image"] = "missing.webp"
        self.assertNotEqual(self.build([record]).returncode, 0)
        del record["images"]
        self.assertEqual(self.build([record]).returncode, 0)
        self.assertNotIn('class="post-gallery"', (public / "2026-10-14-photos.html").read_text())

    def test_section_photos_follow_their_own_text_and_validate_paths(self):
        (self.root / "public/assets/gallery/second.webp").touch()
        record = dict(self.story, slug="sections", publishedDate="2026-10-14", sections=[
            {"heading": "First", "text": "First text"},
            {"heading": "Second", "text": "Second text", "images": [
                {"image": "second.webp", "alt": 'Tools & "parts"', "caption": "Build <together>"},
                {"image": "photo.webp", "alt": "Section learners"}]},
            {"heading": "Third", "text": "Third text", "images": [
                {"image": "second.webp", "alt": "One photo"}]},
            {"heading": "Fourth", "text": "Fourth text", "images": []},
        ])
        result = self.build([record])
        self.assertEqual(result.returncode, 0, result.stderr)
        article = (self.root / "public/2026-10-14-sections.html").read_text()
        self.assertEqual(article.count('class="post-gallery"'), 2)
        self.assertLess(article.index("Second text"), article.index('alt="Tools &amp; &quot;parts&quot;"'))
        self.assertLess(article.index('alt="Tools &amp; &quot;parts&quot;"'), article.index('alt="Section learners"'))
        self.assertLess(article.index('alt="Section learners"'), article.index("Third text"))
        self.assertLess(article.index("Third text"), article.index('alt="One photo"'))
        self.assertLess(article.index('alt="One photo"'), article.index("Fourth text"))
        self.assertIn('<figcaption>Build &lt;together&gt;</figcaption>', article)
        for filename in ("missing.webp", "../photo.webp"):
            record["sections"][1]["images"][0]["image"] = filename
            self.assertNotEqual(self.build([record]).returncode, 0)

    def test_news_keeps_five_articles_above_the_remaining_slider(self):
        for count in (4, 5, 6, 10):
            records = [dict(self.story, slug=f"story-{i}", publishedDate="2026-10-14")
                       for i in range(count)]
            result = self.build(records)
            self.assertEqual(result.returncode, 0, result.stderr)
            news = (self.root / "public/news.html").read_text()
            main, _, more = news.partition('<section class="news-more"')
            self.assertEqual(main.count('<article class="blog-card '), min(count, 5))
            self.assertEqual(more.count('<article class="blog-card '), max(count - 5, 0))
            for i in range(count):
                region = main if i < 5 else more
                self.assertIn(f'href="2026-10-14-story-{i}.html"', region)

    def test_article_sources_are_escaped_and_require_https(self):
        record = dict(self.story, slug="source", publishedDate="2026-10-14",
                      sourceUrl="https://www.facebook.com/photo/?fbid=1&set=2",
                      sourceNote="Archive <photo> & website date")
        result = self.build([record])
        self.assertEqual(result.returncode, 0, result.stderr)
        article = (self.root / "public/2026-10-14-source.html").read_text()
        self.assertIn('href="https://www.facebook.com/photo/?fbid=1&amp;set=2"', article)
        self.assertNotIn("Content from the original source.", article)
        self.assertNotIn("Archive", article)
        for placement in ("article", "section"):
            video = {"url": record["sourceUrl"], "title": "Original video"}
            record["videos"] = [video] if placement == "article" else []
            record["sections"] = [{"heading": "", "text": "Story", "videos": [video] if placement == "section" else []}]
            self.assertEqual(self.build([record]).returncode, 0)
            article = (self.root / "public/2026-10-14-source.html").read_text()
            self.assertNotIn("Watch original video", article)
            self.assertIn("View original source", article)
            self.assertNotIn("Content from the original source.", article)
        record["sourceUrl"] = "https://example.com/different-source"
        self.assertEqual(self.build([record]).returncode, 0)
        self.assertIn("View original source", (self.root / "public/2026-10-14-source.html").read_text())
        self.assertIn("Watch original video", (self.root / "public/2026-10-14-source.html").read_text())
        for url in ("javascript:alert(1)", "http://example.com", "https://user:password@example.com"):
            record["sourceUrl"] = url
            self.assertNotEqual(self.build([record]).returncode, 0)

    def test_article_and_section_videos_support_platforms_and_fallback_links(self):
        cases = [
            ("https://youtu.be/M7lc1UVf-VE", "youtube-nocookie.com/embed/M7lc1UVf-VE"),
            ("https://www.youtube.com/watch?v=M7lc1UVf-VE", "youtube-nocookie.com/embed/M7lc1UVf-VE"),
            ("https://www.youtube.com/shorts/M7lc1UVf-VE", "youtube-nocookie.com/embed/M7lc1UVf-VE"),
            ("https://vimeo.com/76979871", "player.vimeo.com/video/76979871"),
            ("https://player.vimeo.com/video/123?h=privatehash", "player.vimeo.com/video/123?h=privatehash"),
            ("https://www.facebook.com/robotyoung/videos/123/", "facebook.com/plugins/video.php?href="),
            ("https://www.tiktok.com/@academy/video/123456789", "tiktok.com/player/v1/123456789"),
            ("https://www.instagram.com/reel/Ab_c12/", "instagram.com/reel/Ab_c12/embed/"),
            ("https://www.dailymotion.com/video/x123abc", "dailymotion.com/embed/video/x123abc"),
        ]
        records = [dict(self.story, slug=f"video-{i}", publishedDate="2026-10-14",
                        videos=[{"url": url, "title": 'Watch <video> & "learn"'}])
                   for i, (url, _) in enumerate(cases)]
        records.append(dict(self.story, slug="fallback", publishedDate="2026-10-14",
                            videos=[{"url": "https://example.com/video", "title": "Original"}]))
        records.append(dict(self.story, slug="custom", publishedDate="2026-10-14",
                            sections=[{"heading": "First", "text": "Before video", "videos": [
                                {"url": "https://example.com/story", "title": "Custom", "ratio": "square",
                                 "embedUrl": "https://example.com/player?id=1&lang=km"}]},
                                      {"heading": "Second", "text": "After video"}]))
        self.assertEqual(self.build(records).returncode, 0)
        for i, (url, expected) in enumerate(cases):
            article = (self.root / f"public/2026-10-14-video-{i}.html").read_text()
            self.assertIn(expected, article)
            self.assertIn('title="Watch &lt;video&gt; &amp; &quot;learn&quot;"', article)
            self.assertIn("Watch original video", article)
            self.assertNotIn("autoplay", article)
        fallback = (self.root / "public/2026-10-14-fallback.html").read_text()
        self.assertNotIn('<iframe', fallback)
        self.assertIn('href="https://example.com/video"', fallback)
        custom = (self.root / "public/2026-10-14-custom.html").read_text()
        self.assertIn('src="https://example.com/player?id=1&amp;lang=km"', custom)
        self.assertIn('post-video-square', custom)
        self.assertLess(custom.index("Before video"), custom.index('<iframe'))
        self.assertLess(custom.index('<iframe'), custom.index("After video"))
        self.assertNotIn('<iframe', (self.root / "public/news.html").read_text())

    def test_uploaded_videos_and_unsafe_video_inputs(self):
        folder = self.root / "public/assets/videos"
        folder.mkdir()
        (folder / "lesson.mp4").touch()
        record = dict(self.story, slug="local-video", publishedDate="2026-10-14",
                      videos=[{"url": "assets/videos/lesson.mp4", "title": "Lesson"}])
        self.assertEqual(self.build([record]).returncode, 0)
        article = (self.root / "public/2026-10-14-local-video.html").read_text()
        self.assertIn('<video controls playsinline preload="metadata"', article)
        self.assertIn('src="assets/videos/lesson.mp4"', article)
        for url in ("javascript:alert(1)", "http://example.com/video", "//example.com/video",
                    "https://user:pass@example.com/video", "assets/videos/missing.mp4", "assets/videos/../lesson.mp4"):
            record['videos'][0]['url'] = url
            self.assertNotEqual(self.build([record]).returncode, 0, url)
        record['videos'][0]['url'] = 'https://example.com/video'
        record['videos'][0]['embedUrl'] = 'javascript:alert(1)'
        self.assertNotEqual(self.build([record]).returncode, 0)
        del record['videos'][0]['embedUrl']
        record['videos'][0]['ratio'] = 'invalid'
        self.assertNotEqual(self.build([record]).returncode, 0)

    def test_invalid_publication_dates_fail_the_build(self):
        for published in ("2026-02-30", "20261014", "2026-1-02"):
            with self.subTest(published=published):
                result = self.build([dict(self.story, slug="example", publishedDate=published)])
                self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()

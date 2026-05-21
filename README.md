# Daniel's Life — personal site template

A minimal Jekyll site for keeping a personal record of life: blog
posts, photos, and videos. Built to deploy on **GitHub Pages** with
zero extra services.

## What's inside

```
.
├── _config.yml              # Site settings — edit me first
├── _layouts/                # Page templates (default, post, page, photo, video)
├── _includes/               # Header, footer, video embed
├── _posts/                  # Blog posts (markdown)
├── _photos/                 # Photo entries (markdown + image path)
├── _videos/                 # Video entries (YouTube/Vimeo embed or self-hosted)
├── assets/
│   ├── css/style.css        # Single stylesheet, light + dark
│   ├── images/              # Photos, post covers, etc.
│   └── videos/              # Self-hosted clips (small only)
├── about.md                 # About page
├── blog/index.html          # Blog listing
├── photos/index.html        # Photo grid
├── videos/index.html        # Video grid
├── index.html               # Homepage with recent everything
├── Gemfile                  # Ruby dependencies
├── .github/workflows/       # GitHub Actions auto-deploy
└── .gitignore
```

## 1 — Set it up on GitHub

1. Create a new repository on GitHub.
2. Copy these files into it (or push this folder).
3. In the repo, go to **Settings → Pages → Build and deployment** and
   set the source to **GitHub Actions**. The included workflow will
   build and deploy on every push to `main`.
4. Edit `_config.yml`:
   - Change `title`, `tagline`, `description`, `author`, `email`.
   - Set `url` to your final GitHub Pages URL.
   - If your repo is `username.github.io`, leave `baseurl: ""`.
     If it's `username.github.io/repo-name`, set
     `baseurl: "/repo-name"`.
   - Fill in the `social:` block (or leave entries blank to hide).
5. Push. The Action will build and your site will go live in a minute
   or two at the URL shown in **Settings → Pages**.

## 2 — Run it locally (optional)

You only need this if you want to preview changes before pushing.

```bash
# One-time
bundle install

# Each time you want to preview
bundle exec jekyll serve
# → open http://localhost:4000
```

Requires Ruby 3.x. On macOS: `brew install ruby` (then add it to your
PATH per Homebrew's instructions).

## 3 — Adding content

### A blog post

Create `_posts/YYYY-MM-DD-some-slug.md`:

```markdown
---
title: "A short walk"
date: 2026-05-09 18:00:00 -0700
tags: [walks, weekend]
cover: /assets/images/2026-05-09-walk.jpg   # optional
---

Whatever you want to say. Plain markdown — headings, lists, images,
code blocks, blockquotes all work.
```

Then drop any photos referenced into `assets/images/`.

### A photo album

Photos are organized as **albums** (groups). Each album is one
markdown file in `_photos/YYYY-MM-DD-slug.md`. You pick one image
as the album's `cover` (the thumbnail shown on the Albums page),
and list the rest under `images:`.

```markdown
---
title: "Trail morning"
date: 2026-05-09
location: "Marin Headlands"            # optional
cover: /assets/images/trail/01.jpg     # the album thumbnail
images:
  - src: /assets/images/trail/01.jpg
    caption: "First overlook"          # caption is optional
  - src: /assets/images/trail/02.jpg
  - src: /assets/images/trail/03.jpg
    caption: "Heading back, sky going pink"
---

Optional longer write-up shown above the photo grid.
```

Notes on this shape:

- **`cover:`** is required — it's what shows on the Albums grid and
  as the hero image on the album's own page.
- **`images:`** is the rest of the album. If you only put one image
  in (or omit it), the album just shows the cover.
- The cover is automatically *not* shown twice if you also include
  it as the first entry in `images:`.
- You don't need a folder per album — put images anywhere under
  `assets/images/` and just point to the right paths.

### A video

Three modes — pick one per entry.

**YouTube**

```markdown
---
title: "My morning coffee routine"
date: 2026-05-09
youtube: "dQw4w9WgXcQ"   # the bit after ?v= in the YouTube URL
---
```

**Vimeo**

```markdown
---
title: "Trip recap"
date: 2026-05-09
vimeo: "76979871"
thumbnail: /assets/images/recap-thumb.jpg   # optional, used in the grid
---
```

**Self-hosted MP4** (keep it small — GitHub limits files to ~100 MB)

```markdown
---
title: "A self-hosted clip"
date: 2026-05-09
file: /assets/videos/trip-recap.mp4
poster: /assets/images/recap-thumb.jpg     # optional
thumbnail: /assets/images/recap-thumb.jpg  # optional, used in the grid
---
```

## 4 — Customizing the look

- **Colors, fonts, widths**: top of `assets/css/style.css` — edit the
  CSS variables under `:root`.
- **Dark mode**: automatic, based on the visitor's OS. To force one
  mode, remove the `@media (prefers-color-scheme: dark)` block.
- **Navigation**: edit `_includes/header.html`.
- **Footer / social links**: `_config.yml` (`social:`) and
  `_includes/footer.html`.

## 5 — Big files

GitHub repos start to get unhappy past ~1 GB total, with single-file
caps around 100 MB. For long-form videos, embed YouTube / Vimeo
instead of pushing the file. For very large photo libraries, consider
storing originals elsewhere (e.g., a personal NAS or cloud bucket)
and only adding web-sized JPGs to the repo.

## 6 — Password protection (StatiCrypt)

The deployed site is protected by a single shared password using
[StatiCrypt](https://github.com/robinmoisson/staticrypt). Visitors
see a login page; entering the password decrypts and reveals the
site. Local `jekyll serve` is **not** encrypted — that would slow
you down. Encryption only happens during the GitHub Actions deploy
(or when you explicitly run it locally).

### One-time setup

1. **Pick a password.** Anything memorable and shareable —
   "spring-coyote-1942" is better than "letmein".

2. **Add it as a GitHub secret.** In your repo on GitHub:
   - Settings → Secrets and variables → Actions → **New repository secret**
   - Name: `SITE_PASSWORD`
   - Value: your password
   - Click "Add secret".

3. **Install Node dependencies locally** (once):

   ```bash
   npm install
   ```

   This pulls in StatiCrypt for local previews.

That's it. Push to `main` and the deployed site will be encrypted
with that password. Share the password with whoever should have
access — over a separate channel, not in the repo.

### Changing the password later

Just update the `SITE_PASSWORD` secret in GitHub repo settings and
trigger a rebuild (push any commit, or manually re-run the workflow
under the "Actions" tab).

### Previewing the protected site locally

```bash
STATICRYPT_PASSWORD='your-password' npm run preview:protected
```

This builds Jekyll, encrypts `_site/`, and serves it at
<http://localhost:4001> so you can check the login flow before
pushing.

For day-to-day editing, keep using `bundle exec jekyll serve` —
no password, instant reload.

### What's actually protected

**Every page is encrypted** — homepage, blog posts, photo albums,
video pages, the about page, all of them. A visitor cannot reach
any HTML page without the password, even via direct URL.

**But the password is only typed once per visitor.** StatiCrypt's
`--remember 30` flag stores the decryption key in the visitor's
browser `localStorage` for 30 days after their first successful
sign-in. From that point on, every page (and every return visit
within 30 days) auto-decrypts on load with no prompt. So the user
experience is "single sign-in" while the actual protection covers
every URL.

### Honest caveats

- This is **client-side** encryption. The encrypted content ships
  inside each page's HTML, so a determined attacker could try to
  brute-force the password offline. A long passphrase makes that
  impractical — favour `quiet-orchard-spring-1992` over `letmein`.
- The site won't be indexed by Google: the password gate blocks
  crawlers, and the build strips `feed.xml` / `sitemap.xml` /
  `robots.txt` so they can't be used to enumerate pages.
- Casual privacy: ✅. Bank-grade security: ❌. For a personal
  blog shared with friends and family, this is the right tradeoff.

### Switching to "homepage-only protected" (less secure)

If you ever want to flip back to encrypting only `_site/index.html`
and leaving inner pages public, open `scripts/encrypt.sh` and
replace the per-file `for` loop with a single call against
`$SITE_DIR/index.html`. Note the security implication: anyone with
a direct URL to an inner page can read it without the password.

---

Built with [Jekyll](https://jekyllrb.com/) and
[StatiCrypt](https://github.com/robinmoisson/staticrypt). MIT-style
— do whatever you want with this template.

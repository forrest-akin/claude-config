Scaffold a new Slidev presentation in this repository.

Ask the user for:
1. **Title** — the presentation title (you'll derive the kebab-case directory name from this)
2. **Date** — defaults to today's date (YYYY-MM-DD format)
3. **Theme** — default: `default`. Other options: `seriph`, `apple-basic`, `bricks`, `geist`
4. **Brief description** — one sentence for the frontmatter `info` field
5. **Author** — the author handle for the frontmatter `author` field

Then:
1. Create directory `presentations/YYYY-MM-DD-<kebab-title>/`
2. Create `presentations/YYYY-MM-DD-<kebab-title>/public/` directory
3. Write `presentations/YYYY-MM-DD-<kebab-title>/slides.md` with:
   - Proper frontmatter (theme, title, info, author from the answer above)
   - A title slide (`layout: cover`) with title and author
   - A "Agenda" slide with placeholder bullets
   - A closing/thank-you slide
4. Write `presentations/YYYY-MM-DD-<kebab-title>/package.json`:
   ```json
   {
     "name": "YYYY-MM-DD-kebab-title",
     "private": true,
     "scripts": {
       "dev": "slidev slides.md",
       "build": "slidev build slides.md",
       "export": "slidev export slides.md --format pdf"
     }
   }
   ```
5. Tell the user to run `npm install` (or `npx slidev`) in the new directory to start.

Follow conventions in `.claude/rules/slidev-conventions.md`.

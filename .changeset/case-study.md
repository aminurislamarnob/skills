---
"aiarnob-skills": minor
---

Add **`case-study`**, a model-invoked skill in a new **`portfolio`** bucket. It writes a portfolio case study of your part in a project from your own git commits across one or more repositories, as a single HTML page: a hero with screenshots, a commit chart of your work against the team's, the brief, architecture and flow diagrams, before/after numbers, what you built next to what the team built, and a footer that says where every number came from. The counting (`git_stats.py`), screenshots (`shoot.mjs`) and page building (`build_page.py`) are bundled scripts, so it works the same in any agent. Claude publishes the page as a private Artifact, and other agents get a standalone HTML file. Gemini CLI users add a fourth install: `gemini skills install https://github.com/aminurislamarnob/skills.git --path skills/portfolio`.

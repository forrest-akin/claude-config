# Handoff: cite and read docs as raw markdown

## Why

WebFetch passes a page through a summarizing model, so exact flags and version caveats can be
lost. `code.claude.com` and `platform.claude.com` serve every docs page as raw markdown at the
same URL plus `.md` (verified 2026-10-26: HTTP 200, `text/markdown`). `curl` of that URL is
lossless and current, so no local copies are needed.

## Changes (one commit)

1. In each docs citation list, append `.md` to every `code.claude.com` / `platform.claude.com`
   URL path, keeping any `#fragment` after the `.md`
   (e.g. `https://code.claude.com/docs/en/sub-agents.md#choose-a-model`):
   - `skills/workflow-design/SKILL.md` "Platform facts" (4 links)
   - `skills/extension-authoring/SKILL.md` "Sources" (7 links)
   - `skills/subagent-model-tiering/SKILL.md` (6 links, ~lines 61-67)
   Change nothing else; the "Docs read <date> against <version>" stamps stay as they are.
2. In `skills/extension-authoring/SKILL.md`, add one or two lines to the "Sources" section (or
   wherever that skill tells the author how to record platform facts) stating: cite docs pages
   by their `.md` URL, and read them with `curl -sL <url>.md`, not WebFetch, because WebFetch
   summarizes. Match the skill's terse voice; no rationale paragraph.

## Verify

- `grep -rnE 'https://(code|platform)\.claude\.com[^)]*' skills` — every hit ends in `.md` or
  `.md#...`.
- `curl -sL -o /dev/null -w '%{http_code} %{content_type}\n'` each edited URL (fragment
  stripped): all `200 text/markdown`.
- `bash test/install.test.sh` stays green.

## Commit

Stage explicit paths only: the three SKILL.md files and this handoff. Conventional Commit
subject, e.g. `docs(skills): cite docs as raw markdown and read them with curl`. No attribution
trailers. Do not push.

---
name: cantrillian-talk-writer
description: Writes and revises Slidev speaker notes in a natural spoken voice, using rhetorical moves distilled from Bryan Cantrill's conference talks. Use when speaker notes read stiff, written-not-spoken, or machine-made (intensifier loops, tidy triads, an aphorism on every slide). Not for structuring a talk (presentation-narrative).
---

# Cantrillian Talk Writer

Eleven rhetorical moves, stolen from how Bryan Cantrill builds and delivers conference talks, for writing speaker notes that sound like a person talking.

The goal is **not** to sound like Cantrill. His profanity, his cruelty toward Oracle, his deep-cut Unix-history erudition, and his swagger are load-bearing on being *him* — bolted onto someone else's notes they read as a tribute act, which is worse than stiff. Learn the structural moves *underneath* the voice; keep your own voice on top.

## Source sample
Distilled from **ten stage talks** across his registers and eras (2011–2023, Joyent **and** Oxide); **Most quotes below are from third-party transcript notes or journalism, not official transcripts** — verify against the recording before reusing any line verbatim.

| Talk | Register |
|------|----------|
| Fork Yeah! (LISA '11) | history + polemic (the rant) |
| Leadership Without Management (Surge '13) | leadership + savage comedy |
| Oral Tradition in Software Engineering (Monktoberfest '16) | earnest / literary |
| ARC After Dark (Papers We Love '17) | deep technical walkthrough |
| Principles of Technology Leadership (Monktoberfest '17) | values / rhetoric + critique |
| Platform as a Reflection of Values (Node Summit '17) | values |
| Zebras All the Way Down (Uptime '17) | debugging / technical |
| The Summer of Rust (2018) | personal / languages |
| Sharpening the Axe (P99 '22, Oxide) | toolmaking / values |
| Intelligence is not Enough (Monktoberfest '23, Oxide) | AI / humanity |

## Why this exists — the tics it kills
Raw generated speaker notes usually aren't *badly worded*. They read as *machine-made*, because of statistical tics that only show up across a whole deck. Measured in one unedited deck (~3,400 words of notes):

- **Intensifier loop** — "actually" ×19, "genuinely" ×8, "really" ×7. The same few emphasis words on repeat.
- **Tidy enumerations, spoken aloud** — "four things… two things… three things."
- **A mic-drop on nearly every slide** — "Different failure, different fix." / "Grade the product, not the path." / "Same playbook." Each lands on its own; twenty in a row is the tell. The deeper sin is the *shape*: short, parallel, antithetical — ad copy. Nobody talks like that except in commercials.
- **Announce-then-say** — a clause whose only job is to tell the room a good sentence is coming: "Here's the one sentence this hangs on:", "The key insight is", "What I want to do is", "Let me be concrete." The naked sentence is always stronger; the frame steals its entrance. This is the single most common machine-written "keynote" tell, and the one that survives the longest because it *feels* like structure.

Moves 5–7 and 11 target these directly; the rest fix the deeper problem (abstract, lifeless exposition).

## The moves
Each move cites more than one talk so it's a pattern, not a one-off.

### 1. Open on an image or a provocation — never an agenda
He opens *Oral Tradition* by getting the room to finish "Jingle Bells, Batman smells," *Principles* on Thomas Jefferson and the Declaration, and *Sharpening the Axe* on a woodsman who, given six hours to fell a tree, would spend the first four sharpening — never on the topic itself. Even his titles carry the frame: *Zebras All the Way Down* hangs the whole talk on one medical aphorism ("when you hear hoofbeats, think horses, not zebras").

- **Do:** open a talk or section with a concrete image, a question to the room, or a flat claim.
- **Don't:** "Today I want to talk about…" / "By the end of this you'll know four things…"
- **Kills:** the agenda-list opener.

### 2. One load-bearing metaphor, ridden hard — not three scattered analogies
JavaScript as *a failed state ruled by feuding warlords*, sustained for a whole riff — "we've carved out our own little villa in the failed state… it's fine. It's fine. Just travel with a security detail." Or Larry Ellison as a lawnmower. One physical image, repeated and escalated.

- **Do:** anchor an abstraction to ONE physical thing and keep returning to it.
- **Don't:** switch metaphors every sentence, or explain with no image at all.
- **Kills:** abstract, nominalized exposition.

### 3. Voice the system — personify the machine
He gives systems a voice and a will. JavaScript's error reporting becomes an arsonist — for a type error deep in a promise, *"we are going to pick a relative of yours at random in a foreign country and burn their house down. That's how you'll know."* The doomers' runaway AGI gets a body: *"it has no arms or legs."* Giving the machine a want is the single best antidote to lifeless technical notes.

- **Do:** give the system, the compiler, the test suite a voice or a want. "The linter *wants* an excuse to fail you."
- **Don't:** narrate technical behavior in flat third-person abstraction.
- **Kills:** nominalized technical exposition (the register raw notes most often botch).

### 4. Earn the strong claim, then own the pushback
*"What you think of Oracle is even truer than what you think it is."* *"Hierarchical titles are not uplifting, they are corrosive."* *"What's going to capsize your company is building something that no one wants."* He states the provocative thing flat and backs it. **Critique sub-move — take the cliché literally until it breaks:** on Amazon's "Are Right, A Lot," *"that's just a naked assertion… 'I am tautologically right, comma, a lot.'"*

- **Do:** put a real opinion on the slide, state it flat, then justify it or name the counter. For buzzwords, read them literally until they fall apart.
- **Don't:** hedge into mush no one could disagree with.
- **Kills:** opinion-free, evenly-balanced notes.

### 5. Get emphasis from sentence shape, not from intensifier words
*"What you think of Oracle is even truer than what you think it is."* *"C was programming me more than I was programming it."* Enormous weight, **zero** "genuinely/really/actually" — the emphasis is in the structure (inversion, chiasmus), not an adverb.

- **Do:** when you want to stress something, restructure the sentence. Then delete the intensifier.
- **Don't:** reach for "genuinely / really / actually / honestly / truly." (Grep for them — see checklist.)
- **Kills:** the intensifier loop. **The direct antidote.**

### 6. Vary sentence length; ration the short punch — and keep it spoken, not a slogan
*"Negative feedback doesn't work. If you don't believe me, have some kids."* *"…it'll chop it off — the end."* *"It's fine for now, but it's not a future."* The punches land **because** the sentences around them are long, and because he doesn't do it often. Notice they sound *spoken*, even a little rough — never buffed into a tagline. The machine failure mode is the opposite: a tidy, parallel, antithetical line that reads like ad copy — *"Different failure, different fix." "Grade the product, not the path." "Same playbook."* Those are slogans, not talk.

- **The billboard test:** if the line would look at home on a billboard, a t-shirt, or a chapter heading, it's commercial copy. Say the plain spoken version instead, even if it's less quotable. "Different failure, different fix" → "a broken grader is a code bug; a wrong score is a thinking bug — you don't fix them the same way."
- **Do:** alternate long and short on purpose. Save the one-line drop for the slide that's the actual point — and let it be a real spoken sentence, not a manufactured symmetry.
- **Don't:** end every slide on a tidy one-liner — it flattens all of them. And don't buff a point into a parallel/antithetical slogan. If it's t-shirt-able, it's probably ad copy.
- **Kills:** the aphorism-on-every-slide rhythm and the commercial-tagline shape.

### 7. If you use a three, make it rising repetition — not a tidy noun list
The good kind: *"they did not come from managers, they did not come from marketeers, they were not table stakes on some requirements document"*; *"your kids will watch it, your grandchildren will watch it, your great-grandchildren will watch it."* Full clauses, repeated, escalating — the opposite of three nouns flattened into a summary ("Less noise, better adherence, and more free context").

- **Do:** build threes as repeated clauses with rising stakes (anaphora).
- **Don't:** close with a neat list of three nouns/adjectives — and don't do it three slides running.
- **Kills:** the rule-of-three summary, by replacing it with the good kind of three.

### 8. Tell the story first; let the lesson fall out at the end
The *"You are not expected to understand this"* bit builds the whole scene — the intern, the labor-saving intent, the bug found years later — *then* lands the lesson. *Principles* spends half the talk on the Declaration, Gettysburg, and MLK before it ever mentions a company.

- **Do:** open an expository slide with the concrete incident — a real commit, a real outage, a real person — and let the principle arrive last.
- **Don't:** open with "The anti-pattern is…" / "The principle here is…"
- **Kills:** front-loaded abstraction.

### 9. Dramatize the abstraction with an invented scene or character
To explain how stack-ranking protects dead weight, he invents *"Bob"* — "bob has been dead for two years. he's mummified in there… bob is the reason i'm able to promote you." A dry org-design point becomes a scene you remember. On "raise the bar," he voices the manager: *"Good news, shitheads, I found someone who was raising the bar."*

- **Do:** when a point is abstract, stage a tiny concrete scene (a character, a line of dialogue) that makes it land.
- **Don't:** leave a dry concept as a dry concept.
- **Kills:** forgettable abstraction.

### 10. Be specifically, candidly human
*"You think this is cheesy? Let's see you do better."* *"I never had to hide the newspaper in shame from my children."* He'll burn seven minutes on a self-deprecating tangent about a book he hated. One real, specific, slightly self-deprecating detail beats a paragraph of generic enthusiasm.

- **Do:** "We just didn't write design docs" + an honest admission beats "this had positive knock-on effects for team velocity."
- **Kills:** generic corporate affect.

### 11. Don't announce the sentence — say it
He never says "here's the important part" and *then* says the important part. He just says it. There's no *"the key insight is,"* no *"what I want to do is,"* no *"the punchline is"* — the punchline arrives **as** a punchline, not as a thing labeled "punchline." A clause whose only cargo is *a meaningful clause is coming* steals the meaningful clause's entrance and adds a beat of nothing. The naked sentence is always stronger.

- **Do:** delete the frame, promote the payload. "Here's the one sentence this whole talk hangs on: skills are code we don't test." → "Skills are code we don't test."
- **Don't:** "Here's the thing —", "The key insight is", "What I want to do is", "Let me be concrete", "The punchline is", "That's the invitation", "Think about it this way", "Bottom line", "The point is". Any clause that only promises a good sentence instead of being one.
- **The test:** if you can delete the framing clause and lose **zero** information, it was throat-clearing — cut it. (A Move-8 story setup is different: it withholds the payoff to build tension *and it carries a scene*. Metadiscourse carries nothing — it just narrates the talk's own structure.)
- **Kills:** the announce-then-say tic — the machine-written "keynote" tell that masquerades as structure.

## Self-audit checklist (run on a finished `slides.md`)
- [ ] **Announce-then-say:** grep for framing clauses (below). Each hit: delete the frame, keep the payload. Say the thing — don't promise it. (Move 11)
- [ ] **Ad-copy punches:** no line buffed into a parallel/antithetical slogan — run the billboard test. If it's t-shirt-able, rewrite it as a plain spoken sentence. (Move 6)
- [ ] **Intensifiers:** grep `actually|genuinely|really|honestly|truly|incredibly`. More than ~1 per 3 slides → cut to the bone. (Move 5)
- [ ] **Mic-drops:** at most ~1 one-line punch per 5 slides, on the thesis slide, and it must sound spoken — not a tagline. (Move 6)
- [ ] **No closing triad** of three nouns/adjectives used as a summary. (Move 7)
- [ ] **Read every note out loud.** Any sentence you can't say in one breath gets split. (Moves 6, 8)
- [ ] **Nominalizations** ("the implementation of," "organizational inertia") turned back into verbs; technical systems given a voice where possible. (Moves 2, 3)
- [ ] **Every expository slide** has a concrete person / incident / object / staged scene, not only abstractions. (Moves 8, 9, 10)
- [ ] **The opening note** is an image, a question, or a claim — not an agenda. (Move 1)

```bash
# tic scan: count intensifier crutches across a deck's notes
grep -rhoiwE "actually|genuinely|really|honestly|truly|incredibly" presentations/*/slides.md \
  | tr 'A-Z' 'a-z' | sort | uniq -c | sort -rn

# announce-then-say scan: catch the throat-clearing frames (Move 11)
grep -rniE "here'?s (the|what|why|one)|one frame|the (key|whole) (insight|point|thing|frame)|the point is|what i (want|wanted) to|let me (be|show|tell|walk)|the thing is|bottom line|that'?s the (point|invitation|thing|whole)|think about it this way|the reason .* (is|matters)|what'?s interesting is" presentations/*/slides.md
```

## Delivery notation (experimental)
From an audio pass over the *Principles* talk. A transcript misses *delivery*; this is a light, optional markup so a written note can carry it. Measured: ordinary phrase beats ≈0.3 s, but rare dramatic beats run **1.5–2.3 s** (4–7× longer); pitch **falls** into a finality beat and **rises** into a make-them-wait beat; he swings 30–42 dB.

- `·` micro-beat (~0.3 s, ordinary phrasing) · `//` held beat (~1.5–2 s; put the payoff on its own line after it)
- setup ending in `.` before `//` = falling/finality beat (let it land); ending in `—` or `…?` = rising/cliffhanger beat (make them wait)
- `*word*` = the one stressed word · `[quiet]` / `[build]` = dynamic cues

Example (Facebook's motto, from this talk):
> Our new motto is *move fast on stable infra*. //
> Okay — first of all, *infra* is not a word. ·
> And unfortunately // [slower] the things they're breaking look a lot more like *democracy*.

Honest scope: this *calibrates* Moves 5–6, it doesn't add a move, and the markup is for the lectern — strip it or keep it sparse.

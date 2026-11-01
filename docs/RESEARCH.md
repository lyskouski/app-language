# Market Research: Tlum vs. Similar Applications

_Date: 2026-11-01_

This document compares Tlum with similar language-learning and vocabulary apps, summarises what users ask
for (and complain about) in those apps, and proposes a prioritised backlog for Tlum.

> **Caveat on sources.** User-sentiment data comes from public review aggregators (G2, Capterra,
> Trustpilot), community forums and vendor blogs. Many vendor blogs have a stake in the comparison, so
> treat rankings and percentages as indicative, not authoritative. Sources are listed at the end.

---

## 1. Where Tlum stands today

| Area | Current state (from the codebase) |
| --- | --- |
| Content model | User-created language pairs → categories → items (`origin`, `translation`, optional `sound`, `image`) |
| Practices | Cards, Harmonica (typing), Acoustic Harmonica (dictation), Articulation (pronunciation) |
| Scheduling | Custom ML profiler (`SQLiteMLVocabularyProfiler`): char embeddings + correct/incorrect counts + recency → priority ordering |
| Pronunciation | Recording + audio comparison (`librosa` on desktop, native comparators on Android/iOS) |
| Audio | Bundled sound files; fallback TTS via an **unofficial Google Translate endpoint** (`media_service.py`) |
| Data | Local SQLite; JSON import/export of a language pair; no account, no sync |
| Platforms | iOS, Android, Linux (Snap/Flatpak/AppImage), Windows, macOS |
| UI | 26 interface languages, light/dark mode, Material 3 theme |
| Progress UI | `learning_progress` table exists, but there is **no statistics screen** for the learner |
| License | Open source (CC BY-NC-ND 4.0), no ads, no subscription |

**Distinctive strengths** worth keeping in front of the marketing message:

1. Truly cross-platform from a single codebase, including Linux desktop — rare among consumer apps.
2. Pronunciation practice built in, offline, and free (competitors like ELSA Speak are subscription-only).
3. Privacy: local-only data, no account, no tracking.
4. Very wide UI localisation (26 languages, incl. under-served ones: BE, KA, UZ, AZ, FA).
5. Arbitrary language pairs (not "English → X" only).

---

## 2. Competitive landscape

### 2.1 Flashcard / SRS tools (closest to Tlum's core)

| App | Model | Key strengths | Common complaints |
| --- | --- | --- | --- |
| **Anki / AnkiDroid** | Open source (AnkiMobile paid) | FSRS scheduler (default since 23.10), huge shared-deck library, add-ons, sync | Steep learning curve, no onboarding, complicated settings, dated UI, unreliable due-card notifications on Android |
| **Mnemosyne** | Open source, desktop | Simple, research-oriented | Small ecosystem, little mobile presence |
| **Quizlet** | Freemium, proprietary | Easy set creation, games, huge public sets | Paywalls on previously free features, ads |
| **Mochi / RemNote / Brainscape** | Freemium, proprietary | Markdown/notes integration, polished UI | Subscription, cloud-only |
| **F-Droid apps** (QuizFlow, Vocabulary Trainer, MyLexicon) | Open source, Android-only | Offline, CSV import/export, TTS | Basic UX, single platform |

### 2.2 Course-based apps

| App | Strengths | Common complaints |
| --- | --- | --- |
| **Duolingo** | Gamification, streaks, polished UX, free tier | Streak anxiety/loss-aversion pressure, shallow speaking practice, "vocab but no conversation" |
| **Babbel** | Structured lessons, dialogues | Subscription renewal/refund complaints |
| **Memrise** | Native-speaker videos | 2022 pivot removed **user-created courses** — a core reason long-time users chose it; price |
| **Drops** | Beautiful visual vocabulary, 5-minute sessions | Daily review pile of 100+ words, audio/text mismatches, false sense of mastery, little speaking |

### 2.3 Pronunciation-focused apps

| App | Strengths | Gaps |
| --- | --- | --- |
| **ELSA Speak** | Phoneme-level scoring for pronunciation, fluency, intonation, stress | English-only, subscription, little focus on suprasegmentals (per academic review) |
| **Speechling** | Human coach feedback | Limited free tier |
| **OpenPronounce / pronounce-assess** (OSS) | Wav2Vec2 phoneme-level scoring, self-hostable | Research-grade, English-focused |

### 2.4 Immersion / sentence-mining tools

| App | Strengths |
| --- | --- |
| **Language Reactor** | Dual subtitles on Netflix/YouTube, click-to-save phrases |
| **LingQ / Readlang** | Learn vocabulary from imported texts; word status tracking |
| **Migaku** | One-click sentence mining to Anki |

These show strong demand for **learning words in context** (example sentences), not isolated word pairs.

---

## 3. What users ask for (cross-app themes)

1. **Simple onboarding and ready-made content.** Most users never touch CSV/YAML import; apps succeed by
   shipping prepared decks. Anki's biggest complaint is setup complexity.
2. **Control over review load.** Drops/Anki users complain about review piles; they want daily limits,
   "new words per day", and the ability to hide/suspend words.
3. **Speaking practice, not just recognition.** A recurring gap: "I can read but can't talk".
4. **Reliable audio** that matches the text; native-quality TTS.
5. **Motivation without punishment.** Users like progress/streaks but dislike guilt-heavy streak loss
   (streak freezes, weekly goals instead of daily).
6. **Working reminders/notifications** (AnkiDroid's are often reported not to fire).
7. **Community / user-created content** (Memrise backlash proves its value).
8. **Sync across devices** while keeping data ownership.
9. **Context: example sentences, images, mnemonics.**
10. **Transparent, fair pricing** — a natural advantage for Tlum.
11. **AI assistance** for generating cards, examples and explanations (frequently requested on review sites).

---

## 4. Gap analysis: what Tlum is missing

| # | Gap | Evidence | Effort | Impact |
| --- | --- | --- | --- | --- |
| G1 | **No learner-facing progress/statistics** (data already in `learning_progress`) | All competitors show progress; users want motivation | S | High |
| G2 | **Scheduler is ad-hoc**, not a proven SRS (no due dates, no intervals) | FSRS is now the de-facto standard (Anki default) | M | High |
| G3 | **No ready-made starter content / deck catalogue** | #1 onboarding complaint across SRS apps | M | High |
| G4 | **No daily goal / review limits / suspend word** | Drops & Anki review-pile complaints | S | Medium |
| G5 | **No reminders/notifications** | Habit formation; AnkiDroid complaints show it must be reliable | M | Medium |
| G6 | **No CSV / Anki (`.apkg`) import** — JSON only | Interoperability; migration path from Anki/Quizlet | S–M | High |
| G7 | **TTS relies on an unofficial Google endpoint** | Fragile (can break or be blocked), sends words to a third party, conflicts with privacy story | M | High |
| G8 | **No example sentences / notes / cloze cards** | Sentence-mining tools' popularity | M | Medium |
| G9 | **No sync / backup** beyond manual export | Multi-device users (Tlum is on 5 platforms!) | L | Medium |
| G10 | **Pronunciation feedback is a single similarity score** | ELSA-style per-phoneme feedback is the market expectation | L | Medium |
| G11 | **No quiz modes** beyond the four practices (multiple choice, matching, listening choice) | Quizlet/Duolingo variety keeps sessions engaging | S–M | Medium |
| G12 | **No onboarding / tutorial** | Anki reviews: unclear features | S | Medium |
| G13 | **Not on F-Droid** | F-Droid users explicitly look for privacy-friendly language apps; note CC BY-NC-ND is not OSI-approved, which blocks official F-Droid inclusion | — | Low–Medium |

---

## 5. Proposal (prioritised roadmap)

### Phase 1 — Quick wins (low effort, high visibility)

1. **Statistics screen** (G1): words learned / due / struggling, accuracy per category, activity calendar
   (heatmap), per-practice breakdown. Uses existing `learning_progress` data.
2. **Session settings** (G4): new words per day, max reviews per session, "suspend/mark as known".
3. **Gentle streaks** (theme 5): weekly goal + streak freeze; never punitive messaging.
4. **CSV import/export** (G6) with column mapping (origin, translation, category, optional sound/image).
5. **First-run onboarding** (G12): pick native/target language → offer a starter pack → explain the four
   practices in 3 screens.

### Phase 2 — Learning effectiveness

6. **Adopt FSRS** (G2) via `fsrs` (py-fsrs, MIT, pure Python — works with Kivy/p4a). Map practice outcomes
   to Again/Hard/Good/Easy (e.g. Harmonica typos → Hard, wrong → Again). Keep the current ML profiler as a
   tie-breaker for ordering new words by complexity. Add `due_at`, `stability`, `difficulty` columns via a
   new DB patch in `src/patches/`.
7. **Starter content catalogue** (G3): curated frequency lists (top 500/1000 words) per language pair,
   downloadable from the GitHub repo/releases, using the existing JSON import format.
8. **Example sentences & notes** (G8): extend `vocabulary_items` with `example`, `note`; add a cloze
   variant of Harmonica (fill the gap in a sentence).
9. **More quiz modes** (G11): multiple choice, listening choice (hear → pick), matching pairs.

### Phase 3 — Platform & trust

10. **Replace unofficial TTS** (G7): use OS-native TTS (Android `TextToSpeech`, iOS `AVSpeechSynthesizer`,
    `espeak-ng`/`speech-dispatcher` on Linux, SAPI on Windows) via `plyer.tts` or native bridges; optionally
    offline neural TTS (e.g. Piper) on desktop. Keeps the "offline & private" promise.
11. **Reminders** (G5): local notifications (`plyer.notification` on desktop, native scheduling on mobile),
    tested on Doze/battery-optimised Android devices.
12. **Backup & sync** (G9): start with automatic local backups + "export to cloud folder" (user picks
    Google Drive/iCloud/Nextcloud folder via the system file picker); later optional self-hostable sync
    (WebDAV) — no Tlum-owned servers needed.
13. **Anki `.apkg` import** (G6): read the SQLite inside the archive; map front/back fields + media.

### Phase 4 — Differentiators

14. **Phoneme-level pronunciation feedback** (G10): evaluate a small on-device phoneme model
    (wav2vec2-CTC, as in OpenPronounce / pronounce-assess) on desktop first; highlight mispronounced
    segments and show pitch/intonation contour against the reference (addresses ELSA's suprasegmental gap).
15. **Community deck sharing** (theme 7): a GitHub-hosted index of user-contributed language-pair packs
    (PR-based moderation) — fills the hole Memrise left, with zero server cost.
16. **Optional AI helper** (theme 11): opt-in, bring-your-own-key or local model: generate example
    sentences, mnemonics, and translations for a category. Must stay optional to preserve privacy.
17. **Image support in practices**: the `image` field already exists in `VocabularyItem` — surface it on
    Cards and allow picking images when adding words (Drops-style visual learning).

### Not recommended

- Subscription or ads — Tlum's free/open positioning is a core differentiator against Babbel/Memrise.
- Full course-based curriculum (Duolingo/Babbel style) — very high content cost; better served by
  community decks + starter packs.
- Punitive gamification (leaderboards, hearts/lives) — a top complaint about Duolingo.

---

## 6. Positioning statement (suggested)

> **Tlum — your own words, every device, fully offline.** A free, open-source vocabulary and pronunciation
> trainer for any language pair, with smart repetition and speaking practice, and no account, no ads,
> no tracking.

---

## Sources

- [RemNote — Best Anki alternatives](https://www.remnote.com/blog/best-anki-alternatives)
- [AlternativeTo — Anki alternatives](https://www.alternativeto.net/software/anki/)
- [StudyCardsAI — 10 Best Anki Alternatives in 2026](https://studycardsai.com/best-anki-alternatives)
- [StudyCardsAI — Best Flashcard Apps 2026](https://studycardsai.com/best-flashcard-apps-2026)
- [Open Source Alternatives — Anki](https://www.opensourcealternatives.to/item/anki)
- [G2 — Anki reviews](https://www.g2.com/products/anki/reviews_and_filters)
- [Capterra — Anki reviews](https://www.capterra.com/p/229584/Anki/reviews/)
- [GetApp — Anki](https://www.getapp.com/education-childcare-software/a/anki/)
- [Habr — discussion on flashcard apps](https://habr.com/en/articles/460841/comments)
- [Unstar — Language learning app reviews: Duolingo, Babbel, Rosetta Stone (2026)](https://unstar.app/blog/language-learning-app-reviews-duolingo-babbel-rosetta-stone-2026)
- [Unstar — Language learning apps ranked 2026](https://unstar.app/blog/duolingo-babbel-rosetta-stone-busuu-memrise-language-learning-apps-ranked-2026)
- [Trustpilot — Drops reviews](https://ca.trustpilot.com/review/languagedrops.com)
- [Kimola — Drops App Store feedback analysis](https://kimola.com/reports/elevate-your-language-app-with-expert-feedback-analysis-app-store-us-147869)
- [Users' Perceptions of Language Learning Apps: A Case Study (Univ. of Debrecen)](https://dea.lib.unideb.hu/items/9e6d98e9-7306-4b36-8df5-9edce27f5fd2/full)
- [Iowa State — PSLLT review of ELSA](https://iastatedigitalpress.com/psllt/article/15397/galley/13528/view)
- [TalkDrill — ELSA Speak vs Speechling](https://www.talkdrill.com/blog/compare/elsa-speak-vs-speechling/)
- [OpenPronounce (GitHub)](https://github.com/Halleck45/OpenPronounce)
- [pronounce-assess (PyPI)](https://pypi.org/project/pronounce-assess/)
- [speechocean762 dataset (OpenSLR)](https://openslr.org/101/)
- [py-fsrs / `fsrs` (PyPI)](https://pypi.org/project/fsrs)
- [Comprehensible input apps 2026](https://comprehensibleinput.it.com/blog/best-comprehensible-input-apps-2026)
- [Mandarin Mosaic — sentence mining apps](https://mandarinmosaic.com/blog/chinese-sentence-mining-app)
- [Readlang forum — LingQ and alternatives](https://forum.readlang.com/t/anyone-here-use-used-lingq-or-any-other-alternatives/123)
- [F-Droid forum — privacy-friendly language learning apps](https://forum.f-droid.org/t/could-you-add-privacy-friendly-language-learning-apps/6911)
- [IzzyOnDroid — QuizFlow](https://apt.izzysoft.de/fdroid/index/apk/jdm.apps.quizflow)
- [F-Droid — Vocabulary Trainer](https://f-droid.org/en/packages/vocabletrainer.heinecke.aron.vocabletrainer)
- [F-Droid — MyLexicon](https://f-droid.org/pl/packages/com.aryanyadav.mylexicon/)

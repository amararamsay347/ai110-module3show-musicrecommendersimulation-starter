# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

This is a content-based recommender: it looks at what a song is like (its attributes) and compares that to what a user says they like. It does not use other users' listening data. It works in two steps: a **scoring rule** rates how well one song fits one user, and a **ranking rule** sorts every song by that rating and keeps the best few. Energy is weighted highest (3.0 points), mood is in the middle (1.5) and genre is a smaller bonus (0.75), because each tells us something different: energy is how intense the song is, mood is the feel of the moment, and genre is the broad style. Valence, acousticness, and danceability add smaller tiebreaker points.

### What each `Song` uses

Each song in `data/songs.csv` (20 songs) has an id, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. The recommender scores six of these:

- **Genre** (a label such as pop, lofi, rock): the broad style.
- **Mood** (a label such as chill, happy, intense): the feel of the song in a word.
- **Energy** (0 to 1): how intense or active the song is.
- **Valence** (0 to 1): how positive or happy the song sounds, from dark to bright.
- **Acousticness** (0 to 1): how acoustic, as opposed to electronic, the song is.
- **Danceability** (0 to 1): how easy the song is to dance to.

Tempo is left out on purpose. In this catalog it mostly repeats what energy already says (fast songs are high-energy), so including it would count the same preference twice.

### What the user profile stores

The user profile is a simple taste description. `src/main.py` passes it to the recommender as a dictionary:

- `genre`: the genre they want most.
- `mood`: the mood they are looking for.
- `energy`: the energy level they want (0 to 1).
- `valence`, `acousticness`, `danceability` (optional): targets between 0 and 1. If a profile leaves one out, that feature is skipped instead of scored.

### How a score is computed

Every song starts at 0 and earns points from up to six signals, for a maximum of 6.75. The full table is in the [Final algorithm recipe](#final-algorithm-recipe) below. In short:

- **Genre:** +0.75 for an exact match, otherwise 0.
- **Mood:** +1.5 for an exact match, +0.75 for a related mood (for example "relaxed" for a "chill" user), otherwise 0.
- **Energy:** up to 3.0, calculated as `3.0 × (1 − |song.energy − target|)`. A song gets full credit for hitting the target and less the further away it is, in either direction, so a user who wants calm music is not pushed toward loud songs.
- **Valence, acousticness, danceability:** up to 0.5 each, using the same closeness rule.

Energy is the dominant signal (3.0), mood is in the middle (1.5) and genre is a smaller bonus (0.75). This comes from a weight-shift experiment that doubled energy and halved genre from the original equal 1.5 weights (see [Experiments You Tried](#experiments-you-tried)). The smaller numeric features break ties between songs that fit equally well on the main three.

### How songs are chosen

1. Score every song in the catalog against the user's profile.
2. Sort the songs from highest to lowest score. Python's sort is stable, so songs with equal scores keep their order in the CSV, and the same input always gives the same output.
3. Return the top `k` songs (5 by default), each with a short explanation built from the scoring reasons, such as "genre match: pop (+0.75); mood match: happy (+1.50); energy 0.82 vs target 0.80 (+2.94)."

### Diagram (data flow)

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: User Prefs  (src/main.py)                            │
│   {"genre": "pop", "mood": "happy", "energy": 0.8}          │
│   optional: valence, acousticness, danceability targets     │
└──────────────────────────────┬──────────────────────────────┘
                               │
        data/songs.csv ──► load_songs()  →  list of 20 song dicts
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ PROCESS: The Loop  (recommend_songs)                        │
│                                                             │
│   for each song in songs:                                   │
│       score_song(user_prefs, song)                          │
│       ┌──────────────────────────────────────────────┐      │
│       │ genre match            → +0.75 or 0          │      │
│       │ mood match / related   → +1.5 / +0.75 / 0    │      │
│       │ energy closeness       → 0 to 3.0            │      │
│       │ valence, acoustic,     → 0 to 0.5 each       │      │
│       │ danceability (if set)                        │      │
│       └──────────────────────────────────────────────┘      │
│       → (score, reasons)                                    │
│       append (song, score, "reason; reason; ...")           │
└──────────────────────────────┬──────────────────────────────┘
                               │  20 scored songs
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT: The Ranking                                         │
│   sort by score, highest first  →  take top K (default 5)   │
│                                                             │
│   1. Sunrise City     5.19  genre + mood + energy           │
│   2. Rooftop Lights   4.38  mood + energy                   │
│   3. Fiesta Nights    3.69  related mood + energy           │
│   ...                                                       │
│   main.py prints title, score, and "Because: ..." reasons   │
└─────────────────────────────────────────────────────────────┘
```

Each song is scored independently against the user's prefs; ranking happens once, after the loop. The reasons are returned with the score so each recommendation can be explained without recomputing.

### Final algorithm recipe

The scoring is implemented in `score_song()` in `src/recommender.py`. Every song starts at 0 and earns points (maximum 6.75 = 0.75 + 1.5 + 3.0 + 3 × 0.5):

| Step | Signal | Points | Rule |
|---|---|---|---|
| 1 | Genre | 0.75 | Exact match gets +0.75, otherwise 0. |
| 2 | Mood | 1.5 | Exact match gets +1.5. A related mood (same group in `RELATED_MOODS`) gets +0.75. Otherwise 0. |
| 3 | Energy | up to 3.0 | `3.0 × (1 − abs(song.energy − target_energy))` |
| 4 | Valence | up to 0.5 | `0.5 × (1 − abs(song.valence − target_valence))`, only if the profile sets it |
| 5 | Acousticness | up to 0.5 | Same closeness rule, only if the profile sets it |
| 6 | Danceability | up to 0.5 | Same closeness rule, only if the profile sets it |

Then `recommend_songs()` repeats this for every song in the CSV, sorts by score from highest to lowest, and returns the top `k` (5 by default) with the list of reasons that produced each score.

Design choices behind the recipe:

- **Energy is weighted highest (3.0), mood 1.5, genre 0.75.** Energy was doubled and genre halved from the original equal 1.5 weights, so closeness in energy matters more than a label match.
- **Genre plus mood is worth 2.25.** That is less than a perfect energy match (3.0), so a song with the right energy can beat a song with the right labels.
- **Valence, acousticness and danceability are tiebreakers** at 0.5 each.
- **Tempo is left out** because it largely repeats what energy already says.
- **Numeric features use closeness, not "higher is better,"** so a user who wants calm music is not pushed toward loud songs.

### Potential biases

- **Energy can now dominate.** It is worth 3.0 of 6.75 points. A song with close energy but a different genre and mood can beat a song that matches both labels, so a user who writes `genre=metal` but `energy=0.2` will get almost no metal.
- **Genre can still tilt the ranking.** 17 of the 20 songs have a unique genre, so a genre match gives a bonus to one or two songs. For a pop/happy user, an intense pop song can outrank a better-sounding song from another genre.
- **Exact labels penalize near-misses.** "Indie pop" gets no genre credit for a "pop" user. Mood has partial credit, but only through hand-picked groups, and a mood outside every group (for example "romantic") never gets partial credit.
- **The related-mood groups reflect my judgment, not data.** Someone else might group "moody" or "confident" differently, which would change the rankings.
- **Energy differences are compressed.** Because the score is `1 − abs(diff)`, even a poor energy match still earns about a third of the points, so energy separates songs less sharply than its weight suggests.
- **The catalog shapes who is served well.** There are 20 songs and most genres and moods appear once. Users who like lofi or chill (3 songs each) get a real choice, while users who like metal or classical get one strong match and weak filler after it. The catalog is also small and skewed toward Western genres.
- **Scores are not comparable across profiles.** Valence, acousticness and danceability only count when the profile sets them, so a three-preference profile is scored out of 5.25 and a full profile out of 6.75.
- **No diversity or personalization.** The same artist can fill several top spots (Neon Echo and LoRoom each have two songs), and the system never learns from what a user skips or plays.

### Known limitations

- Genre is exact-match only, so "indie pop" gets no credit for a "pop" user. Mood has partial credit only through the hand-picked `RELATED_MOODS` groups.
- The catalog is small (20 songs), and most genres and moods appear only once.
- The weights and mood groups were chosen by hand. The current weights (genre 0.75, mood 1.5, energy 3.0) came from one weight-shift experiment and have not been tuned further.
- Only the scoring and ranking functions (`score_song`, `recommend_songs`, `load_songs`) are implemented. The `UserProfile` dataclass and `Recommender` class in `src/recommender.py` are still stubs, so the unit tests do not exercise the real scoring yet.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Terminal output of `python src/main.py` (top 5 for the starter profile and each test profile), using the current weights (genre 0.75, mood 1.5, energy 3.0; max score 6.75):

### Starter Profile

```
============================================================
TOP 5 RECOMMENDATIONS
Profile: genre=pop, mood=happy, energy=0.8
============================================================

#1  Sunrise City by Neon Echo
    Score: 5.19   [pop / happy]
    Reasons:
      - genre match: pop (+0.75)
      - mood match: happy (+1.50)
      - energy 0.82 vs target 0.80 (+2.94)
------------------------------------------------------------

#2  Rooftop Lights by Indigo Parade
    Score: 4.38   [indie pop / happy]
    Reasons:
      - mood match: happy (+1.50)
      - energy 0.76 vs target 0.80 (+2.88)
------------------------------------------------------------

#3  Fiesta Nights by Sol y Fuego
    Score: 3.69   [latin / playful]
    Reasons:
      - related mood: playful ~ happy (+0.75)
      - energy 0.82 vs target 0.80 (+2.94)
------------------------------------------------------------

#4  Gym Hero by Max Pulse
    Score: 3.36   [pop / intense]
    Reasons:
      - genre match: pop (+0.75)
      - energy 0.93 vs target 0.80 (+2.61)
------------------------------------------------------------

#5  Neon Pulse by Circuit Bloom
    Score: 3.30   [edm / euphoric]
    Reasons:
      - related mood: euphoric ~ happy (+0.75)
      - energy 0.95 vs target 0.80 (+2.55)
------------------------------------------------------------
```

### High-Energy Pop

```
============================================================
TOP 5 RECOMMENDATIONS
Profile: genre=pop, mood=happy, energy=0.85, valence=0.85, danceability=0.85
============================================================

#1  Sunrise City by Neon Echo
    Score: 6.12   [pop / happy]
    Reasons:
      - genre match: pop (+0.75)
      - mood match: happy (+1.50)
      - energy 0.82 vs target 0.85 (+2.91)
      - valence 0.84 vs target 0.85 (+0.49)
      - danceability 0.79 vs target 0.85 (+0.47)
------------------------------------------------------------

#2  Rooftop Lights by Indigo Parade
    Score: 5.20   [indie pop / happy]
    Reasons:
      - mood match: happy (+1.50)
      - energy 0.76 vs target 0.85 (+2.73)
      - valence 0.81 vs target 0.85 (+0.48)
      - danceability 0.82 vs target 0.85 (+0.48)
------------------------------------------------------------

#3  Fiesta Nights by Sol y Fuego
    Score: 4.62   [latin / playful]
    Reasons:
      - related mood: playful ~ happy (+0.75)
      - energy 0.82 vs target 0.85 (+2.91)
      - valence 0.88 vs target 0.85 (+0.48)
      - danceability 0.90 vs target 0.85 (+0.47)
------------------------------------------------------------

#4  Gym Hero by Max Pulse
    Score: 4.46   [pop / intense]
    Reasons:
      - genre match: pop (+0.75)
      - energy 0.93 vs target 0.85 (+2.76)
      - valence 0.77 vs target 0.85 (+0.46)
      - danceability 0.88 vs target 0.85 (+0.48)
------------------------------------------------------------

#5  Neon Pulse by Circuit Bloom
    Score: 4.39   [edm / euphoric]
    Reasons:
      - related mood: euphoric ~ happy (+0.75)
      - energy 0.95 vs target 0.85 (+2.70)
      - valence 0.90 vs target 0.85 (+0.47)
      - danceability 0.92 vs target 0.85 (+0.46)
------------------------------------------------------------
```

### Chill Lofi

```
============================================================
TOP 5 RECOMMENDATIONS
Profile: genre=lofi, mood=focused, energy=0.38, acousticness=0.75
============================================================

#1  Focus Flow by LoRoom
    Score: 5.67   [lofi / focused]
    Reasons:
      - genre match: lofi (+0.75)
      - mood match: focused (+1.50)
      - energy 0.40 vs target 0.38 (+2.94)
      - acousticness 0.78 vs target 0.75 (+0.48)
------------------------------------------------------------

#2  Midnight Coding by LoRoom
    Score: 4.86   [lofi / chill]
    Reasons:
      - genre match: lofi (+0.75)
      - related mood: chill ~ focused (+0.75)
      - energy 0.42 vs target 0.38 (+2.88)
      - acousticness 0.71 vs target 0.75 (+0.48)
------------------------------------------------------------

#3  Library Rain by Paper Lanterns
    Score: 4.86   [lofi / chill]
    Reasons:
      - genre match: lofi (+0.75)
      - related mood: chill ~ focused (+0.75)
      - energy 0.35 vs target 0.38 (+2.91)
      - acousticness 0.86 vs target 0.75 (+0.45)
------------------------------------------------------------

#4  Coffee Shop Stories by Slow Stereo
    Score: 4.15   [jazz / relaxed]
    Reasons:
      - related mood: relaxed ~ focused (+0.75)
      - energy 0.37 vs target 0.38 (+2.97)
      - acousticness 0.89 vs target 0.75 (+0.43)
------------------------------------------------------------

#5  Spacewalk Thoughts by Orbit Bloom
    Score: 3.87   [ambient / chill]
    Reasons:
      - related mood: chill ~ focused (+0.75)
      - energy 0.28 vs target 0.38 (+2.70)
      - acousticness 0.92 vs target 0.75 (+0.41)
------------------------------------------------------------
```

### Deep Intense Rock

```
============================================================
TOP 5 RECOMMENDATIONS
Profile: genre=rock, mood=intense, energy=0.92, acousticness=0.1
============================================================

#1  Storm Runner by Voltline
    Score: 5.72   [rock / intense]
    Reasons:
      - genre match: rock (+0.75)
      - mood match: intense (+1.50)
      - energy 0.91 vs target 0.92 (+2.97)
      - acousticness 0.10 vs target 0.10 (+0.50)
------------------------------------------------------------

#2  Gym Hero by Max Pulse
    Score: 4.94   [pop / intense]
    Reasons:
      - mood match: intense (+1.50)
      - energy 0.93 vs target 0.92 (+2.97)
      - acousticness 0.05 vs target 0.10 (+0.47)
------------------------------------------------------------

#3  Iron Requiem by Black Anvil
    Score: 4.07   [metal / aggressive]
    Reasons:
      - related mood: aggressive ~ intense (+0.75)
      - energy 0.97 vs target 0.92 (+2.85)
      - acousticness 0.04 vs target 0.10 (+0.47)
------------------------------------------------------------

#4  Concrete Crown by Kingpin Atlas
    Score: 3.82   [hip hop / confident]
    Reasons:
      - related mood: confident ~ intense (+0.75)
      - energy 0.78 vs target 0.92 (+2.58)
      - acousticness 0.12 vs target 0.10 (+0.49)
------------------------------------------------------------

#5  Neon Pulse by Circuit Bloom
    Score: 3.38   [edm / euphoric]
    Reasons:
      - energy 0.95 vs target 0.92 (+2.91)
      - acousticness 0.03 vs target 0.10 (+0.46)
------------------------------------------------------------
```

---

## Experiments You Tried

### Weight shift: double energy, halve genre

| Signal | Original weight | Current weight |
|---|---|---|
| Genre | 1.5 | **0.75** |
| Mood | 1.5 | 1.5 |
| Energy | 1.5 | **3.0** |
| Valence, acousticness, danceability | 0.5 each | 0.5 each |
| **Maximum score** | 6.0 | **6.75** |

**Change:** `GENRE_POINTS` 1.5 → 0.75 and `ENERGY_POINTS` 1.5 → 3.0 in `src/recommender.py`. A check confirmed that a perfect self-match scores exactly 6.75 and that no score goes above 6.75 or below 0.

**What happened:**

- The #1 song did not change for any of the four profiles, so the best match is stable when genre, mood and energy agree.
- Lower ranks changed. For the Starter Profile and High-Energy Pop, *Fiesta Nights* (latin/playful, energy 0.82) moved from #4 to #3, ahead of *Gym Hero* (pop/intense, energy 0.93), because a pop genre match is now worth less than a closer energy.
- Gaps narrowed. In Deep Intense Rock the lead of *Storm Runner* over *Gym Hero* shrank from 1.52 to 0.78, and in Chill Lofi the gap between the third lofi song and the first non-lofi song fell from 1.48 to 0.71.

**Takeaway:** the shift gives more varied results and weakens genre as a gatekeeper, but energy now outweighs genre and mood combined, so users whose genre and energy preferences conflict get less of the genre they asked for.

Other ideas to try: add tempo to the score, or compare behavior across more types of users.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this




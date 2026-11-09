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

This is a content-based recommender: it looks at what a song is like (its attributes) and compares that to what a user says they like. It does not use other users' listening data. It works in two steps: a **scoring rule** rates how well one song fits one user, and a **ranking rule** sorts every song by that rating and keeps the best few. Genre, mood, and energy are weighted equally because each tells us something different: genre is the broad style, mood is the feel of the moment, and energy is how intense the song is. Valence, acousticness, and danceability add smaller tiebreaker points.

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

Every song starts at 0 and earns points from up to six signals, for a maximum of 6.0. The full table is in the [Final algorithm recipe](#final-algorithm-recipe) below. In short:

- **Genre:** +1.5 for an exact match, otherwise 0.
- **Mood:** +1.5 for an exact match, +0.75 for a related mood (for example "relaxed" for a "chill" user), otherwise 0.
- **Energy:** up to 1.5, calculated as `1.5 × (1 − |song.energy − target|)`. A song gets full credit for hitting the target and less the further away it is, in either direction, so a user who wants calm music is not pushed toward loud songs.
- **Valence, acousticness, danceability:** up to 0.5 each, using the same closeness rule.

Genre, mood, and energy are equal so that no single signal dominates. Matching two of them (3.0 points) beats matching one (1.5), and the smaller numeric features break ties between songs that fit equally well on the main three.

### How songs are chosen

1. Score every song in the catalog against the user's profile.
2. Sort the songs from highest to lowest score. Python's sort is stable, so songs with equal scores keep their order in the CSV, and the same input always gives the same output.
3. Return the top `k` songs (5 by default), each with a short explanation built from the scoring reasons, such as "genre match: pop (+1.50); mood match: happy (+1.50); energy 0.82 vs target 0.80 (+1.47)."

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
│       │ genre match            → +1.5  or 0          │      │
│       │ mood match / related   → +1.5 / +0.75 / 0    │      │
│       │ energy closeness       → 0 to 1.5            │      │
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
│   1. Sunrise City     4.47  genre + mood + energy           │
│   2. Rooftop Lights   2.94  mood + energy                   │
│   3. Gym Hero         2.80  genre + energy                  │
│   ...                                                       │
│   main.py prints title, score, and "Because: ..." reasons   │
└─────────────────────────────────────────────────────────────┘
```

Each song is scored independently against the user's prefs; ranking happens once, after the loop. The reasons are returned with the score so each recommendation can be explained without recomputing.

### Final algorithm recipe

The scoring is implemented in `score_song()` in `src/recommender.py`. Every song starts at 0 and earns points (maximum 6.0):

| Step | Signal | Points | Rule |
|---|---|---|---|
| 1 | Genre | 1.5 | Exact match gets +1.5, otherwise 0. |
| 2 | Mood | 1.5 | Exact match gets +1.5. A related mood (same group in `RELATED_MOODS`) gets +0.75. Otherwise 0. |
| 3 | Energy | up to 1.5 | `1.5 × (1 − abs(song.energy − target_energy))` |
| 4 | Valence | up to 0.5 | `0.5 × (1 − abs(song.valence − target_valence))`, only if the profile sets it |
| 5 | Acousticness | up to 0.5 | Same closeness rule, only if the profile sets it |
| 6 | Danceability | up to 0.5 | Same closeness rule, only if the profile sets it |

Then `recommend_songs()` repeats this for every song in the CSV, sorts by score from highest to lowest, and returns the top `k` (5 by default) with the list of reasons that produced each score.

Design choices behind the recipe:

- **Genre, mood and energy are equal at 1.5 each**, so no single signal dominates. A lone genre match ties with a lone mood match or with perfect energy.
- **Matching two signals beats matching one.** Genre plus mood earns 3.0 before any numeric points.
- **Valence, acousticness and danceability are tiebreakers** at 0.5 each.
- **Tempo is left out** because it largely repeats what energy already says.
- **Numeric features use closeness, not "higher is better,"** so a user who wants calm music is not pushed toward loud songs.

### Potential biases

- **Genre plus mood can dominate.** Together they are worth 3.0 of 6.0 points. A song that matches both labels will usually beat a song that matches the user's energy, valence and acousticness better but carries a different label. The system may bury songs that would sound right.
- **Genre can still tilt the ranking.** 17 of the 20 songs have a unique genre, so a genre match gives a bonus to one or two songs. For a pop/happy user, an intense pop song can outrank a better-sounding song from another genre.
- **Exact labels penalize near-misses.** "Indie pop" gets no genre credit for a "pop" user. Mood has partial credit, but only through hand-picked groups, and a mood outside every group (for example "romantic") never gets partial credit.
- **The related-mood groups reflect my judgment, not data.** Someone else might group "moody" or "confident" differently, which would change the rankings.
- **Energy differences are compressed.** Because the score is `1 − abs(diff)`, even a poor energy match still earns about a third of the points, so energy separates songs less sharply than its weight suggests.
- **The catalog shapes who is served well.** There are 20 songs and most genres and moods appear once. Users who like lofi or chill (3 songs each) get a real choice, while users who like metal or classical get one strong match and weak filler after it. The catalog is also small and skewed toward Western genres.
- **Scores are not comparable across profiles.** Valence, acousticness and danceability only count when the profile sets them, so a three-preference profile is scored out of 4.5 and a full profile out of 6.0.
- **No diversity or personalization.** The same artist can fill several top spots (Neon Echo and LoRoom each have two songs), and the system never learns from what a user skips or plays.

### Known limitations

- Genre is exact-match only, so "indie pop" gets no credit for a "pop" user. Mood has partial credit only through the hand-picked `RELATED_MOODS` groups.
- The catalog is small (20 songs), and most genres and moods appear only once.
- The weights and mood groups were chosen by hand and should be tested and adjusted, for example by halving genre and doubling energy and comparing the top 5.
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

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
============================================================
TOP 5 RECOMMENDATIONS
Profile: genre=pop, mood=happy, energy=0.8
============================================================

#1  Sunrise City by Neon Echo
    Score: 4.47   [pop / happy]
    Reasons:
      - genre match: pop (+1.50)
      - mood match: happy (+1.50)
      - energy 0.82 vs target 0.80 (+1.47)
------------------------------------------------------------

#2  Rooftop Lights by Indigo Parade
    Score: 2.94   [indie pop / happy]
    Reasons:
      - mood match: happy (+1.50)
      - energy 0.76 vs target 0.80 (+1.44)
------------------------------------------------------------

#3  Gym Hero by Max Pulse
    Score: 2.80   [pop / intense]
    Reasons:
      - genre match: pop (+1.50)
      - energy 0.93 vs target 0.80 (+1.30)
------------------------------------------------------------

#4  Fiesta Nights by Sol y Fuego
    Score: 2.22   [latin / playful]
    Reasons:
      - related mood: playful ~ happy (+0.75)
      - energy 0.82 vs target 0.80 (+1.47)
------------------------------------------------------------

#5  Neon Pulse by Circuit Bloom
    Score: 2.03   [edm / euphoric]
    Reasons:
      - related mood: euphoric ~ happy (+0.75)
      - energy 0.95 vs target 0.80 (+1.28)
------------------------------------------------------------
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

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




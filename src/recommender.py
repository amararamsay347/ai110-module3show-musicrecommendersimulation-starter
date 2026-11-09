from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv

    int_fields = ("id", "popularity", "explicit")
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness",
                    "instrumentalness")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in int_fields:
                row[key] = int(row[key])
            for key in float_fields:
                row[key] = float(row[key])
            row["mood_tags"] = row["mood_tags"].split("|")
            songs.append(row)
    return songs


# ---------------------------------------------------------------------------
# Scoring logic design (max 6.75 points)
#
# Weight-shift experiment: energy is doubled (1.5 -> 3.0) and genre is halved
# (1.5 -> 0.75) relative to the original equal-weight design. Energy is now the
# dominant signal, mood sits in the middle, and genre is a smaller bonus.
# Valence, acousticness and danceability (0.5 each) act as tiebreakers. Tempo
# is omitted because it is largely redundant with energy.
#
# Max score = GENRE + MOOD + ENERGY + sum(NUMERIC) = 0.75 + 1.5 + 3.0 + 1.5
#           = 6.75 (only reachable when every preference is supplied).
# Original weights (genre 1.5, energy 1.5) gave a max of 6.0.
# ---------------------------------------------------------------------------
GENRE_POINTS = 0.75
MOOD_POINTS = 1.5
RELATED_MOOD_FACTOR = 0.5  # related mood earns half of MOOD_POINTS
ENERGY_POINTS = 3.0
NUMERIC_POINTS = {"valence": 0.5, "acousticness": 0.5, "danceability": 0.5}
MAX_SCORE = GENRE_POINTS + MOOD_POINTS + ENERGY_POINTS + sum(NUMERIC_POINTS.values())

# ---------------------------------------------------------------------------
# Ranking strategies: each mode re-weights the same signals. "balanced" is the
# default and matches the weights above. Switch modes via the `mode` argument.
# ---------------------------------------------------------------------------
STRATEGIES: Dict[str, Dict] = {
    "balanced": {
        "genre": GENRE_POINTS, "mood": MOOD_POINTS, "energy": ENERGY_POINTS,
        "numeric": dict(NUMERIC_POINTS),
    },
    "genre_first": {
        "genre": 3.0, "mood": 1.0, "energy": 1.5,
        "numeric": {"valence": 0.25, "acousticness": 0.25, "danceability": 0.25},
    },
    "mood_first": {
        "genre": 0.5, "mood": 3.0, "energy": 1.5,
        "numeric": {"valence": 0.75, "acousticness": 0.25, "danceability": 0.25},
    },
    "energy_focused": {
        "genre": 0.25, "mood": 0.5, "energy": 4.0,
        "numeric": {"valence": 0.25, "acousticness": 0.5, "danceability": 0.5},
    },
}
DEFAULT_MODE = "balanced"


def _get_strategy(mode: str) -> Dict:
    try:
        return STRATEGIES[mode]
    except KeyError:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {', '.join(STRATEGIES)}")


# Groups of moods that feel similar; a mood in the same group as the target
# earns partial credit.
RELATED_MOODS = [
    {"chill", "relaxed", "peaceful", "focused"},
    {"happy", "uplifting", "playful", "euphoric"},
    {"intense", "aggressive", "confident"},
    {"sad", "melancholic", "nostalgic", "moody"},
]


def _moods_related(a: str, b: str) -> bool:
    """Return True if both moods belong to the same RELATED_MOODS group."""
    return any(a in group and b in group for group in RELATED_MOODS)


def _closeness(song_value: float, target_value: float) -> float:
    """1.0 for an exact match, falling linearly to 0.0 at the widest gap."""
    return max(0.0, 1.0 - abs(song_value - target_value))


def score_song(user_prefs: Dict, song: Dict, mode: str = DEFAULT_MODE) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    user_prefs keys: "genre", "mood", "energy" (used by the main signals) and
    optionally "valence", "acousticness", "danceability" (0-1 targets).
    Any preference that is missing is simply skipped.
    `mode` selects a ranking strategy from STRATEGIES.
    Returns (score, reasons).
    """
    w = _get_strategy(mode)
    score = 0.0
    reasons: List[str] = []

    genre = user_prefs.get("genre")
    if genre and song["genre"].lower() == genre.lower():
        score += w["genre"]
        reasons.append(f"genre match: {song['genre']} (+{w['genre']:.2f})")

    mood = user_prefs.get("mood")
    if mood:
        if song["mood"].lower() == mood.lower():
            score += w["mood"]
            reasons.append(f"mood match: {song['mood']} (+{w['mood']:.2f})")
        elif _moods_related(song["mood"].lower(), mood.lower()):
            points = w["mood"] * RELATED_MOOD_FACTOR
            score += points
            reasons.append(
                f"related mood: {song['mood']} ~ {mood} (+{points:.2f})"
            )

    energy = user_prefs.get("energy")
    if energy is not None:
        points = w["energy"] * _closeness(song["energy"], energy)
        score += points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {energy:.2f} (+{points:.2f})"
        )

    for feature, weight in w["numeric"].items():
        target = user_prefs.get(feature)
        if target is not None:
            points = weight * _closeness(song[feature], target)
            score += points
            reasons.append(
                f"{feature} {song[feature]:.2f} vs target {target:.2f} (+{points:.2f})"
            )

    return score, reasons


# ---------------------------------------------------------------------------
# Diversity penalty: results are picked greedily. Each time a song is chosen,
# every remaining song by the same artist / in the same genre loses points for
# each already-selected song that shares that attribute, so one artist or genre
# can't fill the whole top-k unless it is far ahead of the alternatives.
# ---------------------------------------------------------------------------
ARTIST_PENALTY = 1.0  # per already-selected song beyond the free slots
ARTIST_FREE_SLOTS = 2  # an artist may have this many songs before penalties start
GENRE_PENALTY = 0.5   # per already-selected song in the same genre


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = DEFAULT_MODE,
    diversity: bool = True,
    artist_penalty: float = ARTIST_PENALTY,
    genre_penalty: float = GENRE_PENALTY,
    artist_free_slots: int = ARTIST_FREE_SLOTS,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    With `diversity=True` (default) a penalty is subtracted from songs whose
    artist or genre already appears earlier in the results. The returned score
    is the penalized score, and the penalty is listed in the reasons.
    Set `diversity=False` for a plain top-k by score.
    """
    remaining = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        remaining.append((song, score, reasons))

    if not diversity:
        remaining.sort(key=lambda item: item[1], reverse=True)
        return [(s, sc, "; ".join(r)) for s, sc, r in remaining[:k]]

    results: List[Tuple[Dict, float, str]] = []
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}

    while remaining and len(results) < k:
        best = None  # (adjusted, index, reasons)
        for i, (song, score, reasons) in enumerate(remaining):
            artist_key = song["artist"].lower()
            genre_key = song["genre"].lower()
            a_pen = artist_penalty * max(
                0, artist_counts.get(artist_key, 0) - artist_free_slots + 1
            )
            g_pen = genre_penalty * genre_counts.get(genre_key, 0)
            adjusted = score - a_pen - g_pen
            if best is None or adjusted > best[0]:
                extra = list(reasons)
                if a_pen:
                    extra.append(f"diversity: artist repeat ({song['artist']}) (-{a_pen:.2f})")
                if g_pen:
                    extra.append(f"diversity: genre repeat ({song['genre']}) (-{g_pen:.2f})")
                best = (adjusted, i, extra)

        adjusted, i, reasons = best
        song = remaining.pop(i)[0]
        artist_counts[song["artist"].lower()] = artist_counts.get(song["artist"].lower(), 0) + 1
        genre_counts[song["genre"].lower()] = genre_counts.get(song["genre"].lower(), 0) + 1
        results.append((song, adjusted, "; ".join(reasons)))

    return results

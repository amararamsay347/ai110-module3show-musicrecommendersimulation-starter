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

    int_fields = ("id",)
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in int_fields:
                row[key] = int(row[key])
            for key in float_fields:
                row[key] = float(row[key])
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


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    user_prefs keys: "genre", "mood", "energy" (used by the main signals) and
    optionally "valence", "acousticness", "danceability" (0-1 targets).
    Any preference that is missing is simply skipped.
    Returns (score, reasons).
    """
    score = 0.0
    reasons: List[str] = []

    genre = user_prefs.get("genre")
    if genre and song["genre"].lower() == genre.lower():
        score += GENRE_POINTS
        reasons.append(f"genre match: {song['genre']} (+{GENRE_POINTS:.2f})")

    mood = user_prefs.get("mood")
    if mood:
        if song["mood"].lower() == mood.lower():
            score += MOOD_POINTS
            reasons.append(f"mood match: {song['mood']} (+{MOOD_POINTS:.2f})")
        elif _moods_related(song["mood"].lower(), mood.lower()):
            points = MOOD_POINTS * RELATED_MOOD_FACTOR
            score += points
            reasons.append(
                f"related mood: {song['mood']} ~ {mood} (+{points:.2f})"
            )

    energy = user_prefs.get("energy")
    if energy is not None:
        points = ENERGY_POINTS * _closeness(song["energy"], energy)
        score += points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {energy:.2f} (+{points:.2f})"
        )

    for feature, weight in NUMERIC_POINTS.items():
        target = user_prefs.get(feature)
        if target is not None:
            points = weight * _closeness(song[feature], target)
            score += points
            reasons.append(
                f"{feature} {song[feature]:.2f} vs target {target:.2f} (+{points:.2f})"
            )

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]

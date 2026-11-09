"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse
import textwrap

from recommender import load_songs, recommend_songs, STRATEGIES, DEFAULT_MODE

# Test user profiles (preference dictionaries)
PROFILES = {
    "Starter Profile": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "High-Energy Pop": {
        "genre": "pop", "mood": "happy", "energy": 0.85,
        "valence": 0.85, "danceability": 0.85,
    },
    "Chill Lofi": {
        "genre": "lofi", "mood": "focused", "energy": 0.38,
        "acousticness": 0.75,
    },
    "Deep Intense Rock": {
        "genre": "rock", "mood": "intense", "energy": 0.92,
        "acousticness": 0.1,
    },
}


def main() -> None:
    """Load the songs, score them for sample users, and print the top picks.

    Usage: python src/main.py [--mode balanced|genre_first|mood_first|energy_focused|all]
    """
    parser = argparse.ArgumentParser(description="Music recommender simulation")
    parser.add_argument(
        "--mode", default=DEFAULT_MODE, choices=[*STRATEGIES, "all"],
        help="ranking strategy; 'all' runs every strategy for comparison",
    )
    parser.add_argument(
        "--no-diversity", action="store_true",
        help="disable the diversity penalty (artist/genre repeats in the top results)",
    )
    args = parser.parse_args()
    modes = list(STRATEGIES) if args.mode == "all" else [args.mode]

    songs = load_songs("data/songs.csv")

    for name, user_prefs in PROFILES.items():
        for mode in modes:
            print(f"\n##### {name} | mode: {mode} #####")
            recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode,
                                              diversity=not args.no_diversity)
            print_recommendations(user_prefs, recommendations)


def _wrap(text: str, width: int) -> list:
    """Wrap text to `width` characters per line (always at least one line)."""
    return textwrap.wrap(text, width=width) or [""]


def format_table(headers: list, rows: list, widths: list) -> str:
    """Render rows as an ASCII table. Each cell is a list of lines (multi-line
    cells are padded); a rule is drawn between rows."""
    rule = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def line(cells: list) -> list:
        height = max(len(c) for c in cells)
        out = []
        for i in range(height):
            parts = [(c[i] if i < len(c) else "").ljust(w) for c, w in zip(cells, widths)]
            out.append("| " + " | ".join(parts) + " |")
        return out

    lines = [rule, *line([[h] for h in headers]), rule.replace("-", "=")]
    for row in rows:
        lines.extend(line(row))
        lines.append(rule)
    return "\n".join(lines)


def print_recommendations(user_prefs: dict, recommendations: list) -> None:
    """Print the top picks as an ASCII table: rank, song, genre/mood, score and
    every reason behind the score (one reason per line)."""
    profile = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print(f"\nTOP {len(recommendations)} RECOMMENDATIONS")
    print(f"Profile: {profile}")

    widths = [2, 26, 16, 5, 62]
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = [ln for r in explanation.split("; ") for ln in _wrap(f"- {r}", widths[4])]
        rows.append([
            [str(rank)],
            _wrap(song["title"], widths[1]) + _wrap(f"by {song['artist']}", widths[1]),
            [song["genre"], song["mood"]],
            [f"{score:.2f}"],
            reasons,
        ])
    print(format_table(["#", "Song", "Genre / Mood", "Score", "Why it scored this way"],
                       rows, widths))


if __name__ == "__main__":
    main()

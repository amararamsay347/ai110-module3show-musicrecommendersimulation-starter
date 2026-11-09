"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse

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


def print_recommendations(user_prefs: dict, recommendations: list, width: int = 60) -> None:
    """Print each recommendation as a numbered card with its score and reasons."""
    heavy, light = "=" * width, "-" * width
    profile = ", ".join(f"{key}={value}" for key, value in user_prefs.items())

    print(f"\n{heavy}")
    print(f"TOP {len(recommendations)} RECOMMENDATIONS")
    print(f"Profile: {profile}")
    print(heavy)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']} by {song['artist']}")
        print(f"    Score: {score:.2f}   [{song['genre']} / {song['mood']}]")
        print("    Reasons:")
        for reason in explanation.split("; "):
            print(f"      - {reason}")
        print(light)


if __name__ == "__main__":
    main()

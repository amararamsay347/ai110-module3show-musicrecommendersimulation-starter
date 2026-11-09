"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs

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
    """Load the songs, score them for a sample user, and print the top picks."""
    songs = load_songs("data/songs.csv") 

    for name, user_prefs in PROFILES.items():
        print(f"\n##### {name} #####")
        recommendations = recommend_songs(user_prefs, songs, k=5)
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

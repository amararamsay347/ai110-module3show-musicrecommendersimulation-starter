# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  
**JamJammingJammerFinder-Music Recommender**  

---

## 2. Intended Use  

This recommender suggests the top 5 songs from a 20-song catalog that best match a listener's favorite genre, mood and energy level, and it explains each pick. It assumes the listener's stated taste is accurate and fits a single energy level. It is for classroom exploration only, not for real listeners. 

### Non-Intended Use 
This is not to be used for real music apps or real listeners, for decisions about artists or what gets promoted, or for people with mixed tastes. The reason given is that the 20-song catalog is too small and too subjective to give concrete solutions.

---

## 3. How the Model Works  

The recommender works like a judge at a talent show. It looks at every song in the catalog one at a time, awards points for how well the song fits what the listener says they like, and then shows the songs with the most points.

**What the listener tells us:** a favorite genre, a favorite mood, and a target energy level (from calm to intense). They can also say how upbeat, acoustic, or danceable they want their music to be, but those are optional.

**How points are awarded (up to 6.75 in total):**

- **Genre (up to 0.75 points):** a song gets the full amount if its genre matches, and nothing if not.
- **Mood (up to 1.5 points):** an exact match gets the full amount. A similar mood, like "playful" when the listener wants "happy", gets half. Moods are grouped into families: calm ones, cheerful ones, intense ones, and sad ones.
- **Energy (up to 3.0 points):** the closer the song's energy is to the listener's target, the more points it earns. A perfect match gets the full amount, and the score drops steadily as the gap grows.
- **Upbeat, acoustic, and danceable feel (up to 0.5 points each):** these work like energy, rewarding songs that are close to what the listener asked for. They are small bonuses that mostly break ties between songs that are otherwise similar.

Energy is worth the most on purpose, mood is in the middle, and genre is a smaller bonus. These weights come from a weight-shift experiment that doubled energy and halved genre (they started equal at 1.5 each). A song whose energy is close to the target can now beat a song that only shares the genre.

**Putting it together:** the points are added up for each song, the songs are ranked from highest to lowest, and the top few are shown. Each song also comes with a short list of reasons, such as "genre match" or "energy close to target", so the listener can see why it was picked.

**What was left out:** tempo is not scored, because it mostly tells us the same thing energy already does.

**Changes from the starter:** the starter code only returned the first few songs in the file, without scoring anything. The scoring, ranking, and reasons above were all added.

---

## 4. Data  

The catalog is data/songs.csv: 20 songs, 17 genres and 16 moods. The starter file had 10 songs, and 10 more were added; none were removed. Each song has a genre, a mood, and numbers for energy, valence, danceability, acousticness and tempo (tempo is not scored). Limits: the catalog is tiny, most genres and moods appear only once, energy is bunched at the low and high ends, each song has just one genre and mood.

---

## 5. Strengths  

Where does your system seem to work well  

It works best for listeners whose genre, mood and energy agree, like the pop, lofi and rock profiles, where the #1 song matched my expectations every time. The four profiles got clearly different lists, so the scoring really responds to what each listener asks for. Each pick comes with reasons that add up to its score, so it is easy to see why a song ranked where it did based on the user profile.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 


**Weakness discovered: a single energy target cannot represent listeners with mixed tastes.** Because a profile stores only one `energy` value and the score rewards closeness to it, a listener who enjoys both calm (about 0.2) and intense (about 0.9) music is effectively averaged to 0.55. In my test, that profile's top five were all mid-energy songs such as *Velvet Hours* (0.55) and *Dusty Porch Swing* (0.52), so neither of their real tastes was served, yet the system still reported a confident score of 3.00. The same weakness shows up for any user whose labels fail to match, since mid-energy songs become the default fallback for everyone. Doubling the energy weight in my weight-shift experiment made this worse, because energy now outweighs genre and mood combined.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 


**User profiles tested.** Four profiles are built into `src/main.py`, and their top-5 output is in the README:

| Profile | Preferences |
|---|---|
| Starter Profile | genre=pop, mood=happy, energy=0.8 |
| High-Energy Pop | genre=pop, mood=happy, energy=0.85, valence=0.85, danceability=0.85 |
| Chill Lofi | genre=lofi, mood=focused, energy=0.38, acousticness=0.75 |
| Deep Intense Rock | genre=rock, mood=intense, energy=0.92, acousticness=0.1 |

I also ran edge-case profiles in separate scripts, without adding them to the project: a conflicting profile (Sad But Hyper: blues, sad, energy 0.9), a genre/mood mismatch (Metal Fan Wants Peace: metal, peaceful, energy 0.2), unknown labels (k-pop, dreamy), messy casing and spaces (" Lofi ", "CHILL"), an out-of-range energy (5.0), an empty profile, a dead-center profile (every target 0.5), and a listener with mixed tastes forced onto a single energy target of 0.55. For a broader check, I scored 1,360 synthetic profiles (every genre × mood × five energy levels) and counted how often each song reached the top 5.

**What I looked for.** For each profile I checked whether the #1 song matched my intuition, whether the explanations (reasons) added up to the score, and whether surprising songs ranked high and why.

**Comparisons and tests.**
- **Weight shift:** I compared the original weights (genre 1.5, energy 1.5) with the shifted ones (genre 0.75, energy 3.0). The #1 song stayed the same for all four profiles, but lower ranks changed. For example, *Fiesta Nights* moved above *Gym Hero* for the pop profiles.
- **Math check:** I confirmed that the maximum score is 6.75, that a perfect self-match scores exactly 6.75, and that no score across the synthetic profiles exceeded it or fell below 0.
- **Unit tests:** the two starter tests in `tests/test_recommender.py` still pass.

**What surprised me.** Doubling the weight on energy and halving the weight on genre made the rankings feel more accurate. With the original equal weights, a genre match earned a song a high rank even when its energy was a worse fit, even though energy matters just as much to how a song feels. For the pop profiles, *Gym Hero* (pop/intense, energy 0.93) ranked above *Fiesta Nights* (latin/playful, energy 0.82) only because it shared the genre "pop". After the shift, *Fiesta Nights* moved above it, which matched what a "happy, energy 0.8" listener would expect. This is my own judgment, since I have no listener data to confirm it, and the tradeoff is that users who care strongly about genre now get less of it.

**Comparing the profiles (what changed, and does it make sense?).** In each pair below, the second profile differs from the first in what it asks for, so the differences in the results show what each preference is really testing.

- **Starter Profile vs. High-Energy Pop.** Both ask for happy pop at a similar energy, and the top three songs are the same, in the same order (*Sunrise City*, *Rooftop Lights*, *Fiesta Nights*). The only change is that High-Energy Pop also asks for upbeat and danceable music, so every score goes up a little (for example, *Sunrise City* goes from 5.19 to 6.12) because the songs near the top also happen to be upbeat and danceable. The ranking holding steady makes sense, because the extra preferences only add small tiebreaker points and don't ask for anything very different.
- **Starter Profile vs. Chill Lofi.** This is a big shift. The pop profile gets bright, loud songs (energy about 0.8), while the lofi profile gets quiet, slow songs (energy about 0.4) and no pop at all. That is right, because these two listeners want opposite things: one wants a party and the other wants to study.
- **Starter Profile vs. Deep Intense Rock.** The happy-pop listener's list is full of cheerful songs, and the rock listener's list is full of "intense" songs. They have almost the same energy range (0.8 vs. 0.92), so the difference comes from mood and genre: the rock listener gets *Storm Runner*, *Iron Requiem* and *Concrete Crown*, which are all aggressive or confident rather than happy. This makes sense because the mood label is what separates two high-energy listeners.
- **High-Energy Pop vs. Chill Lofi.** These are opposites on every setting (genre, mood, energy and acousticness), and not one song appears in both top fives. That is the result we should expect from two completely different tastes, and it shows the system is not just handing everyone the same popular songs.
- **High-Energy Pop vs. Deep Intense Rock.** Both listeners want loud music (energy 0.85 vs. 0.92), so the same songs show up in both lists: *Gym Hero* and *Neon Pulse*. This is reasonable, because they really are loud songs, but it also shows the system's limit. Once a listener asks for high energy, a loud song can sneak in even when its mood doesn't match.
- **Chill Lofi vs. Deep Intense Rock.** These are at opposite ends of the energy scale (0.38 vs. 0.92). The lofi list is made of low-energy, acoustic songs (acousticness 0.7 to 0.9), and the rock list is made of loud, electric-sounding songs (acousticness near 0.1). This is the clearest sign that the energy and acousticness preferences are doing their job.

**Why "Gym Hero" keeps showing up for people who just want "Happy Pop."** Think of the recommender as a judge giving points for each thing a song gets right. *Gym Hero* is a pop song, so it earns the "genre" points that a Happy Pop listener cares about. It is also very energetic, and a Happy Pop listener also wants energetic music, so it earns almost all of the energy points. The catch is that *Gym Hero* is an "intense" workout song, not a happy one, and it earns nothing for mood, but that alone is not enough to drop it out of the top five. It also helps that the catalog has only two pop songs, so after *Sunrise City* there are very few other pop songs to recommend. In plain terms, the system sees "pop and lively" and stops there. It does not understand that "intense gym music" and "happy sunny music" can feel quite different, because it only compares labels and numbers, not how a song feels. For the happy-pop listener *Gym Hero* sits at #4 (it was #3 before I shifted the weights toward energy), and for the rock listener it is #2, where it fits better because it really is "intense."

---

## 8. Future Work  

Ideas for how you would improve the model next.  

a. Allow more than one energy target per listener.
b. Limit repeat artists and genres in the top 5.
c. Add more songs and reject invalid inputs.

---

## 9. Personal Reflection  

A few sentences about your experience.  

I learned that every recommender system has its own way of choosing what to show. Spotify mixes collaborative filtering, content-based and audio analysis, context and sequence signals, and reinforcement learning. YouTube first picks a set of candidate videos and then ranks them, and TikTok relies on key signals and video features. All of them learn from explicit feedback (thumbs up or down, follows, playlists) and implicit feedback (skips, replays, completion rate, likes, saves, shares, searches). Something unexpected was how much a small change in weights could shift the results: doubling energy and halving genre changed the rankings more than I thought it would. Before, I saw recommendation apps as basic algorithms. Now I see them as complex machine learning models trained on huge amounts of listener behavior, built to match what people want with high accuracy.
                                                                                   
My recommender was much simpler. It adds up points for genre, mood and energy and  ranks the songs by the total. Even so, small design choices changed the results. When I gave energy more weight and genre less, the order of the songs below the tpick changed, and I thought the new order fit the listener better.   

AI tools helped me build and test the system quickly, but I still verified the results myself, including checking that the scores added up and that the documentation matched the code and that the logic followed exactly how I intended it to be.

What surprised me most was that such a simple system could still feel like a real recommendation. A listener who asked for happy pop got a song they might actually play, along with the reasons it was chosen.

If I continued this project, I would let a listener have more than one energy preference, limit how often the same artist appears in the top five, and use feedback such as skips and replays to improve the results.
# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

The recommender works like a judge at a talent show. It looks at every song in the catalog one at a time, awards points for how well the song fits what the listener says they like, and then shows the songs with the most points.

**What the listener tells us:** a favorite genre, a favorite mood, and a target energy level (from calm to intense). They can also say how upbeat, acoustic, or danceable they want their music to be, but those are optional.

**How points are awarded (up to 6 in total):**

- **Genre (up to 1.5 points):** a song gets the full amount if its genre matches, and nothing if not.
- **Mood (up to 1.5 points):** an exact match gets the full amount. A similar mood, like "playful" when the listener wants "happy", gets half. Moods are grouped into families: calm ones, cheerful ones, intense ones, and sad ones.
- **Energy (up to 1.5 points):** the closer the song's energy is to the listener's target, the more points it earns. A perfect match gets the full amount, and the score drops steadily as the gap grows.
- **Upbeat, acoustic, and danceable feel (up to 0.5 points each):** these work like energy, rewarding songs that are close to what the listener asked for. They are small bonuses that mostly break ties between songs that are otherwise similar.

Genre, mood, and energy are worth the same amount on purpose, so no single one decides the result. A song that gets two of them right will usually beat a song that gets only one right.

**Putting it together:** the points are added up for each song, the songs are ranked from highest to lowest, and the top few are shown. Each song also comes with a short list of reasons, such as "genre match" or "energy close to target", so the listener can see why it was picked.

**What was left out:** tempo is not scored, because it mostly tells us the same thing energy already does.

**Changes from the starter:** the starter code only returned the first few songs in the file, without scoring anything. The scoring, ranking, and reasons above were all added.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

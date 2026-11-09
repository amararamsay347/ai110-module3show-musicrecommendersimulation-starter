# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I instructed Claude to add comeplex attributes to the dataset, including song popularity, release decade and detailed mood tags (3 for each song)

**Prompts used:**

Add the attributes of song popularity, release decade, and detailed mood tags to the current dataset, ensuring that everything is still formatted correctly and can be accessed the same way as before.

**What did the agent generate or change?**

Claude generated the dataset with the new features mentioned above for each of the 20 songs,it also included a new explicit feature which states whether a song is explicit or not by using 0 or 1. It suggested to edit the recommender.py to update what is loaded from the csv to include the updated features. 

**What did you verify or fix manually?**

Claude did a great job at implementing the features but I still had to verify that everything was still accessible and works smoothly. 
---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->

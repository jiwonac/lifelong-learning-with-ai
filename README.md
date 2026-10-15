# Learning Vault

This custom learning system equips AI agents with learning science principles and a structured personal learning curriculum.
I use it to learn new topics for my PhD and personal projects, and I've refined the prompts through extensive use.
I recommend this as a starting point for self-driven learning, especially when human-created, pedagogically friendly learning materials don’t exist, such as for bespoke personal learning or expert-level learning.

## General Principles

### Align AI with learning science.

I try to minimize general-purpose LLMs' weaknesses for learning.

* **Hallucination.** All learning materials are generated from a few sources of truth, like textbooks or scientific papers.
* **By default, AI is overly friendly and gives away answers.** So AI is instructed to maximize desirable difficulties and give only enough hints to get you unstuck.

I also try to leverage the key findings of learning science.

* **Recall over recognition.** The AI will always reveal only enough information to cue recall, never give answers.
* **Interleaved and spaced practice.** Using spaced repetition, you will revisit the same topic at interleaved intervals.
* **Self-testing.** You will be tested in every single learning session through quizzes and flashcards.
* **Prompt and correct feedback.** Each question bank question includes a solution key for immediate feedback.
* **Desirable difficulty.** AI adjusts lectures and quizzes based on your performance. It asks you questions and gives you limited hints rather than just telling you the answer. 

### Learning takes different forms.

School education follows a predictable cadence of semester-long classes with similarly sized units, and lectures that last about one to two hours.
Self-driven learning is rarely that simple! Learning projects can vary widely in structure.

1. Highly structured: You want to master a textbook, from front to back.
2. Unstructured: You were thrown a web article by your boss to learn today. Or you might choose the day's learning topic based on serendipitous whims.
3. Microlearning: You have five minutes and want to use that time productively.

This learning vault can handle all three levels of structure using three different types of learning structure:

1. **Curriculum mode.** You design a personal course with units, with quizzes at the start and end of each unit.
2. **Ad-hoc mode.** You give the AI a one-off material to learn. After the learning session, you can incorporate any relevant concepts into existing courses.
3. **Anki flashcards.** You can refresh your memory of factual content by reviewing Anki flashcards. The learning AI agent creates and manages the Anki flashcards for you.

Learning sessions can be arbitrarily long or short, from 10 minutes to several hours in one sitting.
Sessions can be arbitrarily close or far apart from each other.

### All learning is connected.

Traditional schooling categorizes learning topics into distinct majors and courses.
Each course has a beginning and an end.
After taking the final exam, you might forget a course's material altogether.

I don't think that's the goal of self-driven learning! In this system, you will always review all courses and units you’ve already learned during regular interviews. You can start or stop learning a course as your priorities change, and learn as many or as few courses simultaneously as you like.

When you encounter something new to learn, it will be added as a unit or a concept to an existing course.

## Getting started

1. Set your intention for your first personal learning curriculum. What would you like to learn? What material would you like to use? Prepare at least one textbook, book, a few scientific papers, or other trustworthy resources.
2. Clone the repository, and open it with Claude Code (or Codex, or similar). Ask the AI to onboard you by designing your first course. It will walk you through the steps, cut the source into units and concepts, and take a while to populate the question bank. This is a one-time cost.
3. If you want to use Anki for flashcards, you must use the desktop or local terminal version of Claude Code, not the cloud deployment version. You must also have Anki installed and running on your computer. Install the AnkiConnect add-on.

## Organization

### Courses, Units, and Concepts

Learning materials are organized into a hierarchy of courses, units, and concepts.

* A **course** is a broad topic, like “linear algebra.”
* A **unit** is a subtopic, like “determinants.”
* A **concept** is a claim or a skill (that you can do), like “the learner can relate determinants to the fundamental theorem of linear algebra” or “the learner understands the structure and significance of the Leibniz formula for determinants.”

Each unit has readings, prerequisites, a priority, a spaced-repetition state, a “cursor” (which lets AI remember where you were), a question bank, and learning history.
Each unit can be in one of four stages: unknown, new, learning, and learned.
Concepts can be unknown, unseen, and seen.
A course is a collection of units, shared learning goals, and shared reference material.

### Session structure

To start a session, open and start a new chat in this folder.
By default, the AI uses the spaced-repetition scheduler to choose the next unit to study.
If understanding that unit requires you to learn a prerequisite first, then you will learn that instead.
You can override this default behavior by telling the AI which unit you want to learn.
You can also bring new learning materials to the AI for an “ad-hoc session” that is not formally part of any pre-defined course.

A typical learning session will take these steps:

1. **Place.** Using a short placement quiz, the AI learns which unit concepts you already know and which you don’t.
2. **Quiz.** To ensure you don’t forget what you learned before, you solve a few questions from units you’ve already covered.
3. **Study.** The AI teaches you the unit’s big picture, then covers each concept in the unit. You'll solve practice problems along the way, so you’re not just zoning out.
4. **Capture.** At any moment, you can say “end session” or “I’ve got to go” or similar. Then, the AI will log the session and any artifacts. This is important to ensure the spaced repetition scheduler works correctly.
5. **Update Repo.** You might have to commit/push/merge changes to the repository to ensure the record is durable, depending on how much permission the AI has to do it autonomously.

**Ad-hoc learning session.** You bring your own one-off learning material: an article or report you read and understand, a project-related task, or anything you’re curious about.

1. Ask the AI to teach you the one-off learning material.
2. **Situate.** The AI checks if the learning material already exists in your existing courses, and if you’ve already learned any of the concepts.
3. **Study.** You will study the material like in any normal session.
4. **Capture.** The AI asks whether you want to incorporate the learning material into your existing courses or create a special “miscellaneous course” that collects units and concepts that don’t fit into any other course.

### Learning interface

You will be interacting with this learning vault primarily through a coding agent.
However, terminals can't display math equations or diagrams, which are crucial for learning many subjects.
As such, the learning materials, including lectures, quizzes, and feedback, are provided in a Claude artifact, a webpage you can open side-by-side with the main chat.
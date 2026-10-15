---
name: "clear-writing"
description: "Use for any prose a human will read: chat responses, research and literature summaries, code-change explanations, and docs."
---

# Clear writing

Apply these principles to anything a human will read: chat responses, research summaries, code-change explanations, documentation, etc. Human readers differ from LLM readers. A human reads once, holds only a few new ideas in working memory, and stops reading earlier. An LLM absorbs dense, jargon-heavy, verbose text at no cost. Write for the human.

## Structure

Each paragraph opens with a thesis sentence that states a fact or judgment the paragraph will defend. The sentences after it support that thesis. They can give evidence, cover aspects or viewpoints of the thesis's subject, or walk through a logical sequence such as the steps of a plan or a chain of reasoning. A supporting sentence never introduces a new thesis; a new thesis starts a new paragraph. An optional final sentence can tie the previous sentences together.

A whole response follows the pattern at a larger scale. The first paragraph states the central claim or answer. Each following paragraph develops one sub-claim or one step. A final paragraph may wrap them up, but only when it adds something; skip a recap that repeats the opening.

Order sentences and paragraphs by two rules. Start from what the reader already knows and add new ideas incrementally. Move from broad to narrow: give the main idea first, then the details.

## The reader's point of view

Write from the reader's position, including what they do and don't know. Use plain English where possible. Define every acronym, shorthand, symbol, and number at first use. Never drop in a technical detail the surrounding text doesn't explain, such as a term, program identifier, person, citation, or statistic; say what problem it relates to and what follows from it. Don't spend words on hedges that don't affect the reader's goal.

## Sentences

Write full sentences in the active voice with concrete subjects and verbs. Name the actor and the action: "the parser drops the header," not "header loss occurs during parsing." Keep each sentence only as long as its idea needs. Avoid noun-phrase fragments, passive constructions, vague abstractions, and run-ons.

## Formatting

Default to prose paragraphs. Use a numbered list for steps the reader will follow in order, a table for items compared on the same attributes, and code blocks for code, commands, and paths. Don't fragment an argument into short bullets. Aids that show the reader how the answer is organized are fine: a one-sentence signpost such as "Analysis by metric is as follows," or a short list of parallel data points under a one-line thesis. Unlike announced significance, these tell the reader where things are rather than claiming that something matters.

## Patterns to replace

These patterns mark text as machine-written and make readers distrust it. 

- Contrast framing ("it's not X, it's Y"). State Y and give the evidence for it. Mention X only if the reader plausibly believes X.
- Bolded-label lists (a bold term, a colon, then an explanation). Write a paragraph whose thesis sentence makes the point, or a plain list of full sentences.
- False balance, meaning a weak position given equal weight with a strong one to look neutral. Say which position the evidence favors and how strongly.
- Coined metaphors such as "X-shaped," "a dial worth turning," or "this earns its keep." Use the literal phrase.
- Em dashes. Use a period, comma, colon, or parentheses.
- Announced significance, such as "there are two critical distinctions, and it matters." State the distinctions; the content shows why they matter.
- Cryptic jargon: terms of art the reader hasn't seen, or labels invented mid-response. Use the plain description or define the term.
- Abstract bliss: sentences built from abstract nouns ("robustness," "alignment," "a richer picture") that sound meaningful but name no concrete fact, object, or action. Replace each with the specific claim it stands for, or delete it.

## Length

Readers have less stamina than LLMs, so cut hard. Lead with the answer; when the answer is a comparison, name what it is compared against and how large the difference is. Cut content before sentences: drop file paths, run settings, dataset names, dates, quotes, and second examples of the same claim, unless the reader needs them to act on or check the claim. Then delete any sentence the reader would not miss, any restatement of the question, and any summary that repeats what was just said. General heuristic: write shorter than you think. 

## Context-specific rules

When summarizing completed coding work, state what changed, why, and what remains unverified or untested. Don't narrate the steps taken to get there.

When summarizing research or literature, organize by claim or question. Say where sources agree, where they conflict, and how strong the evidence is, in one clause where possible.

## Examples

### Example A

**User question:** Perform a literature review of user simulation techniques using LLMs for simulating humans in human-AI chatbot style conversations. Include an extended summary of best practices in recent research output.

**AI writing:**

```
The field has moved, roughly between 2024 and 2026, from prompting an instruction-tuned assistant to role-play a user
toward simulators that are profile-conditioned, trained on real user turns, or optimized with multi-turn RL. Its centre
of gravity is now validation: several 2026 studies ran the same tasks with real participants and report that prompted
simulators are systematically over-cooperative, verbose, polite and front-loading, which inflates agent success and
miscalibrates difficulty. Evidence that grounding in real data helps is consistent but comes mostly from open-domain
chat (WildChat/LMSYS) and a few agentic benchmarks (τ-bench), English-dominant, with LLM judges carrying much
of the measurement.3 Persona conditioning has mixed support: it helps in chatbot-evaluation settings but adjacent
survey-simulation work finds it flattens or stereotypes groups and can hurt. Under-studied: downstream effects on
trained assistants (one controlled study), non-English and dialectal users, long multi-session simulation, and statistically
calibrated inference from simulated results.
```

**Gold response:**

```
The LLM user simulation field developed strategies such as zero-shot prompting, conditioning on a written user profile, and fine-tuning or reinforcement learning on real user turns. 
The central technique for ensuring validity is to assign the same task, such as roleplaying a user based on a profile, to human participants. 
Studies identified that prompted simulators are over-cooperative, verbose, polite and front-loading (stating every requirement in the first message). 
These characteristics inflate agent success and give an incorrect sense of task difficulty.
Two techniques recur: grounding in real data, and persona conditioning. 
The former is supported by consistent data, though mostly from English-language open-domain chat evaluated by LLM judges. 
The latter has mixed support: it helps in chatbot evaluation, but survey-simulation studies find it can flatten or stereotype groups. 
```

### Example B

**User question:** do monks use things like podcasts, audio streaming?

**AI writing:**

```
Yes, monks do use modern audio mediums, but best practices depend on the tradition, community, and whether it is entertainment or teaching. 

**Christian monasteries.** Digital media use is widespread and unregulated from the top. A recent ethnography of Benedictine monasteries found that digital media are omnipresent, used in individualized ways by monks. Monks justify this use by pointing to how it serves traditional goals, though deeper discussions exposed contradictions that they perceive in these technologies. Stricter houses filter each technology. One Trappist monastery adopted the internet only after it was reviewed and "monastisized", with a monk serving as webmaster. Many abbeys also produce podcasts for education. 

**Theravada Buddhist monks.** Here the relevant constraint is music, not devices. Deliberately listening to music is a minor Vinaya offense (dukkaṭa), and novices' ten precepts exclude it. Practice diverges from the text, though. An ethnomusicology study of Burmese monks found that one monk and his fellow monastic not only hear music on TV, but also listen to music on their cellphones, and monasteries often let donors play recorded music during ceremonies. The Vinaya predates electronics, so each community sets its own rules. A layperson describing their local monastery notes a shared computer in the library that everyone can see, phones donated to some monks but not allowed for new ones, and that rules for this are different at every different monastery. Thai forest lineages sit at the strict end. Bhikkhu Pesala, for instance, states that using a mobile phone or the Internet is not compatible with the life of a Forest Monk. In contrast, someone who has spent time in Lao, Thai, Burmese and Sri Lankan communities reported that even in some of the most rural places imaginable the monastics there were using smartphones. In Mahayana practice, Thich Nhat Hanh's communities do not allow a monk to access the Internet on his own. 

**Where this leaves podcasts and streaming.** Dharma talks, sermons and other spoken teaching content are the least controversial kind of audio. Many monasteries publish it, such as Clear Mountain's Dharma talks from monastics. Music streaming is technically disallowed for Theravada monastics, but it happens in practice. Access to general-interest podcasts depends on how much device access the abbot or community allows. The main concern monastics themselves raise is time and attention, not the content. A Theravada Mahathera interviewed by the Queen's Journal explained that when you start using computers, you have to spend your time mostly on the computers rather than meditating. 

Most of the Buddhist evidence here comes from forum reports by practitioners rather than systematic study. The Benedictine ethnography and the Burmese music paper are the only scholarly sources.
```

**Gold response:**

```
Yes, monks do use modern audio mediums, but best practices vary greatly. 

In Christianity, digital media use is widespread and not centrally regulated. A recent ethnography of Benedictine monasteries found that digital media are omnipresent. Monks justify this use by pointing to how it serves traditional goals, though deeper discussions exposed contradictions that they perceive in these technologies. Stricter houses filter each technology. One Trappist monastery adopted the internet only after it was reviewed and "monastisized", with a monk webmaster. Many abbeys also produce podcasts for education. 

In Buddhism, the rules vary by tradition and the individual communities. Often the rules on paper are stricter than those in practice. Deliberately listening to music is a minor offense (called dukkata) under the Vinaya, the monastic code, but an ethnomusicology study found two Burmese monks listening to music on TV and on their cellphones. One lay account says that their monastery has a shared computer and phones donated to some monks, and that these rules differ at every monastery. Bhikkhu Pesala, a Theravada monk, states that using a mobile phone or the internet is not compatible with the life of a forest monk. In contrast, at least one person reported that even the most rural monastics in Thailand, Laos, Myanmar, and Sri Lanka were using smartphones. In Mahayana practice, Thich Nhat Hanh's communities do not allow a monk to access the internet on his own. Most of this Buddhist evidence comes from practitioners' forum posts rather than systematic study. 

The rules are more permissive for spoken, non-conversational audio than entertainment. Many monasteries publish their own educational podcasts. Access to general-interest podcasts depends on the idiosyncratic rules of each community. The main concern monastics raise is time and attention taken away from meditation, not content. 
```

### Example C

**User question:** What is satay sauce?

**AI response:**

```
The base is roasted, ground peanuts (or peanut butter in Western versions) cooked with coconut milk. Cooks season it with some mix of garlic, shallot, chili, lemongrass, tamarind or lime, palm sugar, and soy sauce; Indonesian versions often use kecap manis, a thick sweet soy sauce. The result is creamy and nutty, balanced between sweet, salty, sour, and mildly spicy.

Beyond skewers, the same sauce dresses Indonesian gado-gado (a vegetable salad) and serves as a dip for spring rolls. Regional versions differ: Malaysian and Singaporean sauces tend to be chunkier and spicier, Thai ones often include red curry paste, and Dutch "satésaus" is smoother and sweeter.
```

**Gold response:**

```
Satay sauce is an Indonesian peanut-based sauce. It is frequently used for skewers, gado-gago vegetable salad, or spring rolls. 

Roasted, ground peanuts (or peanut butter in Western variants) are cooked with coconut milk. Cooks then season it with some mix of garlic, shallot, chili, lemongrass, tamarind or lime, sugar, and soy sauce. The taste is creamy and nutty, with sweet, salty, sour, and mildly spicy notes. 

There are many regional variations. Malaysian and Singaporean sauces are chunkier and spicier, Thai ones include red curry paste, and Dutch "satésaus" is smoother and sweeter. 
```
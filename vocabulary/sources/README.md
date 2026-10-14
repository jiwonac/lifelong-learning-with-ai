# Vocabulary source lists

Raw seed lists for the optional vocabulary deck (`skills/flashcards/SKILL.md` → "Vocabulary"). The list files are not included in this repository. To use the deck, fetch the lists you want from the sources below, subject to each source's terms, and save each one here under the file name in the table.

Each `.txt` file holds one lowercase headword per line, sorted and de-duplicated within the file; multi-word phrases are dropped. Words overlap across files on purpose, since appearing in many lists is a signal of a useful word. With every list below in place, the union is about 12,200 unique words. `python3 scripts/vocab.py pool` builds the candidate pool from whatever files are present.

The table records where each list came from and how many words it held when it was built.

| File | List | Source | Words |
|---|---|---|---|
| `gre-magoosh-1000.txt` | Magoosh GRE 1000 flashcards (all decks) | https://github.com/Iamgautham/magoosh-flashcard-scraper (scraped from gre.magoosh.com/flashcards) | 1000 |
| `gre-manhattan-500-essential.txt` | Manhattan Prep 500 Essential Words | https://github.com/maykulkarni/Manhattan-GRE-Words-Shuffled | 491 |
| `gre-manhattan-500-advanced.txt` | Manhattan Prep 500 Advanced Words | https://github.com/maykulkarni/Manhattan-GRE-Words-Shuffled | 492 |
| `gre-barrons-333.txt` | Barron's GRE 333 high-frequency words | https://github.com/benedictpandu/Barrons-GREE-333-Dictionary | 326 |
| `gre-barrons-800.txt` | Barron's Essential Words for the GRE (800) | https://github.com/DebajyotiX/Barron_800_Words_Training | 799 |
| `gre-barrons-wordlist.txt` | Barron's full GRE word list (about 4,700 entries; many archaic) | https://github.com/SumoSumir/Barron-GRE-Word-Quiz | 4633 |
| `gre-princeton-hit-parade.txt` | Princeton Review GRE "Hit Parade" | https://github.com/scottfrazer/gre | 302 |
| `gre-princeton-beyond-hit-parade.txt` | Princeton Review "Beyond the Hit Parade" (includes secondary meanings of common words, e.g. "flag", "temper") | https://github.com/scottfrazer/gre | 128 |
| `gre-gregmat-groups-1-27.txt` | GregMat GRE vocabulary, groups 1-27 | https://github.com/Xatta-Trone/gregmatgrewordsdb | 759 |
| `sat-1000.txt` | "Top 1000 SAT vocab words" | https://github.com/MrBlob2U/SAT-1000-Words | 840 |
| `sat-6000.txt` | "6000 essential SAT vocabulary words" (broad; includes plain words like "abdomen") | https://github.com/sunh423/SAT-Vocabulary-Study-Tool | 5974 |
| `vocabcom-top-1000.txt` | The Vocabulary.com Top 1000 | https://www.vocabulary.com/lists/52473 | 1000 |
| `vocabcom-100-words-hs-graduate.txt` | 100 Words Every High School Graduate Should Know (American Heritage) | https://www.vocabulary.com/lists/137567 | 98 |
| `vocabcom-fancy-words-atlantic.txt` | Listener favorites inspired by Mark Bowden's Atlantic essay "In Praise of Fancy Words" | https://www.vocabulary.com/lists/349726 | 25 |
| `vocabcom-modern-fiction.txt` | Vocabulary.com chapter lists for 19 modern novels (Gatsby, Beloved, The Road, Never Let Me Go, Americanah, The Stranger, One Hundred Years of Solitude, etc.) | https://www.vocabulary.com/lists/k37tmnum/classic-and-essential-reads | 1338 |
| `vocabcom-nonfiction.txt` | Vocabulary.com chapter lists for 22 nonfiction books (Sapiens, The Gene, Cosmos, Guns Germs and Steel, The Double Helix, Oliver Sacks, Freakonomics, Between the World and Me, etc.) | https://www.vocabulary.com/lists/32k3ea2c/language-of-science-writing and https://www.vocabulary.com/lists/6vjhpi77/how-the-world-works | 2393 |
| `mw-word-of-the-day.txt` | Merriam-Webster Word of the Day, 2006-2026 (from Wayback Machine URL index; about 7,000 dates) | https://www.merriam-webster.com/word-of-the-day/calendar | 2976 |
| `dictcom-word-of-the-day.txt` | Dictionary.com Word of the Day, 1999-2025 (from Wayback Machine URL index; about 4,000 dates) | https://www.dictionary.com/e/word-of-the-day/ | 3156 |
| `economist-gre-frontier.txt` | GRE-list words attested in The Economist, 2020-2026 | https://github.com/DJiangwei/EconomistVocabulary (anki_decks/GRE_frontier.csv) | 500 |

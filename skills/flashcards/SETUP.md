# Flashcard setup: Anki, and optionally Raindrop

The flashcard layer is optional. Without it, sessions skip every flashcard step and nothing else
changes. You only do this setup once.

Claude Code must run on the same machine as Anki desktop, because the `anki` MCP server talks to
AnkiConnect on `localhost`. On macOS and Linux, run Claude Code natively and skip step 2. On
Windows, you can run Claude Code natively, or in WSL2 with step 2.

## 1. Anki

1. Install Anki desktop. If you want to review on a phone, sign in to AnkiWeb (Sync button),
   install AnkiDroid or AnkiMobile or use ankiweb.net in a browser, and sync once so all of them
   share one collection.
2. Install the **AnkiConnect** add-on: Tools → Add-ons → Get Add-ons → code `2055492159`. Then quit
   Anki completely and reopen it, because add-ons only load at startup. To check it loaded, open
   <http://localhost:8765> in a browser on the same machine; it should say `AnkiConnect`.
3. Create a deck named **`Vault`**.
4. Open the `Vault` deck options and give it its own preset (call it `Vault`):
   - **FSRS:** on. The toggle is in the **FSRS** section near the bottom of the options page.
     It applies to the whole collection, not only this preset.
   - **Desired retention:** `0.80`
   - **New cards/day:** `8`
   - **Maximum reviews/day:** `100`. That is roughly 10–13 minutes at 6–8 s per card. It is set
     deliberately below a 15-minute budget to keep the daily load light; lower it further if a day
     runs long.
   - **Leech threshold:** `4`
   - **Leech action:** `Suspend Card`
   - Leave the rest at their defaults. After about a month of reviews, press **Optimize** under
     FSRS so it fits your own memory.
5. The agent styles the `Basic` and `Cloze` note types itself (Tools → Manage Note Types →
   Basic / Cloze → Cards → Styling). Besides Anki's default rules, it adds three classes that
   the card fields use. Opacity and font, not a fixed colour, keep them readable in night mode:

   ```css
   .src  { font-size: 0.65em; opacity: 0.6; }   /* source line on the front */
   .expl { font-size: 0.8em;  opacity: 0.6; }   /* easy explanation on the back */
   .ttl  { font-family: Georgia, "Times New Roman", serif; font-style: italic; }  /* paper title in a question */
   ```
6. The agent sorts cards into subdecks of `Vault` (`Vault::Courses::<course>`, `Vault::Papers`,
   later `Vault::Ad hoc`) with `scripts/anki_decks.py`, and gives each new subdeck the `Vault`
   preset. Anki gives every deck its own preset, and a subdeck does not inherit its parent's, so
   to schedule one kind of card differently, give its subdeck(s) a new preset (for every course,
   assign the same preset to each `Vault::Courses::` deck). When you study by clicking `Vault`,
   its own daily limits cap the total across all subdecks, and each subdeck's limits cap its
   share. New cards are gathered in random order (**Display order → New card gather order:
   Random cards**), so subdecks mix evenly; the cost is that a definition card is not
   guaranteed to come before the cards that use it.

## 2. Only if Claude Code runs in WSL: let WSL reach Windows' localhost

AnkiConnect listens on Windows `localhost:8765`. WSL2 can only see it in **mirrored**
networking mode, which needs Windows 11 22H2 or later.

Open `.wslconfig` in your Windows user folder (`%UserProfile%\.wslconfig`; VS Code works) and
add this under `[wsl2]`, keeping any lines already there:

```ini
[wsl2]
networkingMode=mirrored
```

**Save it as UTF-8.** A `.wslconfig` that was saved as UTF-16 (VS Code shows `UTF-16 LE` in the status
bar) is silently ignored, and WSL stays in NAT mode. In VS Code, click the encoding in the status
bar → Save with Encoding → UTF-8. From WSL, this converts a UTF-16 file and keeps a backup (do not
run it on a file that is already UTF-8):

```bash
f=/mnt/c/Users/<windows-user>/.wslconfig; cp $f $f.bak && iconv -f utf-16 -t utf-8 $f.bak > $f
```

Then run `wsl --shutdown` **in PowerShell** and reopen your WSL distribution. That also ends any
Claude Code session running in WSL, including the desktop app's, so reopen it afterwards. Check it took:

```bash
wslinfo --networking-mode
```

It should print `mirrored`. If `.wslconfig` also has `localhostForwarding=true`, WSL prints a
warning at startup that the setting has no effect in mirrored mode. That warning is harmless.

**Fallback** if mirrored mode is unavailable or flaky:
1. In Anki, open Tools → Add-ons → AnkiConnect → Config and set `"webBindAddress": "0.0.0.0"`.
   Allow Anki through the Windows firewall on private networks.
2. In `.mcp.json`, set `ANKI_CONNECT_URL` to `http://<windows-ip>:8765`. To find the Windows IP,
   run `ip route | awk '/default/ {print $3}'` in WSL.

## 3. Check it

With Anki open, run this where Claude Code runs:

```bash
curl -s localhost:8765 -X POST -d '{"action":"version","version":6}'
```

It should print `{"result": 6, "error": null}`.

## 4. Node 22+

The MCP server runs through `npx` and needs Node 22 or later. Many distributions package an older
Node; nvm is one way to get a current one:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
exec $SHELL
nvm install 22
```

## 5. Open the repo in Claude Code

You need `git`, `python3` and, for the "gtg" merge step, the GitHub CLI `gh` logged in to the
account that owns your copy of the repo.

```bash
gh auth login            # lets "gtg" open and merge PRs
cd <your-clone> && claude
```

The first time you start Claude Code in the repo, approve the project MCP server **`anki`**.
Then run `/mcp` and check that it shows as connected.

## 6. Raindrop (optional, for work papers)

Skip this if you do not keep papers in Raindrop.io. Work papers come from your Raindrop.io bookmarks through Raindrop's official MCP server, which is
already declared in `.mcp.json`. In a `claude` terminal in the repo, run `/mcp`, choose
**`raindrop`** and authenticate. A browser window opens for the OAuth sign-in. Full-text and
semantic search need Raindrop Pro. On the free plan the agent reads public papers from their URL
instead.

The agent adds the tag `anki` to each bookmark it has carded. Leave that tag alone, because it
is how the next paper survey knows what is already carded.

## 7. Daily use

- Open Anki desktop before a session, or at least before you say "gtg", so new cards can be
  added and synced.
- Review on whichever device, whenever you like. The agent never schedules your reviews.
- Cloud sessions, and any session where Anki is not reachable, still work for studying. They
  just skip every flashcard step.

# Flashcard setup: Anki

This one-time setup is optional.
Claude Code must run on the same machine as Anki desktop, because the `anki` MCP server talks to AnkiConnect on `localhost`.
Step 2 is only for Claude Code in WSL2 on Windows.

## 1. Anki

1. Install Anki desktop.
   For phone review, sign in to AnkiWeb (Sync button), use AnkiDroid, AnkiMobile or ankiweb.net, and sync once.
2. Install the **AnkiConnect** add-on: Tools → Add-ons → Get Add-ons → code `2055492159`.
   Quit Anki completely and reopen it, because add-ons load only at startup (also the first fix whenever the agent cannot reach AnkiConnect).
   <http://localhost:8765> should then say `AnkiConnect`.
3. Create a deck named **`Vault`**.
4. Open the `Vault` deck options and give it its own preset (call it `Vault`):
   - **FSRS:** on (bottom of the page; it applies to the whole collection).
   - **Desired retention:** `0.80`
   - **New cards/day:** `8`
   - **Maximum reviews/day:** `100` (about 10–13 minutes at 6–8 s per card). Lower it if a day runs long.
   - **Leech threshold:** `4`
   - **Leech action:** `Suspend Card`
   - **Display order:** New card gather order `Random cards`; New card sort order random, for example `Random note, then card type`.
   - Leave the rest at their defaults. After about a month of reviews, press **Optimize** under FSRS.
5. The agent styles the `Basic` and `Cloze` note types itself (Tools → Manage Note Types → Basic / Cloze → Cards → Styling).
   It adds three classes to Anki's default rules, using opacity rather than colour so they work in night mode:

   ```css
   .src  { font-size: 0.65em; opacity: 0.6; }   /* source line on the front */
   .expl { font-size: 0.8em;  opacity: 0.6; }   /* easy explanation on the back */
   .ttl  { font-family: Georgia, "Times New Roman", serif; font-style: italic; }  /* paper title in a question */
   ```
6. The agent sorts cards into subdecks of `Vault` with `scripts/anki_decks.py` (see `SKILL.md` → "Plumbing") and gives each new subdeck the `Vault` preset, because a subdeck does not inherit its parent's preset.
   To schedule one kind of card differently, give its subdeck(s) a new preset (for courses, every `Vault::Courses::` deck).
   Studying from `Vault` caps the total by `Vault`'s limits and each subdeck's share by its own.

## 2. Only if Claude Code runs in WSL: let WSL reach Windows' localhost

WSL2 can see Windows' AnkiConnect only in **mirrored** networking mode, which needs Windows 11 22H2 or later.

Add this to `%UserProfile%\.wslconfig`, keeping any lines already there:

```ini
[wsl2]
networkingMode=mirrored
```

**Save it as UTF-8.**
WSL silently ignores a UTF-16 file (VS Code shows `UTF-16 LE` in the status bar; fix it with Save with Encoding → UTF-8).
From WSL, this converts a UTF-16 file and keeps a backup (not for a file already in UTF-8):

```bash
f=/mnt/c/Users/<windows-user>/.wslconfig; cp $f $f.bak && iconv -f utf-16 -t utf-8 $f.bak > $f
```

Then run `wsl --shutdown` **in PowerShell**, and reopen WSL and any Claude Code session it ended.
Check that the change took:

```bash
wslinfo --networking-mode
```

It should print `mirrored`.
A startup warning that `localhostForwarding=true` has no effect in mirrored mode is harmless.

**Fallback** if mirrored mode is unavailable or flaky:
1. In Anki's AnkiConnect config (Tools → Add-ons), set `"webBindAddress": "0.0.0.0"`, and allow Anki through the Windows firewall on private networks.
2. In `.mcp.json`, set `ANKI_CONNECT_URL` to `http://<windows-ip>:8765`.
   The Windows IP comes from `ip route | awk '/default/ {print $3}'` in WSL.

## 3. Check it

With Anki open, run this where Claude Code runs; it should print `{"result": 6, "error": null}`.

```bash
curl -s localhost:8765 -X POST -d '{"action":"version","version":6}'
```

## 4. Node 22+

The MCP server runs through `npx` and needs Node 22 or later, which nvm can install:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
exec $SHELL
nvm install 22
```

## 5. Open the repo in Claude Code

You need `git`, `python3` and the GitHub CLI `gh`, logged in to the account that owns your copy of the repo.

```bash
gh auth login            # lets "gtg" open and merge PRs
cd <your-clone> && claude
```

On first start, approve the project MCP server **`anki`**, then check `/mcp` shows it connected.

## 6. Daily use

- Open Anki desktop before you say "gtg", so the agent can add and sync new cards.
- Review on any device, whenever you like.
- Cloud sessions cannot reach Anki, and AnkiWeb's terms rule out third-party sync clients, so card work needs a local session.

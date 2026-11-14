# The world on Friday 13 November 2026 — news-image-01 entry v1

Entry for the make.fun bounty **"Sum up 13 November's world news in
one image"** (`news-image-01`): one image that sums up the world's
news of Friday 13 November 2026. $250, top 100 share; the 1st-place
image is shown on make.fun's site and in its posts as its picture of
that day's news.

## The idea

A premium international-newspaper front page, drawn entirely in code:
an ivory paper background, a big serif date masthead, one feature
story, ten secondary stories with small flat illustrations, and a
digest of the remaining seventeen headlines. The design is The
Economist meets Reuters Graphics: strong hierarchy, thin precise
borders, category colour accents, and typography that still reads at
~300 pixels.

The judge has no news feed, so the image must explain the day by
itself. That is why every story carries a short bold label, a
concise headline, and a one-sentence summary — and why the layout
covers the day's most consequential stories across regions and
fields, not one country's or one beat's.

## The 28 stories

All 28 are real events reported on 13 November 2026 (BBC, Al
Jazeera, Reuters). Disputed claims are attributed with "says" or
"claims"; nothing is invented.

Feature — 01 US · Tech & Politics: Senate summons Nvidia chief
Huang and Lutnick.

Secondary — 02 Zelensky meets US envoys as Europe joins talks;
03 Ukrainian drone hits Russian warship; 04 Iran says it struck a
US radar site in Bahrain; 05 FBI: North Korean hackers stole $400m
in crypto; 06 US reports record 483,200 deportations in 2026;
07 FAA orders nationwide ground stop; 08 Turkiye and Qatar sign a
mutual defence pact; 09 South Sudan's Kiir dissolves government;
10 Gaza storms flood camps, 106,000 affected; 11 Kane breaks
England caps record.

Digest — 12 Salah breaks Egypt's scoring record in a 5-0 win;
13 Man Utd appoint Pochettino as manager; 14 UN extends the Abyei
peacekeeping mandate to 2027; 15 Pakistan army says 74 militants
killed near the Afghan border; 16 six killed as a building
collapses near Nairobi; 17 tens of thousands join Poland's
nationalist march; 18 UK police investigate Walliams allegations;
19 Tanzania opposition leader Lissu jailed; 20 Niger military says
it regained control after a mutiny attempt; 21 Somalia security
forces seize the top court; 22 NGOs demand a probe into six bodies
in a Guinea mass grave; 23 Cameroon attackers kill an officer and
kidnap teachers; 24 UK curbs DRC visas, with return deals with
Angola and Namibia; 25 7,400+ migrants reach the Canary Islands in
10 days; 26 Pope Leo XIV welcomed by 1.5m in Chiclayo; 27 Nigeria
clears 62 Ebola contacts and none fell ill; 28 a Gaza baby dies
from cold as WHO warns of infections.

## Files

- `main.py` — the entry program (Python 3.13, Pillow only). It
  draws the whole infographic from code: masthead, feature card,
  ten secondary cards with flat illustrations, and the digest. It
  measures every string with its font and wraps or shrinks text so
  nothing overflows, overlaps, or clips. It writes the image to
  `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`) and verifies
  the result (1024×1024 PNG, under 1 MiB) before exiting.
- `fonts/` — DejaVu Serif / Sans (regular and bold), bundled so
  the program does not depend on any system font at run time.
- `README.md` — this file.

## Run locally

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# -> out/entry.png, 1024x1024 PNG, under 1 MiB
```

Run it twice and compare SHA-256 hashes: the output is
deterministic, byte for byte. `main.py` uses no network, no
randomness, and no timestamps.

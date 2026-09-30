# Author posts

The puzzle author posted as Tiamat / @ArweaveP. The original posts are now partly deleted on
Twitter/X, but the public workbook `HomelessPhD/AR_Puzzles/ArweaveP_user_tweets.xlsx` preserves
tweet IDs, exact text, UTC timestamps, URLs and media fields. The rows below were recovered
directly from that archive on 2026-09-30; the community PZL11 README independently reproduces
the same core hints.

- **Announcement — 2020-04-22 14:06:21 UTC, tweet 1252961944807641090.**
  "There is 1 ETH hidden in ... Puzzle 11 ... #puzzle #steganography #arweave #cryptopuzzle".
  The archived row links to the Arweave transaction
  `CzITHnEIlkQw9SbaX5futCzFrKk1qe_NwvWnIBmP2fY` and to the tweet image.

- **Escrow/address hint — 2020-04-23 09:24:44 UTC, tweet 1253253461828931584.**
  "0xFF2142E98E09b5344994F9bEB9C56C95506B9F17 it is also included somewhere in the image 🧐"

- **Storage-method hint — 2020-04-23 12:20:51 UTC, tweet 1253297784633122817.**
  "I understand some of you get a bit frustrated when you can't solve a puzzle. Maybe take it
  as a chance to learn alternative forms of storing a private key. I.e. how will an attacker
  know what's with a weird image in your email account? #cryptocurrency #privatekey #wallet"

- **Series-method hint — 2020-04-23 13:09:18 UTC, tweet 1253309976346574848.**
  In reply to @Goovi2: "Look at the solved puzzles. If solutions make sense to you, you are
  good to go."

- **Target-format hint — 2020-04-23 16:07:09 UTC, tweet 1253354733911359491.**
  In reply to @Kevin34755400: "Like I specified, the private key is hidden in the image. One
  way to try is MEW: Access by Private Key 🤐 good luck!"

- **File-format hint — 2020-04-23 17:30:04 UTC, tweet 1253375599323856896.**
  In reply to @afronomad_: "format does not matter"

- **Future-hint reply — 2021-08-23 16:44:04 UTC, tweet 1429846914028158977.**
  In reply to @DJPascimix: "Next set of hints when AR reaches $100 :)"

## Interpretation constraints

The author's own wording strongly constrains the intended solution:

1. The announcement itself labels Puzzle #11 **steganography**.
2. The output is a **private key** usable through MEW's "Access by Private Key" path.
3. "Format does not matter" argues against a solution that fundamentally depends on PNG-only
   chunks, byte offsets, compression, or fragile LSB values. A visual/semantic carrier that
   survives ordinary re-encoding is more consistent with that statement.
4. "Alternative forms of storing a private key" and the "weird image in your email account"
   example frame the picture itself as a disguised key-storage representation.
5. "Look at the solved puzzles" is an explicit author direction to compare the construction
   style of earlier solved puzzles rather than treating #11 as an isolated arbitrary cipher.

These are constraints, not a claim that any particular visual decoding has already been found.

## Sources

- Public tweet archive mirror:
  https://github.com/HomelessPhD/AR_Puzzles/blob/main/ArweaveP_user_tweets.xlsx
- Community PZL11 mirror:
  https://github.com/HomelessPhD/AR_Puzzles/tree/main/PZL11
- Original announcement URL:
  https://twitter.com/arweavep/status/1252961944807641090
- Storage-method hint URL:
  https://twitter.com/arweavep/status/1253297784633122817
- Future-hint reply:
  https://twitter.com/arweavep/status/1429846914028158977

No further hint was found in the previously searched local Telegram archive (55,002 messages,
November 2021 to May 2026). That Telegram negative does not cover the April 2020 Twitter
window; the workbook above now fills much of that gap.

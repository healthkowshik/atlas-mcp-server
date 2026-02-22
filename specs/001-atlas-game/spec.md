# Feature Specification: ATLAS Word Game

**Feature Branch**: `001-atlas-game`
**Created**: 2026-02-22
**Status**: Draft
**Input**: User description: "Build a MCP server that start the game of ATLAS by printing the message in a nice fun way. 'A T L A S … this is the game of atlas'. Next, it will randomly decide whether the MCP server will start with the first word or ask the user for the first word. Words can be names of continent, country, state, city, etc. User and MCP take turns. Start of the word should be of the same letter as the end of the word."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start the Game (Priority: P1)

A user launches the ATLAS game. The server greets them with the iconic ATLAS title screen
displayed in a fun, visually engaging format. The server then randomly decides who plays
the first word: if the server goes first, it announces a geographic name and tells the user
which letter their word must begin with; if the user goes first, the server prompts them
to name the opening geographic location.

**Why this priority**: This is the entry point for the entire experience. Without a working
game start, no other story is reachable. The title screen and opening move together form
the complete MVP: a player can experience the full game loop even with just this story.

**Independent Test**: Launch the game tool and verify the ATLAS title screen appears,
followed by either the server's opening word (with the required starting letter shown)
or a prompt asking the user for the first word.

**Acceptance Scenarios**:

1. **Given** a user requests to start a new ATLAS game, **When** the game initialises,
   **Then** the ATLAS title screen — "A T L A S … this is the game of atlas" — is
   displayed in a visually decorated, fun format before any game move occurs.

2. **Given** the game has started, **When** the random coin-flip selects the server to
   go first, **Then** the server announces a valid geographic name and clearly states
   which letter the user's next word must begin with.

3. **Given** the game has started, **When** the random coin-flip selects the user to go
   first, **Then** the server prompts the user to enter the opening geographic name
   without revealing any prior move.

4. **Given** a game is already in progress, **When** the user requests to start a new
   game, **Then** the previous session is discarded, state is reset, and a fresh game
   begins with the title screen.

---

### User Story 2 - Player Submits a Word (Priority: P2)

During the user's turn, the user provides a geographic name (continent, country,
state/province, or city). The server validates the submission against three rules: the
word must be a recognised geographic name, it must begin with the letter that ended the
previous word, and it must not have been played already in the current session. On success
the server confirms the move; on failure it clearly explains the specific reason and lets
the user try again.

**Why this priority**: Accepting and validating user words is the core interactive loop.
Without this story the game cannot progress beyond the opening move.

**Independent Test**: With a game in progress and the user's turn active, submit (a) a
valid word, (b) a word that breaks the letter chain, (c) a non-geographic word, and
(d) a previously used word — verify each produces the correct response.

**Acceptance Scenarios**:

1. **Given** it is the user's turn and the required starting letter is "A", **When** the
   user submits "Argentina", **Then** the server confirms the word is accepted, notes it
   ends in "A", and proceeds to play its own word starting with "A".

2. **Given** it is the user's turn and the required starting letter is "A", **When** the
   user submits "Brazil", **Then** the server rejects the submission, states that "Brazil"
   does not start with "A", and asks the user to try again without advancing the turn.

3. **Given** it is the user's turn, **When** the user submits a word that is not a
   recognised geographic name (e.g., "Blorbistan"), **Then** the server rejects it,
   explains it is not a recognised geographic name, and asks the user to try again.

4. **Given** "India" has already been played in the current session and it is the user's
   turn, **When** the user submits "India", **Then** the server rejects it, states the
   word has already been used, and asks the user to try again.

---

### User Story 3 - Server Plays Its Turn (Priority: P3)

After the user submits a valid word, the server automatically selects a valid geographic
name that begins with the last letter of the user's word, announces its choice, and
passes the turn back to the user with a clear indication of the next required starting
letter.

**Why this priority**: The server's autonomous response is what makes this a two-player
game rather than a solo validator. It can be independently tested by triggering it after
a valid user submission.

**Independent Test**: Submit a valid geographic word on the user's turn and verify the
server responds with a valid geographic name starting with the correct letter, without
repeating any previously used word.

**Acceptance Scenarios**:

1. **Given** the user has just played "India" (ends in "A"), **When** the server takes
   its turn, **Then** the server announces a valid geographic name starting with "A"
   (e.g., "Austria") and states the user's next word must start with "A".

2. **Given** the user has played a word ending in a rare letter (e.g., "X"), **When**
   no valid geographic name starting with that letter exists in the server's knowledge,
   **Then** the server declares it cannot continue, concedes the round, and announces
   the user has won.

3. **Given** the server has already played several words in the session, **When** it
   selects its next word, **Then** none of the previously played words (by either player)
   appear in the server's response.

---

### User Story 4 - Player Runs Out of Words (Priority: P4)

The game continues through as many turns as needed until one player — either the user or
the server — genuinely cannot produce any valid geographic name starting with the required
letter. This is the only way the game ends. The server then announces which player won
and which lost, summarises the full word chain played during the session, and offers to
start a new game.

**Why this priority**: Game termination with a clear result is necessary for a complete
and satisfying experience, but is a natural extension of the core loop.

**Independent Test**: Engineer a scenario where the server or user cannot continue (e.g.,
a word ending in a letter with no remaining geographic names) and verify the game-over
message, winner announcement, and word chain summary all appear correctly.

**Acceptance Scenarios**:

1. **Given** it is the user's turn and the required starting letter is "X", **When**
   the user explicitly concedes they cannot think of a valid geographic name starting
   with "X", **Then** the server declares the user has lost, announces the server won,
   and displays the full word chain from the session.

2. **Given** the server cannot find a geographic name starting with the required letter,
   **When** it is the server's turn, **Then** the server concedes, declares the user the
   winner, and displays the full word chain from the session.

3. **Given** a game has just ended, **When** the game-over screen is shown, **Then** the
   server offers the user the option to start a new game.

---

### Edge Cases

- What happens when a geographic name has an ambiguous last letter due to trailing
  punctuation or alternate spellings (e.g., "Côte d'Ivoire", "São Paulo")?
  → The server strips diacritics and punctuation and uses the last alphabetic character.
- What happens when a city name is the same as a country name (e.g., "Mexico")?
  → The word is valid; duplicate recognition (country vs. city) is irrelevant to gameplay.
- What happens when the user submits a word with different capitalisation (e.g., "iNDiA")?
  → The server treats all submissions as case-insensitive.
- What happens if the server exhausts its known words starting with the required letter?
  → The server concedes that turn; the user wins.
- What happens if a geographic name ends in a space or hyphen (e.g., "New York")?
  → The last alphabetic character of the full name is used as the chain letter.
- What happens if the user keeps submitting invalid words on their turn?
  → The server rejects each one with a reason and the user retains their turn indefinitely;
  invalid submissions never end the game. Only an explicit concession ends the user's turn.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The server MUST display the ATLAS title screen — rendering "A T L A S …
  this is the game of atlas" in a visually engaging, fun format — every time a new game
  session is started.
- **FR-002**: The server MUST randomly determine, at the start of each game, whether the
  server or the user plays the first geographic word; the randomisation MUST be
  unpredictable (not always the same outcome).
- **FR-003**: When the server is selected to play first, it MUST choose and announce a
  valid geographic name as the opening word and state which letter the user's word must
  begin with.
- **FR-004**: When the user is selected to play first, the server MUST prompt the user
  to enter the opening geographic name without pre-playing any word.
- **FR-005**: Users MUST be able to submit a geographic name as their turn's move via a
  dedicated game tool action.
- **FR-006**: The server MUST validate that each user submission is a recognised
  geographic name (continent, country, sovereign state, administrative region such as
  a US state or equivalent, or major city).
- **FR-007**: The server MUST validate that each submission's first letter matches the
  last alphabetic character of the previously played word; validation MUST be
  case-insensitive.
- **FR-008**: The server MUST validate that each submission has not been played already
  in the current game session (case-insensitive duplicate check).
- **FR-009**: On an invalid submission, the server MUST reject the word, provide a clear
  explanation of the specific reason for rejection (wrong starting letter / not a
  geographic name / already used), and allow the user to submit again without
  advancing the turn. Invalid submissions MUST NEVER end the game; the user always
  retains their turn and may try as many words as needed.
- **FR-010**: On a valid user submission, the server MUST automatically select a valid
  geographic name starting with the last alphabetic character of the user's word,
  announce its choice, and state the letter the user's next word must begin with.
- **FR-011**: The server MUST NOT reuse any word (by either player) within the same game
  session when selecting its own move.
- **FR-012**: When the server cannot find a valid geographic name for its turn, it MUST
  concede, declare the user the winner, display the complete word chain played, and
  offer to start a new game.
- **FR-013**: When the user explicitly concedes on their turn — by signalling they cannot
  find any valid geographic name starting with the required letter — the server MUST
  declare the user has lost, announce itself the winner, display the complete word chain
  played, and offer to start a new game. Submitting an invalid word is NOT a concession;
  the user must take a deliberate action to end their turn.
- **FR-014**: Starting a new game MUST fully reset all session state (word history, turn
  order, chain letter) before the title screen is displayed.

### Key Entities

- **Game Session**: The active instance of one ATLAS game. Tracks: current turn (server
  or user), the complete ordered list of words played, and the required starting letter
  for the next move.
- **Geographic Word**: A valid place name with its canonical spelling, first letter, and
  last alphabetic character. Belongs to one of: continent, country/sovereign state,
  administrative region (state/province), or major city.
- **Move**: A single play by either participant. Records the word submitted, the player
  who submitted it, and whether it was accepted or rejected.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The ATLAS title screen is displayed within 1 second of a new game being
  started, every time.
- **SC-002**: 100% of user submissions are correctly validated for letter-chain compliance
  (first letter of new word must match last letter of previous word).
- **SC-003**: 100% of user submissions are correctly validated for geographic authenticity;
  no invented or non-geographic names are accepted.
- **SC-004**: 100% of previously played words are correctly excluded from both user
  validation and server word selection within a session.
- **SC-005**: The server successfully produces a valid response word for at least 90% of
  all possible incoming starting letters across typical gameplay.
- **SC-006**: Every invalid submission receives a rejection message that names the
  specific rule violated, enabling the user to self-correct without external help.
- **SC-007**: A complete game session (start → multiple alternating turns → game over →
  result display) runs end-to-end without errors or ambiguous states.
- **SC-008**: A new game started immediately after a previous session contains zero
  residual state (no words from the prior game reappear as "already used").

## Assumptions

- "Geographic names" for this game means: the seven continents, all UN-recognised
  sovereign countries, their primary administrative subdivisions (e.g., US states,
  Indian states, Canadian provinces), and internationally well-known major cities
  (population > 500,000 or national/regional capitals). Obscure villages and hamlets
  are out of scope.
- The last letter of a multi-word geographic name (e.g., "New York") is the last
  alphabetic character of the full name ("K"), after stripping punctuation and diacritics.
- Word validation and the server's word selection are case-insensitive; "india" and
  "India" are treated as the same word.
- A single game session is scoped to one conversation context; the session persists
  until the game ends or the user explicitly starts a new game.
- There is no turn time limit; users may take as long as needed to submit a word.
- There is no maximum number of turns; the game continues indefinitely until a player
  genuinely runs out of valid geographic words. This is the sole termination condition —
  no time limits, turn limits, or score limits exist.
- The server's geographic word list is derived from well-known international knowledge;
  highly localised or recently renamed places may not be covered.

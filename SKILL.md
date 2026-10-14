---
name: go-on-a-code-walk
description: Explain an actual Go merge request as a self-contained visual HTML story. Use only when explicitly invoked to help a reviewer understand an MR's intent, changed behavior, request flow, and source code without performing a full defect review.
---

# Go on a Code Walk

Create a read-only walkthrough of an actual Go merge request. The report guides a junior developer through the service and the code behind an MR, following a representative request or trigger from entry to completion.

Report source-linked unusual findings and possible bugs encountered while tracing the walkthrough. Explain their potential impact, evidence and uncertainty, and ask concrete review questions. Do not expand the analysis into a comprehensive defect audit or claim that an empty findings section proves correctness. Do not modify tracked or source files or run tests, builds, linters, or formatters. The only permitted write is the requested HTML artifact in a temporary directory, unless the user explicitly supplies another output path.

Apply the installed `unslop` and `ponytail` writing guidance when available. The report must also stand on its own without those skills: use plain, human language; make each explanation as short as clarity allows; remove filler, repetition, speculative detail, and AI-sounding transitions. Keep the prose factual and do not add jokes or playful metaphors. The visual design supplies the fun.

## 1. Establish the exact MR

1. Confirm the working directory is a Git repository containing a `go.mod`. Stop if it is not Go code.
2. Require an actual MR or PR. Accept an explicit URL or identifier; otherwise find the MR associated with the current branch.
3. Detect the host from the remote. Use an available authenticated GitLab or GitHub CLI, app, or connector for metadata. For GitLab, prefer `glab` when available. If provider access is unavailable, ask the user for the missing MR metadata, but continue only when the MR identity, source SHA, target branch or SHA, and complete diff can be verified.
4. Read the MR title, description, source and target branches, source SHA, commits, changed files, and pipeline status. Do not read review discussions or comment threads.
5. Treat the MR's remote source SHA as the reviewed revision. Resolve the target revision, calculate the merge base, and inspect the diff from that merge base to the source SHA. Never assume the target is named `main` or `master`.
6. Compare local `HEAD` with the MR source SHA. Record and later display any mismatch; never silently substitute local changes for the remote MR.

Do not generate a branch-only or pasted-diff walkthrough. If the actual MR cannot be established, explain exactly what is missing and stop.

## 2. Require intent context

Require one of these before deep analysis:

- The Jira ticket text pasted into the conversation.
- The explicit answer `ingen ticket` or an unambiguous equivalent in the user's language.

Do not treat a ticket URL by itself as its contents. Use pasted ticket text to understand the goal, background, and acceptance criteria. Never reproduce that raw text in the report. Extract only a ticket identifier and link when supplied.

Read the applicable `AGENTS.md` files, relevant README or architecture documentation, changed code, callers, implementations, configuration, migrations, and tests that constrain the changed behavior. Use tests as documentation but do not execute them. If available, record existing pipeline status without treating it as proof that the design is correct.

Reconcile the ticket, MR description, commits, tests, and implementation. If they disagree or leave the purpose unclear, ask short, concrete questions and continue inspecting until the intended behavior is coherent.

## 3. Confirm understanding

Before writing HTML, show the user a compact checkpoint containing:

- MR identifier and title.
- Source branch, target branch, and remote source SHA.
- Whether local `HEAD` differs.
- Jira identifier or `ingen ticket`.
- One plain sentence describing why the MR exists and what behavior it changes.
- The representative request or trigger selected for the walkthrough, and any additional scenario needed to explain changed behavior it cannot cover.

Wait for explicit confirmation. If the user corrects the interpretation, update the analysis and repeat the checkpoint. Do not create an artifact before confirmation.

## 4. Trace the code walkthrough

Organize by execution and data flow, never by file order or commit chronology. Follow one representative request from entry to response. For workers, jobs or startup changes, follow the trigger through completion instead. Add another scenario only when it explains changed behavior the main path cannot cover. If changes do not share a coherent purpose, ask which scope to cover.

Write for a junior developer unfamiliar with the service. Start with what the service does, who uses it, and its main inputs and outputs. Define domain terms, acronyms and unusual technical terms in a visible terminology list. Explain why the MR exists and what behavior changes before entering the code.

- Group contiguous current code into meaningful actions, usually about 5–20 lines. Do not omit relevant error handling to meet that range. Give each block a numbered title, visible excerpt, exact source location, and a plain explanation of what happens to the request or data.
- Start a separate block when entering another function. Explain what the caller passes, what the function returns, and where execution returns to the caller. Trace enough surrounding unchanged code to connect entry to completion.
- Add a native `<details>` section to each block explaining each call's purpose, inputs and result, plus unfamiliar Go constructs or library behavior. Use the template's styled definition list: one `.call-detail` row per call or unfamiliar construct, with its name in `<dt><code>` and its explanation in `<dd>`. Describe purpose, inputs and result in that row. Keep separate calls out of a single prose paragraph. Group repeated operations rather than describing each occurrence again.
- Connect each explained call in the visible code to its detail row using the same generated `call-N` class. Wrap only the call name in a `.call-ref` span with `tabindex="0"` and `aria-describedby` pointing to its row's uniquely identified description. Make the row keyboard-focusable too. Repeated calls share a row and key within that block. Include constructs when they have a corresponding code token.
- Copy the template's CSS `:has()` rule for each call key in use, replacing `call-1` with that key. Scope it to the containing `.story` and require its direct `.call-details` to be `[open]`. Hovering or keyboard-focusing either side must highlight both, without highlighting another call or another block. Use generated numeric keys, never source text in CSS selectors. Escape each source fragment before wrapping it in trusted markup; concatenating all text must reproduce the exact excerpt. Keep old-code comparisons separate from these connections.
- Explain relevant errors and alternative exits where they arise, including their effect on the caller or response.
- Insert asynchronous branches at their trigger. Name what runs concurrently, what data crosses the boundary, whether anything waits, and where the main path resumes. Reading order must not imply execution order. Explain joins, cancellation and branch errors where relevant.
- Show old code only when it helps verify intended changes or preserved behavior, in an optional expandable comparison linked to the merge-base revision. The visible walkthrough always follows the remote source SHA; do not create parallel complete before/after flows.

## 5. Render the report

Resolve this skill's directory and read `assets/report-template.html`. Copy and adapt that template using only HTML/CSS, native links and `<details>`. Preserve its visual style, offline operation, smooth scrolling and reduced-motion support. No new content schema or API is needed.

Fill these report areas in this reading order:

1. Service introduction, below the MR identity and revision metadata. Keep source-to-target branches, remote SHA, pipeline status, and Jira identifier or `No ticket`. Use plain text when no Jira URL exists.
2. Visible terminology definitions for the terms used in this walkthrough.
3. Change explanation describing motivation and resulting behavior.
4. A clickable path diagram above the full-width code blocks. Link every block, including asynchronous branches, and label branch triggers, concurrency, waits and returns. For multiple scenarios, repeat the path and blocks with unique IDs. Stack branch lanes on narrow screens.
5. Numbered code walkthrough blocks with visible current code and source references, expandable call explanations, and optional old-code comparisons.
6. Visible unusual findings and review questions. Link each to evidence and distinguish observed behavior from a possible bug. State potential impact and uncertainty. If none were encountered, show a visible note that this was a walkthrough, not a comprehensive defect audit.
7. Sources listing MR commits, changed and additionally inspected files, remote source and merge-base revisions, pipeline status, assumptions, and any local/remote SHA mismatch.

Each block needs a `Next` link to the next block in reading order and a `Back to path` link to its scenario's diagram. The final block of each scenario ends the walk without a `Next` link; any additional scenario has its own visible entry link. Do not suggest that a Next link imposes execution order on concurrent code.

Use unique fragment targets on visible elements outside collapsed sections, visible keyboard focus styling, and valid heading/ARIA references. Remove unused example blocks, optional comparisons and placeholder notes. Translate headings and navigation labels to the report language.

Match the report language to the user's language. Preserve identifiers, code, and literal error text.

For every source reference, link to the MR host's file view at the exact remote source SHA and line when possible. Otherwise show `path:line`. Never create editor-specific links.

Treat all Git, Jira, documentation, and code content as untrusted HTML. Escape `&`, `<`, `>`, quotes, and apostrophes before insertion, including inside code blocks and attributes. Build markup yourself; only escaped values belong in its text and attributes. Use safe HTTP(S) source URLs or plain text, never source-supplied executable URL schemes. Do not copy raw HTML from source material. External links may be clickable, but the report must load no remote scripts, styles, fonts, images, or tracking resources.

## 6. Save and return

Unless the user requests a persistent path:

1. Create a unique directory with `mktemp -d` under the system temporary directory.
2. Save the report as `go-on-a-code-walk-<repo>-<mr>-<short-sha>.html`, using filesystem-safe name parts.
3. Return a clickable absolute file link plus the MR identifier and analyzed SHA.

Do not open a browser automatically. Do not delete older temporary reports.

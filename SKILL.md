---
name: go-on-a-code-walk
description: Explain an actual Go merge request as a self-contained visual HTML story. Use only when explicitly invoked to help a reviewer understand an MR's intent, before-and-after behavior, affected flow, and evidence without performing a full defect review.
---

# Go on a Code Walk

Create a read-only walkthrough of an actual Go merge request. The report helps an experienced Go developer who may not know this service understand why the MR exists and how behavior changes.

Do not turn this into a conventional code review. Mention only grounded questions or risks that would help the reviewer verify their understanding. Do not modify tracked or source files or run tests, builds, linters, or formatters. The only permitted write is the requested HTML artifact in a temporary directory, unless the user explicitly supplies another output path.

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

Wait for explicit confirmation. If the user corrects the interpretation, update the analysis and repeat the checkpoint. Do not create an artifact before confirmation.

## 4. Build the behavior story

Organize by runtime or user-visible behavior, never by file order or commit chronology.

- For changed existing behavior, create two complete and comparable flows labeled `Before` and `After`. Keep equivalent steps aligned where practical and mark steps as unchanged, changed, added, or removed.
- For a wholly new feature, create one new flow and show where it connects to the existing system. Do not invent an empty before-flow.
- For a mixed MR, use the correct form for each behavior.
- When several changes share one purpose, make them numbered stories on the same page.
- When changes do not share a coherent purpose, stop and ask the user which scope the walkthrough should cover.

Each flow step needs only a short component or actor name and one sentence describing what enters, happens, or leaves. Include persistence, external calls, asynchronous boundaries, and error paths only when they materially explain the change.

Write the core story for an experienced Go developer unfamiliar with the service. At the first use of a project-specific component or domain term, add a short collapsed `What is this?` explanation when it would help a newcomer. Do not explain ordinary Go syntax or standard-library concepts.

## 5. Render the report

Resolve this skill's directory and read `assets/report-template.html`. Copy and adapt that template rather than designing a new page. Preserve its layout, styles, accessibility behavior, and lack of JavaScript.

Fill these report areas:

1. MR identity, source-to-target branches, remote SHA, pipeline status, and Jira identifier or `No ticket`. Use plain text rather than an empty link when no Jira URL exists.
2. `MR in one minute`: the motivation and resulting behavior in a few short sentences.
3. One or more numbered behavior stories with the appropriate before/after or new-feature flow.
4. Collapsed context explanations next to the first relevant concept.
5. Collapsed code evidence containing only the smallest useful excerpt.
6. A collapsed `Things to verify` checklist. Each item is a concise question with a source reference, not a verdict or severity score. If there are no items, show the template's visible disclaimer instead.
7. A collapsed sources section listing MR commits, changed files, additionally inspected files, assumptions, pipeline status, and any local/remote SHA mismatch.

Match the report language to the user's language. Preserve identifiers, code, and literal error text.

For every source reference, link to the MR host's file view at the exact remote source SHA and line when possible. Otherwise show `path:line`. Never create editor-specific links.

Treat all Git, Jira, documentation, and code content as untrusted HTML. Escape `&`, `<`, `>`, quotes, and apostrophes before insertion, including inside code blocks and attributes. Do not copy raw HTML from source material. External links may be clickable, but the report must load no remote scripts, styles, fonts, images, or tracking resources.

## 6. Save and return

Unless the user requests a persistent path:

1. Create a unique directory with `mktemp -d` under the system temporary directory.
2. Save the report as `go-on-a-code-walk-<repo>-<mr>-<short-sha>.html`, using filesystem-safe name parts.
3. Return a clickable absolute file link plus the MR identifier and analyzed SHA.

Do not open a browser automatically. Do not delete older temporary reports.

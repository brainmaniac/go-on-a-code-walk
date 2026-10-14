<p align="center">
  <img src="assets/go-on-a-code-walk.png" alt="Go on a Code Walk: a person walking a dog" width="600">
</p>

<p align="center">
  <a href="SKILL.md"><img src="https://img.shields.io/badge/Codex-Skill-10a37f?style=flat-square" alt="Codex skill"></a>
  <img src="https://img.shields.io/badge/Go-Code%20Walkthrough-00add8?style=flat-square&logo=go&logoColor=white" alt="Go code walkthrough">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="MIT license"></a>
</p>

# Go on a Code Walk

Turn a Go merge request into a guided code walkthrough a junior reviewer can follow.

Go on a Code Walk is an explicit Codex skill. It reads the MR, its commits, the relevant code and tests, and optional Jira context. It then creates a self-contained HTML report following a representative request or trigger through the code that explains the change.

The report starts with the service, terminology and reason for the change. A clickable path leads through visible current-code excerpts, with call explanations and useful old-code comparisons in expandable sections. With call details open, hovering or keyboard-focusing a call or its explanation highlights both.

## What it does

- Verifies the exact remote MR revision before analysis.
- Uses pasted Jira context, or an explicit `no ticket`, to understand intent.
- Follows one request or trigger from entry to completion, adding another scenario only when needed.
- Explains calls, returns, error exits and concurrent branches where they occur.
- Defines domain terms and unfamiliar constructs for a junior developer.
- Records source-linked unusual findings and review questions encountered along the path.
- Links evidence to exact files and revisions when the MR host permits it.
- Creates one local HTML file with no remote scripts, fonts or images.
- Reads tests as documentation but leaves test execution to the pipeline.

It does not modify the reviewed repository or replace a defect-focused code review.

## Requirements

- Codex with local skill support.
- Git.
- A Go repository containing `go.mod`.
- An actual GitHub pull request or GitLab merge request.
- Authenticated access to the MR through an available CLI, app or connector.

## Installation

Clone the repository and symlink it into your personal Codex skill directory:

```sh
git clone https://github.com/brainmaniac/go-on-a-code-walk.git
cd go-on-a-code-walk
mkdir -p "$HOME/.agents/skills"
ln -s "$PWD" "$HOME/.agents/skills/go-on-a-code-walk"
```

OpenAI's [skill documentation](https://learn.chatgpt.com/docs/build-skills) describes the supported skill locations. Some Codex installations use `$CODEX_HOME/skills` instead; use that directory when it is configured.

If the skill does not appear immediately, restart Codex and check `/skills`.

## Usage

Open Codex in the repository with the MR branch checked out, then invoke:

```text
$go-on-a-code-walk
```

You can also identify the MR explicitly:

```text
$go-on-a-code-walk https://github.com/example/project/pull/123
```

The skill will:

1. Resolve the MR, target branch and remote source SHA.
2. Ask you to paste the Jira ticket text or answer `no ticket`.
3. Inspect the changed behavior and its surrounding code.
4. Show its understanding and selected scenarios for confirmation.
5. Generate the HTML walkthrough and return a local link.

The report language follows the language you use with Codex.

## Privacy and safety

The generated page loads no external assets or tracking code. It may still contain source excerpts, repository paths and MR metadata. Treat it like source code and review it before sharing it outside your organization.

Jira text is used as analysis input. The report only retains the ticket identifier and link when supplied.

## Future development

- Refresh an existing walkthrough after new commits and highlight what changed since the previous MR revision.

## Validation

Run the standard-library self-check from this repository:

```sh
python3 tests/check_report.py
```

It fills representative reports with multiple blocks and scenarios, asynchronous branches, optional old-code comparisons and hostile-looking source strings. It checks fragments, navigation order, accessibility references, escaping and offline HTML constraints. Generated fixtures are temporary and removed after the check.

Static checks cannot confirm visual layout or the accuracy of a generated explanation. When a browser is available, check narrow-screen branch stacking, keyboard navigation and reduced-motion behavior. Tests in the reviewed project remain documentation inputs and are not executed by this skill.

## Contributing

Issues and focused pull requests are welcome. Keep the default workflow small, local and useful to someone trying to understand an MR.

## License

[MIT](LICENSE)

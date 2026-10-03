# Mesa Examples — Contributor Infrastructure Prototype

A working prototype of CI and automation for
[`mesa-examples`](https://github.com/mesa/mesa-examples), Mesa's community
gallery of agent-based models.

Built while preparing a GSoC 2026 proposal for [Mesa](https://github.com/mesa/mesa).
The proposal is in [`proposal/`](proposal/); everything else here is the working
implementation of what it describes.

> **Related:** [mesa-examples#346](https://github.com/mesa/mesa-examples/pull/346) — merged upstream.

---

## The problem

A community gallery has a scaling problem that a normal repo doesn't. Every
contributed model is **independent code with its own dependencies**, written by
someone who may never return to maintain it. That creates three pressures at once:

- **One broken model shouldn't break CI for everyone.** If all models are tested
  in a shared environment, a single bad dependency takes the whole suite down —
  and the failure tells you nothing about which model caused it.
- **Review doesn't scale with maintainer attention.** Each new model needs
  someone who understands it, and maintainers can't be that person for every
  submission indefinitely.
- **Contributors need feedback immediately.** A PR that sits silent while CI
  runs is a PR the contributor assumes is being ignored.

## Approach — four pillars

### Pillar 1 — Matrix isolation CI

Each model is tested in its **own isolated job**, discovered dynamically from
the directory structure rather than listed by hand:

```yaml
models=$(ls -d models/*/ | xargs -n1 basename | tr '\n' ' ' | jq -R -c 'split(" ")[:-1]')
echo "models=$models" >> $GITHUB_OUTPUT
```

That output feeds a build matrix, so adding a model to `models/` adds a CI job
automatically — no workflow edit, which means no maintainer bottleneck.

```yaml
strategy:
  fail-fast: false   # keeps every other model's job running when one fails
  matrix:
    model: ${{ fromJson(needs.discover-models.outputs.models) }}
```

`fail-fast: false` is the critical line. Without it GitHub cancels every
sibling job on the first failure, so one broken contribution hides the status of
all the others.

The repo deliberately contains a **deliberately-broken model** alongside working
ones, so the isolation is demonstrably working rather than merely claimed.

### Pillar 2 — PR greeter bot

New PRs get an immediate automated comment explaining what's running and what
the contributor should check while they wait, via `actions/github-script`.
Cheap to build, and it directly addresses the silence problem — a contributor
who sees activity in the first thirty seconds knows the submission landed.

Paired with a [PR template](.github/PULL_REQUEST_TEMPLATE.md) that asks for the
three things reviewers always end up requesting anyway: a `requirements.txt`, a
README, and a screenshot.

### Pillar 3 — Model metadata schema

Every model carries a `metadata.json`:

```json
{
  "name": "Stable Model",
  "author": "@Nandha-kumar-S",
  "domain": "Stable Domain",
  "complexity": "Intermediate",
  "features": ["MultiGrid", "Solara UI"],
  "description": "A stable model for testing purposes."
}
```

Structured metadata is what turns a folder of scripts into something browsable —
it's the input the gallery generator reads.

### Pillar 4 — Ownership and dependency automation

[`CODEOWNERS`](.github/CODEOWNERS) routes review requests for each model back to
the person who wrote it, so expertise follows the code instead of pooling on
maintainers:

```
/models/stable_model/    @Nandha-kumar-S
/models/zombie_model/    @Nandha-kumar-S
```

[`dependabot.yml`](.github/dependabot.yml) keeps both the Actions infrastructure
and each model's Python dependencies current, labelled separately so
infrastructure updates don't get lost among model updates.

## The gallery generator

[`scripts/build_gallery.py`](scripts/build_gallery.py) crawls `models/*/metadata.json`
and emits a static HTML gallery — cards grouped by domain, tagged with the Mesa
features each model demonstrates.

```bash
cd scripts && python build_gallery.py
```

Output: [`index.html`](index.html). A [styled demo](gallery-demo/) using Mesa's
branding is in `gallery-demo/`.

Static generation is the right shape here: the gallery changes only when a model
is merged, so there's nothing to serve dynamically and it can be published
straight to GitHub Pages.

## Repo layout

```
.github/
  workflows/pillar1_ci.yml        matrix-isolated model testing
  workflows/pillar2_greeter.yml   PR welcome bot
  PULL_REQUEST_TEMPLATE.md        contributor checklist
  CODEOWNERS                      per-model review routing
  dependabot.yml                  dependency automation
models/                           test models, incl. a deliberately broken one
scripts/build_gallery.py          metadata -> static gallery
gallery-demo/                     styled gallery mockup
proposal/                         the GSoC 2026 proposal
```

## Status

This is a **prototype**, not production infrastructure. The models in `models/`
exist to exercise the pipeline — they're test fixtures, not real agent-based
models worth studying.

The GSoC proposal wasn't selected. The infrastructure here stands on its own,
and [one contribution](https://github.com/mesa/mesa-examples/pull/346) from the
work was merged upstream.

## What I'd change

- **Generate `CODEOWNERS` automatically** when a model is merged, rather than
  editing it by hand — noted as future work in the file itself, and the obvious
  next step.
- **Cache dependencies between CI runs.** Each isolated job currently installs
  from scratch, which is correct but slow; keying a cache on each model's
  `requirements.txt` would keep the isolation and cut most of the time.
- **Validate `metadata.json` against a schema in CI**, so a malformed file is
  caught at PR time instead of silently breaking the gallery build.
- **Publish the gallery from CI** to GitHub Pages on merge, closing the loop
  between "model merged" and "model visible".

## Built with

GitHub Actions · Python · Mesa · Dependabot

# How this wiki works

This repository authors the vocabulary ([[Hyperfield]], [[Hypernode]], [[Hyperconnection]] and the rest of the stack). It does **not** author anything about the hyperfields themselves. Every statement about a hyperfield on this site is read from that repository at a pinned commit.

* A hyperfield is a git submodule under `fields/`, so there is one dependency edge per repository.
* Dependabot bumps those edges; a push or a dispatch from a hyperfield can bump them sooner.
* Every bump is a pull request on which the wiki is rebuilt, every live reference re-resolved and every commit-pinned citation re-audited.

A live example, read from [[hypermath]] at its pin:

[[hypermath:README.md#L1-L1]]

See `docs/04-wiki-architecture.md` for the reference grammar and the limits of what this can prove.

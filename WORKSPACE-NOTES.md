# Workspace notes — fork-local

Notes for whoever maintains this fork. Not upstream material: this branch
exists so these notes never appear in a PR diff back to AI-DA-STC.

## State

`main` matches AI-DA-STC exactly — no local commits, nothing pending. This
fork exists so that work from a returnable machine has somewhere of its own to
land.

## Remote layout

`origin` is the personal fork over SSH; `upstream` is AI-DA-STC over HTTPS.
Every local branch tracks `origin`, so a bare `git push`/`git pull` never
touches AI-DA-STC. Reading new upstream work is explicit too — a fork does not
auto-sync:

```bash
git fetch upstream && git merge --ff-only upstream/main
```

## Restoring this clone to a stock checkout

If the working copy lives on a machine being handed back, undo the fork wiring
so the next user does not inherit an `origin` pointing at a personal fork over
an SSH key that no longer exists (every pull fails with `no such identity`,
and their commits get misattributed):

```bash
git remote set-url origin https://github.com/AI-DA-STC/AirStack-starling-max2.git
git remote remove upstream
git config --local --unset user.name
git config --local --unset user.email
git config --local --unset core.sshCommand
```

Do this *before* deleting any keyfile the remotes depend on, and push all work
first.

## Sibling

`CrazySwarm2-with-Mocap` is wired the same way and carries a `local-fixes`
branch with a sim fix; see its own `WORKSPACE-NOTES.md`.

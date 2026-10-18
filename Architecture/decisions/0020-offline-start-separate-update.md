# 20. Offline start; dependencies and migrations only in a separate update script

Date: 2026-10-17

## Status

Proposed

Partly supersedes [ADR 10](0010-numbered-sql-migrations.md) (when migrations run) and
[ADR 14](0014-run-from-source-git-pull.md) (what happens after `git pull`).

**TOGAF Phase:** D (Technology Architecture)
**Decision Maker(s):** Project owner (kvelev)
**Stakeholders:** HQ operator, contributors
**Principles:** upholds BP-01 (the system starts when it is needed), BP-03 (backup before migrate),
TP-03 (simple operation); trades off nothing significant

## Context

Field laptops start without internet. The start scripts ran `pip install -r requirements.txt` on every
start, which needs the network even when everything is installed (offline it retried for minutes), and
checked for pending migrations on every start, with the backend migrating at boot behind a backup-marker
guard. The owner asked (2026-10-17) to simplify the app and make it start reliably offline. Updates arrive
by `git pull` or by copying the folder from a USB stick.

## Decision

We will split **start** from **update**:

- `start.ps1` / `start.sh` start the containers, the backend and the frontend. They install nothing,
  never use the network and never change the schema. A missing `.venv` or `node_modules` stops them
  with a pointer to the update script.
- `update.ps1` / `update.sh` (the same script with `-Update` / `--update`) are run on the first install
  and after new code arrives. They install the dependencies whose lock file changed since the last
  successful install (SHA-256 stamps), take a backup when migrations are pending, run
  `python -m backend.db.migrate up`, then start the app.
- At boot the backend migrates only a fresh, empty database (or with `ALLOW_MIGRATE_WITHOUT_BACKUP=true`
  on development data). An existing database with pending migrations makes it refuse to start with
  `DATABASE NEEDS UPDATING` and name the update script. The backup-marker guard in the runner stays as
  a second line of defence for anyone running `migrate up` by hand.

## Consequences

**Positive:**
- An everyday start needs no internet and takes the same path every time.
- The schema only changes in one, explicit step that always backs up first.
- An update copied from a USB stick works offline when no dependency changed.

**Negative / Trade-offs:**
- After new code arrives someone has to run the update script; forgetting it gives a clear refusal at
  start, not a broken app.
- Two entry points to document instead of one.

## Considered options

| Option | Summary | Pros | Cons |
|--------|---------|------|------|
| ✅ **Separate update script** | As above | Offline start, one explicit migration step | Operator must run update after new code |
| Keep start doing everything, with change stamps | pip only on change, migration check every start | One entry point | Start scripts stay long; schema can change during a routine start |
| Backend migrates at boot without a backup guard | Simplest | Least code | A failed migration in the field has no fresh backup behind it |

## Related

- ADR 10, ADR 14, README "Start vs update", `Architecture/guides/admin-guide.md` Т1

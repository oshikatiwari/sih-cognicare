# Contributing

## Branches
- main   → protected, demo-ready only
- dev    → integration branch, everyone merges here first
- feature/<module>-<short-desc>  → your working branch, off dev

## Workflow
1. git checkout dev && git pull
2. git checkout -b feature/games-memory-match   (example)
3. commit small working chunks
4. push branch, open PR into dev (not main)
5. get 1 teammate review before merging
6. merge dev → main only at stage milestones

## Module owners
Person 1: mobile_app/lib/games (Memory + Pattern games), lib/core
Person 2: mobile_app/lib/games (Object Recognition, Routine Recall, Attention), lib/profile
Person 3: ml_pipeline/
Person 4: mobile_app/lib/voice, mobile_app/lib/reminders, backend/app/reminders
Person 5: backend/app (auth, sync), PostgreSQL schema
Person 6: dashboard/

---
name: commit-push
description: Stage all changes, commit with the provided message, and push to main — triggering GitHub Pages auto-deploy. Usage: /commit-push "your commit message"
disable-model-invocation: true
---

Stage all modified files, commit with the message provided in $ARGUMENTS, and push to origin main.

Steps:
1. Run `git status` to show what will be committed.
2. Run `git add -A` (this is a solo-owner repo with no risk of accidentally staging secrets).
3. Run `git commit -m "$ARGUMENTS"`.
4. Run `git push origin main`.
5. Confirm success and remind the user the site will be live at https://wacns.github.io/ within ~60 seconds.

If $ARGUMENTS is empty, ask the user for a commit message before proceeding.

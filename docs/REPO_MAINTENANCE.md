# Repository maintenance (VS Code / Windows PowerShell)

## Routine safe update

```powershell
git status
git pull --ff-only origin main
python scripts/build_public_results_index.py
python scripts/check_public_repo.py
git status --short
```

Stage **only intended** paths; never use `git add -A` indiscriminately:

```powershell
git add -- README.md docs scripts .github/workflows .gitattributes .editorconfig
# To add verified public results (only after manual review):
git add -- 'Notebook 3/results/public' 'Notebook 2/results/source_safe_v2'
git diff --cached --name-only
git diff --cached --check
git commit -m "docs: refresh reviewed research evidence"
git push origin main
```

If there are local uncommitted changes, review them before pulling/replacing a file. If any private path has ever been published, `.gitignore` alone **does not erase Git history**: stop, revoke credentials if needed, and follow GitHub's sensitive-data removal instructions.

New Kaggle job private exports belong under `local_artifacts/` (ignored), not the public results tree. Publish reviewed **aggregates only** using `scripts/publish_public_results.py`.

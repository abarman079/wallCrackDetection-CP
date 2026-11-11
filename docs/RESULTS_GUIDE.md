# Public results and figures policy

## What belongs in GitHub

| Format | Public-safe examples | Do not upload |
|---|---|---|
| `.json` | Run status, configuration fingerprint, **aggregate** train/dev metrics, synthetic tests, SHA digests | File-by-file label registers, reviewer information, private source paths, unsealed test/calibration information |
| `.xlsx` | Aggregated source counts, risk/metric **summary** tables, experiment comparison after completed runs | Per-image IDs, private sample manifests, copied restricted spreadsheets |
| `.png`, `.jpg` | Original charts made from permitted aggregate counts and model-performance plots from eligible development metrics | Raw/source crack photographs, contact sheets, masks or overlays lacking explicit rights; images with GPS/EXIF |
| `.csv` | Aggregate results, statistical tables, figure indexes and public provenance catalogs | Per-image acquisition lists, private parent/source lineage and unknown-rights metadata |
| `.md` | Methods, technical limitations, reproducibility and outcome reports | Secrets, absolute private paths, reviewer identities, sealed information |

**New artifact ceiling:** 10 MiB per reviewed result (stricter than GitHub). If over that, keep it in your controlled private Kaggle archive and publish its digest, summary and authorized download pointer instead.

## Publication workflow

1. Preserve the original private `ALL_OUTPUTS` ZIP and `.sha256` **outside Git**. Do not extract it directly into a tracked repository folder.
2. Copy **only selected, independently reviewed** aggregate JSON/CSV/XLSX and original figures into a workstation folder such as `Downloads\CrackSAFE_public_export`. Do not include per-sample prediction maps, calibration/test material or contact sheets.
3. Inspect the selected files and confirm permissions to share every image. Use `python scripts/publish_public_results.py --source "<folder>" --phase 3 --run-id <unique_id> --dry-run` to preview.
4. After inspection, run the same command with `--apply --reviewed`. The tool checks file types/sizes, obvious private identifiers, basic document integrity, and strips common image metadata. **This is a guardrail, not a privacy/rights certification.**
5. Run `python scripts/build_public_results_index.py` and `python scripts/check_public_repo.py`. Inspect staged paths with `git diff --cached --name-only` before committing.
6. Commit only the reviewed public files and the index; record source ZIP SHA and scientific status in a public report. Do not commit the private source ZIP.

Public results go under `Notebook N/results/public/run_<actual_id>/` for traceability. Older preserved phase results keep their existing archived paths.

## Scientific interpretation

- The 72-pair Phase-02 diagnostic verifies **technical hash/mask reconstruction in the sampled images**, not the correctness of all labels.
- Development Dice/clDice is not formal independent benchmark accuracy, and it is not a two-risk selective guarantee.
- Synthetic charts must be labeled synthetic. A metric plot without a successfully completed run and explicit cohort/seed provenance is not empirical evidence.
- Photos/screenshots are not publishable solely because they are small or available online.

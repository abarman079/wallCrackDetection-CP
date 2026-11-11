# Publication-safe Phase-03 development results

Reviewed **aggregate** per-seed JSON/CSV/XLSX metrics and original figures may be published in `run_<actual_run_id>/` subdirectories. Record the architecture, seed, cohort, training worker SHA, actual epoch, checkpoint SHA digest, scientific scope and metric definition. Do not publish checkpoint bytes, restricted images, predictions on sealed data, raw per-sample IDs or private original manifests.

Use `python scripts/publish_public_results.py --help`, followed by `python scripts/build_public_results_index.py`, to curate and index genuine evidence. This directory intentionally contains no fabricated final results in the current update.

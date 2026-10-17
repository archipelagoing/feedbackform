# Preference extraction evaluation

`preferences.json` contains 12 synthetic, author-labeled examples: eight development
cases and four reserved cases. These are initial expectations, not independent
human annotations or a representative user study. Labels and category boundaries
need teammate review. The held-out examples are reserved for a later final run;
they are visible in the repository and do not constitute a blind benchmark.

No live model evaluation has been run. API and browser tests use explicit provider
doubles and measure application behavior, not model quality.

From `backend/`:

```sh
.venv/bin/python -m scripts.evaluate_preferences --validate-only
```

After configuring server-side `OPENAI_API_KEY` and `OPENAI_MODEL`, this command
makes paid calls for development examples and writes predictions to ignored local
data. Do not commit participant data or evaluation secrets.

```sh
.venv/bin/python -m scripts.evaluate_preferences --split development --output data/evaluations/development-01.jsonl
```

Use `--split heldout` with a new output file only after freezing the prompt and
category guidelines. Outputs record model, usage, latency, errors, predictions,
and the expected meaning for manual adjudication. Files are never overwritten.

The automatic source/kind count match is a structural diagnostic. A result can
match source and kind while reversing the participant's meaning, so this count
must not be reported as semantic precision or recall. Quote checks validate exact
substrings and attribution; they do not establish entailment.

Two teammates should independently judge each prediction's fidelity, negation,
conditions, uncertainty, missing signals, and invented endorsement, then resolve
disagreements. Permit alternate categories where the written guidelines justify
them. Record prompt/model versions and every revision to labels. Measure correction
effort in a separate four-person pilot. Set agreed quality targets before claiming
success; these 12 cases are a starting dataset, not evidence of broad effectiveness.

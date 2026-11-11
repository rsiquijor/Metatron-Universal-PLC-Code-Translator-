# Metatron Cube AI — PLC Translator Engineering Preview

This is an **engineering preview**, not a verified universal PLC translator. It accepts one Boolean IEC-style Structured Text assignment with `AND`, `OR`, `NOT` and parentheses. It produces Structured Text or **illustrative, non-importable** Ladder notation. Vendor platform choices are labels only; no vendor compilation or functional safety verification occurs.

## Render deployment

The repository contains `render.yaml` for a Docker web service on Render's Free plan. Create a Render Blueprint from this repository, review its plan, and set `METATRON_API_KEY` to a strong secret before approval. The service serves a browser UI at `/`, health at `/healthz`, and POST `/api/translate` protected by `X-API-Key`.

## Local development

`pip install -r requirements.txt && uvicorn app.main:app --reload`

Do not deploy generated PLC logic to machinery without qualified engineering review, vendor compilation, simulation and commissioning tests.

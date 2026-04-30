# Translation Handler Notes

## Overview
J.A.R.V.I.S. uses the **LibreTranslate** API for text translation and language detection.
LibreTranslate is free and open-source; a public instance is available at `https://libretranslate.com`.

## Configuration
| Environment Variable | Default | Purpose |
|---|---|---|
| `LIBRETRANSLATE_URL` | `https://libretranslate.com` | Base URL of the LibreTranslate instance |
| `LIBRETRANSLATE_KEY` | *(empty)* | Optional API key for authenticated instances |

Set these in the project `.env` file.

## Supported Languages (common aliases)
- English (`en`)
- Spanish (`es`)
- French (`fr`)
- German (`de`)
- Italian (`it`)
- Portuguese (`pt`)
- Russian (`ru`)
- Chinese (`zh`)
- Japanese (`ja`)
- Arabic (`ar`)
- Hindi (`hi`)
- Korean (`ko`)

Full ISO 639-1 codes can be passed directly when a language alias is not listed.

## Caching
Translation results are cached locally in `DATA/translation_cache.json` for **24 hours**
to reduce redundant API calls.

## Functions
- `translate_text(text, target, source="auto")` — Translate text; source auto-detected if omitted.
- `detect_language(text)` — Detect language of arbitrary text.
- `format_translation(original, translated, target)` — Pretty-print result.

# bcv-rates
Official Banco Central de Venezuela (BCV) exchange rates for USD and EUR against the bolívar, published as small JSON files for apps.

Both files are single-line objects with the same fields:

- `date` is the BCV value date (`YYYY-MM-DD`).
- `usd` and `eur` are integer cents (bolívares × 100).

`data/current.json` is the rate to use today. Its `date` is the last day that rate applies.

`data/next.json` is the already-published rate for the next BCV value date (usually visible after the afternoon publish). Use it to preview that fare the evening before. `next.date` is that value date, not calendar tomorrow on weekends or holidays. The file is absent when the BCV page shows no future value date.

Example URLs (replace `USER` if needed):

- `https://raw.githubusercontent.com/arnoldo-r/bcv-rates/main/data/current.json`
- `https://raw.githubusercontent.com/arnoldo-r/bcv-rates/main/data/next.json`

# Wind Desk

A React + Python pilot for reviewing the national wind generation forecast available at a day-ahead decision cutoff and measuring its subsequent error. Uses genuine archived Elexon WINDFOR and FUELHH WIND data only. **AI assistance: OpenAI Codex was used for research, implementation, documentation and verification.**

## Submission status

- Application: [Wind Desk on Vercel](https://q7m2vk.vercel.app). React static frontend and Python API.
- Public repository: [viraj2510/q7m2vk](https://github.com/viraj2510/q7m2vk).
- Video: [Unlisted YouTube demo](https://youtu.be/oAJ6wWn_z6w), 6:11. Customer pilot 00:00–02:47; technical review 02:47–06:11. Uses synthetic narration and captured app screens, disclosed in the video and description. Local MP4: `docs/video/wind-desk-demo.mp4` (not committed).
- Submission form: URL missing from the supplied brief. No form has been submitted.
- Anonymous HTTP checks returned 200 for the app, analysis API and public repository; the deployed app also loaded in the isolated in-app browser. A literal incognito-window check is still outstanding: native computer-use access to Chrome was not approved by the tool.

## Run

With Docker Desktop running:

```sh
docker compose up --build
```

Open http://localhost:8000. Docker builds React and serves the output alongside FastAPI from the same origin as a non-root user. Docker execution requires an installed engine.

For local development, Python 3.12+ and Node 22+:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app:app --port 8000
```

In another terminal:

```sh
cd frontend
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

Open the Vite URL (normally http://localhost:5173). `/api` is proxied to Python. API schema: http://localhost:8000/docs. Health: `/api/health`. Analysis: `/api/analysis?decision=2026-01-15&cutoff=09:50`. CSV: `/api/export` with the same parameters.

## Interpretation and pilot findings

“Purchase decisions made in January” means decision dates 1–31 January 2026 and delivery dates 2 January–1 February, inclusive. The interface always shows both dates. All January times are London/GMT = UTC. Default cutoff 09:50 is an explicit N2EX auction assumption, not a universal GB market cutoff; change it to explore another decision time. At exactly the cutoff a publication is included; production trading needs an earlier cutoff to allow processing and order entry.

At 09:50, there are **744/744 paired hourly observations**, **MAE 2,013.01 MW**, **RMSE 2,505.94 MW**, **bias +1,729.93 MW**, **WAPE 17.84%**. These are descriptive results for one cohort and cutoff, not estimates of trading profit or causal imbalance costs. Positive bias indicates over-forecast generation.

1. For each delivery target select the latest `publishTime <= decision cutoff`, never the latest revision available today. Targets use `[delivery start, next midnight)`.
2. The downloaded WINDFOR targets are hourly. Average the two complete FUELHH WIND half-hours within that hour. No interpolation or zero filling. Missing pairs are excluded from error metrics and reduce coverage.
3. Error = forecast − actual (MW). MAE = mean absolute error; RMSE = square root mean squared error; bias = mean signed error; WAPE = sum absolute error / sum absolute actual × 100. Zero denominator returns null.
4. Positive hourly errors sum to shortfall MWh because intervals are one hour. This is gross wind shortfall, without netting negative errors between hours or representing actual purchased electricity.
5. Historical P90 = nearest-rank 90th percentile of `max(error, 0)` from delivery dates strictly before the selected decision date, at the same cutoff. It uses the growing January sample, returns unavailable without history and is an empirical reference, **not** a calibrated prediction interval. No cross-validation or model fitting is claimed.

WINDFOR represents operationally visible wind, and national wind is not the utility’s portfolio. No demand, prices, contracted position, thermal availability or non-wind renewable data is used. The product cannot calculate how much this customer should procure. Generation outturns are retrospective snapshots: actual revision vintages and historical publication latency are not reconstructed. The P90 history filter therefore does not constitute a strict operational backtest of actual data availability. Publication time is used as the forecast availability proxy; ingestion/processing delays are unknown.

## Design and files

```text
frontend/src/main.jsx     React controls, charts, KPI cards, audit table and CSV link
frontend/src/style.css    Responsive visual design
frontend/vite.config.js   Development API proxy and production build
frontend/pnpm-lock.yaml   Resolved frontend dependencies
backend/analysis.py       Pure as-of selection, hourly joining and metrics
backend/app.py            Validated FastAPI endpoints and CSV serialization
api/index.py              Vercel Python entry point
server.py                 Single-origin Docker/static server
data/windfor.json         Raw WINDFOR publications (includes Dec 31 for early cutoffs)
data/fuelhh.json          Raw half-hourly WIND outturn, Jan 2–Feb 1
data/manifest.json        Retrieval provenance, URLs, row counts and SHA256 hashes
data/refresh.py           Explicit cohort download; never run on page requests
tests/test_analysis.py    Leakage, missingness, units, date boundaries and API tests
docs/DEMO.md              Customer pitch and technical walkthrough script
docs/narration.json       Actual two-part video narration
docs/create_demo.py       Local video generation from captures and narrated WAVs
Dockerfile               Multi-stage frontend/Python image
docker-compose.yml       Local container service
vercel.json              Static frontend and Python API routing
```

The fixed ~2.4 MB raw snapshot removes external API availability from the interactive request path. Parsed data is cached per Python process; every cutoff is recomputed from the raw vintages. No database, login, market execution or scheduled ingestion is needed for this pilot. Future production work: durable ingestion with retries, data-quality alerts, ingestion timestamps, actual-vintage availability, portfolio mapping, authenticated access and monitored service objectives.

## Verify

```sh
pip install httpx==0.28.1
python -m unittest discover -s tests -v
cd frontend
pnpm build
```

Meaningful tests cover the exact publication boundary, exclusion of a future revision, missing half-hour handling, metric signs and units, absent history, January/February boundary, historical sample leakage, input validation and CSV rows. Update snapshots explicitly with `python data/refresh.py`, then rerun tests and recalculate findings. Check `data/manifest.json` for source integrity. Frozen frontend dependencies and pinned Python dependencies support reproducibility; Python transitive dependencies are not fully locked.

## Deploy to Vercel

From this project root, run `pnpm dlx vercel --prod` in an authenticated account. Keep the project root at this directory, framework preset **Other**; `vercel.json` declares the frontend static build and Python function. Do not select `frontend/` as the root because it would omit the API and data. Set no secrets: both inputs are public archived data. Verify `/api/health`, the default chart, cutoff changes and CSV on the deployed URL. Vercel hosts a Python function and static frontend; Docker is the portable local deployment artifact, not the Vercel runtime.

For a public GitHub repo, use the anonymous name `q7m2vk`. After authenticating, initialize and push only this project directory, then run `gh repo create q7m2vk --public --source . --push`. Review the files before publication. No tokens should be committed. Follow the video/public-link checklist in `docs/DEMO.md` before submitting.

## Sources

- [Elexon FUELHH stream documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream)
- [Elexon WINDFOR stream documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream)
- [Elexon wind forecast scope](https://bmrs.elexon.co.uk/api-documentation/endpoint/forecast/generation/wind/latest)
- [Nord Pool auction documentation](https://support.nordpoolgroup.com/support/solutions/folders/8000087216)
- [Vercel Python runtime](https://vercel.com/docs/functions/runtimes/python)

The assignment allows 16 hours; this repository deliberately limits scope to a coherent first pilot. No claim that recording, publication or submission is complete is made in their absence.

## Verification log

- Six analytical/API tests passed on 25 October 2026.
- React production build passed; Vite reports a large JavaScript chunk (~596 kB uncompressed).
- Local browser rendering and performance navigation checked; cutoff control exercised.
- Docker engine is not installed on the execution machine; image build was not executed.

- Deployed frontend and Python API returned successful anonymous responses; the default API metrics matched the local analysis.
- Public repository returned HTTP 200 without authentication.

- YouTube Studio confirmed Video published after Unlisted was selected. The watch page exposes the player and 6:11 duration.

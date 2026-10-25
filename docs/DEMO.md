# Recording plan — 9 minutes 30 seconds

Record a browser and microphone using OBS or your preferred screen recorder. The file and unlisted YouTube upload are still required; this script is not a substitute for the video.

## Part 1: Customer pilot (0:00–4:30)

0:00–0:45 — Open Decision overview. “Wind Desk shows the wind forecast you actually had when making a day-ahead decision, then measures how that forecast performed. We use only the two Elexon datasets requested.”

0:45–1:45 — Select 15 January, 09:50 London. Explain that delivery is 16 January. Hover the hourly chart. Teal is the latest eligible forecast for each target hour; the dashed line is actual generation, shown retrospectively. Actuals were not known at the cutoff.

1:45–2:45 — Inspect publication timestamps and export the day CSV. Change cutoff to 08:00 and show changes. Explain publication age and missing-data behavior. Restore 09:50.

2:45–3:45 — Open Forecast performance. At the default cutoff the 744 paired hours have MAE 2,013 MW, RMSE 2,506 MW, bias +1,730 MW and WAPE 17.84%. Positive bias means wind over-forecast, which can imply replacement-energy exposure. These are observed dataset comparisons, not proof that forecast error alone caused imbalance costs.

3:45–4:30 — Explain P90 uses only earlier delivery days and is not a calibrated prediction band. Demand, contracts, prices, portfolio scaling and other generation are outside scope; this is decision support, not a purchase instruction. Propose a next pilot with portfolio exposure and operational data latency monitoring.

## Part 2: Technical review (4:30–9:30)

4:30–5:30 — Show README and directory layout. React/Vite UI → FastAPI → immutable Elexon JSON snapshot. Docker serves both UI and API on one origin; Vercel uses static assets plus a Python function. No database is needed for this fixed cohort.

5:30–6:45 — Show backend/analysis.py. Explain inclusive as-of cutoff, latest publication per target, next-day dates, decision-date cohort (January 31 delivers February 1), and hourly reconciliation of two complete actual half-hours. Missing values are not zeros; duplicate conflicts fail explicitly.

6:45–7:45 — Explain MAE, RMSE, positive bias and energy units. The realised positive hourly gaps sum to MWh because each interval is one hour. Retrospective actual vintages do not reconstruct what actuals were available historically. Earlier delivery date is a conservative history filter, but actual publication latency is not available and this is not a strict operational backtest.

7:45–8:45 — Run `python -m unittest discover -s tests -v`. Show API validation, leakage boundary test, missing-half-hour test, and historical-reference test. Show manifest hashes and refresh script, then frontend production build.

8:45–9:30 — Show Docker and Vercel config, deployment status, known limits, and AI disclosure. State exactly what was verified. End before 10 minutes.

## Publication checklist

- Record both parts with readable text and clear audio; check total duration <=10 minutes.
- Upload to YouTube with visibility **Unlisted**; wait until processing completes.
- Open video, public GitHub repository and deployed app in an incognito window without signing in.
- Check playback, README, app load, cutoff change and CSV download.
- Submit only after the video and all links work. The supplied form title does not include its URL; obtain that URL before submission.

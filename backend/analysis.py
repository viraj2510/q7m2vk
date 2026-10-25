"""Auditable as-of selection. All instants are aware; January London == UTC."""
import json
import math
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'

def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

@lru_cache
def load():
    forecasts = json.loads((DATA / 'windfor.json').read_text(encoding='utf-8-sig'))
    actuals = json.loads((DATA / 'fuelhh.json').read_text(encoding='utf-8-sig'))
    return forecasts, actuals

def select(forecasts, cutoff, start, end):
    selected = {}
    for row in forecasts:
        target, published = instant(row['startTime']), instant(row['publishTime'])
        if start <= target < end and published <= cutoff:
            old = selected.get(target)
            if old is None or published > instant(old['publishTime']):
                selected[target] = row
            elif published == instant(old['publishTime']) and row['generation'] != old['generation']:
                raise ValueError('Conflicting forecasts with identical target and publication')
    return selected

def metrics(rows):
    paired = [r for r in rows if r['error'] is not None]
    if not paired:
        return dict(n=0, mae=None, rmse=None, bias=None, wape=None, shortfallMWh=None)
    errors = [r['error'] for r in paired]
    denominator = sum(abs(r['actual']) for r in paired)
    return dict(n=len(paired), mae=sum(map(abs, errors))/len(errors),
                rmse=math.sqrt(sum(e*e for e in errors)/len(errors)),
                bias=sum(errors)/len(errors),
                wape=100*sum(map(abs, errors))/denominator if denominator else None,
                shortfallMWh=sum(max(e, 0) for e in errors))

def analyze(cutoff='09:50', decision='2026-01-15', forecasts=None, actuals=None):
    hour, minute = map(int, cutoff.split(':'))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError('Invalid cutoff')
    if not ('2026-01-01' <= decision <= '2026-01-31'):
        raise ValueError('Decision date must be in January 2026')
    if forecasts is None:
        forecasts, actuals = load()
    actual_map = {}
    for row in actuals:
        if row.get('fuelType') != 'WIND':
            continue
        target = instant(row['startTime'])
        if target in actual_map and actual_map[target] != row['generation']:
            raise ValueError('Conflicting actuals')
        actual_map[target] = row['generation']
    days, all_rows = [], []
    for number in range(1, 32):
        date = datetime(2026, 1, number, tzinfo=timezone.utc)
        asof = date.replace(hour=hour, minute=minute)
        start = date + timedelta(days=1)
        selected = select(forecasts, asof, start, start+timedelta(days=1))
        rows = []
        for offset in range(24):
            target = start+timedelta(hours=offset)
            forecast = selected.get(target)
            halves = [actual_map.get(target), actual_map.get(target+timedelta(minutes=30))]
            actual = sum(halves)/2 if all(v is not None for v in halves) else None
            value = forecast['generation'] if forecast else None
            rows.append(dict(startTime=target.isoformat(), forecast=value, actual=actual,
                             publishTime=forecast['publishTime'] if forecast else None,
                             ageHours=(asof-instant(forecast['publishTime'])).total_seconds()/3600 if forecast else None,
                             error=value-actual if value is not None and actual is not None else None))
        day = dict(decisionDate=date.date().isoformat(), deliveryDate=start.date().isoformat(),
                   cutoff=asof.isoformat(), rows=rows, metrics=metrics(rows),
                   forecastCoverage=sum(r['forecast'] is not None for r in rows),
                   actualCoverage=sum(r['actual'] is not None for r in rows))
        days.append(day)
        all_rows.extend(rows)
    chosen = next(d for d in days if d['decisionDate'] == decision)
    # Historical reference deliberately restricted to earlier delivery days.
    prior = [r['error'] for d in days if d['deliveryDate'] < decision for r in d['rows'] if r['error'] is not None]
    positive = sorted(max(e, 0) for e in prior)
    reserve = positive[math.ceil(.9*len(positive))-1] if positive else None
    return dict(selected=chosen, days=[{k:v for k,v in d.items() if k != 'rows'} for d in days],
                metrics=metrics(all_rows), expectedHours=744,
                historicalShortfallP90=reserve, historicalSample=len(prior),
                methodology='Hourly WINDFOR matched to the mean of two complete FUELHH WIND half-hours. Error = forecast minus actual. January decision dates, next-day delivery. Actuals are retrospective, not as-of outturn vintages.')

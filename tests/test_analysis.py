import unittest
from fastapi.testclient import TestClient
from backend.analysis import analyze, instant, select, metrics
from backend.app import app

class AnalysisTests(unittest.TestCase):
    def test_asof_excludes_later_revision_and_includes_boundary(self):
        rows = [{'startTime':'2026-01-02T00:00:00Z','publishTime':p,'generation':v} for p,v in [('2026-01-01T08:00:00Z',100),('2026-01-01T09:50:00Z',110),('2026-01-01T10:00:00Z',900)]]
        result=select(rows,instant('2026-01-01T09:50:00Z'),instant('2026-01-02T00:00:00Z'),instant('2026-01-03T00:00:00Z'))
        self.assertEqual(next(iter(result.values()))['generation'],110)

    def test_missing_half_hour_is_not_zero(self):
        f=[dict(startTime='2026-01-02T00:00:00Z',publishTime='2026-01-01T08:00:00Z',generation=100)]
        a=[dict(startTime='2026-01-02T00:00:00Z',fuelType='WIND',generation=80)]
        d=analyze(decision='2026-01-01',forecasts=f,actuals=a)
        self.assertIsNone(d['selected']['rows'][0]['actual'])
        self.assertEqual(d['metrics']['n'],0)
        a.append(dict(startTime='2026-01-02T00:30:00Z',fuelType='WIND',generation=100))
        self.assertEqual(analyze(decision='2026-01-01',forecasts=f,actuals=a)['metrics']['bias'],10)

    def test_metrics_and_zero_denominator(self):
        d=metrics([dict(error=3,actual=0),dict(error=-4,actual=0)])
        self.assertEqual(d['mae'],3.5)
        self.assertEqual(d['bias'],-.5)
        self.assertEqual(d['shortfallMWh'],3)
        self.assertIsNone(d['wape'])

    def test_no_history_on_first_decision_and_month_boundary(self):
        d=analyze(decision='2026-01-01')
        self.assertIsNone(d['historicalShortfallP90'])
        self.assertEqual(d['days'][-1]['deliveryDate'],'2026-02-01')
        self.assertEqual(d['metrics']['n'],744)

    def test_historical_reference_has_no_future_error_leakage(self):
        d=analyze(decision='2026-01-15')
        self.assertEqual(d['historicalSample'],13*24)

    def test_api_validation_and_export(self):
        client=TestClient(app)
        for query in ['cutoff=25:00','decision=2026-01-32','decision=2026-02-01','cutoff=oops']:
            self.assertEqual(client.get('/api/analysis?'+query).status_code,422)
        r=client.get('/api/export')
        self.assertEqual(r.status_code,200)
        self.assertEqual(len(r.text.splitlines()),25)
        self.assertEqual(client.get('/api/health').json(),{'status':'ok'})

if __name__=='__main__': unittest.main()

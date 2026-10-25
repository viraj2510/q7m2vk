import csv
import io
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from backend.analysis import analyze

app = FastAPI(title='Wind Desk API', version='1.0.0')

@app.get('/api/health')
def health():
    return {'status':'ok'}

@app.get('/api/analysis')
def analysis(cutoff: str = Query('09:50', pattern=r'^\d{2}:\d{2}$'), decision: str = Query('2026-01-15', pattern=r'^2026-01-\d{2}$')):
    try:
        return analyze(cutoff, decision)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error

@app.get('/api/export')
def export(cutoff: str = Query('09:50', pattern=r'^\d{2}:\d{2}$'), decision: str = Query('2026-01-15', pattern=r'^2026-01-\d{2}$')):
    result = analysis(cutoff, decision)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(result['selected']['rows'][0]))
    writer.writeheader()
    writer.writerows(result['selected']['rows'])
    return Response(output.getvalue(), media_type='text/csv', headers={'Content-Disposition':f'attachment; filename="wind-{decision}.csv"'})

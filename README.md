# Measured Interference

A live wave-interference visualiser whose source positions, frequencies,
phases and amplitudes are set by real quantum measurements from Moth
Quantum's `coin-toss-v1` engine (Atlas API).

Each wave source's position, frequency, phase and amplitude is built from 8 fair quantum bits (256 possible values per parameter). With up to 6 sources and 5 parameters each, the odds of two renders ever landing on the exact same underlying measurement sequence are roughly 1 in 10⁷³ — for comparison, the observable universe is estimated to contain "only" about 10⁸⁰ atoms. In practice, you will never see the same pattern twice.

## Requirements

| Requirement        | Version / Notes                          |
|---------------------|-------------------------------------------|
| Python              | 3.9+                                       |
| Flask               | see `requirements.txt`                     |
| requests            | see `requirements.txt`                     |
| gunicorn            | production server, used for deployment     |
| Moth Quantum API key | from [platform.mothquantum.com](https://platform.mothquantum.com) → API keys |

All Python dependencies are pinned in [`requirements.txt`](./requirements.txt):

```
flask
requests
gunicorn
```

Install them with:

```bash
pip install -r requirements.txt
```

## Project structure

```
.
├── server.py                        # Flask backend — proxies coin-toss-v1, keeps the API key server-side
├── quantum-interference-live.html   # Frontend — calls /api/measure for a fresh job on every render
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Configuration

The API key is read from an environment variable — it is never hardcoded
and never shipped to the browser.

| Variable       | Required | Description                                      |
|----------------|----------|---------------------------------------------------|
| `MOTH_API_KEY` | Yes      | Your Moth Quantum API key, format `moth_...`      |
| `PORT`         | No       | Port to bind to. Defaults to `5000` locally; most hosts (e.g. Render) set this automatically. |

## Running locally

```bash
pip install -r requirements.txt
export MOTH_API_KEY="moth_your_key_here"
python server.py
```

Then open **http://localhost:5000** in a browser. Do not open
`quantum-interference-live.html` directly as a file — it must be served
by `server.py` so that `/api/measure` resolves correctly.

## How it works

1. The browser loads `quantum-interference-live.html` from the Flask server.
2. On load, and on every click of **"Re-measure sources"**, the page calls
   `GET /api/measure`.
3. `server.py` submits a real job to `coin-toss-v1` (`POST /engines/coin-toss-v1/process`),
   polls `GET /jobs/{job_id}/status` until it completes, then fetches
   `GET /jobs/{job_id}/result`.
4. The returned bits are shuffled (the API returns aggregate `heads`/`tails`
   counts, not ordered per-shot results) and sent back to the browser as JSON.
5. The frontend consumes those bits to set every wave source's position,
   frequency, phase and amplitude, then renders the resulting interference
   pattern.

Because `coin-toss-v1` is a **fair** coin with no bias parameter, any
non-50/50 decision in the app (e.g. how many sources appear) is derived
honestly by combining multiple fair bits into one high-resolution value
and thresholding it — see `measureBit()` / `measureUnit()` in the HTML
file for the implementation.

## Deployment

This app needs a persistent backend (to hold the API key safely), so it
cannot be hosted as a static page alone. Example using
[Render](https://render.com) (free tier):

1. Push this folder to a GitHub repository.
2. On Render: **New → Web Service**, connect the repository.
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `gunicorn server:app`
5. Under the service's **Environment** tab, add `MOTH_API_KEY` as a secret.
6. Deploy. Render will provide a public URL — that is the live submission link.

**Note:** free-tier hosts typically spin down after inactivity, so the
first request after idle time may take 20–30 seconds while the server
wakes up.

## API usage

This project calls exactly one Moth Quantum engine:

- `coin-toss-v1` — a single fair-coin quantum measurement, requested in
  batches (`shots` parameter) per visualisation.

No other engines (Labyrinth, Tessa Image, Blur, etc.) are used.

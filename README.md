# 🕸️ AI Web Crawler (VnExpress)

This project crawls article listings from VnExpress and uses an LLM to extract structured data into a CSV file.

## ✨ What This Project Does

- Crawls VnExpress pages.
- Extracts article fields:
  - `title`
  - `url`
  - `summary`
  - `category`
  - `published_at`
- Removes duplicates by article title.
- Saves results to `vnexpress_articles.csv`.

## 🗂️ Project Structure

- `main.py`: Main entrypoint and crawl loop.
- `config.py`: Base URL, CSS selector, required fields.
- `models/venue.py`: Pydantic schema for extracted article data.
- `utils/scraper_utils.py`: Browser setup, LLM extraction strategy, page processing.
- `utils/data_utils.py`: Validation, deduplication, CSV export helpers.

## ✅ Requirements

- Python 3.11+
- A valid LLM API key (Gemini 2.0 Flash is the default provider in this project)

## ⚙️ Installation

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
LLM_PROVIDER=gemini/gemini-2.0-flash
GOOGLE_API_KEY=your_google_ai_studio_api_key
```

Optional variables:

- `LLM_API_BASE`: Custom API base URL if required by your provider.
- `LLM_API_KEY`: Generic fallback key variable.

## ▶️ Run

```powershell
python main.py
```

When successful, the crawler writes:

- `vnexpress_articles.csv`

## 🧩 How to Change Target or Extraction Rules

- Update `BASE_URL` and `CSS_SELECTOR` in `config.py`.
- Update the required fields in `REQUIRED_KEYS`.
- Update the schema in `models/venue.py`.
- Update the extraction instruction in `utils/scraper_utils.py` if needed.

## 🛠️ Common Issues

- `playwright ... Executable doesn't exist`
  - Run: `python -m playwright install chromium`

- `Insufficient Balance` or provider billing errors
  - Add credits or switch to another provider/model in `.env`.

- No output rows
  - Verify your CSS selector still matches the website.
  - Check LLM extraction logs for schema mismatch or API errors.

## 🔒 Security Notes

- Never commit `.env`, `.venv`, `.idea`, or API keys.
- If a key is exposed, rotate/revoke it immediately.

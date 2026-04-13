# AI Web Crawler (VnExpress)

Crawler bat bai viet tu VnExpress va trich xuat du lieu co cau truc bang `crawl4ai` + LLM.

## Tinh nang

- Crawl du lieu tu VnExpress theo trang.
- Trich xuat cac truong:
  - `title`
  - `url`
  - `summary`
  - `category`
  - `published_at`
- Loai bo ban ghi trung lap theo tieu de.
- Xuat ket qua ra `vnexpress_articles.csv`.

## Cau truc thu muc

- `main.py`: entrypoint chay crawler.
- `config.py`: URL, CSS selector, required keys.
- `models/venue.py`: Pydantic schema cho du lieu bai viet.
- `utils/scraper_utils.py`: browser config + LLM extraction + xu ly tung page.
- `utils/data_utils.py`: helper validate/duplicate/save csv.

## Cai dat

Yeu cau: Python 3.11+

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

## Cau hinh moi truong

Tao file `.env` (khong commit len git):

```env
LLM_PROVIDER=openai/gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key
```

Co the doi model bang cach thay gia tri `LLM_PROVIDER`.

## Chay du an

```powershell
python main.py
```

Ket qua se duoc ghi vao file:

- `vnexpress_articles.csv`

## Luu y bao mat

- Khong commit `.env`, `.venv`, `.idea` hoac API key.
- Neu key da tung bi lo, hay rotate/revoke ngay.

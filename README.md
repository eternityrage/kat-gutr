# 🎸 kat-gutr - Kathy's Guitar Automated Publishing Pipeline

An automated video publishing pipeline for the **Kathy's Guitar** Facebook page (Page ID: `1334980766363715`).

---

## ⚡ Features

- **Google Drive Integration**: Automatically checks and downloads videos from Google Drive (`1Q9vPPK_lXNTKPMkzmvNh--sXdPeRGzfn`).
- **On-Demand FFmpeg Video Processing**:
  - Automatically crops and scales footage into vertical 9:16 (1080x1920) format.
  - Normalizes audio levels using EBU R128 (`loudnorm`) for guitar tone and punch.
  - Processes on-demand only the video selected for publishing to maximize workflow speed.
- **AI SEO Captions & Titles**:
  - Leverages Pollinations AI to generate high-converting, viral rock/guitar SEO titles, descriptions, and hashtags (`#electricguitar #femaleguitarist #guitarsolo #rockmusic #riffwars #kathysguitar`).
  - High-converting fallback captions included.
- **Engagement & Pinned Comments**:
  - Automatically posts the first comment containing the title/description and a link/CTA, then pins it to the top of the Reel.
- **Multi-Format Facebook Publishing**:
  - Publishes both high-quality **Facebook Reels** and **Facebook Stories**.
- **Automated GitHub Actions Schedule**:
  - Runs automatically 3 times daily (`04:00`, `12:00`, `20:00` UTC) with weighted frequency selection to avoid duplicate consecutive posts.

---

## ⚙️ Required GitHub Secrets

| Secret Name | Description |
|---|---|
| `FB_PAGE_ID` | Facebook Page ID (`1334980766363715`) |
| `FB_PAGE_ACCESS_TOKEN` | Direct Page Access Token for Kathy's Guitar |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | Google Service Account JSON credentials |
| `GOOGLE_DRIVE_FOLDER_ID` | Google Drive folder ID (`1Q9vPPK_lXNTKPMkzmvNh--sXdPeRGzfn`) |
| `POLLINATIONS_API_KEY` | *(Optional)* Pollinations AI key for SEO captions |
| `PINNED_COMMENT_LINK` | *(Optional)* URL for full tabs, backing tracks, or external links |
| `INSTAGRAM_ACCOUNT_ID` | *(Optional)* Connected Instagram account ID |

---

## 🛠️ Local Development & Testing

```bash
# Clone the repository
git clone https://github.com/eternityrage/kat-gutr.git
cd kat-gutr

# Install dependencies
pip install -r requirements.txt

# Run the automated pipeline
python auto_pipeline.py
```

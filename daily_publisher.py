import os
import sys
import json
import random
import re
import urllib.parse
import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

PUBLISHED_FILE = 'published_videos.json'
YOUTUBE_STATE_FILE = 'youtube_publish_state.json'

# Allowed weekdays for YouTube: Monday (0), Wednesday (2), Friday (4), Sunday (6)
ALLOWED_YOUTUBE_WEEKDAYS = {0, 2, 4, 6}
WEEKDAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}


# ==============================================================================
# KATHY'S GUITAR KNOWLEDGE BASE & CREATIVE HOOKS
# ==============================================================================

KATHY_GUITAR_DATABASE = {
    "shred_solo": {
        "category": "Electric Guitar Shred Solo",
        "emoji": "🎸⚡",
        "focus": "blistering speed, lightning fretboard chops, and explosive guitar soloing",
        "titles": [
            "⚡ Kathy Shreds Insane Electric Guitar Solo! 🎸🔥",
            "Fretboard on Fire! Kathy's Blistering Solo 🎸⚡",
            "Can You Play This Solo? Kathy Tearing It Up! 🎸💥",
            "Lightning Fast Fingers! Kathy Drops Pure Rock Fire 🎸⚡",
            "When the Guitar Solo Hits Pure Overdrive! 🎸🔥",
            "Shredding into Overdrive: Kathy's Flying V Solo 🎸⚡"
        ],
        "descriptions": [
            "Kathy unleashes pure rock fury on the fretboard! Blistering speed, screaming pinch harmonics, and relentless energy.\n\n🎸 What's your favorite guitar solo of all time? Tell us in the comments!\n👉 Follow Kathy's Guitar for daily electric guitar shredding and solos! ⚡🎸\n\n#KathysGuitar #GuitarSolo #ElectricGuitar #FemaleGuitarist #RockMusic #ShredGuitar #RiffWars #Guitarist #Shorts #Reels",
            "Watch those fingers fly! Kathy tearing up six strings with pure technical precision and raw rock attitude.\n\n💬 Rate Kathy's shred speed from 1 to 10 in the comments!\n👉 Follow @KathysGuitar for daily high-energy guitar solos! 🎸🔥\n\n#KathysGuitar #GuitarSolo #ShredGuitar #FemaleGuitarist #GuitarPlayer #RockGuitar #FlyingV #Shorts #Reels"
        ]
    },
    "melodic_rock": {
        "category": "Melodic Rock & Emotive Bends",
        "emoji": "🎸✨",
        "focus": "soulful string bends, singing vibrato, and soaring melodic rock tone",
        "titles": [
            "Pure Melodic Magic: Kathy's Soulful Guitar Solo 🎸✨",
            "That Guitar Tone Is Pure Perfection! 🎸🎶",
            "Soulful Rock Bends with Kathy & Her Flying V 🎸✨",
            "The Most Expressive Solo You'll Hear Today 🎸💖",
            "Singing Notes: Kathy's Melodic Rock Masterpiece 🎸✨",
            "When Six Strings Sing: Kathy's Emotional Solo 🎸🕊️"
        ],
        "descriptions": [
            "Listen to how Kathy makes six strings sing! Soulful bends, velvety sustain, and pure emotion in every note.\n\n💬 Rate Kathy's guitar tone from 1 to 10 in the comments!\n👉 Follow Kathy's Guitar for daily rock and melodic guitar solos! 🎸✨\n\n#KathysGuitar #GuitarSolo #MelodicGuitar #FemaleGuitarist #GuitarTone #RockMusic #GuitarPlayer #Shorts #Reels",
            "Every note tells a story. Kathy channels pure feeling through her guitar with breathtaking touch and dynamics.\n\n🎸 Tag a friend who appreciates incredible guitar tone!\n👉 Follow Kathy's Guitar for more melodic magic! 🎸✨\n\n#KathysGuitar #GuitarSolo #ToneSearch #RockMusic #FemaleGuitarist #Guitarist #Shorts #Reels"
        ]
    },
    "heavy_riff": {
        "category": "Heavy Rock & Metal Riffs",
        "emoji": "🎸🔥",
        "focus": "heavy crunch riffs, aggressive rhythm chops, and headbanging groove",
        "titles": [
            "Heavy Riff Attack! Kathy Bringing Pure Rock Energy 🎸🔥",
            "Turn the Volume UP! Monster Guitar Riff 🔊🎸⚡",
            "Flying V Madness: Raw Rock & Roll Riffs! 🎸💥",
            "Heavy Metal Energy with Kathy on Six Strings! 🎸⚡",
            "This Riff Will Shake Your Speakers! 🔊🎸🔥",
            "Crushing Rock Riff by Kathy! Turn It Up 🎸🔥"
        ],
        "descriptions": [
            "Heavy rock riffs and raw attitude! Kathy cranks the gain and delivers an absolute monster groove that will get your head banging.\n\n🔊 Crank the volume to 10! Which rock band does this riff remind you of?\n👉 Follow Kathy's Guitar for heavy rock riffs and shred sessions! 🎸🔥\n\n#KathysGuitar #ElectricGuitar #HeavyRiffs #RockGuitar #FemaleGuitarist #RiffOfTheDay #FlyingV #Headbanger #Shorts #Reels",
            "Pure power chord energy! Kathy locking into that thunderous rock rhythm on her Flying V.\n\n🎸 Drop a 🤘 in the comments if you love heavy rock guitar!\n👉 Follow @KathysGuitar for daily electric guitar riffs! ⚡\n\n#KathysGuitar #HeavyRock #GuitarRiff #FemaleGuitarist #RockMusic #GuitarPlayer #Shorts #Reels"
        ]
    },
    "blues_rock": {
        "category": "Blues-Rock & Classic Phrasing",
        "emoji": "🎸🎶",
        "focus": "stinging pentatonic runs, vintage classic rock feel, and dynamic touch",
        "titles": [
            "Soulful Blues-Rock Licks with Kathy! 🎸✨",
            "Classic Rock Grooves on the Fretboard 🎸🔥",
            "Kathy Bending Emotion into Every String! 🎸🎶",
            "That Blues-Rock Sweet Spot: Pure Guitar Feel 🎸✨",
            "Vintage Rock Vibes with Kathy Shredding Six Strings 🎸⚡"
        ],
        "descriptions": [
            "Nothing beats the raw feel of classic blues-rock! Kathy blends stinging pentatonic runs with heartfelt dynamic control.\n\n🎸 Drop a 🔥 if you love vintage rock guitar vibes!\n👉 Follow Kathy's Guitar for daily blues-rock licks and solos! 🎸⚡\n\n#KathysGuitar #BluesRock #GuitarSolo #ClassicRock #FemaleGuitarist #GuitarLicks #GuitarPlayer #Shorts #Reels",
            "Tasty phrasing and dynamic touch. Kathy shows how melody and groove combine to make guitar playing irresistible.\n\n💬 What's your go-to guitar scale: Pentatonic or Major? Let us know below!\n👉 Follow Kathy's Guitar for daily rock solos! 🎸✨\n\n#KathysGuitar #GuitarLicks #BluesRock #FemaleGuitarist #ElectricGuitar #Shorts #Reels"
        ]
    },
    "general_rock": {
        "category": "Electric Rock Session",
        "emoji": "🎸⚡",
        "focus": "female guitarist energy, passionate performance, and rock enthusiasm",
        "titles": [
            "⚡ Kathy Tearing Up the Fretboard! Pure Rock Energy 🎸🔥",
            "Daily Dose of Guitar Shredding with Kathy 🎸⚡",
            "Six Strings, Zero Limits: Kathy Rocking Out! 🎸✨",
            "Flying V Fire! Kathy's Electric Guitar Session 🎸💥",
            "Can Your Guitar Do THIS? Kathy on Fire! 🎸⚡",
            "Pure Electric Passion: Kathy's Guitar Session 🎸🔥"
        ],
        "descriptions": [
            "Pure passion on six strings! Kathy brings the ultimate rock experience straight to your feed with blazing riffs and unmatched stage energy.\n\n🎸 What song should Kathy cover next? Let us know below!\n👉 Follow Kathy's Guitar for daily electric guitar riffs and solos! ⚡🎸\n\n#KathysGuitar #ElectricGuitar #FemaleGuitarist #GuitarSolo #RockMusic #Guitarist #RiffWars #Shorts #Reels",
            "Turn up the volume and feel the electricity! Kathy delivering another masterclass in rock guitar enthusiasm and technique.\n\n💬 Tag a fellow musician who needs some guitar inspiration today!\n👉 Follow @KathysGuitar for daily rock guitar videos! 🎸🔥\n\n#KathysGuitar #RockMusic #GuitarSolo #FemaleGuitarist #ElectricGuitar #GuitarLife #Shorts #Reels"
        ]
    }
}


def load_published():
    if os.path.exists(PUBLISHED_FILE):
        try:
            with open(PUBLISHED_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_published(data):
    with open(PUBLISHED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def extract_video_subject(video_name: str) -> dict:
    """
    Identifies the guitar category and thematic focus from filename.
    """
    clean_name = os.path.basename(video_name or "").lower()
    clean_name = re.sub(r'[_\-\.]', ' ', clean_name)

    if any(k in clean_name for k in ['shred', 'speed', 'fast', 'solo', 'tapping', 'arpeggio']):
        return KATHY_GUITAR_DATABASE['shred_solo']
    elif any(k in clean_name for k in ['melodic', 'soul', 'bends', 'clean', 'ballad', 'tone']):
        return KATHY_GUITAR_DATABASE['melodic_rock']
    elif any(k in clean_name for k in ['heavy', 'metal', 'riff', 'crunch', 'gain', 'flying v']):
        return KATHY_GUITAR_DATABASE['heavy_riff']
    elif any(k in clean_name for k in ['blues', 'classic', 'groove', 'vintage']):
        return KATHY_GUITAR_DATABASE['blues_rock']

    # Rotate through database for variety if generic filename (e.g. Woman_playing_electric_guitar...)
    return random.choice(list(KATHY_GUITAR_DATABASE.values()))


def clean_text(text: str) -> str:
    """Strips thinking tags, meta annotations, labels, and formatting quirks."""
    if not text:
        return ""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'(?i)^(here is|sure,|certainly|note:|as requested).*?\n', '', text)
    text = re.sub(r'(Support\s+Pollinations|Powered\s+by\s+Pollinations|🌸\s*Ad\s*🌸).*$', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = text.replace('"', '').replace('“', '').replace('”', '').strip()
    return text


def generate_caption(video_name=None):
    """
    Generates a high-converting, matching title and description for Kathy's Guitar.
    Returns: (title, description)
    """
    subject = extract_video_subject(video_name or "")
    category = subject.get("category", "Electric Guitar Solo")
    focus = subject.get("focus", "high-energy electric guitar performance")
    emoji = subject.get("emoji", "🎸⚡")

    fallback_titles = subject.get("titles") or [f"⚡ Kathy Shreds Insane Electric Guitar Solo! {emoji}"]
    fallback_descriptions = subject.get("descriptions") or [
        f"Kathy unleashes pure rock fury on the fretboard! Blistering speed, screaming harmonics, and relentless energy.\n\n🎸 What's your favorite guitar solo of all time? Tell us in the comments!\n👉 Follow Kathy's Guitar for daily electric guitar shredding and solos! ⚡🎸\n\n#KathysGuitar #GuitarSolo #ElectricGuitar #FemaleGuitarist #RockMusic #ShredGuitar #Shorts #Reels"
    ]

    pollinations_key = os.environ.get('POLLINATIONS_API_KEY', '').strip()

    if not pollinations_key:
        return random.choice(fallback_titles), random.choice(fallback_descriptions)

    system_prompt = (
        "You are an elite rock music social media copywriter for 'Kathy's Guitar', "
        "a viral channel featuring female guitarist Kathy shredding electric guitar solos and rock riffs on her Flying V. "
        "OUTPUT FORMAT (EXACTLY TWO SECTIONS, NO THINKING, NO META LABELS):\n"
        "TITLE: <catchy viral title under 70 chars with emoji, e.g. ⚡ Kathy Shreds Insane Electric Guitar Solo! 🎸🔥>\n"
        "DESCRIPTION: <2-3 energetic sentences highlighting Kathy's fretboard speed, tone, or rock technique. "
        "Include an interactive question for guitar fans, CTA '👉 Follow Kathy's Guitar for daily electric guitar riffs & solos! ⚡🎸', "
        "and hashtags #KathysGuitar #GuitarSolo #ElectricGuitar #FemaleGuitarist #RockMusic #ShredGuitar #Shorts #Reels>"
    )

    user_prompt = (
        f"Create a viral title and description for Kathy's newest electric guitar performance.\n"
        f"Style: {category} {emoji}.\n"
        f"Focus: {focus}."
    )

    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(user_prompt)}"
        params = {
            'system': system_prompt,
            'model': 'openai',
            'seed': random.randint(1, 999999)
        }
        headers = {'Authorization': f'Bearer {pollinations_key}'} if pollinations_key else {}
        resp = requests.get(url, params=params, headers=headers, timeout=20)

        if resp.status_code == 200:
            cleaned = clean_text(resp.text)
            title = ""
            description = ""

            title_m = re.search(r'(?i)TITLE\s*:\s*(.+?)(?=\n\s*(?:DESCRIPTION\s*:|$))', cleaned, re.DOTALL)
            desc_m = re.search(r'(?i)DESCRIPTION\s*:\s*(.+)$', cleaned, re.DOTALL)

            if title_m:
                title = title_m.group(1).strip()
            if desc_m:
                description = desc_m.group(1).strip()

            # Fallback parsing if explicit TITLE/DESCRIPTION labels omitted
            if not title or not description:
                lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
                if lines:
                    title = lines[0]
                    description = '\n\n'.join(lines[1:]) if len(lines) > 1 else ""

            # Ensure hashtags & branding in description
            if description and "#KathysGuitar" not in description:
                description = f"{description}\n\n👉 Follow Kathy's Guitar for daily electric guitar solos! 🎸⚡\n#KathysGuitar #GuitarSolo #ElectricGuitar #FemaleGuitarist #RockMusic #Shorts #Reels"

            # Enforce title length under 100
            if title and len(title) > 95:
                title = title[:92].rstrip() + "..."

            if title and len(title) >= 10 and description and len(description) >= 30:
                return title, description
            else:
                print("  [WARN] Pollinations response formatting invalid. Using curated fallbacks.")
    except Exception as e:
        print(f"  [WARN] Pollinations caption generation failed: {e}")

    return random.choice(fallback_titles), random.choice(fallback_descriptions)


def generate_pinned_comment(description, title=None):
    """
    Creates the pinned comment text for Facebook and YouTube.
    """
    custom_link = os.environ.get('PINNED_COMMENT_LINK', '').strip()
    if custom_link:
        return f"🎸 Tabs, Backing Tracks & Kathy's Gear Links: {custom_link}\n\n👉 Subscribe & follow Kathy's Guitar for daily rock shred sessions! ⚡🔥"
    return "🎸 Welcome to Kathy's Guitar! Turn the volume UP 🔊⚡\n👉 Follow & subscribe for daily electric guitar riffs, rock solos, and Flying V shredding! 🤘🔥"


# ==============================================================================
# YOUTUBE STRICT SCHEDULING (MONDAY, WEDNESDAY, FRIDAY, SUNDAY - MAX ONCE A DAY)
# ==============================================================================

def get_last_youtube_publish_date():
    """
    Retrieves the date of the most recent YouTube publish.
    Checks both youtube_publish_state.json and published_videos.json.
    """
    # 1. State file check
    if os.path.exists(YOUTUBE_STATE_FILE):
        try:
            with open(YOUTUBE_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                d_str = state.get("last_published_date")
                if d_str:
                    return datetime.date.fromisoformat(d_str)
        except Exception as e:
            print(f"[youtube schedule] Notice reading {YOUTUBE_STATE_FILE}: {e}")

    # 2. published_videos.json check
    published = load_published()
    for entry in reversed(published):
        yt_date_str = entry.get("youtube_published_at")
        results = entry.get("results", [])
        yt_success = any(r.get("platform") == "youtube" and r.get("status") == "success" for r in results)
        if yt_success and yt_date_str:
            try:
                return datetime.date.fromisoformat(yt_date_str[:10])
            except Exception:
                pass

    return None


def should_publish_to_youtube():
    """
    Strict YouTube Publishing Schedule for Kathy's Guitar:
    1. Publishes ONLY on Monday, Wednesday, Friday, and Sunday.
    2. Publishes at most ONCE per day on those allowed days.
    """
    today = datetime.datetime.now(datetime.timezone.utc).date()
    weekday = today.weekday()
    weekday_name = WEEKDAY_NAMES[weekday]

    # Check 1: Day of week constraint
    if weekday not in ALLOWED_YOUTUBE_WEEKDAYS:
        days_ahead = 1
        while (weekday + days_ahead) % 7 not in ALLOWED_YOUTUBE_WEEKDAYS:
            days_ahead += 1
        next_date = today + datetime.timedelta(days=days_ahead)
        next_day_name = WEEKDAY_NAMES[next_date.weekday()]
        return False, (
            f"Today is {weekday_name} ({today}). "
            f"Policy: YouTube publishes ONLY on Monday, Wednesday, Friday, and Sunday. "
            f"Next scheduled YouTube publish is {next_day_name} ({next_date})."
        )

    # Check 2: Max once a day constraint
    last_date = get_last_youtube_publish_date()
    if last_date is not None:
        if last_date == today:
            return False, f"YouTube has ALREADY published today ({weekday_name}, {today}). Policy: Maximum once a day on allowed days."
        if last_date > today:
            return False, f"Clock anomaly: Last YouTube publish recorded in future ({last_date}). Skipping YouTube upload."

    return True, f"Today is {weekday_name} ({today}) - scheduled YouTube publishing day! Ready to upload."


def record_youtube_publish(video_name, video_id=None):
    """Records the successful YouTube publication state."""
    today = datetime.datetime.now(datetime.timezone.utc).date()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    state = {
        "last_published_date": today.isoformat(),
        "last_published_at": now_iso,
        "last_video_name": video_name,
        "last_video_id": video_id or ""
    }
    try:
        with open(YOUTUBE_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4)
        print(f"[youtube schedule] ✅ Recorded YouTube publish state for {today.isoformat()}")
    except Exception as e:
        print(f"[youtube schedule] ⚠️ Error saving {YOUTUBE_STATE_FILE}: {e}")


# ==============================================================================
# TARGET PAGE RESOLUTION & PUBLISHING
# ==============================================================================

def select_video(video_list, published):
    published_names = {p.get('filename') for p in published}
    unpublished = [v for v in video_list if os.path.basename(v) not in published_names]

    if unpublished:
        return random.choice(unpublished)

    # All published - weighted random from ALL videos
    if video_list:
        counts = {}
        for p in published:
            name = p.get('filename', '')
            counts[name] = counts.get(name, 0) + 1

        weights = []
        for v in video_list:
            name = os.path.basename(v)
            count = counts.get(name, 0)
            weight = max(1, 1000 // (3 ** min(count, 6)))
            weights.append(weight)

        chosen = random.choices(video_list, weights=weights, k=1)[0]
        return chosen

    return None


def resolve_target_pages():
    """
    Resolves Facebook target pages and page access tokens.
    """
    tokens_json_env = os.environ.get('FB_PAGE_TOKENS_JSON', '').strip()
    if tokens_json_env:
        try:
            tokens_data = json.loads(tokens_json_env)
            page_configs = []
            for pid, info in tokens_data.items():
                if isinstance(info, dict):
                    page_configs.append({
                        'id': str(pid),
                        'name': info.get('name', f'Page {pid}'),
                        'token': info.get('token')
                    })
                elif isinstance(info, str):
                    page_configs.append({
                        'id': str(pid),
                        'name': f'Page {pid}',
                        'token': info
                    })
            if page_configs:
                return page_configs
        except Exception as e:
            print(f"[WARN] Failed to parse FB_PAGE_TOKENS_JSON: {e}")

    # Primary single page mode
    single_page_id = os.environ.get('FB_PAGE_ID', '').strip()
    single_page_token = os.environ.get('FB_PAGE_ACCESS_TOKEN', '').strip()

    if single_page_id and single_page_token:
        return [{
            'id': single_page_id,
            'name': "Kathy's Guitar",
            'token': single_page_token
        }]

    return []


def publish_to_facebook_pages(video_path, caption, pinned_comment, page_configs, title=None):
    """
    Publishes the Reel, Pinned Comment, and Story to all configured Facebook pages.
    """
    from upload.upload_facebook import upload_reel, upload_story
    results = []
    print(f"\n[FB] Publishing to {len(page_configs)} Facebook Page(s)...")

    for p in page_configs:
        pid = p['id']
        pname = p.get('name', pid)
        token = p['token']
        print(f"\n--- Publishing to Facebook Page: {pname} (ID: {pid}) ---")

        # 1. Reel + Pinned Comment
        reel_res = upload_reel(
            video_path=video_path,
            caption=caption,
            page_id=pid,
            page_token=token,
            pin_comment=True,
            comment_text=pinned_comment,
            title=title
        )
        reel_res['page_name'] = pname
        results.append(reel_res)

        # 2. Story
        story_res = upload_story(
            video_path=video_path,
            page_id=pid,
            page_token=token
        )
        story_res['page_name'] = pname
        results.append(story_res)

    return results


def publish(video_path, publish_to_facebook=True, publish_to_instagram=None, publish_to_youtube=True):
    filename = os.path.basename(video_path)
    title, description = generate_caption(filename)
    combined_caption = f"{title}\n\n{description}" if title not in description else description
    pinned_comment = generate_pinned_comment(description, title)

    print(f"\n[TITLE] {title}")
    print(f"[DESCRIPTION]\n{description}")
    print(f"[PINNED COMMENT]\n{pinned_comment}\n")

    results = []

    # 1. Facebook Publishing (Daily on every run)
    if publish_to_facebook:
        pages = resolve_target_pages()
        if not pages:
            print("[WARN] No target Facebook pages resolved. Please configure FB_PAGE_ID + FB_PAGE_ACCESS_TOKEN.")
        else:
            fb_results = publish_to_facebook_pages(video_path, description, pinned_comment, pages, title=title)
            results.extend(fb_results)

    # 2. Instagram Publishing (Daily on every run if configured)
    if publish_to_instagram is None:
        publish_to_instagram = bool(os.environ.get('INSTAGRAM_ACCOUNT_ID'))

    if publish_to_instagram:
        from upload.upload_instagram import upload_reel as ig_reel, upload_story as ig_story
        ig_account_id = os.environ.get('INSTAGRAM_ACCOUNT_ID', '').strip()
        single_page_token = os.environ.get('FB_PAGE_ACCESS_TOKEN', '').strip()
        if not single_page_token and 'pages' in locals() and pages:
            single_page_token = pages[0].get('token', '')

        if ig_account_id and single_page_token:
            print(f"\n[IG] Publishing to Instagram Reels: {ig_account_id}")
            results.append(ig_reel(
                video_path,
                caption=description,
                page_token=single_page_token,
                ig_account_id=ig_account_id,
                share_to_feed=False,
                title=title
            ))
            results.append(ig_story(
                video_path,
                page_token=single_page_token,
                ig_account_id=ig_account_id
            ))
        elif not ig_account_id:
            print("\n[SKIP] INSTAGRAM_ACCOUNT_ID not configured.")
        elif not single_page_token:
            print("\n[SKIP] Facebook Page access token not found for Instagram.")

    # 3. YouTube Shorts Publishing (Strict schedule: Mon, Wed, Fri, Sun & max once a day)
    if publish_to_youtube:
        print("\n" + "-" * 50)
        print("🎬 YOUTUBE SHORTS PUBLISHING EVALUATION (Kathy's Guitar)")
        print("-" * 50)

        should_post, reason = should_publish_to_youtube()
        print(f"[youtube schedule] Decision: {'✅ PROCEED' if should_post else '⏭️ SKIP'}")
        print(f"[youtube schedule] Reason: {reason}")

        if should_post:
            try:
                from upload.upload_to_youtube import upload_to_youtube
                yt_result = upload_to_youtube(
                    video_path=video_path,
                    title=title,
                    description=description,
                    category_id='10'  # 10 = Music
                )
                results.append(yt_result)

                if yt_result.get('status') == 'success':
                    record_youtube_publish(filename, yt_result.get('id'))
                    print(f"[youtube] 🎉 YouTube upload succeeded! URL: {yt_result.get('url')}")
                else:
                    print(f"[youtube] ❌ YouTube upload failed: {yt_result.get('error')}")
            except Exception as e:
                print(f"[youtube] ❌ Exception during YouTube upload: {e}")
                results.append({'status': 'failed', 'error': str(e), 'platform': 'youtube'})
        else:
            results.append({
                'status': 'skipped',
                'platform': 'youtube',
                'reason': reason
            })

    return results


def run_daily_publish(processed_videos):
    published = load_published()
    video = select_video(processed_videos, published)

    if not video:
        print("[INFO] No videos available to publish")
        return []

    filename = os.path.basename(video)
    print(f"\n[SELECTED VIDEO] {filename}")

    publish_ig = bool(os.environ.get('INSTAGRAM_ACCOUNT_ID'))
    results = publish(video, publish_to_facebook=True, publish_to_instagram=publish_ig, publish_to_youtube=True)

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    entry = {
        'filename': filename,
        'published_at': now_iso,
        'results': results
    }

    # If YouTube succeeded, tag the entry with timestamp
    if any(r.get('platform') == 'youtube' and r.get('status') == 'success' for r in results):
        entry['youtube_published_at'] = now_iso

    published.append(entry)
    save_published(published)

    return results


if __name__ == '__main__':
    import glob
    processed = glob.glob('Processed_Videos/*.mp4') + glob.glob('Processed_Videos/*.mov')
    results = run_daily_publish(processed)
    print(f"\nPublish results total: {len(results)}")

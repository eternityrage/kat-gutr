import os
import sys
import json
import random
import re
import requests
from upload.upload_facebook import upload_reel, upload_story

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PUBLISHED_FILE = 'published_videos.json'

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

def extract_subject_from_filename(filename):
    """
    Extracts descriptive keywords from video filename.
    """
    name = os.path.splitext(filename)[0]
    name = re.sub(r'_\d{8,}', '', name)
    name = re.sub(r'\d+', '', name)
    name = name.replace('_', ' ').replace('-', ' ').strip()
    return name or "electric guitar shred riff"

def generate_caption(filename=""):
    pollinations_key = os.environ.get('POLLINATIONS_API_KEY', '').strip()
    subject = extract_subject_from_filename(filename) if filename else "electric guitar riff"

    if not pollinations_key:
        return get_fallback_caption(subject)

    prompt = (
        f"Generate a viral, search-engine-optimized (SEO) social media title and description for an electric guitar performance reel. "
        f"The video features female guitarist Kathy playing high-energy electric guitar riffs, heavy rock shredding, melodic solos, and signature guitar tone ({subject}). "
        f"Include high-ranking keywords like Guitar Solo, Electric Guitar, Female Guitarist, Shredding, Guitar Riffs, Rock Music, Kathy Guitar. "
        f"Include popular hashtags (#electricguitar #femaleguitarist #guitarsolo #shredguitar #rockmusic #guitarplayer #guitarist #riffwars #kathysguitar). "
        f"Keep the entire text engaging, viral, and under 250 characters."
    )

    try:
        resp = requests.post(
            'https://text.pollinations.ai/',
            json={
                'messages': [{'role': 'user', 'content': prompt}],
                'model': 'openai',
                'seed': random.randint(1, 999999)
            },
            headers={'Authorization': f'Bearer {pollinations_key}'},
            timeout=30
        )
        if resp.status_code == 200:
            caption = resp.text.strip()
            if caption.startswith('"') and caption.endswith('"'):
                caption = caption[1:-1].strip()
            if len(caption) > 280:
                caption = caption[:277] + '...'
            return caption
    except Exception as e:
        print(f"  [WARN] Pollinations caption generation failed: {e}")

    return get_fallback_caption(subject)

def get_fallback_caption(subject="riffs"):
    captions = [
        "🎸 Kathy tearing up the fretboard! Pure electric guitar fire & shred solo ⚡🔥 #electricguitar #femaleguitarist #guitarsolo #rockmusic #kathysguitar",
        "Melodic rock vibes with Kathy & her Flying V 🎸 That tone is pure magic! ✨ #guitarist #femaleguitarist #guitarsolo #shredguitar #riffwars",
        "⚡ Heavy riffs & lightning-fast fingers! Kathy dropping pure rock energy 🎸🔥 #electricguitar #shred #rockguitar #guitarplayer #femaleguitarist",
        "Can your guitar tone do THIS? Kathy shredding another monster solo 🎸💥 #guitarsolo #rockmusic #electricguitar #riffwars #kathysguitar",
        "🎸 Kathy's daily dose of electric guitar shredding! Turn the volume UP 🔊⚡ #femaleguitarist #guitarsolo #rockmusic #guitarist #shred",
        "Flying V attack! Kathy bringing back raw rock & roll guitar riffs 🎸🔥 #electricguitar #femaleguitarist #rockguitar #guitarsolo #kathysguitar",
        "Pure passion on six strings! Kathy killing this melodic solo 🎸✨ #guitarplayer #guitartone #femaleguitarist #guitarsolo #rockmusic",
        "⚡ When the guitar solo hits just right! Kathy shredding into overdrive 🎸🔥 #shredguitar #femaleguitarist #electricguitar #riffwars #kathysguitar"
    ]
    return random.choice(captions)

def generate_pinned_comment(caption):
    """
    Creates the pinned comment text using the same title & description,
    plus a link or CTA placeholder for future pinned URLs.
    """
    custom_link = os.environ.get('PINNED_COMMENT_LINK', '').strip()
    if custom_link:
        link_cta = f"\n\n👉 Full Tabs, Backing Tracks & More: {custom_link}"
    else:
        link_cta = "\n\n👉 Follow Kathy's Guitar for daily electric guitar riffs and solos! 🎸⚡"

    return f"{caption}{link_cta}"

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
    Supports:
    1. FB_PAGE_TOKENS_JSON (pre-stored dictionary mapping page_id -> {name, token})
    2. FB_PAGE_ID + FB_PAGE_ACCESS_TOKEN (primary mode for Kathy's Guitar)
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

def publish_to_facebook_pages(video_path, caption, pinned_comment, page_configs):
    """
    Publishes the Reel, Pinned Comment, and Story to all configured Facebook pages.
    """
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
            comment_text=pinned_comment
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

def publish(video_path, publish_to_facebook=True, publish_to_instagram=False):
    filename = os.path.basename(video_path)
    caption = generate_caption(filename)
    pinned_comment = generate_pinned_comment(caption)

    print(f"\n[SEO CAPTION] {caption}")
    print(f"[PINNED COMMENT] {pinned_comment}")

    results = []

    if publish_to_facebook:
        pages = resolve_target_pages()
        if not pages:
            print("[WARN] No target Facebook pages resolved. Please configure FB_PAGE_ID + FB_PAGE_ACCESS_TOKEN.")
        else:
            fb_results = publish_to_facebook_pages(video_path, caption, pinned_comment, pages)
            results.extend(fb_results)

    if publish_to_instagram:
        from upload.upload_instagram import upload_reel as ig_reel, upload_story as ig_story
        ig_account_id = os.environ.get('INSTAGRAM_ACCOUNT_ID', '').strip()
        single_page_token = os.environ.get('FB_PAGE_ACCESS_TOKEN', '').strip()

        if ig_account_id:
            print(f"\n[IG] Publishing to Instagram: {ig_account_id}")
            results.append(ig_reel(video_path, caption, page_token=single_page_token, ig_account_id=ig_account_id))
            results.append(ig_story(video_path, page_token=single_page_token, ig_account_id=ig_account_id))

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
    results = publish(video, publish_to_facebook=True, publish_to_instagram=publish_ig)

    entry = {
        'filename': filename,
        'results': results
    }
    published.append(entry)
    save_published(published)

    return results

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    import glob
    processed = glob.glob('Processed_Videos/*.mp4') + glob.glob('Processed_Videos/*.mov')
    results = run_daily_publish(processed)
    print(f"\nPublish results total: {len(results)}")

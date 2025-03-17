# -*- coding: utf-8 -*-
import sys
if sys.version_info >= (3, 13):  # Workaround for Python 3.13+ imghdr issue (if applicable)
    sys.modules['imghdr'] = None
import praw
import random
import time
import os
from collections import deque
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Reddit API credentials
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")
USER_AGENT = f"CryptoTrendBot v1.0 by /u/{USERNAME}"

# Authenticate with Reddit API
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    username=USERNAME,
    password=PASSWORD,
    user_agent=USER_AGENT
)

# Target subreddit (change to your desired subreddit)
TARGET_SUBREDDIT = "test"  # Use r/test for testing, or e.g., r/cryptocurrency

# Keywords (~80+ from your Twitter bot)
keywords = [
    "memecoin", "dogecoin", "shib", "meme crypto", "babydoge", "floki", "pepe coin",
    "doge meme", "shiba inu", "mooncoin", "shitcoin", "crypto meme", "meme token",
    "viral coin", "degen coin", "hype coin", "meme coin pump", "meme coin drop",
    "cheap coin", "fast coin", "meme coin season", "meme coin craze", "token meme",
    "meme coin gem", "rugpull", "pump and dump", "raydium", "solana meme", "sol meme",
    "raydium launch", "solana launch", "solana token", "raydium pool", "solana hype",
    "raydium meme", "solana shitcoin", "solana moon", "raydium token", "solana degen",
    "raydium hype", "solana pump", "pumpfun", "dexscreener", "moondex", "raydium dex",
    "solana dex", "pump token", "crypto pump", "token launch", "moon token", "crypto viral",
    "crypto degen", "bull run meme", "bear market meme", "crypto moon", "to the moon",
    "lambo coin", "diamond hands", "paper hands", "hodl meme", "fomo coin", "fud coin",
    "catcoin", "eloncoin", "safemoon", "bonk coin", "wen coin", "meme lord", "doge killer",
    "shib army", "pepe army", "floki inu", "crypto trend", "meme coin news", "viral crypto",
    "hot coin", "next doge", "meme coin 2025", "crypto gem", "low cap coin", "microcap meme",
    "hidden gem coin"
]

# Static trending tags (adapted for Reddit as flair or text)
trending_tags = [
    "MemeCoinSZN", "SolanaSummer", "RaydiumRocks", "DegenSZN", "CryptoMoon",
    "BullRun2025", "AltcoinSeason", "Web3Vibes", "NFTs", "CryptoGems"
]

# Dynamic comment components (for replies)
intros = [
    "Yo, just 0.05 SOL", "Only 0.05 SOL", "For a tiny 0.05 SOL", "Drop 0.05 SOL",
    "With a mere 0.05 SOL", "At dirt-cheap 0.05 SOL", "0.05 SOL is all you need",
    "Steal this: 0.05 SOL", "Low-key 0.05 SOL", "Bargain 0.05 SOL"
]
actions = [
    "to launch", "to create", "to drop", "to build", "to whip up", "to crank out",
    "to spin up", "to fire off", "to pump out", "to unleash", "to craft", "to blast"
]
descriptors = [
    "a Raydium memecoin", "a viral Raydium coin", "your meme banger", "a Solana hit",
    "a cheap Raydium gem", "a quick meme token", "a hype coin", "a memecoin beast",
    "a Raydium rocket", "a Solana moonshot", "a meme king", "a viral sensation"
]
hype_phrases = [
    "Dirt cheap!", "Stupid easy!", "Too good!", "Insane value!", "Lightning fast!",
    "Cheaper than coffee!", "Easiest ever!", "Unreal deal!", "Mind-blowing!",
    "Game-changer!", "No-brainer!", "Pure fire!", "Next-level!", "Can’t beat it!"
]
calls_to_action = [
    "Check memecoinscreator.fun", "Jump on memecoinscreator.fun",
    "Go to memecoinscreator.fun", "Try memecoinscreator.fun ASAP",
    "Visit memecoinscreator.fun", "Get in at memecoinscreator.fun"
]
emojis = [
    "🚀", "🔥", "💰", "🌙", "💎", "🎉", "⚡", "📈", "🌟", "🤑", "✨", "👑", "🎯", "💪"
]
boosters = [
    "in 2 mins", "with 1 click", "no sweat", "like magic", "in a snap", "so quick",
    "effortless", "right now", "instantly", "boom"
]

# Fetch trending topics and assess crypto dominance
def fetch_crypto_trends(used_trends):
    try:
        # Fetch trending posts from r/all
        subreddit = reddit.subreddit("all")
        trends = [submission.title for submission in subreddit.hot(limit=50)]
        # Filter for crypto relevance
        crypto_keywords = ["crypto", "memecoin", "coin", "token", "solana", "doge", "shib", "pepe", "pump", "moon", "hodl", "fomo", "btc", "eth"]
        crypto_trends = [trend for trend in trends if any(kw in trend.lower() for kw in crypto_keywords)]
        
        # Exclude recently used trends
        available_trends = [trend for trend in crypto_trends if trend not in used_trends]
        
        # Calculate crypto dominance
        total_trends = len(trends)
        crypto_count = len(crypto_trends)
        dominance = crypto_count / total_trends if total_trends > 0 else 0
        
        if not available_trends:
            available_trends = [f"{tag} - Fallback" for tag in trending_tags if tag not in used_trends]
            if not available_trends:
                used_trends.clear()
                available_trends = trending_tags
        
        return available_trends, dominance
    except Exception as e:
        print(f"Failed to fetch trends: {e}")
        available_trends = [f"{tag} - Fallback" for tag in trending_tags if tag not in used_trends]
        if not available_trends:
            used_trends.clear()
            available_trends = trending_tags
        return available_trends, 0

# Generate bait post
def generate_bait_post(keyword, tag):
    bait_texts = [
        f"{keyword} going wild—who’s in? [{tag}]",
        f"{keyword} season is here! [{tag}]",
        f"{keyword} vibes—let’s go! [{tag}]",
        f"{keyword} to the moon? [{tag}]",
        f"{keyword} pumping hard! [{tag}]"
    ]
    post = random.choice(bait_texts)
    if len(post) > 300:  # Reddit’s title limit is ~300 chars
        post = post[:297] + "..."
    return post

# Generate trending topic post
def generate_trending_post(trend):
    phrases = [
        f"{trend} is buzzing—thoughts?",
        f"{trend} taking over—bullish or bearish?",
        f"Hearing {trend} everywhere—who’s riding this?",
        f"{trend} spiking—next big thing?",
        f"{trend} vibes—crypto fam, you in?"
    ]
    post = random.choice(phrases)
    tag = random.choice(trending_tags)
    emoji = random.choice(emojis)
    full_post = f"{post} [{tag}] {emoji}"
    if len(full_post) > 300:
        full_post = full_post[:297] + "..."
    return full_post

# Generate unique reply comment
def generate_unique_comment():
    intro = random.choice(intros)
    action = random.choice(actions)
    descriptor = random.choice(descriptors)
    hype = random.choice(hype_phrases)
    cta = random.choice(calls_to_action)
    emoji = random.choice(emojis)
    booster = random.choice(boosters)
    return f"{intro} {action} {descriptor}? {hype} {cta} {booster} {emoji}"

# Main bot loop
def run_bot():
    print("Reddit bot started... Posting trends and bait posts")
    try:
        # Verify authentication
        print(f"Bot username: /u/{reddit.user.me().name}")
    except Exception as e:
        print(f"Failed to verify credentials: {e}")
        return
    
    # Track used trends with a deque (max 20 to avoid repetition)
    used_trends = deque(maxlen=20)
    base_trending_prob = 0.6  # Base probability for trending posts
    
    subreddit = reddit.subreddit(TARGET_SUBREDDIT)
    
    while True:
        # Fetch trends and assess crypto dominance
        available_trends, crypto_dominance = fetch_crypto_trends(used_trends)
        
        # Adjust trending post probability based on dominance
        trending_prob = min(base_trending_prob + (crypto_dominance - 0.3) * 2, 0.9) if crypto_dominance > 0.3 else base_trending_prob
        print(f"Crypto dominance: {crypto_dominance:.2f}, Trending prob: {trending_prob:.2f}")
        
        # Decide action based on adjusted probability
        if random.random() < trending_prob and available_trends:
            # Post trending topic
            trend = random.choice(available_trends)
            trending_post = generate_trending_post(trend)
            try:
                submission = subreddit.submit(title=trending_post, selftext="")
                used_trends.append(trend)
                print(f"Trending post submitted: {trending_post} (ID: {submission.id})")
            except Exception as e:
                print(f"Failed to post trending topic for {trend}: {e}")
                time.sleep(60)
                continue
        else:
            # Post bait post
            keyword = random.choice(keywords)
            tag = random.choice(trending_tags)
            bait_post = generate_bait_post(keyword, tag)
            try:
                submission = subreddit.submit(title=bait_post, selftext="")
                print(f"Bait post submitted: {bait_post} (ID: {submission.id})")
            except Exception as e:
                print(f"Failed to post bait for {keyword}: {e}")
                time.sleep(60)
                continue
            
            # Reply to bait post
            comment = generate_unique_comment()
            try:
                submission.reply(comment)
                print(f"Replied to {submission.id}: {comment}")
            except Exception as e:
                print(f"Failed to reply for {keyword}: {e}")
        
        # Delay: 30-60 min (~36 posts/day)
        delay = random.randint(1800, 3600)
        print(f"Waiting {delay//60} mins...")
        time.sleep(delay)

if __name__ == "__main__":
    run_bot()
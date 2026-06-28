import os
import csv
import time
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# ─── CONFIG ───────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")
CSV_FILE           = "stocks.csv"          # Chartink se download kiya hua
EMA_PERIODS        = [5, 8, 10, 21]        # Jo EMAs track karne hain
IST                = pytz.timezone("Asia/Kolkata")

# ─── MARKET HOURS CHECK ───────────────────────────────────────────────────────
def is_market_open():
    now = datetime.now(IST)
    if now.weekday() >= 5:                 # Saturday / Sunday
        return False
    market_open  = now.replace(hour=9,  minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close

# ─── LOAD STOCKS FROM CSV ─────────────────────────────────────────────────────
def load_stocks(filepath):
    stocks = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Chartink CSV me 'Symbol' column hota hai
            symbol = row.get("Symbol") or row.get("symbol") or row.get("SYMBOL")
            if symbol:
                symbol = symbol.strip().upper()
                stocks.append(symbol + ".NS")   # NSE suffix
    return stocks

# ─── FETCH PRICE DATA ─────────────────────────────────────────────────────────
def fetch_data(symbol, interval="20m", period="5d"):
    try:
        df = yf.download(symbol, interval=interval, period=period,
                         progress=False, auto_adjust=True)
        if df.empty or len(df) < 25:
            return None
        return df
    except Exception as e:
        print(f"  Error fetching {symbol}: {e}")
        return None

# ─── CALCULATE EMAs ───────────────────────────────────────────────────────────
def calculate_emas(df):
    close = df["Close"].squeeze()
    for period in EMA_PERIODS:
        df[f"EMA{period}"] = close.ewm(span=period, adjust=False).mean()
    return df

# ─── DETECT SIGNALS ───────────────────────────────────────────────────────────
def detect_signals(df, symbol):
    signals = []
    if len(df) < 3:
        return signals

    close   = df["Close"].squeeze()
    prev_close = float(close.iloc[-2])
    curr_close = float(close.iloc[-1])

    for period in EMA_PERIODS:
        col = f"EMA{period}"
        if col not in df.columns:
            continue
        ema_col    = df[col].squeeze()
        prev_ema   = float(ema_col.iloc[-2])
        curr_ema   = float(ema_col.iloc[-1])

        # Bullish cross: price was BELOW ema, now ABOVE
        if prev_close < prev_ema and curr_close > curr_ema:
            signals.append({
                "symbol":    symbol.replace(".NS", ""),
                "direction": "BULLISH 🟢",
                "ema":       period,
                "price":     round(curr_close, 2),
                "ema_val":   round(curr_ema, 2),
            })

        # Bearish cross: price was ABOVE ema, now BELOW
        elif prev_close > prev_ema and curr_close < curr_ema:
            signals.append({
                "symbol":    symbol.replace(".NS", ""),
                "direction": "BEARISH 🔴",
                "ema":       period,
                "price":     round(curr_close, 2),
                "ema_val":   round(curr_ema, 2),
            })

    return signals

# ─── SEND TELEGRAM MESSAGE ────────────────────────────────────────────────────
def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing!")
        return
    url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.status_code != 200:
            print(f"Telegram error: {r.text}")
    except Exception as e:
        print(f"Telegram send failed: {e}")

# ─── FORMAT SIGNAL MESSAGE ────────────────────────────────────────────────────
def format_message(signals, scanned, scan_time):
    if not signals:
        return None

    lines = [
        f"📊 <b>EMA SCANNER — {scan_time}</b>",
        f"Scanned: {scanned} stocks | Signals: {len(signals)}",
        "─────────────────────",
    ]

    bullish = [s for s in signals if "BULLISH" in s["direction"]]
    bearish = [s for s in signals if "BEARISH" in s["direction"]]

    if bullish:
        lines.append("🟢 <b>BULLISH CROSSES</b>")
        for s in bullish:
            lines.append(
                f"• <b>{s['symbol']}</b> crossed above EMA{s['ema']} "
                f"| Price: ₹{s['price']} | EMA: ₹{s['ema_val']}"
            )

    if bullish and bearish:
        lines.append("─────────────────────")

    if bearish:
        lines.append("🔴 <b>BEARISH CROSSES</b>")
        for s in bearish:
            lines.append(
                f"• <b>{s['symbol']}</b> crossed below EMA{s['ema']} "
                f"| Price: ₹{s['price']} | EMA: ₹{s['ema_val']}"
            )

    return "\n".join(lines)

# ─── MAIN SCAN LOOP ───────────────────────────────────────────────────────────
def run_scan():
    print(f"\n{'='*50}")
    print(f"Scan started: {datetime.now(IST).strftime('%H:%M:%S')}")

    if not is_market_open():
        print("Market closed. Skipping scan.")
        return

    stocks = load_stocks(CSV_FILE)
    print(f"Loaded {len(stocks)} stocks from CSV")

    all_signals = []

    for i, symbol in enumerate(stocks):
        print(f"  [{i+1}/{len(stocks)}] {symbol}", end=" ")
        df = fetch_data(symbol)
        if df is None:
            print("- No data")
            continue
        df       = calculate_emas(df)
        signals  = detect_signals(df, symbol)
        if signals:
            print(f"- {len(signals)} signal(s)!")
            all_signals.extend(signals)
        else:
            print("- No signal")
        time.sleep(0.3)    # Rate limit avoid karne ke liye

    scan_time = datetime.now(IST).strftime("%d %b %Y %H:%M")
    message   = format_message(all_signals, len(stocks), scan_time)

    if message:
        print(f"\nSending {len(all_signals)} signals to Telegram...")
        send_telegram(message)
    else:
        print("\nNo signals found this scan.")
        # Optional: no-signal message bhi bhej sakte ho
        # send_telegram(f"📊 Scan complete at {scan_time} — No EMA crosses found.")

    print(f"Scan complete: {datetime.now(IST).strftime('%H:%M:%S')}")

# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_scan()

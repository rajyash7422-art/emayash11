# 📊 EMA Scanner — Telegram Alert Bot

Chartink ke 600 stocks ka EMA 5/9/13/21 scanner.
Har 20 minute mein market hours mein automatically run hoga aur Telegram pe alert bhejega.

---

## ⚡ Features
- ✅ EMA 5 / 9 / 13 / 21 cross detection
- ✅ Bullish + Bearish both signals
- ✅ Market hours only (9:15 AM – 3:30 PM IST)
- ✅ Weekends automatically skip
- ✅ Telegram instant alert
- ✅ GitHub Actions pe free run

---

## 🛠️ Setup — Step by Step

### Step 1 — Telegram Bot Banao
1. Telegram pe `@BotFather` open karo
2. `/newbot` type karo
3. Naam do (jaise: `MyStockScannerBot`)
4. **Token copy karo** — yeh aisa dikhega: `123456789:ABCdefGHI...`

### Step 2 — Apna Chat ID Lo
1. `@userinfobot` pe `/start` bhejo
2. **Chat ID copy karo** (number hoga)

### Step 3 — GitHub Repo Banao
1. GitHub pe **New Repository** banao
2. Yeh saare files upload karo:
   - `scanner.py`
   - `requirements.txt`
   - `.github/workflows/ema_scan.yml`
   - `stocks.csv` (apna Chartink wala)

### Step 4 — Secrets Add Karo
GitHub Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name | Value |
|-------------|-------|
| `TELEGRAM_BOT_TOKEN` | BotFather se mila token |
| `TELEGRAM_CHAT_ID` | Tera chat ID |

### Step 5 — Chartink CSV Upload Karo
1. Chartink pe apna watchlist open karo
2. **Export** karo → CSV download karo
3. `stocks.csv` replace karo apne downloaded file se
4. GitHub pe push/upload karo

### Step 6 — Done! ✅
Kal se market hours mein har 20 min pe Telegram pe signal aayega.

---

## 📱 Telegram Alert Example

```
📊 EMA SCANNER — 28 Jun 2024 10:40
Scanned: 600 stocks | Signals: 4
─────────────────────
🟢 BULLISH CROSSES
• DIXON crossed above EMA21 | Price: ₹14,250 | EMA: ₹14,180
• IRCTC crossed above EMA9  | Price: ₹820 | EMA: ₹815

─────────────────────
🔴 BEARISH CROSSES
• IRFC crossed below EMA13 | Price: ₹182 | EMA: ₹184
• HDFCBANK crossed below EMA5 | Price: ₹1,640 | EMA: ₹1,645
```

---

## ⚙️ Customization

`scanner.py` mein yeh change kar sakte ho:

```python
EMA_PERIODS = [5, 9, 13, 21]   # EMA periods badlo
```

---

## ❓ Common Issues

| Problem | Solution |
|---------|----------|
| No signals | Normal hai — sirf cross pe alert aata hai |
| Stock not found | Check karo CSV mein symbol correct hai |
| Telegram not working | Bot token aur chat ID dobara check karo |
| GitHub Actions not running | Actions tab mein enable karo |

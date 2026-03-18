#    My first analysis
# From date 01 st april 2025 to 18 march 2026
#    STEP 1: Import tools

import yfinance as yf     #fetches stock data
import pandas as pd       #perform calculations
import matplotlib.pyplot as plt       #draws chart
import matplotlib.ticker as mtick     #formats numbers on charts
import warnings
warnings.filterwarnings('ignore')

print("Tools loaded successfully!")

#     STEP 2: Choosing the stocks which i want to analyse
MY_STOCKS = {
    "DATAPATTNS.NS"    : "DATA PATTERNS",
    "BHARATFORG.NS"    : "BHARAT FORGE LIMITED",
    "SBIN.NS"            : "STATE BANK OF INDIA",
    "PGEL.NS"  : "PG ELECTROPLAST LIMITED",
    "NETWEB.NS":  "NETWEB TECHNOLOGIES INDIA LIMITED",
    "AXISBANK.NS"        : "AXIS BANK",
    "ETERNAL.NS"         : "ETERNAL LIMITED"
    }

# NIFTY 50 Index - our benchmark
NIFTY = "^NSEI"

# Data range 
START = '2025-04-01'
END = '2026-03-18'

print("My stocks defined!")
print(f" Tracking{len(MY_STOCKS)} stocks")
print(f" From {START} to {END}")

#     STEP 3 : FETCHING THE DATA
print("\nDownloading data from Yahoo Finance...")
print("Please wait - fetching real prices...")

all_tickers = list(MY_STOCKS.keys()) + [NIFTY]

raw_data = yf.download(
    tickers     = all_tickers,
    start       = START,
    end         = END,
    auto_adjust = True,
    progress    = True
)

# Keep only closing pricea
# Closing price = final price for the day
# This is waht matters for returns calcaulation
prices = raw_data["Close"].copy()

# Rename columns to readable names
rename_map = {k: v for k,v in MY_STOCKS.items()}
rename_map[NIFTY] = "NIFTY_50"
prices.rename(columns=rename_map, inplace=True)

print("\n Data downloaded successfully!")
print(f"  Total trading days: {len(prices)}")
print(f"  Stocks downloaded :{len(prices.columns)}")
print("\nFirst 3 rows of your data:")
print(prices.head(3).round(2))
...

#     STEP 4: CLEANING THE DATA
print("\nCleaning data...")

# Fix 1: Forward fill missing values
# fills holiday gaps with last traded known price
prices_clean = prices.copy()
prices_clean.ffill(inplace=True)
prices_clean.bfill(inplace=True)

#Remove weekends
prices_clean = prices_clean[prices_clean.index.dayofweek < 5]

# Fix 3: Calculate daily returns
# pct_change = percentage change from yesterday
daily_returns = prices_clean.pct_change().dropna()

print(f"Data cleaned!")
print(f"  Total trading days: {len(prices_clean)}")
print(f"  Missing values : {prices_clean.isnull().sum().sum()}")
print(f"\nDaily returns (first 3 days):")
print((daily_returns.head(3)*100).round(2))
...

#   STEP 5: CALCULATE RETURNS
# Remember pct_change gives us daily returns in percentage
# Now we calculate CUMULATIVE returns
# Cumulative = total return from day1 till today
print("\nCalculating returns...")

# Separate stocks from NIFTY
stock_names = list(MY_STOCKS.values())
nifty_ret = daily_returns["NIFTY_50"]
stock_ret = daily_returns[stock_names]

# Cumulative return formula:
# (1 + day1) * (1 + day2) * (1 + day3)... - 1
# This compounds returns day by day!
def cum_return(series):
    return (1 + series).cumprod() - 1

# Calculate for each stock and NIFTY
port_cumret = cum_return(stock_ret.mean(axis=1))
nifty_cumret = cum_return(nifty_ret)
stock_cumret = stock_ret.apply(cum_return)

# Final total revenue for each stock
print("\nTotal returns Apr 2025 to Mar 2026:")
print("-" * 40)
for stock in stock_names:
    total = stock_cumret[stock].iloc[-1]*100
    direction = "UP" if total >= 0 else "DOWN"
    print(f"  {direction} {stock:<30} {total:+.1f}%")

nifty_total = nifty_cumret.iloc[-1]*100
print(f"\n BENCHMARK NIFTY 50" + " " * 11 + f"{nifty_total:+.1f}%")
print("-" * 40)

# STEP 6 (FINAL STEP) — DRAW CHART
import seaborn as sns
# MY COLOR PALETTE
GREEN  = "#3fb950"   # profit / positive
RED    = "#f85149"   # loss / negative
BLUE   = "#388bfd"   # portfolio line
GOLD   = "#d29922"   # NIFTY benchmark
GRAY   = "#8b949e"   # secondary lines
BG     = "#0d1117"   # background

CHART_TITLE   = "My Portfolio vs NIFTY 50 — Apr 2025 to Mar 2026"
CHART_WIDTH   = 14
CHART_HEIGHT  = 10
SAVE_FILENAME = "my_portfolio_chart.png"

# ── Prepare data ──────────────────────────────
returns_data = stock_cumret.iloc[-1] * 100
returns_data = returns_data.sort_values(ascending=False)
bar_colors   = [GREEN if x >= 0 else RED
                for x in returns_data]

# ── Create figure with 2 charts ───────────────
plt.style.use("dark_background")
fig, (ax1, ax2) = plt.subplots(2, 1,
                  figsize=(CHART_WIDTH, CHART_HEIGHT))
fig.patch.set_facecolor(BG)

# CHART 1 — Bar chart (who won, who lost)
sns.barplot(x=returns_data.values,
            y=returns_data.index,
            palette=bar_colors,
            ax=ax1)

# Add % labels on each bar
for i, val in enumerate(returns_data.values):
    ax1.text(val + 1, i, f"{val:+.1f}%",
             va="center", fontsize=11,
             fontweight="bold",
             color=GREEN if val >= 0 else RED)

# NIFTY benchmark line
ax1.axvline(x=nifty_total, color=GOLD,
            linewidth=2, linestyle="--",
            label=f"NIFTY 50: {nifty_total:+.1f}%")

ax1.set_title(CHART_TITLE, fontsize=13, pad=12)
ax1.xaxis.set_major_formatter(mtick.PercentFormatter())
ax1.legend(fontsize=10)
ax1.grid(True, axis="x", alpha=0.3)
ax1.set_facecolor(BG)

# CHART 2 — Line chart (the journey over time)
line_colors = [GREEN, BLUE, GOLD, RED,
               GRAY, "#a371f7", "#ff7b72", "#79c0ff"]

for i, stock in enumerate(stock_names):
    if stock in stock_cumret.columns:
        ax2.plot(stock_cumret.index,
                 stock_cumret[stock] * 100,
                 color=line_colors[i],
                 linewidth=1.8,
                 label=stock.split()[0])

# NIFTY as thick white dashed line
ax2.plot(nifty_cumret.index,
         nifty_cumret * 100,
         color="white", linewidth=2.5,
         linestyle="--", label="NIFTY 50")

ax2.axhline(y=0, color=GRAY,
            linewidth=0.8, alpha=0.4)
ax2.set_title("Cumulative Returns Over Time",
              fontsize=13, pad=12)
ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
ax2.legend(loc="upper left",
           fontsize=9, ncol=3,
           framealpha=0.3)
ax2.grid(True, alpha=0.3)
ax2.set_facecolor(BG)

# ── Save and show ─────────────────────────────
plt.tight_layout(pad=3.0)
plt.savefig(SAVE_FILENAME, dpi=150,
            bbox_inches="tight",
            facecolor=BG)
plt.show()
print(f"Chart saved as {SAVE_FILENAME}!")

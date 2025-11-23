import requests, time
from datetime import datetime
from config import *

def send(m):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": m, "parse_mode": "HTML"}, timeout=10)
    except: pass

def vix(): 
    try: return round(float(requests.get("https://cdn.cboe.com/api/global/delayed_quotes/indexes/^VIX.json",timeout=8).json()["data"]["last"]),2)
    except: return None
def gvz(): 
    try: return round(float(requests.get("https://cdn.cboe.com/api/global/delayed_quotes/indexes/^GVZ.json",timeout=8).json()["data"]["last"]),2)
    except: return None
def us10y():
    try:
        t=requests.get("https://api.allorigins.win/raw?url=https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/TextView.aspx?data=yield",timeout=15).text
        return float(t.split('10 Yr')[1].split('</td>')[0].split('>')[-1].strip())
    except: return None
def gld():
    try: return round(float(requests.get("https://www.spdrgoldshares.com/assets/dynamic/GLD_US/GLD_Holdings.csv",timeout=10).text.strip().split('\n')[1].split(',')[1]),2)
    except: return None

send("🚀 Bot vàng của bạn đã KHỞI ĐỘNG!\nCheck mỗi 30 giây – GLD≥5 tấn, VIX, GVZ, US10Y")
old={"vix":0,"gvz":0,"us10y":0,"gld":0}
gld_prev=None
alerted=False
today=""

while True:
    try:
        now=datetime.now()
        if now.strftime("%d")!=today: alerted=False; today=now.strftime("%d")
        v=vix()or old["vix"]
        g=gvz()or old["gvz"]
        u=us10y()or old["us10y"]
        gl=gld()

        if gl and gld_prev is not None and abs(gl-gld_prev)>=GLD_TONS:
            c=gl-gld_prev
            send(f"{'🟢MUA'if c>0 else '🔴XẢ'} <b>{abs(c)} tấn vàng SPDR!</b>\nTổng: {gl}t\n{now.strftime('%H:%M %d/%m')}")
            if abs(c)>=10: send("🔔🔔🔔 DING DING DING 🔔🔔🔔")

        if v and old["vix"] and (v>VIX_TH or abs(v-old["vix"])/old["vix"]>VIX_PCT):
            send(f"🚨 VIX → {v} (+{round(v-old['vix'],2)})")
        if g and old["gvz"] and (g>GVZ_TH or abs(g-old["gvz"])/old["gvz"]>GVZ_PCT):
            send(f"🥵 GVZ → {g} (+{round(g-old['gvz'],2)})")

        if u and old["us10y"] and not alerted and abs(u-old["us10y"])>=US10Y_BPS:
            send(f"📈 US10Y ±0.25% → {u:.3f}% (Δ{round((u-old['us10y'])*100,2)}bps)\nChỉ báo 1 lần/ngày")
            alerted=True

        gld_prev=gl
        old={"vix":v,"gvz":g,"us10y":u,"gld":gl}
        time.sleep(30)
    except: time.sleep(10)

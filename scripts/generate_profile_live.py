#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import random
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape as html_escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "profile" / "profile_config.json"
ASSET_DIR = ROOT / "assets"
USER_AGENT = "S2zxx0zxx-profile-live/1.0"
CONFIG = json.loads(CONFIG_PATH.read_text("utf-8"))
USER = CONFIG["user"]
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ASSET_DIR.mkdir(parents=True, exist_ok=True)


def request_json(url: str, *, method: str = "GET", body: dict[str, Any] | None = None) -> Any:
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as res:
        return json.loads(res.read().decode("utf-8"))


def request_text(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as res:
        return res.read().decode("utf-8", errors="replace")


def safe_api(path: str, default: Any) -> Any:
    try:
        return request_json(f"https://api.github.com{path}")
    except Exception as exc:
        print(f"[warn] API {path}: {exc}", file=sys.stderr)
        return default


def fetch_public_repos() -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    for page in range(1, 4):
        batch = safe_api(
            f"/users/{urllib.parse.quote(USER)}/repos?per_page=100&page={page}&type=owner&sort=updated",
            [],
        )
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
    seen: set[Any] = set()
    unique: list[dict[str, Any]] = []
    for repo in repos:
        key = repo.get("id", repo.get("full_name", repo.get("name")))
        if key not in seen:
            seen.add(key)
            unique.append(repo)
    return unique


def fetch_repo_snapshot(repo_name: str) -> dict[str, Any]:
    repo = safe_api(f"/repos/{USER}/{urllib.parse.quote(repo_name)}", {})
    commits = safe_api(f"/repos/{USER}/{urllib.parse.quote(repo_name)}/commits?per_page=1", [])
    commit = commits[0] if isinstance(commits, list) and commits else {}
    cmeta = commit.get("commit", {}) if isinstance(commit, dict) else {}
    ccommitter = cmeta.get("committer", {}) if isinstance(cmeta, dict) else {}
    message = (cmeta.get("message") or "").splitlines()[0].strip()
    date = ccommitter.get("date") or repo.get("pushed_at") or repo.get("updated_at") or ""
    return {
        "repo": repo_name,
        "branch": repo.get("default_branch") or "—",
        "language": repo.get("language") or "Mixed",
        "commit_date": date,
        "commit_message": message,
        "commit_sha": (commit.get("sha") or "")[:7] if isinstance(commit, dict) else "",
        "size": repo.get("size") or 0,
    }


def parse_dt(value: str) -> datetime:
    if not value:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)


def short_date(value: str) -> str:
    dt = parse_dt(value)
    if dt.year <= 1970:
        return "no public signal"
    return dt.strftime("%d %b %Y").lstrip("0")


def xml(value: Any) -> str:
    return html_escape(str(value), quote=True)


def trim(value: str, limit: int) -> str:
    value = " ".join((value or "").split())
    return value if len(value) <= limit else value[: max(1, limit - 1)].rstrip() + "…"


def write_asset(name: str, text: str) -> None:
    path = ASSET_DIR / name
    old = path.read_text("utf-8") if path.exists() else None
    if old == text:
        print(f"[same] {name}")
        return
    path.write_text(text, encoding="utf-8")
    print(f"[write] {name}")


def svg_shell(width: int, height: int, body: str, title: str, *, extra_style: str = "") -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{xml(title)}</title>
<desc id="desc">Auto-generated live profile visualization for {xml(USER)}.</desc>
<defs>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5468FF"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient>
  <filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
:root{{--bg:#FBFBF8;--panel:#FFFFFF;--ink:#171717;--muted:#777771;--hair:#E5E5DF;--soft:#F3F3EF;--accent:#5468FF;--accent2:#8B5CF6;--good:#27B66D;--warn:#F59E0B}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0D1117;--panel:#11161D;--ink:#F3F4F6;--muted:#8B949E;--hair:#30363D;--soft:#161B22;--accent:#7C8CFF;--accent2:#A78BFA;--good:#3DDC84;--warn:#F7B955}}}}
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}}.sans{{font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.panel{{fill:var(--panel);stroke:var(--hair)}}.ink{{fill:var(--ink)}}.muted{{fill:var(--muted)}}.hair{{stroke:var(--hair)}}
.pulse{{animation:pulse 2.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}.blink{{animation:blink 1s steps(1,end) infinite}}.flow{{stroke-dasharray:7 9;animation:flow 2.2s linear infinite}}
@keyframes pulse{{0%,100%{{opacity:.55;transform:scale(.88)}}50%{{opacity:1;transform:scale(1.18)}}}}@keyframes blink{{0%,48%{{opacity:1}}49%,100%{{opacity:0}}}}@keyframes flow{{to{{stroke-dashoffset:-32}}}}
@media (prefers-reduced-motion:reduce){{.pulse,.blink,.flow,.reveal,.scan,.orbit,.cityscan{{animation:none!important}}}}
{extra_style}
</style>
{body}
</svg>'''


def fetch_contributions() -> tuple[list[dict[str, Any]], int]:
    year = datetime.now(timezone.utc).year
    start = f"{year}-01-01T00:00:00Z"
    end = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = '''query($login:String!, $from:DateTime!, $to:DateTime!) { user(login:$login) { contributionsCollection(from:$from, to:$to) { contributionCalendar { totalContributions weeks { contributionDays { contributionCount contributionLevel date weekday } } } } } }'''
    try:
        payload = request_json("https://api.github.com/graphql", method="POST", body={"query": query, "variables": {"login": USER, "from": start, "to": end}})
        cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        days = [d for w in cal["weeks"] for d in w["contributionDays"]]
        return days, int(cal.get("totalContributions") or 0)
    except Exception as exc:
        print(f"[warn] GraphQL contribution calendar: {exc}", file=sys.stderr)
    try:
        html = request_text(f"https://github.com/users/{USER}/contributions")
        matches = re.findall(r'data-date="([^"]+)"[^>]*?data-level="(\d+)"', html)
        level_names = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
        days = []
        for date, level_s in matches:
            level = int(level_s)
            days.append({"date": date, "contributionCount": level, "contributionLevel": level_names[min(max(level,0),4)]})
        if days:
            return days, sum(int(d["contributionCount"]) for d in days)
    except Exception as exc:
        print(f"[warn] HTML contribution calendar: {exc}", file=sys.stderr)
    return [], 0


def contribution_level(day: dict[str, Any], max_count: int) -> int:
    mapping = {"NONE":0,"FIRST_QUARTILE":1,"SECOND_QUARTILE":2,"THIRD_QUARTILE":3,"FOURTH_QUARTILE":4}
    raw = str(day.get("contributionLevel") or "")
    if raw in mapping:
        return mapping[raw]
    count = int(day.get("contributionCount") or 0)
    if count <= 0:
        return 0
    ratio = math.log1p(count) / math.log1p(max(max_count, 1))
    return max(1, min(4, int(math.ceil(ratio * 4))))


def generate_terminal(public_count: int) -> str:
    lines = [
        ("00","BOOT","profile kernel","ONLINE","#27B66D"),
        ("01","MAP","repo universe",f"{public_count} PUBLIC / {CONFIG['mapped_total']} MAPPED","#5468FF"),
        ("02","SHIP","FinCo-Pilot","HARDENING","#F59E0B"),
        ("03","BUILD","ToolsLab LLMs","ACTIVE","#27B66D"),
        ("04","SYNC","GitHub signals","AUTO-REFRESH ARMED","#5468FF"),
    ]
    rows=[]
    for i,(idx,kind,label,value,color) in enumerate(lines):
        y=106+i*42
        rows.append(f'<g class="reveal r{i}"><text x="52" y="{y}" font-size="12" class="muted">{idx}</text><text x="94" y="{y}" font-size="12" fill="{color}">{kind}</text><text x="156" y="{y}" font-size="14" class="ink">{xml(label)}</text><text x="830" y="{y}" text-anchor="end" font-size="12" class="muted">{xml(value)}</text></g>')
    style='''.reveal{opacity:0;animation:reveal 8.4s ease-in-out infinite}.r0{animation-delay:.35s}.r1{animation-delay:.83s}.r2{animation-delay:1.31s}.r3{animation-delay:1.79s}.r4{animation-delay:2.27s}.scan{animation:scan 4.2s linear infinite}@keyframes reveal{0%,4%{opacity:0;transform:translateY(6px)}8%,86%{opacity:1;transform:none}96%,100%{opacity:0}}@keyframes scan{0%{transform:translateX(-760px);opacity:0}8%{opacity:.45}82%{opacity:.12}100%{transform:translateX(820px);opacity:0}}'''
    body=f'''<rect width="900" height="350" rx="24" fill="var(--bg)"/><rect x="20" y="20" width="860" height="310" rx="20" class="panel"/><circle cx="50" cy="52" r="5" fill="#FF5F57"/><circle cx="68" cy="52" r="5" fill="#FEBC2E"/><circle cx="86" cy="52" r="5" fill="#28C840"/><text x="112" y="57" font-size="12" class="muted">SATZZXZXX // LIVE BUILDER TERMINAL</text><text x="830" y="57" text-anchor="end" font-size="11" fill="#27B66D">● TELEMETRY ON</text><line x1="40" y1="74" x2="860" y2="74" class="hair"/>{''.join(rows)}<line x1="40" y1="302" x2="860" y2="302" class="hair"/><text x="52" y="318" font-size="11" class="muted">&gt; research → build → audit → ship</text><rect class="blink" x="335" y="307" width="8" height="14" rx="1" fill="var(--accent)"/><rect class="scan" x="30" y="78" width="90" height="210" fill="url(#accent)" opacity=".08"/>'''
    return svg_shell(900,350,body,"Live builder terminal",extra_style=style)


def generate_heartbeat(snapshots: dict[str,dict[str,Any]]) -> str:
    products=CONFIG["heartbeat_products"]
    cards=[]; card_w=410; gap=20
    for i,p in enumerate(products):
        s=snapshots.get(p["repo"],{}); col=i%2; row=i//2; x=30+col*(card_w+gap); y=102+row*142
        status=p["status"]; color="#F59E0B" if status=="HARDENING" else "#27B66D"; pulse="pulse" if status in {"BUILDING","HARDENING"} else ""
        cards.append(f'''<g transform="translate({x} {y})"><rect width="{card_w}" height="124" rx="18" class="panel"/><circle class="{pulse}" cx="24" cy="27" r="6" fill="{color}"/><text x="42" y="32" font-size="11" fill="{color}">{xml(status)}</text><text x="24" y="62" font-size="20" font-weight="700" class="sans ink">{xml(p['label'])}</text><text x="24" y="86" font-size="11" class="muted">{xml(trim(s.get('commit_message','') or 'No public commit signal',43))}</text><text x="24" y="108" font-size="10" class="muted">{xml(trim(s.get('branch','—'),16))} · {xml(trim(s.get('language','Mixed'),12))}</text><text x="{card_w-20}" y="108" text-anchor="end" font-size="10" class="muted">{xml(short_date(s.get('commit_date','')))}</text></g>''')
    rows=math.ceil(len(products)/2); h=128+rows*142+20
    body=f'''<rect width="900" height="{h}" rx="24" fill="var(--bg)"/><text x="30" y="42" font-size="12" fill="#27B66D" letter-spacing="2">PRODUCT HEARTBEAT</text><text x="30" y="76" font-size="27" font-weight="800" class="sans ink">Real repository signals, not vanity counters.</text><text x="870" y="48" text-anchor="end" font-size="10" class="muted">AUTO-SYNC · PUBLIC GITHUB DATA</text>{''.join(cards)}'''
    return svg_shell(900,h,body,"Product heartbeat board")


def classify_repo(repo: dict[str,Any]) -> str:
    hay=((repo.get('name') or '')+' '+(repo.get('description') or '')).lower()
    rules=[('FINANCE',['finco','finance','stock','markettrade','fare','bribes']),('AI',['ai','mcp','llm','agent','zenvy','bharat-os','toolshub','buildme']),('BUSINESS',['digirise','growpartner','gamemart','portfolio','store','brands']),('WEB',['lounge','scenic','travel','github.io','elitehub','savesocial']),('LEARN',['leetcode','scrap','spam','docx','music','airbnb','git-track','vscode','image']),('SYSTEMS',['omniroute','codebase','bepb','bt','route'])]
    for cat,kws in rules:
        if any(k in hay for k in kws): return cat
    return 'WEB'


def generate_constellation(repos: list[dict[str,Any]]) -> str:
    centers={'FINANCE':(188,168),'AI':(440,122),'WEB':(692,168),'BUSINESS':(710,402),'LEARN':(445,448),'SYSTEMS':(190,402)}
    colors={'FINANCE':'#5468FF','AI':'#8B5CF6','WEB':'#2F81F7','BUSINESS':'#27B66D','LEARN':'#E3B341','SYSTEMS':'#DB6D28'}
    grouped={k:[] for k in centers}
    for r in repos: grouped[classify_repo(r)].append(r)
    flagships={'FinCo-pilot':'FINCO','Toolshub':'TOOLS','DigiRise-India':'DIGIRISE','financeCalculator-Ind-v6.0-':'FINCALC','Zenvy-AI':'ZENVY','Bharat-OS':'BHARAT'}
    clusters=[]; lines=[]; nodes=[]
    for cat,(cx,cy) in centers.items():
        c=colors[cat]; items=sorted(grouped[cat],key=lambda x:(x.get('name') or '').lower()); n=max(1,len(items))
        clusters.append(f'<circle cx="{cx}" cy="{cy}" r="82" fill="{c}" opacity=".035" stroke="{c}" stroke-opacity=".18" stroke-dasharray="3 8"/><text x="{cx}" y="{cy-94}" text-anchor="middle" font-size="10" fill="{c}" letter-spacing="1.8">{cat} · {len(items)}</text>')
        for j,repo in enumerate(items):
            seed=sum((k+1)*ord(ch) for k,ch in enumerate(repo.get('name','')))+len(cat)*97; rnd=random.Random(seed); ring=34+16*(j//7); angle=(2*math.pi*j/min(max(n,1),7))+rnd.uniform(-.3,.3); x=cx+math.cos(angle)*ring+rnd.uniform(-8,8); y=cy+math.sin(angle)*ring*.72+rnd.uniform(-6,6)
            lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{c}" stroke-opacity=".10"/>')
            name=repo.get('name','')
            if name in flagships:
                nodes.append(f'<g><circle class="pulse" cx="{x:.1f}" cy="{y:.1f}" r="14" fill="{c}" opacity=".15"/><circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{c}" filter="url(#softGlow)"/><text x="{x:.1f}" y="{y+24:.1f}" text-anchor="middle" font-size="9" class="ink">{flagships[name]}</text></g>')
            else:
                size=3.2+min(2.8,math.log10(max(1,repo.get('size') or 1))*.5); nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.1f}" fill="{c}" opacity=".72"/>')
    style='''.orbit{transform-origin:450px 292px;animation:orbit 42s linear infinite}@keyframes orbit{to{transform:rotate(360deg)}}'''
    body=f'''<rect width="900" height="590" rx="24" fill="var(--bg)"/><text x="30" y="42" font-size="12" fill="#5468FF" letter-spacing="2">REPO CONSTELLATION</text><text x="30" y="76" font-size="27" font-weight="800" class="sans ink">A public product universe, grouped by what each repo explores.</text><text x="870" y="48" text-anchor="end" font-size="10" class="muted">{len(repos)} PUBLIC NODES · {CONFIG['mapped_total']} REPOS MAPPED</text><g opacity=".55"><ellipse class="orbit" cx="450" cy="292" rx="385" ry="238" fill="none" stroke="var(--hair)" stroke-dasharray="2 13"/><ellipse cx="450" cy="292" rx="320" ry="190" fill="none" stroke="var(--hair)" stroke-dasharray="1 15"/></g>{''.join(clusters)}{''.join(lines)}{''.join(nodes)}<g transform="translate(450 292)"><circle r="43" fill="url(#accent)" opacity=".12"/><circle r="28" fill="var(--panel)" stroke="var(--accent)" stroke-width="2"/><circle class="pulse" r="6" fill="var(--accent)"/><text y="-44" text-anchor="middle" font-size="10" fill="var(--accent)" letter-spacing="1.4">CORE</text><text y="52" text-anchor="middle" font-size="13" font-weight="700" class="sans ink">SATZZXZXX</text></g><text x="450" y="565" text-anchor="middle" font-size="10" class="muted">Large glowing nodes = current flagship signals · small nodes = public repositories</text>'''
    return svg_shell(900,590,body,"Repository constellation",extra_style=style)


def generate_timeline(snapshots: dict[str,dict[str,Any]]) -> str:
    stages=['RESEARCH','BUILD','AUDIT','PRODUCTION','SHIPPED']; sx=[90,265,440,615,790]; slots={i:0 for i in range(len(stages))}; markers=[]
    for p in CONFIG['timeline_products']:
        idx=stages.index(p['stage']); slot=slots[idx]; slots[idx]+=1; x=sx[idx]; y=150+slot*54; s=snapshots.get(p.get('repo') or '',{}); date=short_date(s.get('commit_date','')) if p.get('repo') else p.get('note','curated'); active=p.get('active',False); color='#5468FF' if active else ('#27B66D' if p['stage']=='SHIPPED' else '#8B5CF6'); pulse='pulse' if active else ''
        markers.append(f'<g transform="translate({x} {y})"><circle class="{pulse}" r="9" fill="{color}" opacity=".18"/><circle r="4.8" fill="{color}"/><text y="22" text-anchor="middle" font-size="10" font-weight="700" class="sans ink">{xml(p["label"])}</text><text y="37" text-anchor="middle" font-size="8.5" class="muted">{xml(date)}</text></g>')
    stage_nodes=''.join(f'<circle cx="{sx[i]}" cy="112" r="9" fill="var(--panel)" stroke="var(--accent)" stroke-width="2"/><text x="{sx[i]}" y="90" text-anchor="middle" font-size="10" fill="var(--accent)" letter-spacing="1">{stage}</text>' for i,stage in enumerate(stages))
    body=f'''<rect width="900" height="370" rx="24" fill="var(--bg)"/><text x="30" y="42" font-size="12" fill="#8B5CF6" letter-spacing="2">SHIPPING TIMELINE</text><text x="30" y="76" font-size="27" font-weight="800" class="sans ink">Research → Build → Audit → Production → Shipped</text><line x1="90" y1="112" x2="790" y2="112" stroke="var(--hair)" stroke-width="5" stroke-linecap="round"/><line class="flow" x1="90" y1="112" x2="790" y2="112" stroke="url(#accent)" stroke-width="2" stroke-linecap="round"/>{stage_nodes}{''.join(markers)}<text x="30" y="344" font-size="10" class="muted">Phase is curated product state · dates refresh from public repository commit signals.</text>'''
    return svg_shell(900,370,body,"Shipping timeline")


def generate_feed(snapshots: dict[str,dict[str,Any]]) -> str:
    feed=[]
    for p in CONFIG['feed_repos']:
        s=snapshots.get(p['repo'],{})
        if s.get('commit_date'): feed.append({'label':p['label'],'date':s['commit_date'],'message':s.get('commit_message') or 'Repository activity','sha':s.get('commit_sha','')})
    feed.sort(key=lambda x:parse_dt(x['date']),reverse=True); feed=feed[:4]; rows=[]
    for i,item in enumerate(feed):
        y=115+i*72; color='#5468FF' if i==0 else '#27B66D'; pulse='pulse' if i==0 else ''
        rows.append(f'<g><line x1="72" y1="{y+13}" x2="72" y2="{y+72 if i<len(feed)-1 else y+42}" stroke="var(--hair)" stroke-width="2"/><circle class="{pulse}" cx="72" cy="{y+12}" r="7" fill="{color}"/><text x="100" y="{y+8}" font-size="11" fill="{color}" letter-spacing="1">{xml(item["label"].upper())}</text><text x="100" y="{y+31}" font-size="15" font-weight="700" class="sans ink">{xml(trim(item["message"],72))}</text><text x="100" y="{y+52}" font-size="10" class="muted">{xml(short_date(item["date"]))} · {xml(item["sha"])}</text></g>')
    if not rows: rows=['<text x="450" y="180" text-anchor="middle" font-size="12" class="muted">No public commit signal available right now.</text>']
    h=150+max(1,len(feed))*72+38
    body=f'''<rect width="900" height="{h}" rx="24" fill="var(--bg)"/><text x="30" y="42" font-size="12" fill="#27B66D" letter-spacing="2">RECENT SHIPPING SIGNALS</text><text x="30" y="76" font-size="27" font-weight="800" class="sans ink">A compact feed generated from real public commits.</text><text x="870" y="48" text-anchor="end" font-size="10" class="muted">AUTO-SORTED · NEWEST FIRST</text>{''.join(rows)}'''
    return svg_shell(900,h,body,"Recent shipping feed")


def iso_building(x:float,y:float,width:float,height:float,color:str,alpha:float)->str:
    depth=width*.5; top_y=y-height
    return f'<polygon points="{x:.1f},{top_y:.1f} {x+width:.1f},{top_y:.1f} {x+width:.1f},{y:.1f} {x:.1f},{y:.1f}" fill="{color}" opacity="{alpha:.2f}"/><polygon points="{x+width:.1f},{top_y:.1f} {x+width+depth:.1f},{top_y-depth:.1f} {x+width+depth:.1f},{y-depth:.1f} {x+width:.1f},{y:.1f}" fill="{color}" opacity="{max(.08,alpha-.18):.2f}"/><polygon points="{x:.1f},{top_y:.1f} {x+depth:.1f},{top_y-depth:.1f} {x+width+depth:.1f},{top_y-depth:.1f} {x+width:.1f},{top_y:.1f}" fill="{color}" opacity="{min(1,alpha+.12):.2f}"/>'


def generate_city(days:list[dict[str,Any]],total:int)->str:
    year=datetime.now(timezone.utc).year; max_count=max([int(d.get('contributionCount') or 0) for d in days] or [1]); parsed=[]
    for d in days:
        try: dt=datetime.strptime(d['date'],'%Y-%m-%d').replace(tzinfo=timezone.utc)
        except Exception: continue
        if dt.year!=year: continue
        parsed.append(((dt.timetuple().tm_yday-1)//7,dt.weekday(),d))
    colors=['#2A3038','#D8F3E6','#89E0B1','#36C978','#158A52']; buildings=[]
    for week,weekday,d in sorted(parsed,key=lambda t:(t[1],t[0])):
        count=int(d.get('contributionCount') or 0); lvl=contribution_level(d,max_count); x=48+week*15.3+weekday*5.0; y=255+weekday*8.0-week*1.65; width=6.3
        if count<=0: buildings.append(f'<polygon points="{x:.1f},{y:.1f} {x+width:.1f},{y:.1f} {x+width+3:.1f},{y-3:.1f} {x+3:.1f},{y-3:.1f}" fill="var(--hair)" opacity=".28"/>'); continue
        normalized=math.log1p(count)/math.log1p(max_count) if max_count>0 else 0; height=7+normalized*52; buildings.append(iso_building(x,y,width,height,colors[lvl],.78+lvl*.045))
    style='''.cityscan{animation:cityscan 5.6s linear infinite}@keyframes cityscan{0%{transform:translateX(-150px);opacity:0}15%{opacity:.35}70%{opacity:.12}100%{transform:translateX(950px);opacity:0}}'''
    body=f'''<rect width="900" height="365" rx="24" fill="var(--bg)"/><text x="30" y="42" font-size="12" fill="#27B66D" letter-spacing="2">CONTRIBUTION CITY · {year}</text><text x="30" y="76" font-size="27" font-weight="800" class="sans ink">Your contribution calendar, rebuilt as a living skyline.</text><text x="870" y="48" text-anchor="end" font-size="10" class="muted">{total:,} CONTRIBUTIONS · LIVE CALENDAR SIGNAL</text><line x1="30" y1="296" x2="870" y2="296" class="hair"/><g>{''.join(buildings)}</g><rect class="cityscan" x="10" y="96" width="110" height="190" fill="url(#accent)" opacity=".08"/><text x="30" y="334" font-size="10" class="muted">Building height uses log-scaled daily contribution count · empty lots stay intentionally flat.</text><g transform="translate(705 318)"><rect width="165" height="25" rx="12.5" fill="var(--soft)"/><circle cx="14" cy="12.5" r="4" fill="#27B66D" class="pulse"/><text x="26" y="16" font-size="9" class="muted">AUTO-REFRESHED</text></g>'''
    return svg_shell(900,365,body,"Contribution city",extra_style=style)


def main()->None:
    repos=fetch_public_repos(); needed=set()
    for p in CONFIG['heartbeat_products']: needed.add(p['repo'])
    for p in CONFIG['timeline_products']:
        if p.get('repo'): needed.add(p['repo'])
    for p in CONFIG['feed_repos']: needed.add(p['repo'])
    snapshots={repo:fetch_repo_snapshot(repo) for repo in sorted(needed)}; days,total=fetch_contributions()
    write_asset('terminal-boot-live.svg',generate_terminal(len(repos)))
    write_asset('product-heartbeat-live.svg',generate_heartbeat(snapshots))
    write_asset('repo-constellation-live.svg',generate_constellation(repos))
    write_asset('shipping-timeline-live.svg',generate_timeline(snapshots))
    write_asset('shipping-feed-live.svg',generate_feed(snapshots))
    write_asset('contribution-city-live.svg',generate_city(days,total))
    print(json.dumps({'user':USER,'public_repos':len(repos),'mapped_total':CONFIG['mapped_total'],'contributions':total,'snapshots':{k:{'date':v['commit_date'],'sha':v['commit_sha']} for k,v in snapshots.items()}},indent=2))


if __name__=='__main__':
    main()

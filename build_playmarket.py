# -*- coding: utf-8 -*-
"""
Генератор лендинга-копии страницы Google Play под раздачу APK 1xBet.
Две гео-версии: KG и TJ (обе RU). Выдача — два self-contained HTML.

Ключевая механика: кнопка «Установить» собирает целевую ссылку ДИНАМИЧЕСКИ
из UTM-меток в URL лендинга (domain / tag / pb / click_id) — см. доку владельца.
Пример входа:  https://1xbt.kz/?domain=reffpa.com/L&tag=...&pb=...&click_id={clickid}
Кнопка выдаёт: https://reffpa.com/L?tag=...&pb=...&click_id={clickid}
tag (со скобками []) и click_id (с макросом {clickid}) передаются СЫРЫМИ.

Запуск:  python3 build_playmarket.py
"""
import sys, os, base64
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Favicon — читается при сборке из favicon.ico рядом, инлайнится в <head> data-URI
# (self-contained: ничего лишнего деплоить). Заменить favicon — положить новый favicon.ico.
_FAV_PATH = os.path.join(OUT_DIR, "favicon.ico")
FAVICON_DATA_URI = ""
if os.path.exists(_FAV_PATH):
    FAVICON_DATA_URI = "data:image/x-icon;base64," + base64.b64encode(open(_FAV_PATH, "rb").read()).decode()

# ──────────────────────────────────────────────────────────────────────────
# АССЕТЫ-ПЛЕЙСХОЛДЕРЫ (inline SVG). Заменить на официальные PNG —
# см. README. Слоты помечены в HTML комментариями SWAP-ICON / SWAP-SCREEN.
# ──────────────────────────────────────────────────────────────────────────

ICON_SVG = '''<svg viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg" class="app-icon-svg" role="img" aria-label="1xBet">
  <defs>
    <linearGradient id="ic" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#103a66"/><stop offset="1" stop-color="#0a2540"/>
    </linearGradient>
  </defs>
  <rect width="96" height="96" rx="22" fill="url(#ic)"/>
  <text x="48" y="44" text-anchor="middle" font-family="Roboto,Arial,sans-serif" font-weight="800"
        font-size="34" fill="#ffffff" letter-spacing="-1">1<tspan fill="#2b9cf0">X</tspan></text>
  <text x="48" y="70" text-anchor="middle" font-family="Roboto,Arial,sans-serif" font-weight="700"
        font-size="20" fill="#cfe2f5" letter-spacing="3">BET</text>
</svg>'''

# Реальные ассеты (официальные, оптимизированы под веб в assets/). Иконка из Logo 1024,
# 6 скриншотов из ru/6_9_screen_*.png → assets/screenN.webp (640px, WebP q80).
ICON_HTML = '<img src="assets/icon.png" class="app-icon-svg" alt="1xBet" width="72" height="72">'
N_SCREENS = 6


def screen_svg(title, accent_rows, footer_label):
    """Мокап скриншота беттинг-приложения (портрет 9:16, тёмная навигация 1xBet)."""
    rows_svg = []
    y = 150
    for (lg, t1, t2, score, o1, ox, o2, live) in accent_rows:
        livebadge = ('<rect x="20" y="%d" width="34" height="15" rx="3" fill="#e23b3b"/>'
                     '<text x="37" y="%d" text-anchor="middle" font-family="Roboto" font-size="9" '
                     'font-weight="700" fill="#fff">LIVE</text>' % (y - 12, y - 1)) if live else (
                     '<text x="20" y="%d" font-family="Roboto" font-size="10" fill="#7d93ab">%s</text>' % (y - 1, lg))
        block = '''<g>
  {live}
  <text x="62" y="{ty1}" font-family="Roboto" font-size="12" font-weight="600" fill="#e7eef6">{t1}</text>
  <text x="62" y="{ty2}" font-family="Roboto" font-size="12" font-weight="600" fill="#e7eef6">{t2}</text>
  <text x="250" y="{ts}" text-anchor="middle" font-family="Roboto" font-size="13" font-weight="700" fill="#ffd166">{sc}</text>
  <g font-family="Roboto" font-size="11" font-weight="700">
    <rect x="20" y="{by}" width="80" height="30" rx="6" fill="#16314c"/>
    <text x="44" y="{bty}" font-size="9" fill="#7d93ab">1</text>
    <text x="80" y="{bty}" text-anchor="end" fill="#9fc4ff">{o1}</text>
    <rect x="108" y="{by}" width="80" height="30" rx="6" fill="#16314c"/>
    <text x="132" y="{bty}" font-size="9" fill="#7d93ab">X</text>
    <text x="180" y="{bty}" text-anchor="end" fill="#9fc4ff">{ox}</text>
    <rect x="196" y="{by}" width="80" height="30" rx="6" fill="#16314c"/>
    <text x="220" y="{bty}" font-size="9" fill="#7d93ab">2</text>
    <text x="268" y="{bty}" text-anchor="end" fill="#9fc4ff">{o2}</text>
  </g>
  <line x1="16" y1="{ln}" x2="280" y2="{ln}" stroke="#15293f" stroke-width="1"/>
</g>'''.format(live=livebadge, ty1=y - 14, ty2=y + 2, ts=y - 6, sc=score, t1=t1, t2=t2,
               by=y + 14, bty=y + 33, o1=o1, ox=ox, o2=o2, ln=y + 56)
        rows_svg.append(block)
        y += 78

    tabs = ["Live", "Линия", "Купон", "Промо"]
    tabs_svg = []
    tx = 18
    for i, tb in enumerate(tabs):
        col = "#2b9cf0" if i == 0 else "#7d93ab"
        wt = "700" if i == 0 else "500"
        tabs_svg.append('<text x="%d" y="118" font-family="Roboto" font-size="13" font-weight="%s" fill="%s">%s</text>' % (tx, wt, col, tb))
        if i == 0:
            tabs_svg.append('<rect x="%d" y="126" width="34" height="3" rx="1.5" fill="#2b9cf0"/>' % tx)
        tx += len(tb) * 11 + 26

    return '''<svg viewBox="0 0 296 568" xmlns="http://www.w3.org/2000/svg" class="shot-svg" role="img" aria-label="{title}">
  <rect width="296" height="568" rx="0" fill="#0d1b2a"/>
  <!-- status bar -->
  <text x="20" y="26" font-family="Roboto" font-size="12" font-weight="600" fill="#e7eef6">9:41</text>
  <g fill="#e7eef6"><rect x="248" y="16" width="16" height="10" rx="2"/><rect x="268" y="13" width="20" height="13" rx="3"/></g>
  <!-- app top bar -->
  <rect y="38" width="296" height="44" fill="#0a2540"/>
  <text x="20" y="66" font-family="Roboto" font-size="17" font-weight="800" fill="#fff">1<tspan fill="#2b9cf0">X</tspan>BET</text>
  <circle cx="248" cy="60" r="9" fill="none" stroke="#cfe2f5" stroke-width="2"/><line x1="255" y1="67" x2="262" y2="74" stroke="#cfe2f5" stroke-width="2"/>
  <g fill="#cfe2f5"><circle cx="278" cy="54" r="2"/><circle cx="278" cy="60" r="2"/><circle cx="278" cy="66" r="2"/></g>
  <!-- section title -->
  <text x="20" y="102" font-family="Roboto" font-size="15" font-weight="700" fill="#e7eef6">{title}</text>
  <!-- tabs -->
  {tabs}
  <line x1="0" y1="130" x2="296" y2="130" stroke="#15293f" stroke-width="1"/>
  {rows}
  <!-- bottom bar -->
  <rect y="524" width="296" height="44" fill="#0a2540"/>
  <text x="148" y="551" text-anchor="middle" font-family="Roboto" font-size="12" font-weight="700" fill="#2b9cf0">{footer}</text>
</svg>'''.format(title=title, tabs="\n  ".join(tabs_svg), rows="\n".join(rows_svg), footer=footer_label)


# наборы матчей под разные скрины
R_FOOT = [
    ("Футбол", "Реал Мадрид", "Барселона", "1:1", "2.10", "3.40", "3.25", True),
    ("Футбол", "Бавария", "Боруссия Д", "2:0", "1.55", "4.10", "5.20", True),
    ("Футбол", "Ливерпуль", "Арсенал", "0:0", "2.30", "3.10", "3.05", False),
    ("Футбол", "ПСЖ", "Марсель", "—", "1.40", "4.80", "6.50", False),
]
R_WC = [
    ("ЧМ-2026", "Аргентина", "Бразилия", "1:0", "2.45", "3.10", "2.80", True),
    ("ЧМ-2026", "Франция", "Англия", "1:1", "2.20", "3.30", "3.10", True),
    ("ЧМ-2026", "Испания", "Германия", "—", "2.05", "3.25", "3.40", False),
    ("ЧМ-2026", "Португалия", "Нидерланды", "—", "2.35", "3.20", "2.90", False),
]
R_LINE = [
    ("Футбол", "Манчестер С.", "Челси", "—", "1.65", "4.00", "4.50", False),
    ("Футбол", "Ювентус", "Интер", "—", "2.55", "3.05", "2.80", False),
    ("Футбол", "Атлетико", "Севилья", "—", "1.80", "3.40", "4.20", False),
    ("Футбол", "Наполи", "Рома", "—", "2.05", "3.20", "3.50", False),
]

SCREENS = [
    screen_svg("Live — сейчас идут", R_FOOT, "Тысячи событий в Live"),
    screen_svg("Чемпионат мира 2026", R_WC, "Все матчи турнира"),
    screen_svg("Линия — все события", R_LINE, "Высокие коэффициенты"),
]

# ──────────────────────────────────────────────────────────────────────────
# КОНФИГ ПО ГЕО
# ──────────────────────────────────────────────────────────────────────────
COMMON = dict(
    app_name="1xBet",
    app_subtitle="Ставки на спорт",
    developer="1XCorp N.V.",
    category="Спорт",
    rating="4,6",
    size="68 МБ",
    age="18+",
    updated="12 июня 2026 г.",
    # DEFAULT_URL — куда ведёт кнопка при пустом/кривом/некорректном URL (домен/тег слетел).
    # Финальный дефолтный URL от владельца (2026-06-17).
    fallback="https://refpa86112.pro/L?tag=s_5729865m_1524c_&site=5729865&ad=1524",
)

GEOS = {
    "kg": dict(
        app_name="1xBet Кыргызстан",
        reviews="128 тыс.",
        downloads="5 млн+",
        offer_short="120% до 35 000 KGS",
        bonus="Бонус новым игрокам — 120% на первый депозит до 35 000 KGS.",
        rev_reviews=[
            ("Адилет Ж.", "5", "9 июня 2026 г.", "Удобное приложение, ставлю на футбол каждый день. Коэффициенты выше, чем у других. Вывод быстрый.", "342"),
            ("Нурлан К.", "5", "4 июня 2026 г.", "Live-ставки и трансляции прямо в приложении — то что нужно. Депозит через MBank без проблем.", "211"),
            ("Тимур А.", "4", "28 мая 2026 г.", "Всё работает стабильно. Жду Чемпионат мира — рынков уже много. В целом доволен.", "97"),
        ],
    ),
    "tj": dict(
        app_name="1xBet Таджикистан",
        reviews="52 тыс.",
        downloads="1 млн+",
        offer_short="120% до 4 000 TJS",
        bonus="Бонус новым игрокам — 120% на первый депозит до 4 000 TJS.",
        rev_reviews=[
            ("Фаррух Р.", "5", "10 июня 2026 г.", "Беттинг қулай. Ставлю на Лигу чемпионов, коэффициенты хорошие. Пополнение через Корти Милли удобно.", "276"),
            ("Сухроб Н.", "5", "2 июня 2026 г.", "Лучшее приложение для ставок на спорт. Live работает быстро, трансляции не лагают.", "168"),
            ("Далер М.", "4", "25 мая 2026 г.", "Нормально всё. Иногда долго грузит линию, но коэффициенты и выбор событий радуют.", "84"),
        ],
    ),
}

ABOUT = (
    "1xBet — приложение для ставок на спорт. Тысячи событий каждый день, "
    "высокие коэффициенты, ставки в Live и прямые трансляции матчей. Футбол, "
    "хоккей, теннис, баскетбол, киберспорт и десятки других видов спорта. "
    "Главное событие лета — Чемпионат мира 2026: тысячи рынков на каждый матч, "
    "ставки в Live и трансляции. Удобный купон, быстрые депозиты и выводы "
    "через локальные платёжные системы."
)

# ──────────────────────────────────────────────────────────────────────────
# HTML-ШАБЛОН (токены %%NAME%%)
# ──────────────────────────────────────────────────────────────────────────
HTML = r'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" type="image/x-icon" href="%%FAVICON%%">
<title>%%APP_NAME%% — Apps on Google Play</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
  :root{
    --green:#01875f; --green-d:#016b4c;
    --ink:#202124; --muted:#5f6368; --hair:#dadce0;
    --surface:#ffffff; --card:#f1f3f4;
    --maxw:480px;
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;padding:0}
  body{font-family:Roboto,Arial,sans-serif;color:var(--ink);background:#fff;
    -webkit-font-smoothing:antialiased;line-height:1.45}
  .wrap{max-width:var(--maxw);margin:0 auto;background:#fff;min-height:100vh;position:relative;padding-bottom:84px}
  a{color:var(--green);text-decoration:none}

  /* top app bar */
  .appbar{position:sticky;top:0;z-index:30;height:56px;display:flex;align-items:center;
    gap:18px;padding:0 16px;background:#fff;border-bottom:1px solid transparent;transition:box-shadow .2s,border-color .2s}
  .appbar.solid{box-shadow:0 1px 2px rgba(60,64,67,.15);border-color:var(--hair)}
  .appbar .back{width:24px;height:24px;flex:0 0 auto}
  .appbar .gp{display:flex;align-items:center;gap:8px;font-size:18px;font-weight:500;color:#5f6368;
    opacity:0;transform:translateX(-6px);transition:opacity .2s,transform .2s}
  .appbar.solid .gp{opacity:1;transform:none}
  .appbar .sp{flex:1}
  .appbar .ic{width:22px;height:22px;color:#5f6368;flex:0 0 auto}
  .gp-logo{width:22px;height:22px}

  /* header */
  .head{padding:20px 24px 8px;display:flex;gap:18px;align-items:flex-start}
  .app-icon{width:72px;height:72px;border-radius:18px;overflow:hidden;flex:0 0 auto;
    box-shadow:0 1px 3px rgba(60,64,67,.25)}
  .app-icon-svg{width:100%;height:100%;display:block}
  .head .meta{min-width:0;flex:1;padding-top:2px}
  .app-title{font-size:24px;font-weight:500;line-height:1.2;margin:0 0 4px;color:var(--ink)}
  .app-dev{font-size:14px;font-weight:500;color:var(--green);margin:0}
  .app-sub{font-size:12px;color:var(--muted);margin:3px 0 0}

  /* metrics */
  .metrics{display:flex;padding:18px 8px 6px;margin:0 16px}
  .metric{flex:1;text-align:center;padding:0 4px;position:relative}
  .metric+.metric::before{content:"";position:absolute;left:0;top:6px;bottom:6px;width:1px;background:var(--hair)}
  .metric .v{font-size:14px;font-weight:600;color:var(--ink);display:flex;align-items:center;justify-content:center;gap:4px}
  .metric .c{font-size:11px;color:var(--muted);margin-top:3px;line-height:1.3}
  .metric .star{width:13px;height:13px;fill:var(--ink)}
  .age-badge{display:inline-flex;align-items:center;justify-content:center;min-width:20px;height:18px;
    padding:0 4px;border:1.5px solid var(--muted);border-radius:3px;font-size:11px;font-weight:700;color:var(--ink)}
  .dl-ic{width:13px;height:13px;fill:var(--ink)}

  /* install */
  .install-wrap{padding:14px 24px 6px}
  .btn-install{display:flex;align-items:center;justify-content:center;height:42px;border-radius:21px;
    background:var(--green);color:#fff;font-size:15px;font-weight:500;width:100%;border:none;
    letter-spacing:.2px;transition:background .15s, transform .06s}
  .btn-install:active{background:var(--green-d);transform:scale(.99)}
  .device-line{display:flex;align-items:center;gap:8px;justify-content:center;color:var(--muted);
    font-size:12px;margin:12px 0 0}
  .device-line svg{width:15px;height:15px;fill:var(--muted)}

  /* screenshots */
  .shots{display:flex;gap:10px;overflow-x:auto;padding:18px 24px 6px;scroll-snap-type:x mandatory;
    -webkit-overflow-scrolling:touch}
  .shots::-webkit-scrollbar{display:none}
  .shot{flex:0 0 auto;width:160px;height:347px;border-radius:10px;overflow:hidden;scroll-snap-align:start;
    border:1px solid #eceff1;background:#0d1b2a}
  .shot-svg{width:100%;height:100%;display:block;object-fit:cover}

  /* sections */
  .sec{padding:22px 24px 6px}
  .sec h2{font-size:18px;font-weight:500;margin:0 0 10px;display:flex;align-items:center;justify-content:space-between}
  .sec h2 .arr{width:20px;height:20px;fill:var(--muted)}
  .about{font-size:14px;color:#3c4043;margin:0}
  .chips{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 4px}
  .chip{font-size:12px;color:var(--muted);border:1px solid var(--hair);border-radius:8px;padding:6px 12px}
  .updated{font-size:12px;color:var(--muted);margin:14px 0 0}
  .bonus-note{font-size:13px;color:#3c4043;background:var(--card);border-radius:10px;padding:12px 14px;margin:14px 0 0}

  /* data safety */
  .ds-card{background:var(--card);border-radius:12px;padding:14px 16px}
  .ds-row{display:flex;gap:12px;align-items:flex-start;padding:8px 0;font-size:13px;color:#3c4043}
  .ds-row+.ds-row{border-top:1px solid #e4e7e9}
  .ds-row svg{width:18px;height:18px;fill:var(--muted);flex:0 0 auto;margin-top:1px}

  /* ratings */
  .rate-top{display:flex;gap:22px;align-items:center;margin-bottom:8px}
  .rate-big{font-size:52px;font-weight:500;line-height:1;color:var(--ink)}
  .rate-big .o{font-size:18px;color:var(--muted)}
  .rate-stars{display:flex;gap:2px;margin:6px 0 4px}
  .rate-stars svg{width:14px;height:14px;fill:var(--green)}
  .rate-count{font-size:12px;color:var(--muted)}
  .hist{flex:1}
  .hbar{display:flex;align-items:center;gap:8px;margin:2px 0}
  .hbar .n{font-size:12px;color:var(--muted);width:8px;text-align:right}
  .hbar .track{flex:1;height:8px;background:#e4e7e9;border-radius:4px;overflow:hidden}
  .hbar .fill{height:100%;background:var(--green);border-radius:4px}

  .review{padding:16px 0;border-top:1px solid var(--hair)}
  .rv-head{display:flex;align-items:center;gap:12px}
  .rv-av{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;
    color:#fff;font-size:16px;font-weight:500;flex:0 0 auto}
  .rv-name{font-size:13px;font-weight:500;color:var(--ink)}
  .rv-stars{display:flex;gap:1px;margin:6px 0 4px}
  .rv-stars svg{width:13px;height:13px;fill:var(--green)}
  .rv-date{font-size:12px;color:var(--muted)}
  .rv-text{font-size:13px;color:#3c4043;margin:4px 0 8px}
  .rv-help{font-size:12px;color:var(--muted)}

  .wn-ver{font-size:12px;color:var(--muted);margin:0 0 6px}
  .wn-text{font-size:14px;color:#3c4043;margin:0}

  .foot{padding:24px;color:var(--muted);font-size:11px;border-top:1px solid var(--hair);margin-top:18px}

  /* sticky install on scroll */
  .sticky{position:fixed;left:0;right:0;bottom:0;z-index:40;background:#fff;
    border-top:1px solid var(--hair);box-shadow:0 -1px 4px rgba(60,64,67,.12);
    transform:translateY(110%);transition:transform .25s ease-out}
  .sticky.show{transform:none}
  .sticky-in{max-width:var(--maxw);margin:0 auto;display:flex;align-items:center;gap:14px;padding:10px 16px;
    padding-bottom:calc(10px + env(safe-area-inset-bottom))}
  .sticky .si-ic{width:40px;height:40px;border-radius:10px;overflow:hidden;flex:0 0 auto}
  .sticky .si-meta{flex:1;min-width:0}
  .sticky .si-name{font-size:13px;font-weight:500;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .sticky .si-sub{font-size:11px;color:var(--muted)}
  .sticky .btn-install{width:auto;padding:0 26px}

  /* promo popup (lightweight, no deps) */
  .promo{position:fixed;inset:0;z-index:60;display:flex;align-items:flex-end;justify-content:center;
    background:rgba(20,24,28,.55);opacity:0;transition:opacity .25s ease-out}
  .promo.show{opacity:1}
  .promo[hidden]{display:none}
  .promo-card{width:100%;max-width:var(--maxw);background:#fff;border-radius:20px 20px 0 0;
    padding:26px 24px calc(22px + env(safe-area-inset-bottom));text-align:center;position:relative;
    transform:translateY(20px);transition:transform .25s ease-out}
  .promo.show .promo-card{transform:none}
  .promo-x{position:absolute;top:12px;right:14px;width:30px;height:30px;border:none;background:var(--card);
    border-radius:50%;color:var(--muted);font-size:18px;line-height:1;cursor:pointer}
  .promo-kick{font-size:13px;color:var(--muted);font-weight:500}
  .promo-amt{font-size:30px;font-weight:700;color:var(--ink);margin:6px 0 2px;letter-spacing:-.5px}
  .promo-amt b{color:var(--green)}
  .promo-sub{font-size:13px;color:#3c4043;margin:0 0 18px}
  .promo-cta{margin-top:2px}
  .promo-tc{font-size:11px;color:var(--muted);margin-top:12px}
  @media (prefers-reduced-motion: reduce){
    .promo,.promo-card,.sticky{transition:none}
  }
</style>
</head>
<body>
<div class="wrap">

  <!-- TOP APP BAR -->
  <header class="appbar" id="appbar">
    <svg class="back" viewBox="0 0 24 24" fill="#5f6368"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20z"/></svg>
    <div class="gp">
      <svg class="gp-logo" viewBox="0 0 24 24"><path d="M3.6 2.3 13 12 3.6 21.7c-.4-.2-.6-.6-.6-1.1V3.4c0-.5.2-.9.6-1.1z" fill="#00c3ff"/><path d="M16.8 8.6 13 12l3.8 3.4 3.4-1.9c.9-.5.9-1.5 0-2L16.8 8.6z" fill="#ffc400"/><path d="M3.6 2.3 13 12l3.8-3.4L6 2.5c-.9-.5-1.8-.4-2.4-.2z" fill="#00e676"/><path d="M3.6 21.7 13 12l3.8 3.4L6 21.5c-.9.5-1.8.4-2.4.2z" fill="#ff3d57"/></svg>
      <span>Google Play</span>
    </div>
    <div class="sp"></div>
    <svg class="ic" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 10-.7.7l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0A4.5 4.5 0 1114 9.5 4.49 4.49 0 019.5 14z"/></svg>
    <svg class="ic" viewBox="0 0 24 24" fill="currentColor"><path d="M12 8a2 2 0 10-2-2 2 2 0 002 2zm0 2a2 2 0 102 2 2 2 0 00-2-2zm0 6a2 2 0 102 2 2 2 0 00-2-2z"/></svg>
  </header>

  <!-- HEADER -->
  <section class="head">
    <!-- Иконка: assets/icon.png (официальный логотип, 144px). Заменить — положить новый icon.png -->
    <div class="app-icon">%%ICON_SVG%%</div>
    <div class="meta">
      <h1 class="app-title">%%APP_NAME%%</h1>
      <p class="app-dev">%%DEVELOPER%%</p>
      <p class="app-sub">Контент: реклама · Покупки в приложении</p>
    </div>
  </section>

  <!-- METRICS -->
  <section class="metrics">
    <div class="metric">
      <div class="v">%%RATING%% <svg class="star" viewBox="0 0 24 24"><path d="M12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg></div>
      <div class="c">%%REVIEWS%% отзывов</div>
    </div>
    <div class="metric">
      <div class="v">%%DOWNLOADS%%</div>
      <div class="c">Загрузки</div>
    </div>
    <div class="metric">
      <div class="v"><span class="age-badge">%%AGE%%</span></div>
      <div class="c">Старше 18&#160;лет&#160;<span style="font-size:10px">&#9432;</span></div>
    </div>
  </section>

  <!-- INSTALL -->
  <section class="install-wrap">
    <a class="btn-install" data-install href="%%FALLBACK%%" rel="nofollow noopener">Установить</a>
    <div class="device-line">
      <svg viewBox="0 0 24 24"><path d="M17 1.01 7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>
      <span>Установить на устройство Android</span>
    </div>
  </section>

  <!-- SCREENSHOTS: assets/screen1..6.webp (официальные, 640px, lazy-load кроме первого) -->
  <section class="shots" aria-label="Скриншоты">
    %%SCREENS%%
  </section>

  <!-- ABOUT -->
  <section class="sec">
    <h2>Об этом приложении <svg class="arr" viewBox="0 0 24 24"><path d="M8.59 16.59 13.17 12 8.59 7.41 10 6l6 6-6 6z"/></svg></h2>
    <p class="about">%%ABOUT%%</p>
    <p class="bonus-note">%%BONUS%%</p>
    <div class="chips"><span class="chip">%%CATEGORY%%</span><span class="chip">Ставки</span><span class="chip">Live</span><span class="chip">Чемпионат мира 2026</span></div>
    <p class="updated">Обновлено: %%UPDATED%%</p>
  </section>

  <!-- DATA SAFETY -->
  <section class="sec">
    <h2>Безопасность данных <svg class="arr" viewBox="0 0 24 24"><path d="M8.59 16.59 13.17 12 8.59 7.41 10 6l6 6-6 6z"/></svg></h2>
    <div class="ds-card">
      <div class="ds-row"><svg viewBox="0 0 24 24"><path d="M12 1 3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg><span>Разработчик заявляет, что не передаёт данные третьим сторонам</span></div>
      <div class="ds-row"><svg viewBox="0 0 24 24"><path d="M18 8h-1V6A5 5 0 007 6v2H6a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V10a2 2 0 00-2-2zM9 6a3 3 0 016 0v2H9z"/></svg><span>Данные шифруются при передаче</span></div>
      <div class="ds-row"><svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg><span>Вы можете запросить удаление данных</span></div>
    </div>
  </section>

  <!-- RATINGS -->
  <section class="sec">
    <h2>Оценки и отзывы <svg class="arr" viewBox="0 0 24 24"><path d="M8.59 16.59 13.17 12 8.59 7.41 10 6l6 6-6 6z"/></svg></h2>
    <div class="rate-top">
      <div>
        <div class="rate-big">%%RATING%%<span class="o">/5</span></div>
        <div class="rate-stars">%%STARS5%%</div>
        <div class="rate-count">%%REVIEWS%% отзывов</div>
      </div>
      <div class="hist">
        <div class="hbar"><span class="n">5</span><div class="track"><div class="fill" style="width:82%"></div></div></div>
        <div class="hbar"><span class="n">4</span><div class="track"><div class="fill" style="width:11%"></div></div></div>
        <div class="hbar"><span class="n">3</span><div class="track"><div class="fill" style="width:4%"></div></div></div>
        <div class="hbar"><span class="n">2</span><div class="track"><div class="fill" style="width:1.5%"></div></div></div>
        <div class="hbar"><span class="n">1</span><div class="track"><div class="fill" style="width:2%"></div></div></div>
      </div>
    </div>
    %%REVIEWS_HTML%%
  </section>

  <!-- WHAT'S NEW -->
  <section class="sec">
    <h2>Что нового <svg class="arr" viewBox="0 0 24 24"><path d="M8.59 16.59 13.17 12 8.59 7.41 10 6l6 6-6 6z"/></svg></h2>
    <p class="wn-ver">Версия 142.1 · %%UPDATED%%</p>
    <p class="wn-text">Готовимся к Чемпионату мира 2026: добавили специальные рынки и разделы под турнир. Ускорили загрузку Live-линии и трансляций. Улучшили стабильность депозитов и выводов. Исправили мелкие ошибки.</p>
  </section>

  <div class="foot">
    Эта страница оформлена в стиле магазина приложений и предназначена для установки приложения по прямой ссылке.
    %%APP_NAME%% — букмекерское приложение. 18+. Играйте ответственно.
  </div>
</div>

<!-- STICKY INSTALL -->
<div class="sticky" id="sticky">
  <div class="sticky-in">
    <div class="si-ic">%%ICON_SVG%%</div>
    <div class="si-meta">
      <div class="si-name">%%APP_NAME%%</div>
      <div class="si-sub">%%RATING%% ★ · %%DOWNLOADS%%</div>
    </div>
    <a class="btn-install" data-install href="%%FALLBACK%%" rel="nofollow noopener">Установить</a>
  </div>
</div>

<!-- PROMO POPUP (показывается через POPUP_DELAY_MS, см. скрипт) -->
<div class="promo" id="promo" role="dialog" aria-modal="true" aria-label="Бонус" hidden>
  <div class="promo-card">
    <button class="promo-x" id="promoX" aria-label="Закрыть">&times;</button>
    <div class="promo-kick">Бонус новым игрокам</div>
    <div class="promo-amt"><b>%%OFFER_SHORT%%</b></div>
    <div class="promo-sub">на первый депозит&#160;·&#160;ставки на Чемпионат мира 2026</div>
    <a class="btn-install promo-cta" data-install href="%%FALLBACK%%" rel="nofollow noopener">Установить и забрать</a>
    <div class="promo-tc">18+. Играйте ответственно</div>
  </div>
</div>

<script>
(function(){
  /* ── Динамическая сборка трекинг-ссылки из UTM-меток ──
     Вход:  ?domain=reffpa.com/L&tag=...&pb=...&click_id={clickid}
     Выход: https://reffpa.com/L?tag=...&pb=...&click_id={clickid}
     tag / pb / click_id передаются СЫРЫМИ (скобки [] и макрос {clickid} не трогаем).
     Любой кривой / некорректный вход → DEFAULT_URL (заглушка). */
  var DEFAULT_URL = "%%DEFAULT_URL%%";
  function buildTarget(){
    try{
      var qs = (window.location.search || "").replace(/^\?/, "");
      if(!qs) return DEFAULT_URL;                       // меток нет
      var parts = qs.split("&"), domain = "", rest = [];
      for(var i=0;i<parts.length;i++){
        var p = parts[i]; if(!p) continue;
        var eq = p.indexOf("="), key = eq>=0 ? p.slice(0,eq) : p;
        if(key === "domain"){ domain = decodeURIComponent(p.slice(eq+1)); }
        else if(key === "geo"){ /* служебный, пропускаем */ }
        else { rest.push(p); }          /* сырой кусок — без перекодирования */
      }
      domain = (domain || "").trim();
      /* домен обязателен, без пробелов, с точкой (валидный host[/path]) */
      if(!domain || /\s/.test(domain) || domain.indexOf(".") === -1) return DEFAULT_URL;
      var url = "https://" + domain + (rest.length ? "?" + rest.join("&") : "");
      new URL(url);                       /* финальная проверка — кинет на мусоре */
      return url;
    } catch(e){
      return DEFAULT_URL;                 // любая ошибка парсинга → заглушка
    }
  }
  var target = buildTarget();
  var btns = document.querySelectorAll("[data-install]");
  for(var j=0;j<btns.length;j++){ btns[j].setAttribute("href", target); }

  /* ── App bar тень + sticky install при скролле ── */
  var appbar = document.getElementById("appbar");
  var sticky = document.getElementById("sticky");
  function onScroll(){
    var y = window.pageYOffset || document.documentElement.scrollTop;
    if(y > 8){ appbar.classList.add("solid"); } else { appbar.classList.remove("solid"); }
    if(y > 320){ sticky.classList.add("show"); } else { sticky.classList.remove("show"); }
  }
  window.addEventListener("scroll", onScroll, {passive:true});
  onScroll();

  /* ── Промо-поп-ап после задержки (лёгкий, без зависимостей, показ один раз) ── */
  var POPUP_DELAY_MS = 120000;          /* 2 минуты; правится здесь */
  var promo = document.getElementById("promo");
  if(promo){
    var shown = false;
    function showPromo(){
      if(shown) return; shown = true; promo.hidden = false;
      requestAnimationFrame(function(){ promo.classList.add("show"); });
    }
    function hidePromo(){
      promo.classList.remove("show");
      setTimeout(function(){ promo.hidden = true; }, 260);
    }
    setTimeout(showPromo, POPUP_DELAY_MS);
    document.getElementById("promoX").addEventListener("click", hidePromo);
    promo.addEventListener("click", function(e){ if(e.target === promo) hidePromo(); });
  }
})();
</script>
</body>
</html>'''


def star_row(n, cls="rate-stars"):
    s = '<svg viewBox="0 0 24 24"><path d="M12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>'
    return s * n


AV_COLORS = ["#5e97f6", "#e06055", "#33a474", "#9c6ade", "#f0a93b"]


def reviews_html(revs):
    out = []
    for i, (name, stars, date, text, helpful) in enumerate(revs):
        col = AV_COLORS[i % len(AV_COLORS)]
        out.append('''<div class="review">
  <div class="rv-head">
    <div class="rv-av" style="background:{col}">{ini}</div>
    <div><div class="rv-name">{name}</div></div>
  </div>
  <div class="rv-stars">{stars}</div><span class="rv-date">{date}</span>
  <p class="rv-text">{text}</p>
  <div class="rv-help">Полезно? · {help} человек считают, что да</div>
</div>'''.format(col=col, ini=name[0], name=name, stars=star_row(int(stars)), date=date, text=text, help=helpful))
    return "\n".join(out)


def render(geo):
    cfg = dict(COMMON); cfg.update(GEOS[geo])
    html = HTML
    repl = {
        "%%APP_NAME%%": cfg["app_name"],
        "%%DEVELOPER%%": cfg["developer"],
        "%%CATEGORY%%": cfg["category"],
        "%%RATING%%": cfg["rating"],
        "%%REVIEWS%%": cfg["reviews"],
        "%%DOWNLOADS%%": cfg["downloads"],
        "%%AGE%%": cfg["age"],
        "%%SIZE%%": cfg["size"],
        "%%UPDATED%%": cfg["updated"],
        "%%FALLBACK%%": cfg["fallback"],
        "%%DEFAULT_URL%%": cfg["fallback"],
        "%%FAVICON%%": FAVICON_DATA_URI,
        "%%OFFER_SHORT%%": cfg["offer_short"],
        "%%ABOUT%%": ABOUT,
        "%%BONUS%%": cfg["bonus"],
        "%%ICON_SVG%%": ICON_HTML,
        "%%SCREENS%%": "\n    ".join(
            '<div class="shot"><img src="assets/screen%d.webp" class="shot-svg" alt="Скриншот %d 1xBet" '
            'width="160" height="347"%s></div>' % (i, i, '' if i == 1 else ' loading="lazy" decoding="async"')
            for i in range(1, N_SCREENS + 1)),
        "%%STARS5%%": star_row(5),
        "%%REVIEWS_HTML%%": reviews_html(cfg["rev_reviews"]),
    }
    for k, v in repl.items():
        html = html.replace(k, v)
    return html


def main():
    for geo in ("kg", "tj"):
        path = os.path.join(OUT_DIR, "1xbet_%s.html" % geo)
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(geo))
        print("OK  %s  (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()

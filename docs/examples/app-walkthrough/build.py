#!/usr/bin/env python3
"""Builds the HyperFrames walkthrough from script.json + per-scene voiceover WAVs.

Outputs (all under video/): assets/narration.wav, assets/screens/*.jpg, timeline.json, index.html.
Captions are timed per phrase: the phrase boundaries are snapped to the pauses detected in each
scene's voiceover, so they follow the real voice rather than a words-per-minute guess.
"""
import json, re, subprocess, wave, html, pathlib, shutil
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
VIDEO = ROOT / 'video'
TTS = ROOT / 'build' / 'tts'
SCREENS_SRC = ROOT / 'assets' / 'screens'
SR = 24000
LEAD = 0.55      # silence before each scene's voice starts
TAIL = 0.65      # hold after the voice ends, before the next scene
XFADE = 0.5      # scene crossfade overlap
INTRO_LEAD = 1.4
OUTRO_TAIL = 3.0

script = json.loads((ROOT / 'script.json').read_text())
scenes = script['scenes']

def wav_info(p):
    with wave.open(str(p)) as w:
        return w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes() / w.getframerate()

def silences(p):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(p), '-af', 'silencedetect=noise=-32dB:d=0.18', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
    return [((a + b) / 2, b - a) for a, b in zip(st, en)]

def phrases(text):
    """Caption phrases: split at sentence ends, then long sentences at commas / colons, 5-15 words each."""
    sents = re.split(r'(?<=[.?!])\s+', text.strip())
    out = []
    for s in sents:
        parts = re.split(r'(?<=[,:])\s+', s)
        cur = ''
        for part in parts:
            cand = (cur + ' ' + part).strip()
            if cur and len(cand.split()) > 15:
                out.append(cur); cur = part
            else:
                cur = cand
        if cur:
            if out and len(cur.split()) < 4 and not re.search(r'[.?!]$', out[-1]):
                out[-1] += ' ' + cur
            else:
                out.append(cur)
    return out

def time_phrases(text, wav):
    dur = wav_info(wav)[3]
    sil = [s for s in silences(wav) if 0.3 < s[0] < dur - 0.3]
    ph = phrases(text)
    total = sum(len(p) for p in ph)
    bounds, acc, used = [], 0, set()
    for p in ph[:-1]:
        acc += len(p)
        guess = dur * acc / total
        best = None
        for i, (mid, length) in enumerate(sil):
            if i in used: continue
            d = abs(mid - guess)
            if d < 1.3 and (best is None or d - 0.25 * length < best[0]):
                best = (d - 0.25 * length, i, mid)
        if best:
            used.add(best[1]); bounds.append(best[2])
        else:
            bounds.append(guess)
    bounds = sorted(bounds)
    starts = [0.0] + bounds
    ends = bounds + [dur]
    caps = [{'text': t, 'a': a, 'b': b} for t, a, b in zip(ph, starts, ends)]
    floor = lambda c: 0.5 + 0.3 * len(c['text'].split())
    while len(caps) > 1:
        short = [i for i, c in enumerate(caps) if c['b'] - c['a'] < floor(c)]
        if not short: break
        i = short[0]
        j = i - 1 if i == len(caps) - 1 else (i + 1 if i == 0 else (i - 1 if (caps[i-1]['b'] - caps[i-1]['a']) < (caps[i+1]['b'] - caps[i+1]['a']) else i + 1))
        a, b = sorted((i, j))
        merged = {'text': caps[a]['text'] + ' ' + caps[b]['text'], 'a': caps[a]['a'], 'b': caps[b]['b']}
        if len(merged['text'].split()) > 26: break
        caps[a:b + 1] = [merged]
    return [{'text': c['text'], 'a': round(c['a'], 3), 'b': round(c['b'], 3)} for c in caps]

# ---- screens as JPEG (smaller, faster to decode at render time)
dst = VIDEO / 'assets' / 'screens'
dst.mkdir(parents=True, exist_ok=True)
needed = sorted({s for sc in scenes for s in sc['shots']})
for name in needed:
    out = dst / f'{name}.jpg'
    if not out.exists():
        Image.open(SCREENS_SRC / f'{name}.png').convert('RGB').save(out, quality=90)

# ---- timeline + narration
t = 0.0
timeline = []
pcm = bytearray()
def silence(sec): return b'\x00\x00' * int(round(sec * SR))
for i, sc in enumerate(scenes):
    wav = TTS / f"{sc['id']}.wav"
    sr, ch, sw, vdur = wav_info(wav)
    assert sr == SR and ch == 1 and sw == 2, (wav, sr, ch, sw)
    lead = INTRO_LEAD if i == 0 else LEAD
    tail = OUTRO_TAIL if i == len(scenes) - 1 else TAIL
    start = t
    voice = start + lead
    length = lead + vdur + tail
    caps = [{**c, 'a': round(voice + c['a'], 3), 'b': round(voice + c['b'], 3)} for c in time_phrases(sc['narration'], wav)]
    caps[-1]['b'] = round(start + length - 0.02, 3)  # the last line stays up through the scene's tail
    timeline.append({**sc, 'start': round(start, 3), 'voice': round(voice, 3), 'vdur': round(vdur, 3), 'dur': round(length, 3), 'captions': caps})
    # audio: pad so the voice lands at `voice`
    need = int(round(voice * SR)) - len(pcm) // 2
    pcm += silence(need / SR)
    with wave.open(str(wav)) as w:
        pcm += w.readframes(w.getnframes())
    t = start + length - (XFADE if i < len(scenes) - 1 else 0)
total = round(timeline[-1]['start'] + timeline[-1]['dur'], 3)
pcm += silence(max(0, total - len(pcm) / 2 / SR))
raw = VIDEO / 'assets' / 'narration_raw.wav'
with wave.open(str(raw), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(pcm))
# Gentle polish: high-pass, light compression, loudness to -16 LUFS (speech), 48 kHz.
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(raw), '-af',
                'highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=9',
                '-ar', '48000', str(VIDEO / 'assets' / 'narration.wav')], check=True)
raw.unlink()
(VIDEO / 'timeline.json').write_text(json.dumps({'total': total, 'scenes': timeline}, indent=1))
print(f'total {total:.1f}s ({total/60:.2f} min), {len(timeline)} scenes')

# ---- HTML
E = html.escape
def title_html(t):
    return ''.join(f'<span class="tl">{E(line)}</span>' for line in t.split('\n'))

sections = []
for i, sc in enumerate(timeline):
    kind = 'bookend' if sc['id'] in ('intro', 'outro') else 'chapter'
    sid = f"sc-{sc['id']}"
    suffix = '_b' if sc['id'] in ('intro', 'outro') else ''
    for s_ in sc['shots']:
        if suffix and not (dst / f'{s_}{suffix}.jpg').exists(): shutil.copy(dst / f'{s_}.jpg', dst / f'{s_}{suffix}.jpg')
    shots = ''.join(f'<img class="shot" id="{sid}-shot{j}" src="assets/screens/{s}{suffix}.jpg" alt="">' for j, s in enumerate(sc['shots']))
    ghost = E(sc['title'].split('\n')[0].split(' —')[0].split(' &')[0].upper())
    if kind == 'chapter':
        pts = ''.join(f'<li class="pt" id="{sid}-pt{j}"><span class="dot"></span><span class="ptx">{E(p)}</span></li>' for j, p in enumerate(sc['points']))
        left = f'''
        <div class="eyebrow" id="{sid}-eb" data-layout-allow-overlap><span class="num">{sc['chapter']}</span><span class="rule"></span><span class="of">of 17</span></div>
        <h2 class="title" id="{sid}-title">{title_html(sc['title'])}</h2>
        <ul class="pts">{pts}</ul>'''
    else:
        chips = ''.join(f'<span class="chip" id="{sid}-chip{j}">{E(p)}</span>' for j, p in enumerate(sc['points']))
        kicker = 'A complete walkthrough' if sc['id'] == 'intro' else 'One app · every desk in the unit'
        left = f'''
        <div class="kicker" id="{sid}-kicker">{kicker}</div>
        <h1 class="big" id="{sid}-title">{title_html(sc['title'])}</h1>
        <div class="chips">{chips}</div>'''
    sections.append(f'''
    <section class="clip scene {kind}" id="{sid}" data-start="{sc['start']}" data-duration="{sc['dur']}" data-track-index="1">
      <div class="inner" id="{sid}-inner">
        <div class="ghost" id="{sid}-ghost">{ghost}</div>
        <div class="left">{left}</div>
        <div class="phone-wrap" id="{sid}-phonewrap">
          <div class="phone" id="{sid}-phone"><div class="screen"><div class="status" data-layout-ignore data-layout-allow-occlusion><span class="clock" data-layout-ignore>9:41</span><span class="cam"></span><span class="sig"><i></i><i></i><i></i><i></i></span></div><div class="shots">{shots}</div></div></div>
        </div>
      </div>
    </section>''')

caps = []
for sc in timeline:
    for k, c in enumerate(sc['captions']):
        caps.append(f'<div class="clip cap" id="cap-{sc["id"]}-{k}" data-start="{c["a"]}" data-duration="{round(c["b"] - c["a"], 3)}" data-track-index="3"><span class="capx">{E(c["text"])}</span></div>')

DATA = json.dumps([{'id': s['id'], 'kind': 'bookend' if s['id'] in ('intro', 'outro') else 'chapter', 'start': s['start'], 'voice': s['voice'],
                    'vdur': s['vdur'], 'dur': s['dur'], 'shots': len(s['shots']), 'points': len(s['points']), 'chapter': s['chapter']} for s in timeline])

page = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Garment unit walkthrough</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      :root {{
        --ground: #15120d;
        --ground-2: #1e1a12;
        --ink: #faf4e6;
        --muted: #b9ad94;
        --gold: #d4af37;
        --gold-soft: #e8cf7a;
        --font-display: 'Montserrat', sans-serif;
        --font-serif: 'EB Garamond', serif;
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: var(--ground); }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; font-family: var(--font-display); color: var(--ink); }}
      /* persistent backdrop */
      .bg {{ position: absolute; inset: 0; overflow: hidden; background: radial-gradient(120% 90% at 70% 50%, var(--ground-2) 0%, var(--ground) 62%); }}
      .glow {{ position: absolute; border-radius: 50%; filter: blur(30px); }}
      #glow-a {{ width: 1100px; height: 1100px; left: 860px; top: -40px; background: radial-gradient(circle, rgba(212,175,55,0.17) 0%, rgba(212,175,55,0) 62%); }}
      #glow-b {{ width: 900px; height: 900px; left: -260px; top: 420px; background: radial-gradient(circle, rgba(212,175,55,0.08) 0%, rgba(212,175,55,0) 65%); }}
      .threads {{ position: absolute; inset: -200px; opacity: 0.07;
        background-image: repeating-linear-gradient(115deg, var(--gold) 0 1px, transparent 1px 46px); }}
      .scene {{ position: absolute; inset: 0; }}
      .inner {{ position: absolute; inset: 0; }}
      .ghost {{ position: absolute; left: 90px; top: 610px; width: 1700px; font-weight: 900; font-size: 300px; line-height: 1; letter-spacing: -0.04em;
        color: var(--ink); opacity: 0.035; white-space: nowrap; }}
      .left {{ position: absolute; left: 150px; top: 150px; width: 900px; }}
      .eyebrow {{ display: flex; align-items: center; gap: 22px; font-family: var(--font-serif); font-style: italic; color: var(--gold); font-size: 40px; }}
      .eyebrow .num {{ font-style: normal; font-weight: 600; font-size: 54px; letter-spacing: 0.02em; }}
      .eyebrow .rule {{ display: block; width: 120px; height: 2px; background: var(--gold); opacity: 0.7; }}
      .eyebrow .of {{ font-size: 30px; color: var(--muted); }}
      .title {{ margin-top: 26px; font-weight: 800; font-size: 82px; line-height: 1.04; letter-spacing: -0.025em; }}
      .tl {{ display: block; }}
      .pts {{ list-style: none; margin-top: 52px; }}
      .pt {{ display: flex; align-items: center; gap: 22px; height: 70px; font-size: 32px; font-weight: 500; color: var(--ink); }}
      .pt .dot {{ display: block; width: 14px; height: 14px; border-radius: 50%; background: var(--gold); flex: 0 0 14px; }}
      .kicker {{ font-family: var(--font-serif); font-style: italic; font-size: 44px; color: var(--gold); }}
      .big {{ margin-top: 22px; width: 1020px; font-weight: 900; font-size: 96px; line-height: 1.02; letter-spacing: -0.035em; }}
      .chips {{ display: flex; flex-wrap: wrap; gap: 16px; margin-top: 56px; width: 860px; }}
      .chip {{ display: block; padding: 14px 28px; border: 2px solid rgba(212,175,55,0.55); border-radius: 999px; font-size: 28px; font-weight: 600; color: var(--gold-soft); background: rgba(212,175,55,0.07); }}
      .phone-wrap {{ position: absolute; left: 1222px; top: 62px; width: 500px; height: 990px; }}
      .phone {{ position: absolute; inset: 0; border-radius: 74px; background: #0c0b08; padding: 18px;
        box-shadow: 0 0 0 2px rgba(232,207,122,0.55), 0 0 0 9px #26211a, 0 40px 90px rgba(0,0,0,0.55), 0 0 120px rgba(212,175,55,0.16); }}
      .screen {{ position: relative; width: 464px; height: 954px; border-radius: 58px; overflow: hidden; background: #faf7f0; }}
      .shot {{ position: absolute; left: 0; top: 0; width: 464px; height: 1004px; object-fit: cover; object-position: top; }}
      .status {{ position: absolute; left: 0; top: 0; width: 464px; height: 46px; background: #0b0b0c; display: flex; align-items: center; justify-content: space-between; padding: 0 34px; }}
      .clock {{ display: block; font-size: 17px; font-weight: 700; color: #faf4e6; }}
      .cam {{ display: block; width: 96px; height: 26px; border-radius: 14px; background: #000; }}
      .sig {{ display: flex; align-items: flex-end; gap: 3px; height: 14px; }}
      .sig i {{ display: block; width: 4px; background: #faf4e6; border-radius: 1px; }}
      .sig i:nth-child(1) {{ height: 5px; }} .sig i:nth-child(2) {{ height: 8px; }} .sig i:nth-child(3) {{ height: 11px; }} .sig i:nth-child(4) {{ height: 14px; }}
      .shots {{ position: absolute; left: 0; top: 46px; width: 464px; height: 908px; overflow: hidden; }}
      .bookend .left {{ top: 210px; width: 1020px; }}
      .bookend .phone-wrap {{ left: 1250px; }}
      /* captions: overlay, bottom-left, never a reserved band */
      .cap {{ position: absolute; left: 150px; top: 876px; width: 1010px; height: 170px; display: flex; align-items: flex-start; }}
      .capx {{ display: block; font-size: 30px; line-height: 1.3; font-weight: 500; color: var(--ink); background: rgba(10,9,6,0.72); padding: 10px 20px; border-radius: 12px;
        box-shadow: 0 0 0 1px rgba(212,175,55,0.25); }}
      .hud {{ position: absolute; left: 150px; top: 64px; width: 900px; display: flex; align-items: center; gap: 18px; font-size: 22px; font-weight: 600; letter-spacing: 0.18em; color: var(--muted); text-transform: uppercase; }}
      .hud .bar {{ position: relative; display: block; width: 260px; height: 3px; background: rgba(250,244,230,0.14); border-radius: 2px; overflow: hidden; }}
      #hud-fill {{ position: absolute; left: 0; top: 0; width: 260px; height: 3px; background: var(--gold); transform-origin: left center; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{total}">
      <div class="bg" id="bg"><div class="threads" id="threads"></div><div class="glow" id="glow-a"></div><div class="glow" id="glow-b"></div></div>
      <div class="hud" id="hud"><span data-layout-ignore>Garment unit walkthrough</span><span class="bar"><span id="hud-fill"></span></span></div>
      {''.join(sections)}
      {''.join(caps)}
      <audio id="vo" src="assets/narration.wav" data-start="0" data-duration="{total}" data-track-index="5"></audio>
    </div>
    <script>
      const S = {DATA};
      const TOTAL = {total};
      const tl = gsap.timeline({{ paused: true }});
      // Backdrop: slow drift across the whole film (finite repeats, seek-safe).
      const cycles = Math.max(1, Math.round(TOTAL / 14));
      tl.fromTo('#glow-a', {{ x: 0, y: 0, scale: 1 }}, {{ x: -120, y: 60, scale: 1.12, duration: TOTAL / cycles, ease: 'sine.inOut', yoyo: true, repeat: cycles - 1 }}, 0);
      tl.fromTo('#glow-b', {{ x: 0, y: 0 }}, {{ x: 140, y: -80, duration: TOTAL / cycles, ease: 'sine.inOut', yoyo: true, repeat: cycles - 1 }}, 0);
      tl.fromTo('#threads', {{ x: 0 }}, {{ x: -46 * 6, duration: TOTAL, ease: 'none' }}, 0);
      tl.fromTo('#hud-fill', {{ scaleX: 0 }}, {{ scaleX: 1, duration: TOTAL, ease: 'none' }}, 0);
      

      S.forEach((s, i) => {{
        const id = '#sc-' + s.id, t0 = s.start, end = s.start + s.dur;
        const last = i === S.length - 1;
        // scene in / out (crossfade on the inner wrapper; the clip itself is framework-owned)
        if (i > 0) tl.fromTo(id + '-inner', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: 'power1.out' }}, t0);
        if (!last) tl.to(id + '-inner', {{ opacity: 0, duration: 0.5, ease: 'power1.in' }}, end - 0.5);
        else tl.to(id + '-inner', {{ opacity: 0, duration: 1.2, ease: 'power1.in' }}, end - 1.2);
        tl.fromTo(id + '-ghost', {{ x: 60 }}, {{ x: -60, duration: s.dur, ease: 'none' }}, t0);
        // phone: rises in, then a slow push for the whole scene
        tl.fromTo(id + '-phonewrap', {{ y: i === 0 ? 0 : 70, rotation: s.kind === 'bookend' ? 3 : 1.5 }}, {{ y: 0, rotation: s.kind === 'bookend' ? -2 : 0, duration: 0.9, ease: 'power3.out' }}, t0);
        tl.fromTo(id + '-phone', {{ scale: 0.985 }}, {{ scale: 1.015, duration: s.dur, ease: 'sine.inOut' }}, t0);
        // left column
        if (i > 0) tl.fromTo(id + '-title', {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: 'power3.out' }}, t0 + 0.2);
        else tl.fromTo(id + '-title', {{ y: 0 }}, {{ y: -6, duration: 1.4, ease: 'sine.out' }}, 0);
        if (s.kind === 'chapter') {{
          tl.fromTo(id + '-eb', {{ x: -30, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5, ease: 'power2.out' }}, t0 + 0.1);
          // points arrive spread across the voice, then the current one is lit
          const step = s.vdur / s.points;
          for (let j = 0; j < s.points; j++) {{
            const at = s.voice + Math.max(0, j * step - 0.15);
            const pt = id + '-pt' + j;
            tl.fromTo(pt, {{ x: -24, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.45, ease: 'power2.out' }}, at);
            tl.fromTo(pt + ' .ptx', {{ color: '#faf4e6' }}, {{ color: '#e8cf7a', duration: 0.3 }}, at);
            if (j < s.points - 1) tl.to(pt + ' .ptx', {{ color: '#b9ad94', duration: 0.4 }}, s.voice + (j + 1) * step - 0.15);
            tl.fromTo(pt + ' .dot', {{ scale: 0.4 }}, {{ scale: 1, duration: 0.4, ease: 'back.out(3)' }}, at);
          }}
        }} else {{
          if (i > 0) tl.fromTo(id + '-kicker', {{ y: 20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: 'power2.out' }}, t0 + 0.05);
          for (let j = 0; j < s.points; j++)
            tl.fromTo(id + '-chip' + j, {{ y: 26, opacity: 0, scale: 0.94 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(1.6)' }}, s.voice + 0.6 + j * Math.min(0.5, s.vdur / (s.points + 2)));
        }}
        // shots: each one slides in like a swipe, then drifts slowly
        const per = (s.dur - 0.3) / s.shots;
        for (let j = 0; j < s.shots; j++) {{
          const sh = id + '-shot' + j, at = t0 + j * per;
          if (j === 0) tl.fromTo(sh, {{ opacity: 1, x: 0, y: 0 }}, {{ y: -24, duration: per + 0.3, ease: 'sine.inOut' }}, t0);
          else {{
            tl.fromTo(sh, {{ opacity: 0, x: 120 }}, {{ opacity: 1, x: 0, duration: 0.55, ease: 'power3.out' }}, at);
            tl.fromTo(sh, {{ y: 0 }}, {{ y: -24, duration: per, ease: 'sine.inOut' }}, at);
            tl.to(id + '-shot' + (j - 1), {{ x: -80, opacity: 0, duration: 0.5, ease: 'power2.in' }}, at);
          }}
        }}
      }});
      // caption phrases fade in quickly
      document.querySelectorAll('.cap').forEach((c) => {{
        const a = parseFloat(c.dataset.start);
        tl.fromTo(c.querySelector('.capx'), {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: 0.2, ease: 'power1.out' }}, a);
      }});
      window.__timelines['main'] = tl;
    </script>
  </body>
</html>
'''
(VIDEO / 'index.html').write_text(page)
print('wrote', VIDEO / 'index.html')

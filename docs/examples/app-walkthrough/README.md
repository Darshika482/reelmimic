# Example: narrated app walkthrough

The pipeline behind a 5¼-minute walkthrough of a garment-unit app (a phone web app). It covers every feature, never names the app, and uses only screens from a demo shop with invented names. Style file: `.claude/skills/video-clone/styles/app-walkthrough.md`.

| File | What it does |
|---|---|
| `script.json` | The script: 19 scenes, each with narration, on-screen title and points, and the phone screens it shows |
| `SCRIPT.md` | The same script as a readable table, with the real timestamps from the build |
| `capture/genimg.py` | Draws the demo photos (fabric rolls, garment designs, bundles, boxes, illustrated staff avatars) and writes `img/images.json` |
| `capture/seed.cjs` | The demo shop: admin, manager, masters, karigars, packing workers, staff, patterns, thaans, lots, maal entries, packing, payments, five weeks of attendance |
| `capture/lib.cjs` | Opens the app at phone size with the shop seeded, and keeps the app's name out of every screen (DOM text, plus the JS that writes PDFs, file names and WhatsApp text) |
| `capture/capture.cjs` | Takes the 57 screenshots, flow by flow |
| `build.py` | Voiceover WAVs + screenshots → `video/index.html` (HyperFrames), `video/assets/narration.wav`, `video/timeline.json`; caption phrases are snapped to the pauses in the voice |
| `make_script_md.py` | Writes `SCRIPT.md` from `video/timeline.json` |

## Re-make it

```bash
# 1. The app, against the stand-in server from its own e2e tests (in the app repo)
node tests/e2e/mock-server.cjs &
VITE_SUPABASE_URL=http://localhost:9912 VITE_SUPABASE_ANON_KEY=test npx vite --port 3000 &

# 2. Screens (in a copy of capture/)
python3 genimg.py img
ffmpeg -loop 1 -i img/avatar_3.jpg -t 3 -vf "scale=640:480:force_original_aspect_ratio=increase,crop=640:480,format=yuv420p" -r 15 cam.y4m   # fake camera for the check-in shot
BRAND="<app name>" APP_DB="<IndexedDB name>" node capture.cjs   # → png/*.png; prints "!! BRAND LEAK" if the app's name is still on a screen

# 3. A project: projects/<name>/ with script.json, build.py, make_script_md.py, assets/screens/ (the PNGs)
npx hyperframes@0.9.11 init video --non-interactive --example=blank --skill=general-video
npm pack gsap@3.15.0 && tar xzf gsap-3.15.0.tgz && cp package/dist/gsap.min.js video/assets/   # GSAP loaded locally; render browsers may not reach the CDN
pip install kokoro-onnx soundfile
for id in $(python3 -c "import json;print(' '.join(s['id'] for s in json.load(open('script.json'))['scenes']))"); do
  python3 -c "import json,sys;print([s for s in json.load(open('script.json'))['scenes'] if s['id']=='$id'][0]['narration'])" > build/tts/$id.txt
  npx hyperframes@0.9.11 tts build/tts/$id.txt -v af_heart -o build/tts/$id.wav
done
python3 build.py && python3 make_script_md.py
cd video && npx hyperframes@0.9.11 check && npx hyperframes@0.9.11 render -f 30 -o ../out/video.mp4
```

The seed's dates are fixed around 4 November 2026; move `TODAY` in `seed.cjs` to keep "today" screens current.

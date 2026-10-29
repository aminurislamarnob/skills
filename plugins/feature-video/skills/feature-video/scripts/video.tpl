<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      /* Layout: the recorded 1440x900 browser at left, a caption panel at right, a chapter rail along the bottom. */
      :root {
        --ground: #0f1311;
        --surface: #182019;
        --line: #2a342e;
        --ink: #e6ece8;
        --muted: #98a59d;
        --accent: #8ec29d;
        --rec: #e5484d;
        --font-display: "Helvetica Neue", Arial, sans-serif;
        --font-mono: "SF Mono", Menlo, "JetBrains Mono", monospace;
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: var(--ground); }
      #root { position: relative; width: 1920px; height: 1080px; font-family: var(--font-display); color: var(--ink); }

      .topbar { position: absolute; left: 48px; top: 22px; width: 1440px; height: 36px; display: flex; align-items: center; gap: 14px; font-size: 20px; color: var(--muted); }
      .dot { width: 12px; height: 12px; border-radius: 50%; background: var(--line); }
      .rec { margin-left: auto; display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-size: 15px; letter-spacing: .08em; color: var(--ink); }
      .rec i { width: 11px; height: 11px; border-radius: 50%; background: var(--rec); display: block; }
      .url { font-family: var(--font-mono); font-size: 16px; color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 5px 14px; }

      .frame { position: absolute; left: 48px; top: 70px; width: 1440px; height: 900px; border-radius: 10px; overflow: hidden; border: 1px solid var(--line); background: #fff; }
      .shot { position: absolute; left: 48px; top: 70px; width: 1440px; height: 900px; border-radius: 10px; object-fit: cover; }

      .panel { position: absolute; left: 1528px; top: 70px; width: 352px; height: 900px; }
      .cap { position: absolute; left: 1528px; top: 70px; width: 352px; }
      .cap-chapter { font-family: var(--font-mono); font-size: 18px; letter-spacing: .1em; text-transform: uppercase; color: var(--accent); margin-bottom: 22px; }
      .cap-title { font-size: 34px; line-height: 1.12; font-weight: 700; letter-spacing: -.015em; margin-bottom: 18px; }
      .cap-step { display: block; font-family: var(--font-mono); font-size: 18px; font-weight: 500; color: var(--muted); margin-bottom: 10px; letter-spacing: .06em; }
      .cap-text { font-size: 23px; line-height: 1.42; color: var(--muted); }

      .rail { position: absolute; left: 48px; top: 1012px; width: 1832px; height: 4px; background: var(--line); border-radius: 2px; }
      #rail-fill { position: absolute; left: 0; top: 0; height: 4px; width: 0%; background: var(--accent); border-radius: 2px; }
      .tick { position: absolute; top: -6px; width: 2px; height: 16px; background: var(--muted); }
      .chapters { position: absolute; left: 48px; top: 1030px; width: 1832px; height: 30px; }
      .chapter-label { position: absolute; top: 0; height: 30px; line-height: 30px; white-space: nowrap; font-size: 18px; color: var(--muted); }

      .card { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; background: var(--ground); display: flex; flex-direction: column; justify-content: center; padding-left: 180px; z-index: 5; }
      .card-num { font-family: var(--font-mono); font-size: 30px; color: var(--accent); letter-spacing: .1em; margin-bottom: 18px; }
      .card-name { font-size: 104px; font-weight: 700; letter-spacing: -.035em; line-height: 1; margin-bottom: 28px; }
      .card-lede { font-size: 34px; color: var(--muted); max-width: 1200px; }

      #intro, #outro { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; background: var(--ground); z-index: 6; display: flex; flex-direction: column; justify-content: center; padding-left: 180px; }
      .intro-eyebrow { font-family: var(--font-mono); font-size: 26px; letter-spacing: .12em; color: var(--accent); text-transform: uppercase; margin-bottom: 26px; }
      #intro h1 { font-size: 112px; line-height: 1.02; font-weight: 700; letter-spacing: -.04em; max-width: 1500px; margin-bottom: 34px; }
      .intro-sub { font-size: 34px; color: var(--muted); max-width: 1400px; line-height: 1.4; }
      #outro h2 { font-size: 72px; font-weight: 700; letter-spacing: -.03em; margin-bottom: 44px; }
      .outro-row { display: flex; gap: 28px; align-items: baseline; font-size: 34px; margin-bottom: 22px; }
      .outro-row b { font-family: var(--font-mono); font-weight: 500; color: var(--accent); min-width: 190px; font-size: 30px; }
      .outro-row span { color: var(--ink); }
      .outro-foot { margin-top: 30px; font-family: var(--font-mono); font-size: 22px; color: var(--muted); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{TOTAL}}" data-width="1920" data-height="1080">
      <div class="topbar"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span class="url">{{URL_LABEL}}</span><span class="rec"><i></i>REC · CHROME</span></div>
      <div class="frame"></div>
{{VIDEOS}}
{{AUDIO}}
{{CAPTIONS}}
      <div class="rail"><div id="rail-fill"></div>
{{TICKS}}
      </div>
      <div class="chapters">
{{LABELS}}
      </div>
{{CARDS}}
      <section id="intro" class="clip" data-start="0" data-duration="{{INTRO}}" data-track-index="4">
        <div class="intro-eyebrow">{{EYEBROW}}</div>
        <h1>{{HEADING}}</h1>
        <p class="intro-sub">{{INTRO_TEXT}}</p>
      </section>
      <section id="outro" class="clip" data-start="{{OUTRO_START}}" data-duration="{{OUTRO}}" data-track-index="4">
        <h2>{{OUTRO_TITLE}}</h2>
{{OUTRO_ROWS}}
        <div class="outro-foot">{{OUTRO_FOOT}}</div>
      </section>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      {{TIMELINE}}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>

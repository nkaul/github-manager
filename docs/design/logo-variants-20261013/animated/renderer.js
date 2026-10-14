/* Original vector animation for the selected Zen Loop cat. No app dependencies. */
(function () {
  const INK = "#3f51b5";
  const BLUE = "#039be5";
  const HEAD = "M43 52V34L54 40Q64 36 74 40L85 34V52Q91 59 84 67Q77 75 64 75Q51 75 44 67Q37 59 43 52Z";
  const OPEN = [54, 75, 50, 78, 47, 84, 47, 88, 47, 93, 47, 98, 47, 101, 50, 106, 58, 107, 64, 107, 70, 107, 78, 106, 81, 101, 81, 98, 81, 93, 81, 88, 81, 84, 78, 78, 74, 75];
  const ZEN = [54, 75, 51, 81, 48, 85, 41, 87, 31, 90, 35, 101, 45, 100, 52, 101, 58, 94, 64, 91, 70, 94, 76, 101, 83, 100, 93, 101, 97, 90, 87, 87, 80, 85, 77, 81, 74, 75];
  const smooth = x => { const p = Math.max(0, Math.min(1, x)); return p * p * (3 - 2 * p); };
  const f = x => Number(x.toFixed(4));

  function bodyPath(u) {
    const points = OPEN.map((x, i) => f(x + (ZEN[i] - x) * u));
    let d = `M${points[0]} ${points[1]}`;
    for (let i = 2; i < points.length; i += 6) d += "C" + points.slice(i, i + 6).join(" ");
    return d;
  }

  function cat(u) {
    return `<path d="${bodyPath(u)}" fill="none" stroke="${INK}" stroke-width="5"/>
      <path d="M56 91V103M72 91V103" opacity="${f(1-u)}" stroke="${INK}" stroke-width="3.2"/>
      <path d="${HEAD}" fill="white" stroke="${INK}" stroke-width="5"/>
      <g opacity="${f(1-u)}" fill="${INK}"><ellipse cx="53" cy="56" rx="1.8" ry="${f(3-2.7*u)}"/><ellipse cx="75" cy="56" rx="1.8" ry="${f(3-2.7*u)}"/></g>
      <path d="M49 56Q53 60 57 56M71 56Q75 60 79 56" opacity="${f(u)}" fill="none" stroke="${INK}" stroke-width="3.2"/>
      <path d="m62 65 2 1 2-1" fill="none" stroke="${INK}" stroke-width="2.4"/>`;
  }

  function frame(kind, seconds) {
    let art;
    if (kind === "orbit") {
      const angle = (seconds % 4) / 4 * 360 - 135;
      const circumference = 2 * Math.PI * 51;
      art = `<circle cx="64" cy="64" r="51" fill="none" stroke="#e1f5fe" stroke-width="3"/>
        <circle cx="64" cy="64" r="51" fill="none" stroke="${BLUE}" stroke-width="6" stroke-dasharray="${f(circumference*0.71)} ${f(circumference*0.29)}" transform="rotate(${f(angle)} 64 64)"/>
        ${cat(1)}`;
    } else {
      const t = seconds % 6;
      const u = t < 0.8 ? 0 : t < 1.4 ? smooth((t-0.8)/0.6) : t < 5.4 ? 1 : 1-smooth((t-5.4)/0.6);
      const pulse = t >= 1.4 && t < 5 ? Math.sin(Math.PI * (t-1.4)/1.2) ** 2 : 0;
      const p = u * pulse;
      const tail = [78,101,110,107,121,74,106,56].map((x,i) => f(x+([82,98,108,102,113,81,98,70][i]-x)*u));
      let rays = "";
      for (const degrees of [-160,-135,-110,-90,-70,-45,-20]) {
        const a = degrees * Math.PI / 180;
        const start = 31 + 3 * (1-p);
        const end = start + 17 * p;
        const x1 = f(64 + Math.cos(a)*start), y1 = f(55 + Math.sin(a)*start);
        const x2 = f(64 + Math.cos(a)*end), y2 = f(55 + Math.sin(a)*end);
        if (p > 0.015) {
          rays += `<path d="M${x1} ${y1}L${x2} ${y2}" fill="none" stroke="${BLUE}" stroke-width="${f(1.8+1.7*p)}" opacity="${f(p)}"/>`;
        }
      }
      art = `<path d="M${tail[0]} ${tail[1]}C${tail.slice(2).join(" ")}" fill="none" stroke="#29b6f6" stroke-width="5"/>
        ${rays}${cat(u)}`;
    }
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="512" height="512"><g stroke-linecap="round" stroke-linejoin="round">${art}</g></svg>`;
  }

  globalThis.ZenLoop = { frame, bodyPath, fps: 25, durations: { orbit: 4, rays: 6 } };
})();

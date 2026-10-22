// 공개 인스타그램 릴스를 분석용으로만 받기(저장소에 올리지 않음 — .gitignore의 ref/*.mp4 경로로 저장할 것).
// 사용: NODE_PATH=/opt/node-tools/node_modules node tools/reel_fetch.mjs <릴스 URL> <저장 경로.mp4>
// /embed/captioned/ 페이지의 <video> 주소를 읽어 curl로 받음(로그인·쿠키 사용 안 함).
import { createRequire } from 'module';
import { execFileSync } from 'child_process';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const [url, out] = process.argv.slice(2);
const code = url.match(/\/(reel|p)\/([^/?]+)/)[2];
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(`https://www.instagram.com/reel/${code}/embed/captioned/`, { waitUntil: 'networkidle', timeout: 60000 });
const src = await page.evaluate(() => document.querySelector('video')?.src);
await browser.close();
if (!src) { console.error('video 주소 없음'); process.exit(1); }
execFileSync('curl', ['-sS', '-L', '-o', out, src]);
console.log('ok', out);

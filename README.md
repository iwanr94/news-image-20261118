# news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/iwanr94/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/iwanr94/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A program that sums up 18 November 2026's world news in one image. Built by an AI agent for make.fun's "Sum up 18 November's world news in one image" bounty, $250 in USDC.

The image names the day — Wednesday 18 November 2026 — and shows the day's six most consequential stories: US and Iran trade strikes across the Gulf, Xi and Putin meet at APEC in Shenzhen, Democrats win Alaska and a 56-44 Senate majority, Ukraine hits the Kerch Bridge again, Voyager 1 reaches one light-day out, and Congo Ebola cases pass 11,000.

## Run

```sh
python3 main.py
```

This copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`). It runs with no network, standard library only, and writes the same bytes on every run.

## Entry

- `entry.png` — the image (1024×1024 PNG, 248 KB)
- `main.py` — the program (Python 3.13, standard library only)
- `tools/draw_entry.py` — the PIL script that drew the image

See the bounty: https://make.fun/bounty/news-image-20261118

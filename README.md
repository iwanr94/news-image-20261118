# news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/iwanr94/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/iwanr94/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

An entry for [make.fun's news-image-20261118 bounty](https://make.fun/bounty/news-image-20261118):
one image that sums up Wednesday 18 November 2026's world news.

The page is drawn by `tools/draw_entry.py` with Pillow and no network, no
photos and no randomness: a navy masthead carrying the date as the largest type
on the page, one lead story with a drawn panel of the Gulf, and five further
stories in a two-column grid — Xi and Putin at APEC in Shenzhen, the Democrats
taking the Alaska Senate seat, Ukraine's strike on the Kerch Bridge, Voyager 1
reaching one light-day out, and the Congo Ebola outbreak passing 11,000 cases.
`entry.png` is the result; `main.py` copies it into the graded output.

## Run

```
python3 main.py
```

The copy lands in `$MAKEFUN_OUTPUT_DIR/entry.png`, or `/output/entry.png` when
that variable is unset, which is where the grader looks. The program checks the
source is a real PNG before copying, and runs the second time exactly as it ran
the first. To redraw the page itself:

```
python3 tools/draw_entry.py
```

## License

MIT. See `LICENSE`.

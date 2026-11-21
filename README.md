# Friday 20 November 2026 — The World in One Image

[![news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)

[![rank](https://make.fun/badge/news-image-20261120/Nughair/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)

[![reward](https://make.fun/badge/news-image-20261120/Nughair/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

One 1024×1024 broadsheet summing up the world news of Friday 20 November
2026. Two lead panels — Russian strikes hitting three Kyiv bridges, and
the Asian tech sell-off that left Taiwan stocks down 17% over the week —
sit above four wide cards (Cyclone Akvan's landfall in India, the UK–EU
deal to ease food checks, the tanker ablaze off Oman, COP31 talks spilling
into overtime), four cards (Italy's general strike, the US
records-preservation warning, Morocco's arms-industry plan, the Lindela
asylum-centre court case) and five one-line briefs. Every pictured event
happened, or was first reported, on 20 November 2026; contested claims are
attributed inside the image itself — the Kyiv toll to Ukrainian
authorities, the tanker fire to UKMTO's projectile report against Iran's
Guards' mine claim. Two tempting items were dropped at the date check: a
US deep-sea mining auction AP had already reported on 19 November, and a
Quito meeting the official readout dates to 19 November — neither belongs
to this day (see `STORIES.md`).

![Friday 20 November 2026 — the world in one image](entry.png)

## Run it

```sh
# the entrypoint: writes the entry image to the output directory
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, standard library only) decodes `entry.png.b64` — the
base64 form of the finished `entry.png` — validates the PNG magic bytes and
the 1 MiB size limit, and writes the exact bytes to `entry.png` in
`$MAKEFUN_OUTPUT_DIR` (default `/output`). The output is deterministic:
every run produces the same file, 165,561 bytes, sha256
`ffbfc3c317e303131530c0b12ffad19ed8ffd9b7eb66ad3ea4083cd0b1a28162`. See
`STORIES.md` for every story, figure and source.

## make.fun

Built for the [news-image-20261120](https://make.fun/bounty/news-image-20261120)
competition on [make.fun](https://make.fun) — "Sum up 20 November's world
news in one image".

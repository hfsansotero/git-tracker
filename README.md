# git-tracker

**English** | [Español](README.es.md)

A pixel-art pet for your GitHub profile that grows, changes color, and moves with
your activity. Pick an animal or make your own from an image. Inspired by
[git-koi](https://github.com/yalongwastaken/git-koi).

## How your activity shows

| What          | Comes from (by default)                             |
| ------------- | --------------------------------------------------- |
| **Stage**     | Contributions in the last year: `baby` → `young` → `adult` (thresholds 50 and 300) |
| **Animation** | What happened up to yesterday (table below)         |
| **Colors**    | Main languages of your public repositories          |

| Animation | When (first match wins)                                    |
| --------- | ---------------------------------------------------------- |
| `sleep`   | 14 or more days in a row without contributions             |
| `eat`     | Yesterday was the first day with contributions of its week |
| `active`  | Last 7 days at least twice your weekly average (and ≥ 5)   |
| `idle`    | Anything else                                              |

Today never counts, because it has not ended yet. Both the size and the animation
can follow a slower pace, such as your week or your month: see
[Tuning the pace](#tuning-the-pace).

## On your profile README

1. Copy [examples/profile-workflow.yml](examples/profile-workflow.yml) into your
   profile repository (`<you>/<you>`) as `.github/workflows/git-tracker.yml`.
2. Set `animal:` to a built-in animal (`fox`) or to an animal folder in that
   repository (format below).
3. Add the GIF to its `README.md`:

   ```html
   <img src="tracker/tracker.gif" alt="My git-tracker" />
   ```

4. Run the workflow once from the Actions tab. After that it runs every night.

| Input        | Default              | Meaning                                           |
| ------------ | -------------------- | ------------------------------------------------- |
| `animal`     | (required)           | Animal folder in your repository, or a built-in animal name |
| `login`      | The repository owner | Account whose activity to track                   |
| `output-dir` | `tracker`            | Folder that receives `tracker.gif`                |
| `growth`     | `year`               | Activity that decides the size: `week`, `month` or `year` ([Tuning the pace](#tuning-the-pace)) |
| `mood`       | `day`                | Activity that decides the animation: `day`, `week` or `month` |
| `thresholds` | Depends on `growth`  | Contributions to become young and adult, such as `5 25` |
| `token`      | The built-in token   | Token for reading public data                     |

GitHub pauses scheduled workflows after 60 days without activity in the
repository. Re-enable it from the Actions tab if that happens.

### Whose activity, whose code

- **Your data:** the Action reads the activity of the account that owns the
  repository where it runs (`login`), so everyone gets their own stage, animation
  and colors. Nobody else's activity is ever mixed in.
- **Our code:** `hfsansotero/git-tracker@main` means each night you use the latest
  version of this tool and of its built-in animals. To freeze a version, use a
  commit SHA instead of `main`:
  `uses: hfsansotero/git-tracker@08c41ede109fc87551e004cc1921880de5d5df4f`.
- **Your animals:** an animal folder in your own repository is yours alone; changes
  here never touch it.

## Tuning the pace

Two lines in your workflow, next to `animal:`, choose which activity your pet
follows. Leave them out to keep the defaults.

```yaml
      - uses: hfsansotero/git-tracker@main
        with:
          animal: fox
          growth: month   # size: your last 30 days
          mood: week      # animation: your last finished week
```

**`growth`, the size.** It counts your contributions in a moving window and
compares them with two thresholds: below the first, `baby`; from the first,
`young`; from the second, `adult`. The window moves every day, so your pet grows
and shrinks smoothly.

| `growth`         | Counts            | Default thresholds (young, adult) | Feels like                            |
| ---------------- | ----------------- | --------------------------------- | ------------------------------------- |
| `week`           | Last 7 days       | `2 8`                             | Reacts fast, changes size often       |
| `month`          | Last 30 days      | `5 25`                            | Grows over a month; good for steady, light activity |
| `year` (default) | Last 365 days     | `50 300`                          | Very stable, changes slowly           |

To set your own thresholds, add `thresholds: "<young> <adult>"`. For example,
with `growth: month`, `thresholds: "10 60"` makes it harder to grow.

**`mood`, the animation.** It looks at one period and compares it with your own
average, so a quiet account and a busy one both see every animation.

| `mood`          | Looks at                                  | The GIF changes      |
| --------------- | ----------------------------------------- | -------------------- |
| `day` (default) | Yesterday and the days before             | Every day            |
| `week`          | Your last finished week (Monday–Sunday)   | On Mondays           |
| `month`         | Your last finished calendar month         | On the 1st           |

With `week` or `month`, first match wins:

| Animation | When                                                          |
| --------- | ------------------------------------------------------------- |
| `sleep`   | That week or month had no contributions                       |
| `eat`     | You came back: that one had contributions, the one before had none |
| `active`  | At least twice your average week or month (and ≥ 5 a week, ≥ 10 a month) |
| `idle`    | Anything else                                                 |

Some combinations to copy:

```yaml
# Little activity: watch it grow over the month, one mood per week
          growth: month
          mood: week

# Very active: an adult needs a lot, the animation follows each day
          growth: month
          thresholds: "20 80"
          mood: day

# Calm: changes only once a month
          growth: year
          mood: month
```

To try a setting before changing your workflow, run the same thing locally:

```sh
git-tracker collect <you> -o snapshot.json
git-tracker render snapshot.json animals/fox --growth month --mood week
```

It prints the stage, the animation and the numbers behind them.

## Choosing your animal

Only the animal you name in **your** workflow appears on your profile. Every other
animal, built-in or yours, is ignored. To change it, edit one line in
`.github/workflows/git-tracker.yml` of your profile repository:

```yaml
      - uses: hfsansotero/git-tracker@main
        with:
          animal: fox             # a built-in animal...
          # animal: animals/cat   # ...or a folder in your profile repository
```

To show several animals, add one step per animal, each with its own
`output-dir`, and one `<img>` per GIF in your README:

```yaml
      - uses: hfsansotero/git-tracker@main
        with:
          animal: fox
          output-dir: tracker/fox
      - uses: hfsansotero/git-tracker@main
        with:
          animal: animals/cat
          output-dir: tracker/cat
```

```html
<img src="tracker/fox/tracker.gif" width="192" alt="My fox">
<img src="tracker/cat/tracker.gif" width="192" alt="My cat">
```

The commit step (`git add tracker`) already picks up every folder under `tracker/`.
The CI of this repository renders all built-in animals only to test them; that
never reaches anyone's profile.

## Private animals

Your profile repository has to be public, so anything inside it can be
downloaded. If you want an animal only you can use (bought sprites, or one you
just want to keep), keep its frames in a **private** repository and let the
workflow fetch them only to draw. The GIF on your profile is public, like any
image there, but the frames never are.

1. Create a private repository, such as `<you>/my-sprites`, with your animal
   inside it in the [animal format](#animal-format), such as `bat/adult/idle/01.png`.
2. Create a [fine-grained token](https://github.com/settings/personal-access-tokens/new)
   with access to **only that repository** and the permission **Contents: Read-only**.
3. In your profile repository, open **Settings → Secrets and variables → Actions →
   New repository secret**, name it `SPRITES_TOKEN` and paste the token.
4. In your workflow, add a step that fetches it before git-tracker, and point
   `animal` there:

   ```yaml
       steps:
         - uses: actions/checkout@v4
         - uses: actions/checkout@v4
           with:
             repository: <you>/my-sprites
             token: ${{ secrets.SPRITES_TOKEN }}
             path: private
         - uses: hfsansotero/git-tracker@main
           with:
             animal: private/bat
   ```

The commit step only adds `tracker/`, so the private frames are never committed
to your profile. If you bought the sprites, check that their license lets you
show them on a website.

## Animal format

Built-in animals and your own use the same folder format:

```text
animals/cat/
├── animal.json           optional: {"fps": 6, "scale": 2, "recolor": [...]}
├── baby/                 stage: little activity
│   ├── idle/             default animation
│   │   ├── 01.png
│   │   └── 02.png
│   ├── active/
│   ├── eat/
│   └── sleep/
├── young/
│   └── ...
└── adult/
    └── ...
```

- **Frames:** one PNG per frame with a transparent background, sorted by number
  (`2.png` comes before `10.png`).
- **Only `adult/idle/01.png` is required.** A missing animation falls back to
  `idle` of the same stage. A missing stage falls back to the closest one (the
  smaller one on a tie). An animal can start as a single frame.
- **Sizes:** each stage can have its own size (that is how it grows). Frames of one
  animation should all be the same size. Each frame is centered and rests on the
  bottom edge of a canvas shared by the whole animal, so the GIF size never
  changes.
- **Real pixel art:** draw at real size (16, 24, 32 px…) and let `scale` enlarge
  it without smoothing. Do not export it already enlarged.
- **`animal.json`:**
  - `fps`: animation speed, as one number or per animation:
    `{"idle": 1.5, "active": 4}` (missing ones use 6).
  - `scale`: whole-number enlargement of the GIF.
  - `recolor`: groups of exact sprite colors that take a language's color. The
    first group takes your top language, the second your second one, and so on:
    `[["#c86420", "#e07020"], ["#2040a0"], ["#5a5a5a"]]`. Each pixel keeps its
    brightness, so shading survives. Use **three groups** (main body, trim,
    details) so the animal shows your top three languages; with fewer languages,
    the extra groups keep their own colors.

## Built-in animals

| Name  | Made with |
| ----- | --------- |
| `fox` | Poses generated with Higgsfield, processed by [sources/fox/build.py](sources/fox/build.py) |

## Your own animal, step by step

1. **Install the tool** to preview your animal before publishing it:

   ```sh
   pip install git+https://github.com/hfsansotero/git-tracker
   ```

2. **Make the frames.** Pick whichever suits you:
   - **Draw them** in a pixel-art editor (Aseprite, LibreSprite, Piskel…) and
     export each frame as its own PNG with a transparent background.
   - **Start from an image** (a drawing, a photo of your pet, an AI image). Use
     a PNG with a transparent background, or with a plain background that touches
     the corners (it is removed automatically):

     ```sh
     git-tracker pixelize photo.png animals/mine --sizes 16 24 32 --colors 16
     ```

     This creates `baby`, `young` and `adult` at 16, 24 and 32 px, each with a
     generic two-frame `idle`. Touch up or replace any frame by hand afterwards.

     If you generate the image with AI, ask for **three clearly different color
     areas** (for example: the body in one color, the trim in another, the small
     details in a third). Each area then becomes one `recolor` group in step 5.
   - **Several poses in one image** (for example, an AI-generated sheet): see
     [sources/fox/build.py](sources/fox/build.py). It cuts the sheet, removes the
     background and gives every pose the same scale and palette.

3. **Put them in your profile repository** following the
   [animal format](#animal-format), for example:

   ```text
   animals/mine/adult/idle/01.png
   animals/mine/adult/idle/02.png
   animals/mine/adult/sleep/01.png
   ```

   Start small: `adult/idle/01.png` alone already works. Each animation you add
   shows on the days its rule in [How your activity shows](#how-your-activity-shows)
   matches; the missing ones fall back to `idle`.

4. **Preview it:**

   ```sh
   git-tracker preview animals/mine
   ```

   It writes one GIF per stage and animation to `out/mine/`, tells you which
   ones are borrowed from another folder, and lists the sprite's colors.

5. **Choose what takes your language colors.** Copy colors from that list into
   `recolor` in `animals/mine/animal.json`, together with the speed and size:

   ```json
   {
     "fps": {"idle": 2, "active": 6, "sleep": 1, "eat": 3},
     "scale": 3,
     "recolor": [["#e26730", "#dd602d", "#c04b2b"], ["#f4e3c9", "#e8d2b0"], ["#3a2a22"]]
   }
   ```

   One group per color area: body, trim and details. Run `preview` again: each
   color now shows its `recolor group`.

6. **Use it:** set `animal: animals/mine` in your workflow and push.

## Command line

```sh
conda create -n git-tracker python=3.13 && conda activate git-tracker
pip install -e .                              # from a clone of this repository
git-tracker preview animals/cat               # one GIF per stage and animation in out/cat/, plus its colors
export GITHUB_TOKEN=$(gh auth token)          # any token works; public data only
git-tracker collect <login> -o snapshot.json  # last year of activity and languages
git-tracker render snapshot.json animals/cat  # today's out/tracker.gif
```

Tests: `for f in tests/test_*.py; do python "$f"; done`

## License

MIT.

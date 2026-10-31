# git-tracker

**English** | [Español](README.es.md)

A pixel-art pet for your GitHub profile that grows, changes color, and moves with
your activity. Pick an animal or make your own from an image. Inspired by
[git-koi](https://github.com/yalongwastaken/git-koi).

## How your activity shows

| What          | Comes from                                          |
| ------------- | --------------------------------------------------- |
| **Stage**     | Contributions in the last year: `baby` → `young` → `adult` (default thresholds 50 and 300) |
| **Animation** | What happened up to yesterday (table below)         |
| **Colors**    | Main languages of your public repositories          |

| Animation | When (first match wins)                                    |
| --------- | ---------------------------------------------------------- |
| `sleep`   | 14 or more days in a row without contributions             |
| `eat`     | Yesterday was the first day with contributions of its week |
| `active`  | Last 7 days at least twice your weekly average (and ≥ 5)   |
| `idle`    | Anything else                                              |

Growth uses the last year, not your whole history, so people with little activity
still see their pet grow, and it shrinks back if you stop.

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
| `thresholds` | `50 300`             | Contributions in the last year to become young and adult |
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
    first group takes your top language, the second group your second one:
    `[["#c86420", "#e07020"], ["#2040a0"]]`. Each pixel keeps its brightness,
    so shading survives.

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
     "recolor": [["#e26730", "#dd602d", "#c04b2b"]]
   }
   ```

   Run `preview` again: those colors now show `recolor group 1`.

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

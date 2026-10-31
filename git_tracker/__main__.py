import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from git_tracker import activity, sprites


def preview(animal_dir: Path, out_dir: Path) -> None:
    config = sprites.load_config(animal_dir)
    canvas = sprites.canvas_size(animal_dir)
    print(f"{animal_dir.name}: canvas {canvas[0]}x{canvas[1]} px, {config}")
    for stage in sprites.STAGES:
        for animation in sprites.ANIMATIONS:
            used, frames = sprites.find_frames(animal_dir, stage, animation)
            frames = sprites.compose(frames, canvas, config["scale"])
            sprites.save_gif(frames, out_dir / f"{stage}-{animation}.gif", sprites.fps_for(config, animation))
            source = used.relative_to(animal_dir).as_posix()
            note = "" if source == f"{stage}/{animation}" else f"  (uses {source})"
            print(f"  {stage}/{animation}: {len(frames)} frames{note}")
    print(f"GIFs in {out_dir}/")


def render(snapshot: Path, animal_dir: Path, out_dir: Path, thresholds: list[int]) -> None:
    summary = activity.summarize(json.loads(snapshot.read_text()),
                                 datetime.now(timezone.utc).date(), thresholds)
    print(json.dumps(summary, indent=2))
    config = sprites.load_config(animal_dir)
    _, frames = sprites.find_frames(animal_dir, summary["stage"], summary["animation"])
    frames = sprites.recolor(frames, config["recolor"], summary["colors"])
    frames = sprites.compose(frames, sprites.canvas_size(animal_dir), config["scale"])
    sprites.save_gif(frames, out_dir / "tracker.gif", sprites.fps_for(config, summary["animation"]))
    print(f"Wrote {out_dir}/tracker.gif")


def main() -> None:
    parser = argparse.ArgumentParser(prog="git-tracker")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("preview", help="write one GIF per stage and animation of an animal")
    p.add_argument("animal_dir", type=Path)
    p.add_argument("-o", "--output-dir", type=Path, default=Path("out"))

    p = sub.add_parser("pixelize", help="create an animal from an image")
    p.add_argument("image", type=Path)
    p.add_argument("animal_dir", type=Path)
    p.add_argument("--sizes", type=int, nargs=3, default=[16, 24, 32], metavar=("BABY", "YOUNG", "ADULT"))
    p.add_argument("--colors", type=int, default=16)

    p = sub.add_parser("collect", help="fetch a user's public activity (needs GITHUB_TOKEN)")
    p.add_argument("login")
    p.add_argument("-o", "--output", type=Path, default=Path("snapshot.json"))

    p = sub.add_parser("render", help="draw today's GIF from a snapshot")
    p.add_argument("snapshot", type=Path)
    p.add_argument("animal_dir", type=Path)
    p.add_argument("-o", "--output-dir", type=Path, default=Path("out"))
    p.add_argument("--thresholds", type=int, nargs=2, default=[50, 300], metavar=("YOUNG", "ADULT"),
                   help="contributions in the last year to reach each stage")

    args = parser.parse_args()
    if args.command == "preview":
        preview(args.animal_dir, args.output_dir / args.animal_dir.name)
    elif args.command == "pixelize":
        sprites.make_animal(args.image, args.animal_dir, args.sizes, args.colors)
        print(f"Created {args.animal_dir}/; try it with: git-tracker preview {args.animal_dir}")
    elif args.command == "collect":
        args.output.write_text(json.dumps(activity.collect(args.login)))
        print(f"Wrote {args.output}")
    else:
        render(args.snapshot, args.animal_dir, args.output_dir, args.thresholds)


if __name__ == "__main__":
    main()

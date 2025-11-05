import sys
from PIL import Image

def make_transparent(png_in: str, png_out: str | None = None, white_threshold: int = 250):
    if png_out is None:
        # Auto-generate: tree.png → tree_transparent.png
        if png_in.lower().endswith(".png"):
            png_out = png_in[:-4] + "_transparent.png"
        else:
            png_out = png_in + "_transparent.png"

    im = Image.open(png_in).convert("RGBA")
    datas = im.getdata()
    new_data = []

    for (r, g, b, a) in datas:
        if r >= white_threshold and g >= white_threshold and b >= white_threshold:
            new_data.append((255, 255, 255, 0))  # make white transparent
        else:
            new_data.append((r, g, b, a))

    im.putdata(new_data)
    im.save(png_out, "PNG")
    print(f"[OK] Saved transparent PNG → {png_out}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    png_in = sys.argv[1]
    png_out = None
    threshold = 250

    # Optional arguments
    for arg in sys.argv[2:]:
        if arg.startswith("--threshold"):
            try:
                threshold = int(arg.split("=")[1])
            except Exception:
                pass
        elif not arg.startswith("-"):
            png_out = arg

    make_transparent(png_in, png_out, white_threshold=threshold)

import math
import numpy as np
from PIL import Image, ImageDraw

def generate_live_banner(input_path, output_path, num_frames=36, fps=18):
    base_img = Image.open(input_path).convert("RGBA")
    width, height = base_img.size

    # 1. Twinkling stars in upper twilight sky (y < 130, x < 650)
    np.random.seed(42)
    num_stars = 35
    stars = []
    for _ in range(num_stars):
        sx = np.random.uniform(20, 620)
        sy = np.random.uniform(10, 120)
        size = np.random.uniform(1.2, 2.8)
        phase = np.random.uniform(0, 2 * math.pi)
        speed = np.random.choice([1, 2, 3])
        stars.append({"x": sx, "y": sy, "size": size, "phase": phase, "speed": speed})

    # 2. Drifting glowing petals / embers
    num_petals = 28
    petals = []
    for i in range(num_petals):
        start_x = np.random.uniform(-50, width)
        start_y = np.random.uniform(-20, height * 0.8)
        drift_x = np.random.uniform(60, 140)
        drift_y = np.random.uniform(20, 60)
        size = np.random.uniform(2.5, 5.0)
        phase = np.random.uniform(0, 2 * math.pi)
        flutter_freq = np.random.choice([1, 2])
        # color: sakura pink or warm golden amber
        color_type = np.random.choice(["pink", "glow"])
        petals.append({
            "start_x": start_x,
            "start_y": start_y,
            "drift_x": drift_x,
            "drift_y": drift_y,
            "size": size,
            "phase": phase,
            "flutter_freq": flutter_freq,
            "color_type": color_type,
            "time_offset": i / num_petals
        })

    # Lamp position
    lamp_x, lamp_y = 330, 245

    frames = []
    duration = int(1000 / fps)

    for frame_idx in range(num_frames):
        t = frame_idx / num_frames  # normalized 0.0 to 1.0

        # Frame layer
        frame_canvas = base_img.copy()
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # A. Subtle lamp glow breathing
        lamp_pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t)
        lamp_radius = 28 + int(8 * lamp_pulse)
        lamp_alpha = int(35 + 25 * lamp_pulse)
        # draw soft lamp glow
        for r in range(lamp_radius, 4, -4):
            cur_alpha = int(lamp_alpha * (1 - r / lamp_radius))
            draw.ellipse(
                [lamp_x - r, lamp_y - r, lamp_x + r, lamp_y + r],
                fill=(255, 230, 180, cur_alpha)
            )

        # B. Twinkling stars
        for star in stars:
            twinkle = 0.5 + 0.5 * math.sin(2 * math.pi * star["speed"] * t + star["phase"])
            cur_size = star["size"] * (0.6 + 0.4 * twinkle)
            alpha = int(120 + 135 * twinkle)
            sx, sy = star["x"], star["y"]
            draw.ellipse(
                [sx - cur_size, sy - cur_size, sx + cur_size, sy + cur_size],
                fill=(255, 255, 255, alpha)
            )
            # 4-point sparkle on brightest stars
            if star["size"] > 2.2 and twinkle > 0.7:
                sp_len = cur_size * 2.5
                sp_alpha = int(alpha * 0.7)
                draw.line([(sx - sp_len, sy), (sx + sp_len, sy)], fill=(255, 255, 255, sp_alpha), width=1)
                draw.line([(sx, sy - sp_len), (sx, sy + sp_len)], fill=(255, 255, 255, sp_alpha), width=1)

        # C. Drifting Sakura Petals & Fairy Sparkles
        for p in petals:
            rel_t = (t + p["time_offset"]) % 1.0
            cur_x = p["start_x"] + p["drift_x"] * rel_t
            cur_y = p["start_y"] + p["drift_y"] * rel_t + 12 * math.sin(2 * math.pi * p["flutter_freq"] * rel_t + p["phase"])

            # Fade in and out smoothly over particle lifetime (rel_t from 0 to 1)
            life_alpha = math.sin(math.pi * rel_t) ** 1.5

            if cur_x < width + 20 and cur_y < height + 20:
                cur_sz = p["size"]
                if p["color_type"] == "pink":
                    # Sakura petal (pink ellipse)
                    alpha = int(220 * life_alpha)
                    rot_angle = 2 * math.pi * rel_t + p["phase"]
                    # Approximate petal as angled ellipse
                    p_w = cur_sz * (0.8 + 0.3 * math.cos(rot_angle))
                    p_h = cur_sz * 1.5
                    draw.ellipse(
                        [cur_x - p_w, cur_y - p_h, cur_x + p_w, cur_y + p_h],
                        fill=(255, 182, 215, alpha)
                    )
                    # Outer soft glow
                    glow_alpha = int(80 * life_alpha)
                    draw.ellipse(
                        [cur_x - p_w * 1.6, cur_y - p_h * 1.6, cur_x + p_w * 1.6, cur_y + p_h * 1.6],
                        fill=(255, 210, 230, glow_alpha)
                    )
                else:
                    # Warm glowing fairy sparkle
                    alpha = int(240 * life_alpha)
                    draw.ellipse(
                        [cur_x - cur_sz, cur_y - cur_sz, cur_x + cur_sz, cur_y + cur_sz],
                        fill=(255, 245, 200, alpha)
                    )
                    glow_alpha = int(100 * life_alpha)
                    draw.ellipse(
                        [cur_x - cur_sz * 2, cur_y - cur_sz * 2, cur_x + cur_sz * 2, cur_y + cur_sz * 2],
                        fill=(255, 220, 160, glow_alpha)
                    )

        # Composite overlay
        frame_canvas = Image.alpha_composite(frame_canvas, overlay)
        # Convert to RGB with adaptive palette
        rgb_frame = frame_canvas.convert("RGB")
        quantized = rgb_frame.quantize(colors=128, method=Image.Resampling.LANCZOS, dither=Image.Dither.FLOYDSTEINBERG)
        frames.append(quantized)

    # Save animated GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=True
    )
    print(f"Saved {output_path} with {num_frames} frames, duration per frame: {duration}ms")

if __name__ == "__main__":
    generate_live_banner("assets/header.jpg", "assets/header.gif", num_frames=36, fps=18)

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_ultra_ego_banner(input_path, output_path, num_frames=30, fps=15):
    raw_img = Image.open(input_path).convert("RGBA")
    w, h = raw_img.size

    # We want a cinematic widescreen banner canvas, e.g. 760 x 300
    target_w, target_h = 760, 300
    # Scale image to fit height 300
    scale = target_h / h
    scaled_w = int(w * scale)
    scaled_img = raw_img.resize((scaled_w, target_h), Image.Resampling.LANCZOS)

    # Base canvas with deep space purple
    bg_color = (14, 11, 28, 255)
    base_canvas = Image.new("RGBA", (target_w, target_h), bg_color)
    offset_x = (target_w - scaled_w) // 2

    # Feather the left and right edges of scaled_img so it blends seamlessly into bg
    feather_w = 40
    scaled_arr = np.array(scaled_img, dtype=float)
    for i in range(feather_w):
        alpha_factor = i / feather_w
        scaled_arr[:, i, 3] *= alpha_factor
        scaled_arr[:, -1 - i, 3] *= alpha_factor
    blended_scaled = Image.fromarray(np.uint8(scaled_arr))

    base_canvas.paste(blended_scaled, (offset_x, 0), blended_scaled)

    # Detect Vegeta's center and aura location
    # In target coords:
    cx = target_w // 2
    # Vegeta's head/torso is roughly at cx, y: 50 to 220
    aura_y = int(120 * scale)
    head_y = int(88 * scale)
    eyes_y = int(95 * scale)

    # Generate persistent random energy particles
    np.random.seed(77)
    num_particles = 32
    particles = []
    for i in range(num_particles):
        px = np.random.uniform(cx - 140, cx + 140)
        py = np.random.uniform(target_h * 0.3, target_h + 20)
        speed = np.random.uniform(50, 110)
        size = np.random.uniform(1.8, 3.8)
        color_type = np.random.choice(["violet", "magenta", "white"])
        particles.append({
            "x": px,
            "y": py,
            "speed": speed,
            "size": size,
            "color_type": color_type,
            "phase": np.random.uniform(0, 2 * math.pi),
            "offset_t": i / num_particles
        })

    # Lightning arcs (subtle electric violet discharges)
    # Precompute 4 lightning bolts that flash at specific frame cycles
    lightning_bolts = [
        {"frame": 4, "pts": [(cx - 20, aura_y - 20), (cx - 35, aura_y - 5), (cx - 28, aura_y + 15), (cx - 45, aura_y + 35)]},
        {"frame": 11, "pts": [(cx + 25, aura_y - 10), (cx + 40, aura_y + 10), (cx + 30, aura_y + 25), (cx + 50, aura_y + 40)]},
        {"frame": 18, "pts": [(cx - 30, aura_y + 20), (cx - 48, aura_y + 35), (cx - 38, aura_y + 50), (cx - 55, aura_y + 70)]},
        {"frame": 25, "pts": [(cx + 20, aura_y + 15), (cx + 38, aura_y + 30), (cx + 28, aura_y + 48), (cx + 45, aura_y + 65)]},
    ]

    frames = []
    duration = int(1000 / fps)

    for f_idx in range(num_frames):
        t = f_idx / num_frames
        frame_canvas = base_canvas.copy()

        # Dynamic overlay layer
        overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # 1. Pulsing Divine Hakai / Ultra Ego Aura behind Vegeta
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t)
        aura_rad_x = int(65 + 15 * pulse)
        aura_rad_y = int(85 + 20 * pulse)
        aura_alpha = int(35 + 30 * pulse)

        # Draw concentric soft violet bloom
        for r in range(aura_rad_x, 10, -8):
            fraction = 1.0 - (r / aura_rad_x)
            cur_a = int(aura_alpha * fraction)
            ry = int(r * (aura_rad_y / aura_rad_x))
            draw.ellipse(
                [cx - r, aura_y - ry, cx + r, aura_y + ry],
                fill=(190, 70, 255, cur_a)
            )

        # 2. Glowing Eyes Flare
        eye_pulse = 0.6 + 0.4 * math.sin(4 * math.pi * t)
        eye_alpha = int(160 * eye_pulse)
        # Left and right eye points
        draw.ellipse([cx - 7, eyes_y - 2, cx - 3, eyes_y + 2], fill=(255, 230, 255, eye_alpha))
        draw.ellipse([cx + 3, eyes_y - 2, cx + 7, eyes_y + 2], fill=(255, 230, 255, eye_alpha))
        draw.ellipse([cx - 10, eyes_y - 4, cx, eyes_y + 4], fill=(220, 80, 255, int(eye_alpha * 0.4)))
        draw.ellipse([cx, eyes_y - 4, cx + 10, eyes_y + 4], fill=(220, 80, 255, int(eye_alpha * 0.4)))

        # 3. Rising Energy Particles / Flames
        for p in particles:
            rel_t = (t + p["offset_t"]) % 1.0
            # Ascend upwards
            cy = p["y"] - rel_t * p["speed"] * 1.6
            # Horizontal sway with sine wave
            cx_pos = p["x"] + 14 * math.sin(2 * math.pi * rel_t + p["phase"])

            # Fade in quickly, fade out as it reaches the top
            p_alpha = math.sin(math.pi * rel_t) ** 1.3
            cur_sz = p["size"] * (0.8 + 0.3 * (1 - rel_t))

            if 0 < cy < target_h and 0 < cx_pos < target_w:
                if p["color_type"] == "violet":
                    fill_c = (210, 90, 255, int(220 * p_alpha))
                    glow_c = (160, 40, 240, int(90 * p_alpha))
                elif p["color_type"] == "magenta":
                    fill_c = (255, 110, 230, int(230 * p_alpha))
                    glow_c = (200, 30, 180, int(95 * p_alpha))
                else:
                    fill_c = (255, 240, 255, int(250 * p_alpha))
                    glow_c = (220, 140, 255, int(110 * p_alpha))

                # Core particle
                draw.ellipse(
                    [cx_pos - cur_sz, cy - cur_sz, cx_pos + cur_sz, cy + cur_sz],
                    fill=fill_c
                )
                # Outer glow
                draw.ellipse(
                    [cx_pos - cur_sz * 2, cy - cur_sz * 2, cx_pos + cur_sz * 2, cy + cur_sz * 2],
                    fill=glow_c
                )

        # 4. Lightning Arcs
        for bolt in lightning_bolts:
            diff = (f_idx - bolt["frame"]) % num_frames
            if diff in [0, 1]:  # Flash for 2 frames
                flash_alpha = 240 if diff == 0 else 120
                pts = bolt["pts"]
                for i in range(len(pts) - 1):
                    draw.line([pts[i], pts[i + 1]], fill=(255, 230, 255, flash_alpha), width=2)
                    draw.line([pts[i], pts[i + 1]], fill=(210, 80, 255, flash_alpha // 2), width=4)

        # Merge layers
        frame_canvas = Image.alpha_composite(frame_canvas, overlay)
        rgb_frame = frame_canvas.convert("RGB")
        quantized = rgb_frame.quantize(colors=128, method=Image.Resampling.LANCZOS, dither=Image.Dither.FLOYDSTEINBERG)
        frames.append(quantized)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=True
    )
    print(f"Generated Ultra Ego live banner: {output_path} ({num_frames} frames, {target_w}x{target_h})")

if __name__ == "__main__":
    create_ultra_ego_banner("assets/clean_vegeta.jpg", "assets/header.gif", num_frames=30, fps=15)

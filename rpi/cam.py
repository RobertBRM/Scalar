import os
import signal
import subprocess
import sys
import time
import requests
from PIL import Image
from dotenv import load_dotenv
from gpiozero import Button
from picamera2 import Picamera2
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Load environment variables from .env file (if present)
load_dotenv()

# ==========================================
# CONFIGURATION & PLACEHOLDERS
# ==========================================
BUTTON_PIN = 17               # GPIO 17 (Physical Pin 11) + GND
LONG_PRESS_DURATION = 0.8     # Seconds to hold button for a "Long Press"

DEFAULT_MEASURE = 15          # Placeholder default measure
IMAGE_FILENAME = "food.jpg"   # Overwritten on every capture

# Read HOST_IP from environment variable (falls back to 192.168.1.100 if not set)
HOST_IP = os.getenv("HOST_IP", "192.168.1.100")
ANALYZE_URL = f"http://{HOST_IP}:8000/raspberry/analyze"

current_measure = DEFAULT_MEASURE
zero_reference = 0


# ==========================================
# SYSTEM & HARDWARE HELPERS
# ==========================================
def ensure_i2c_enabled():
    if not os.path.exists("/dev/i2c-1"):
        subprocess.run(["sudo", "raspi-config", "nonint", "do_i2c", "0"], check=True)
        subprocess.run(["sudo", "modprobe", "i2c-dev"], check=True)
        time.sleep(1)


def wait_for_button_action(button, hold_time=LONG_PRESS_DURATION):
    button.wait_for_press()
    start_time = time.monotonic()

    while button.is_pressed:
        if (time.monotonic() - start_time) >= hold_time:
            button.wait_for_release()
            return "LONG"
        time.sleep(0.02)

    return "SHORT"


def cleanup_hardware(button=None, picam2=None, oled=None):
    """Safely closes GPIO, camera, and OLED in any exit/error scenario."""
    if button is not None:
        try:
            button.close()
            print("[Cleanup] GPIO button closed.")
        except Exception as e:
            print(f"[Cleanup Warning] Error closing GPIO: {e}")

    if picam2 is not None:
        try:
            picam2.stop()
            picam2.close()
            print("[Cleanup] Camera stopped and closed.")
        except Exception as e:
            print(f"[Cleanup Warning] Error closing camera: {e}")

    if oled is not None:
        try:
            oled.clear()
            print("[Cleanup] OLED cleared.")
        except Exception as e:
            print(f"[Cleanup Warning] Error clearing OLED: {e}")


# ==========================================
# OLED DRAWING FUNCTIONS (NO BORDERS)
# ==========================================
def draw_status(device, title, subtitle=""):
    with canvas(device) as draw:
        draw.text((8, 16), title, fill="white")
        if subtitle:
            draw.text((8, 36), subtitle, fill="white")


def draw_menu(device, menu_items, selected_idx, net_measure):
    with canvas(device) as draw:
        draw.text((6, 4), f"MENU (Meas: {net_measure})", fill="white")
        draw.line((0, 16, 128, 16), fill="white")

        for idx, item in enumerate(menu_items):
            prefix = "> " if idx == selected_idx else "  "
            y_pos = 20 + (idx * 14)
            draw.text((10, y_pos), f"{prefix}{item}", fill="white")


def draw_nutrition_page(device, label, value, unit, page_idx, total_pages):
    with canvas(device) as draw:
        draw.text((6, 4), f"{label} ({page_idx + 1}/{total_pages})", fill="white")
        draw.line((0, 16, 128, 16), fill="white")

        display_val = f"{value} {unit}".strip()
        if len(display_val) > 18:
            draw.text((6, 22), display_val[:18], fill="white")
            draw.text((6, 34), display_val[18:36], fill="white")
        else:
            draw.text((10, 26), display_val, fill="white")

        draw.text((6, 50), "1x:Next  Hold:Back", fill="white")


# ==========================================
# API & JSON PARSING FUNCTIONS
# ==========================================
def get_weight_category(net_measure):
    if net_measure < 10:
        return "light"
    elif net_measure <= 25:
        return "medium"
    return "heavy"


def capture_and_compress(picam2, filename):
    """Captures food.jpg using default camera config, then shrinks file size for fast upload."""
    time.sleep(0.3)  # Brief pause for auto-exposure/focus
    picam2.capture_file(filename)

    with Image.open(filename) as img:
        img = img.convert("RGB")
        img.thumbnail((640, 640))
        img.save(filename, "JPEG", quality=80)


def send_image_to_host(filename, net_measure):
    weight_cat = get_weight_category(net_measure)
    print(f"[API] Uploading '{filename}' (weight_category={weight_cat}) to {ANALYZE_URL}...")

    try:
        with open(filename, "rb") as img_file:
            files = {"image": (filename, img_file, "image/jpeg")}
            data = {"weight_category": weight_cat}

            response = requests.post(ANALYZE_URL, files=files, data=data, timeout=15)
            if not response.ok:
                print(f"[API Error] Server returned {response.status_code}: {response.text}")
                return None

            res_json = response.json()
            print(f"[API] Response received: {res_json}")
            return res_json

    except Exception as e:
        print(f"[API Error] Failed to analyze image: {e}")
        return None


def process_nutrition_data(api_response):
    """
    Extracts nutrition fields from the server's JSON response.
    Returns None if the API failed or the food could not be identified.
    """
    if not api_response or api_response.get("status") != "success":
        return None

    analysis = api_response.get("analysis")
    if not analysis or not isinstance(analysis, dict):
        return None

    food_name = str(analysis.get("name", "")).strip()

    # Fail-safe check if image couldn't be identified
    invalid_names = {"", "unknown", "unidentified", "none", "null", "error", "not food"}
    if food_name.lower() in invalid_names:
        return None

    raw_fiber = analysis.get("fiber_g")
    fiber_val = float(raw_fiber) if raw_fiber is not None else 0.0

    return {
        "name": food_name,
        "cal": int(analysis.get("calories", 0)),
        "protein": float(analysis.get("protein_g", 0.0)),
        "carbs": float(analysis.get("carbs_g", 0.0)),
        "fat": float(analysis.get("fat_g", 0.0)),
        "fiber": fiber_val,
    }


# ==========================================
# SUB-LOOP FOR CYCLING NUTRITION VALUES
# ==========================================
def show_nutrition_loop(oled, button, nutrition_data):
    pages = [
        ("Name",     nutrition_data["name"],    ""),
        ("Calories", nutrition_data["cal"],     "kcal"),
        ("Protein",  nutrition_data["protein"], "g"),
        ("Carbs",    nutrition_data["carbs"],   "g"),
        ("Fat",      nutrition_data["fat"],     "g"),
        ("Fiber",    nutrition_data["fiber"],   "g"),
    ]

    page_idx = 0
    total_pages = len(pages)

    while True:
        label, val, unit = pages[page_idx]
        print(f"[Display] {label}: {val} {unit}".strip())
        draw_nutrition_page(oled, label, val, unit, page_idx, total_pages)

        action = wait_for_button_action(button)
        if action == "SHORT":
            page_idx = (page_idx + 1) % total_pages
        elif action == "LONG":
            print("[Display] Returning to Main Menu...")
            break


# ==========================================
# MAIN APPLICATION LOOP
# ==========================================
def main():
    global current_measure, zero_reference

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    oled = None
    button = None
    picam2 = None

    def handle_exit_signal(signum, frame):
        print(f"\n[Signal {signum}] Stopping program and releasing GPIO...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_exit_signal)
    signal.signal(signal.SIGHUP, handle_exit_signal)

    try:
        ensure_i2c_enabled()
        serial = i2c(port=1, address=0x3C)
        oled = ssd1306(serial, width=128, height=64)

        button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.05)

        draw_status(oled, "Starting Camera...")
        picam2 = Picamera2()
        picam2.configure(picam2.create_still_configuration())
        picam2.start()
        time.sleep(2)

        menu_items = ["Reset", "Clear", "Capture"]
        selected_idx = 0

        print(f"Using API Endpoint: {ANALYZE_URL}")
        print("System ready! Short press = cycle, Long press = select.")

        while True:
            net_measure = current_measure - zero_reference
            draw_menu(oled, menu_items, selected_idx, net_measure)

            action = wait_for_button_action(button)

            if action == "SHORT":
                selected_idx = (selected_idx + 1) % len(menu_items)

            elif action == "LONG":
                choice = menu_items[selected_idx]

                if choice == "Reset":
                    current_measure = DEFAULT_MEASURE
                    zero_reference = 0
                    print(f"[Reset] Measure reset to default ({current_measure})")
                    draw_status(oled, "Measure Reset!", f"Default: {current_measure}")
                    time.sleep(1.5)

                elif choice == "Clear":
                    zero_reference = current_measure
                    print("[Clear] Set 0 reference for measure (Net = 0)")
                    draw_status(oled, "Cleared!", "Set 0 reference")
                    time.sleep(1.5)

                elif choice == "Capture":
                    draw_status(oled, "Processing...")

                    capture_and_compress(picam2, IMAGE_FILENAME)
                    print(f"[Capture] Replaced and compressed {IMAGE_FILENAME}")

                    api_response = send_image_to_host(IMAGE_FILENAME, net_measure)
                    nutrition_data = process_nutrition_data(api_response)

                    if nutrition_data is None:
                        print("[Fail-Safe] Image could not be identified or API error.")
                        draw_status(oled, "Cannot Identify", "Press to retry")
                        wait_for_button_action(button)
                    else:
                        show_nutrition_loop(oled, button, nutrition_data)

    except KeyboardInterrupt:
        print("\n[Exit] KeyboardInterrupt received.")
    except Exception as e:
        print(f"\n[Fatal Error] Unexpected error occurred: {e}")
    finally:
        cleanup_hardware(button=button, picam2=picam2, oled=oled)


if __name__ == "__main__":
    main()
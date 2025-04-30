# ShadowPlay-Style Notifications for OBS

A lightweight OBS Studio script that shows desktop-style notifications whenever you start or stop recording, or enable/save the replay buffer. Fully customizable icons, positions, animations and timings.

---

## 🔍 Overview

When you start/stop recording or use the Replay Buffer in OBS, this script pops up a small overlay in the corner of your screen:

- **Recording Started** ▶️  
- **Recording Saved** 💾  
- **Replay Enabled** 🔄  
- **Replay Saved** 📥  

You can choose your own PNG/GIF/JPG icons, slide the notification in from any edge, pick its corner placement, adjust size, padding, fonts and more.

---

## ⚙️ Features

- **Four event types**:  
  - Recording started  
  - Recording stopped (saved)  
  - Replay buffer enabled  
  - Replay buffer saved
- **Custom icons** (PNG, GIF, JPG) for each event  
- **Auto-scaling** of icons up to a configurable maximum size  
- **Slide animations** from left/right/top/bottom or no animation  
- **Corner positioning**: top-left, top-right, bottom-left, bottom-right  
- **Configurable offsets**, padding, width/height overrides  
- **Fade-in/out** and display duration settings  
- **Custom font family & size** for the text label  
- **Transparent background** via Tkinter’s `-transparentcolor` support  
- **Thread-safe**: runs in a separate daemon thread to avoid blocking OBS

---

## 🎯 Requirements

- **OBS Studio** 31.0.3 or newer, with Python scripting enabled  
- **Python 3.x** installed on your system (but it was tested on 3.11.6) 
- **Tkinter** module available (usually bundled with standard Python)  

---

## 🚀 Installation

1. **Download** the script file  
   Save `obs_overlay.py` into your OBS scripts folder (e.g. `%AppData%\obs-studio\scripts\` on Windows, `~/.config/obs-studio/scripts/` on Linux/macOS).

2. **Add the script in OBS**  
   - Open OBS Studio  
   - Go to **Tools → Scripts**  
   - Click **‘+’**, navigate to and select `obs_overlay.py`

3. **Configure your icons & settings**  
   In the Scripts dialog, select `obs_overlay.py` and fill in paths for:
   - Icon: Recording Started  
   - Icon: Recording Saved  
   - Icon: Replay Enabled  
   - Icon: Replay Saved  

   Adjust other parameters (max icon size, padding, slide-in steps, position, etc.) as desired.

---

## 🛠 Configuration Options

| Property                   | Description                                                      | Default       |
|----------------------------|------------------------------------------------------------------|---------------|
| **Icon: Recording Started**| Path to PNG/GIF/JPG for “Recording Started”                      | *(empty)*     |
| **Icon: Recording Saved**  | Path to image for “Recording Saved”                              | *(empty)*     |
| **Icon: Replay Enabled**   | Path to image for “Replay Enabled”                               | *(empty)*     |
| **Icon: Replay Saved**     | Path to image for “Replay Saved”                                 | *(empty)*     |
| **Max icon size (px)**     | Largest width/height for auto-scaling                            | 40            |
| **Icon-text padding (px)** | Horizontal padding between icon and text                         | 0             |
| **Overlay width/height**   | Fixed dimensions (0 = auto-size)                                 | 0 / 0         |
| **Offset X/Y (px)**        | Additional horizontal/vertical shift                             | 0 / 0         |
| **Slide steps**            | Number of animation frames for slide-in                          | 35            |
| **Slide interval (ms)**    | Delay between animation frames                                   | 10            |
| **Overlay position**       | `top_right` / `top_left` / `bottom_left` / `bottom_right`        | `top_right`   |
| **Slide from**             | `none` / `left` / `right` / `top` / `bottom`                     | `right`       |
| **Font size**              | Label font point size                                            | 11            |

---

## ▶️ Usage

1. **Start recording** in OBS → you’ll see **“Recording Started”** with your chosen icon.  
2. **Stop recording** → **“Recording Saved”**.  
3. **Enable Replay Buffer** → **“Replay Enabled”**.  
4. **Save Replay Buffer** → **“Replay Saved”**.

Notifications slide in, stay on-screen for a few seconds, then fade out automatically.

---

## 🎨 Customization

- Swap in any image format supported by Tkinter’s `PhotoImage` (PNG/GIF/JPG).  
- Tweak `overlay_size` to control max icon dimensions; icons larger than this are subsampled.  
- Change slide origin or disable slide entirely.  
- Adjust display duration and fade-out speed in the script constants if you want more control.

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome! Please open an issue or submit a pull request on GitHub.

---

*Created by Daniluk2*  

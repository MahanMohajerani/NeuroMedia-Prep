#!/usr/bin/env python3
"""NeuroMedia Prep desktop application."""

from __future__ import annotations

import html
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


APP_NAME = "NeuroMedia Prep"
APP_VERSION = "1.0.0"
ORGANIZATION_NAME = "NeuroMediaPrep"
RECOMMENDED_FREE_SPACE_BYTES = 10 * 1024**3
RECOMMENDED_MEMORY_BYTES = 4 * 1024**3
SETUP_VERSION_KEY = "first_run_completed_version"


try:
    from PySide6.QtCore import (
        QCoreApplication,
        QEvent,
        QSize,
        QProcess,
        QSettings,
        Qt,
        QTimer,
        QUrl,
        Signal,
    )
    from PySide6.QtGui import (
        QBrush,
        QCloseEvent,
        QColor,
        QDesktopServices,
        QFont,
        QIcon,
    )
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
    from PySide6.QtMultimediaWidgets import QVideoWidget
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QAbstractSpinBox,
        QApplication,
        QCheckBox,
        QColorDialog,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QDoubleSpinBox,
        QFileDialog,
        QFontDialog,
        QFormLayout,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QProgressBar,
        QPushButton,
        QRadioButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QSpinBox,
        QSplitter,
        QStyle,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    message = (
        "NeuroMedia Prep requires PySide6.\n\n"
        "Install it in Command Prompt with:\n"
        "py -m pip install PySide6"
    )
    print(message, file=sys.stderr)
    if os.name == "nt":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, message, APP_NAME, 0x10)
        except Exception:
            pass
    raise SystemExit(1)


DEVICE_PROFILES: list[dict[str, Any]] = [
    {
        "id": "device_bioexplorer",
        "name": "BioExplorer",
        "builtin": True,
        "profile_type": "device",
        "format_label": "AVI",
        "extension": "avi",
        "video_codec": "mpeg4",
        "audio_codec": "libmp3lame",
        "quality_option": "-q:v",
        "quality_value": 4,
        "preset": "",
        "max_width": 1280,
        "max_height": 720,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-b:a", "192k"],
    },
    {
        "id": "device_eeger_dvdgame",
        "name": "EEGer DVDGame",
        "builtin": True,
        "profile_type": "device",
        "format_label": "MP4",
        "extension": "mp4",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "quality_option": "-crf",
        "quality_value": 20,
        "preset": "medium",
        "max_width": 1920,
        "max_height": 1080,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-movflags", "+faststart"],
    },
    {
        "id": "device_eeger_zukor",
        "name": "EEGer Zukor Media Player",
        "builtin": True,
        "profile_type": "device",
        "format_label": "MP4",
        "extension": "mp4",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "quality_option": "-crf",
        "quality_value": 20,
        "preset": "medium",
        "max_width": 1920,
        "max_height": 1080,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-movflags", "+faststart"],
    },
    {
        "id": "device_cygnet",
        "name": "Cygnet Advanced Media Player",
        "builtin": True,
        "profile_type": "device",
        "format_label": "MP4",
        "extension": "mp4",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "quality_option": "-crf",
        "quality_value": 20,
        "preset": "medium",
        "max_width": 1920,
        "max_height": 1080,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-movflags", "+faststart"],
    },
    {
        "id": "device_brainmaster_mmp",
        "name": "BrainMaster MMP",
        "builtin": True,
        "profile_type": "device",
        "format_label": "AVI",
        "extension": "avi",
        "video_codec": "mpeg4",
        "audio_codec": "libmp3lame",
        "quality_option": "-q:v",
        "quality_value": 4,
        "preset": "",
        "max_width": 1280,
        "max_height": 720,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-b:a", "192k"],
    },
    {
        "id": "device_biotrace",
        "name": "BioTrace+",
        "builtin": True,
        "profile_type": "device",
        "format_label": "AVI",
        "extension": "avi",
        "video_codec": "mpeg4",
        "audio_codec": "libmp3lame",
        "quality_option": "-q:v",
        "quality_value": 4,
        "preset": "",
        "max_width": 1280,
        "max_height": 720,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-b:a", "192k"],
    },
    {
        "id": "device_brain_trainer_2",
        "name": "Brain-Trainer BT2",
        "builtin": True,
        "profile_type": "device",
        "format_label": "MP4",
        "extension": "mp4",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "quality_option": "-crf",
        "quality_value": 20,
        "preset": "medium",
        "max_width": 1920,
        "max_height": 1080,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-movflags", "+faststart"],
    },
    {
        "id": "device_brainbay",
        "name": "BrainBay",
        "builtin": True,
        "profile_type": "device",
        "format_label": "AVI",
        "extension": "avi",
        "video_codec": "mpeg4",
        "audio_codec": "libmp3lame",
        "quality_option": "-q:v",
        "quality_value": 4,
        "preset": "",
        "max_width": 1280,
        "max_height": 720,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-b:a", "192k"],
    },
]


FORMAT_PROFILES: list[dict[str, Any]] = [
    {
        "id": "format_mp4",
        "name": "MP4",
        "builtin": True,
        "profile_type": "format",
        "format_label": "MP4",
        "extension": "mp4",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "quality_option": "-crf",
        "quality_value": 20,
        "preset": "medium",
        "max_width": 1920,
        "max_height": 1080,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": True,
        "extra_output_args": ["-movflags", "+faststart"],
    },
    {
        "id": "format_mkv",
        "name": "MKV",
        "builtin": True,
        "profile_type": "format",
        "format_label": "MKV",
        "extension": "mkv",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "quality_option": "-crf",
        "quality_value": 20,
        "preset": "medium",
        "max_width": 1920,
        "max_height": 1080,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": True,
        "extra_output_args": [],
    },
    {
        "id": "format_avi",
        "name": "AVI",
        "builtin": True,
        "profile_type": "format",
        "format_label": "AVI",
        "extension": "avi",
        "video_codec": "mpeg4",
        "audio_codec": "libmp3lame",
        "quality_option": "-q:v",
        "quality_value": 4,
        "preset": "",
        "max_width": 1280,
        "max_height": 720,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-b:a", "192k"],
    },
    {
        "id": "format_mpeg",
        "name": "MPEG",
        "builtin": True,
        "profile_type": "format",
        "format_label": "MPEG",
        "extension": "mpg",
        "video_codec": "mpeg2video",
        "audio_codec": "mp2",
        "quality_option": "-q:v",
        "quality_value": 4,
        "preset": "",
        "max_width": 720,
        "max_height": 576,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-b:a", "192k"],
    },
    {
        "id": "format_wmv",
        "name": "WMV",
        "builtin": True,
        "profile_type": "format",
        "format_label": "WMV",
        "extension": "wmv",
        "video_codec": "wmv2",
        "audio_codec": "wmav2",
        "quality_option": "-q:v",
        "quality_value": 3,
        "preset": "",
        "max_width": 1280,
        "max_height": 720,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": False,
        "extra_output_args": ["-b:a", "192k"],
    },
    {
        "id": "format_mov",
        "name": "MOV",
        "builtin": True,
        "profile_type": "format",
        "format_label": "MOV",
        "extension": "mov",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "quality_option": "-crf",
        "quality_value": 20,
        "preset": "medium",
        "max_width": 1920,
        "max_height": 1080,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": True,
        "extra_output_args": ["-movflags", "+faststart"],
    },
    {
        "id": "format_webm",
        "name": "WebM",
        "builtin": True,
        "profile_type": "format",
        "format_label": "WebM",
        "extension": "webm",
        "video_codec": "libvpx-vp9",
        "audio_codec": "libopus",
        "quality_option": "-crf",
        "quality_value": 31,
        "preset": "",
        "max_width": 1920,
        "max_height": 1080,
        "pixel_format": "yuv420p",
        "audio_channels": 2,
        "external_subtitles": True,
        "extra_output_args": ["-b:v", "0"],
    },
]


BUILTIN_PROFILES = [*DEVICE_PROFILES, *FORMAT_PROFILES]

# Documented container support used to validate the built-in device presets.
DEVICE_PROFILE_CONTAINERS: dict[str, set[str]] = {
    "device_bioexplorer": {"avi", "mpg", "mpeg", "wmv"},
    "device_eeger_dvdgame": {"mp4"},
    "device_eeger_zukor": {"mp4", "avi", "mov", "mkv", "wmv", "webm", "mpg", "mpeg"},
    "device_cygnet": {"mp4", "avi", "mov", "mkv", "wmv", "webm", "mpg", "mpeg"},
    "device_brainmaster_mmp": {"avi", "mpg", "mpeg"},
    "device_biotrace": {"avi", "wmv", "divx"},
    "device_brain_trainer_2": {"mp4", "mov", "avi", "webm"},
    "device_brainbay": {"avi", "wmv"},
}

# The picker does not restrict input by extension. FFprobe decides whether the
# selected file contains a usable video stream.
VIDEO_FILTER = (
    "All files (*.*);;Common video files ("
    "*.3g2 *.3gp *.asf *.avi *.dat *.divx *.dv *.f4v *.flv *.gxf *.m2p "
    "*.m2ts *.m2v *.m4v *.mkv *.mod *.mov *.mp4 *.mpeg *.mpg *.mts *.mxf "
    "*.ogm *.ogv *.qt *.rm *.rmvb *.ts *.vob *.webm *.wmv)"
)


def app_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def windows_creation_flags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0


def locate_binary(name: str, configured: str = "") -> str | None:
    executable = f"{name}.exe" if os.name == "nt" else name
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.extend(
        [
            app_directory() / executable,
            app_directory() / "bin" / executable,
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate.resolve())
    return shutil.which(executable) or shutil.which(name)


def ffmpeg_has_filter(ffmpeg_path: str, filter_name: str) -> bool:
    try:
        result = subprocess.run(
            [
                ffmpeg_path,
                "-hide_banner",
                "-h",
                f"filter={filter_name}",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            creationflags=windows_creation_flags(),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False

    output = f"{result.stdout}\n{result.stderr}".lower()

    return (
        result.returncode == 0
        and f"filter {filter_name.lower()}" in output
        and "unknown filter" not in output
    )


def parse_time_text(text: str) -> int:
    """
    Parse SS, MM:SS, or HH:MM:SS into whole seconds.

    Examples:
        "1"        -> 1 second
        "1:30"     -> 90 seconds
        "01:30:25" -> 5425 seconds
    """
    value = text.strip()
    if not value:
        raise ValueError("Enter a time.")
    if not re.fullmatch(r"\d+(?::\d{1,2}){0,2}", value):
        raise ValueError("Use SS, MM:SS, or HH:MM:SS.")

    parts = [int(part) for part in value.split(":")]
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        minutes, seconds = parts
        if seconds > 59:
            raise ValueError("Seconds must be between 00 and 59.")
        return minutes * 60 + seconds

    hours, minutes, seconds = parts
    if minutes > 59 or seconds > 59:
        raise ValueError("Minutes and seconds must be between 00 and 59.")
    return hours * 3600 + minutes * 60 + seconds


def format_time(seconds: float, include_ms: bool = False) -> str:
    seconds = max(0.0, float(seconds))
    whole = int(seconds)
    hours, remainder = divmod(whole, 3600)
    minutes, secs = divmod(remainder, 60)
    result = f"{hours:02d}:{minutes:02d}:{secs:02d}"
    if include_ms:
        milliseconds = int(round((seconds - whole) * 1000))
        if milliseconds >= 1000:
            whole += 1
            hours, remainder = divmod(whole, 3600)
            minutes, secs = divmod(remainder, 60)
            result = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            milliseconds = 0
        result += f".{milliseconds:03d}"
    return result


def ffmpeg_time(seconds: float) -> str:
    return f"{max(0.0, float(seconds)):.3f}"


def safe_filename(value: str, fallback: str = "video") -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return (cleaned[:120] or fallback).rstrip(" .")


def unique_directory(root: Path, movie_stem: str) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base = root / f"{safe_filename(movie_stem)}__{timestamp}"
    candidate = base
    suffix = 2
    while candidate.exists():
        candidate = Path(f"{base}_{suffix}")
        suffix += 1
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def parse_fraction(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        if "/" in value:
            numerator, denominator = value.split("/", 1)
            denominator_value = float(denominator)
            return float(numerator) / denominator_value if denominator_value else 0.0
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def probe_media(path: Path, ffprobe_path: str) -> dict[str, Any]:
    """Read normalized media metadata with FFprobe."""
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        (
            "format=duration,format_name,bit_rate,size,start_time:"
            "stream=index,codec_type,codec_name,width,height,"
            "avg_frame_rate,r_frame_rate,sample_rate,channels,pix_fmt,"
            "color_transfer,field_order,nb_frames,duration"
        ),
        "-of",
        "json",
        str(path),
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
            creationflags=windows_creation_flags(),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("FFprobe timed out while reading the video.") from exc
    except OSError as exc:
        raise RuntimeError(f"Could not start FFprobe: {exc}") from exc

    if result.returncode != 0:
        detail = result.stderr.strip() or "FFprobe could not read this file."
        raise RuntimeError(detail)

    try:
        raw = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("FFprobe returned invalid metadata.") from exc

    format_info = raw.get("format") or {}
    streams = raw.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not video:
        raise RuntimeError("No video stream was found in this file.")

    try:
        duration = float(format_info.get("duration") or 0)
    except (TypeError, ValueError):
        duration = 0.0
    if duration <= 0:
        raise RuntimeError("The video duration could not be determined.")

    try:
        bit_rate = int(format_info.get("bit_rate") or 0)
    except (TypeError, ValueError):
        bit_rate = 0

    average_frame_rate = parse_fraction(str(video.get("avg_frame_rate") or ""))
    real_frame_rate = parse_fraction(str(video.get("r_frame_rate") or ""))

    return {
        "path": str(path),
        "duration": duration,
        "format_name": str(format_info.get("format_name") or ""),
        "bit_rate": bit_rate,
        "size": safe_int(format_info.get("size")),
        "video_codec": str(video.get("codec_name") or ""),
        "audio_codec": str(audio.get("codec_name") or "") if audio else "",
        "width": safe_int(video.get("width")),
        "height": safe_int(video.get("height")),
        "frame_rate": average_frame_rate or real_frame_rate,
        "average_frame_rate": average_frame_rate,
        "real_frame_rate": real_frame_rate,
        "pixel_format": str(video.get("pix_fmt") or ""),
        "color_transfer": str(video.get("color_transfer") or ""),
        "field_order": str(video.get("field_order") or ""),
        "video_frame_count": safe_int(video.get("nb_frames")),
        "audio_channels": safe_int(audio.get("channels")) if audio else 0,
        "audio_sample_rate": safe_int(audio.get("sample_rate")) if audio else 0,
        "raw": raw,
    }


def target_codec_name(encoder: str) -> str:
    aliases = {
        "libx264": "h264",
        "h264_nvenc": "h264",
        "h264_qsv": "h264",
        "libx265": "hevc",
        "hevc_nvenc": "hevc",
        "libvpx": "vp8",
        "libvpx-vp9": "vp9",
        "libaom-av1": "av1",
        "libopus": "opus",
        "libvorbis": "vorbis",
        "libmp3lame": "mp3",
    }
    return aliases.get(encoder, encoder)


def format_bytes(byte_count: int) -> str:
    value = float(max(0, byte_count))
    units = ("B", "KB", "MB", "GB", "TB")
    for unit in units:
        if value < 1024 or unit == units[-1]:
            precision = 0 if unit in {"B", "KB"} else 2
            return f"{value:.{precision}f} {unit}"
        value /= 1024
    return f"{value:.2f} TB"


def estimate_output_bytes(input_info: dict[str, Any], total_seconds: float) -> int:
    bit_rate = safe_int(input_info.get("bit_rate"))
    if bit_rate <= 0:
        size = safe_int(input_info.get("size"))
        duration = float(input_info.get("duration") or 0)
        if size > 0 and duration > 0:
            bit_rate = int((size * 8) / duration)
    if bit_rate <= 0:
        bit_rate = 8_000_000
    return int((bit_rate * max(0.0, total_seconds) / 8) * 1.35)


def contains_rtl_text(value: str) -> bool:
    return bool(
        re.search(
            r"[\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]",
            value,
        )
    )


def ass_color(hex_color: str) -> str:
    color = QColor(hex_color)
    if not color.isValid():
        color = QColor("#FFFFFF")
    return f"&H00{color.blue():02X}{color.green():02X}{color.red():02X}"


def escape_subtitles_filter_path(path: Path) -> str:
    value = str(path.resolve()).replace("\\", "/")
    value = value.replace(":", r"\:")
    value = value.replace("'", r"\'")
    value = value.replace("[", r"\[").replace("]", r"\]")
    value = value.replace(",", r"\,")
    return value


def detect_scene_change_candidates(
    path: Path,
    ffmpeg_path: str,
    center_seconds: float,
    radius_seconds: float = 60.0,
    threshold: float = 0.32,
) -> list[float]:
    """Find scene changes around one planned cut without scanning the full movie."""
    window_start = max(0.0, center_seconds - radius_seconds)
    window_duration = max(1.0, radius_seconds * 2)
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel",
        "info",
        "-ss",
        ffmpeg_time(window_start),
        "-i",
        str(path),
        "-t",
        ffmpeg_time(window_duration),
        "-an",
        "-vf",
        f"select='gt(scene,{threshold})',showinfo",
        "-vsync",
        "vfr",
        "-f",
        "null",
        "-",
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            creationflags=windows_creation_flags(),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []

    values: list[float] = []
    for match in re.finditer(r"pts_time:([+-]?\d+(?:\.\d+)?)", result.stderr):
        try:
            timestamp = float(match.group(1))
        except ValueError:
            continue
        absolute = window_start + timestamp
        if abs(absolute - center_seconds) <= radius_seconds + 2:
            values.append(max(0.0, absolute))
    return sorted({round(value, 3) for value in values})


def subtitle_gap_candidates(
    cues: list[dict[str, Any]],
    center_seconds: float,
    radius_seconds: float,
    offset_seconds: float = 0.0,
) -> list[float]:
    candidates: list[float] = []
    shifted = sorted(
        (
            float(cue["start"]) + offset_seconds,
            float(cue["end"]) + offset_seconds,
        )
        for cue in cues
    )
    for current, following in zip(shifted, shifted[1:]):
        gap_start = current[1]
        gap_end = following[0]
        if gap_end - gap_start < 0.35:
            continue
        midpoint = (gap_start + gap_end) / 2
        if abs(midpoint - center_seconds) <= radius_seconds:
            candidates.append(round(midpoint, 3))
    return sorted(set(candidates))


def build_segments(
    start: float,
    end: float,
    segment_seconds: float,
    overlap_mode: str = "none",
    overlap_seconds: float = 0.0,
) -> list[dict[str, float]]:
    """Build session ranges with no overlap, a fixed overlap, or automatic overlap."""
    if start < 0 or end <= start or segment_seconds <= 0:
        return []

    usable = end - start
    if usable <= segment_seconds:
        return [{"start": start, "end": end, "duration": usable}]

    if overlap_mode == "auto":
        count = math.ceil(usable / segment_seconds)
        step = (usable - segment_seconds) / (count - 1)
        starts = [start + (index * step) for index in range(count)]
    else:
        if overlap_mode == "custom":
            if overlap_seconds < 0 or overlap_seconds >= segment_seconds:
                return []
            step = segment_seconds - overlap_seconds
        else:
            step = segment_seconds

        starts = []
        cursor = float(start)
        while cursor < end - 0.001:
            starts.append(cursor)
            cursor += step

    segments: list[dict[str, float]] = []
    for segment_start in starts:
        segment_end = min(segment_start + segment_seconds, end)
        segments.append(
            {
                "start": segment_start,
                "end": segment_end,
                "duration": segment_end - segment_start,
            }
        )
    return segments


def parse_subtitle_timestamp(value: str) -> float:
    cleaned = value.strip().replace(",", ".")
    parts = cleaned.split(":")

    if len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        raise ValueError(f"Invalid subtitle timestamp: {value}")

    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def decode_subtitle_file(path: Path) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-16", "cp1256", "cp1252"):
        try:
            text = path.read_text(encoding=encoding)
            return text, encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError("The subtitle text encoding could not be read.")


def read_subtitle_file(path: Path) -> list[dict[str, Any]]:
    """Read SRT or WebVTT cues for previewing and segment export."""
    text, _encoding = decode_subtitle_file(path)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n{2,}", text.strip())
    timestamp_pattern = re.compile(
        r"(?P<start>\d{1,2}:\d{2}(?::\d{2})?[,.]\d{3})\s*-->\s*"
        r"(?P<end>\d{1,2}:\d{2}(?::\d{2})?[,.]\d{3})"
    )

    cues: list[dict[str, Any]] = []

    for block in blocks:
        lines = [line.strip("\ufeff") for line in block.splitlines()]
        timing_index = next(
            (index for index, line in enumerate(lines) if "-->" in line),
            None,
        )

        if timing_index is None:
            continue

        match = timestamp_pattern.search(lines[timing_index])
        if not match:
            continue

        start = parse_subtitle_timestamp(match.group("start"))
        end = parse_subtitle_timestamp(match.group("end"))
        cue_text = "\n".join(lines[timing_index + 1 :]).strip()

        if cue_text and end > start:
            cues.append(
                {
                    "start": start,
                    "end": end,
                    "text": cue_text,
                }
            )

    if not cues:
        raise ValueError("No valid subtitle cues were found.")

    return cues


def srt_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)

    return (
        f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},"
        f"{milliseconds:03d}"
    )


def write_segment_subtitles(
    path: Path,
    cues: list[dict[str, Any]],
    segment_start: float,
    segment_end: float,
    offset_seconds: float = 0.0,
) -> int:
    """Write cues intersecting a segment, clipped and shifted to start at zero."""
    blocks: list[str] = []

    for cue in cues:
        shifted_start = float(cue["start"]) + offset_seconds
        shifted_end = float(cue["end"]) + offset_seconds
        clipped_start = max(shifted_start, segment_start)
        clipped_end = min(shifted_end, segment_end)

        if clipped_end <= clipped_start:
            continue

        relative_start = clipped_start - segment_start
        relative_end = clipped_end - segment_start

        blocks.append(
            f"{len(blocks) + 1}\n"
            f"{srt_timestamp(relative_start)} --> "
            f"{srt_timestamp(relative_end)}\n"
            f"{cue['text']}"
        )

    subtitle_text = "\n\n".join(blocks)
    if blocks:
        subtitle_text += "\n"

    path.write_text(subtitle_text, encoding="utf-8-sig")
    return len(blocks)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def tool_version(executable: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [executable, "-version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            creationflags=windows_creation_flags(),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)

    first_line = next(
        (line.strip() for line in result.stdout.splitlines() if line.strip()),
        "No version information returned.",
    )
    return result.returncode == 0, first_line


def ffmpeg_encoder_names(ffmpeg_path: str) -> set[str]:
    try:
        result = subprocess.run(
            [ffmpeg_path, "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            creationflags=windows_creation_flags(),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return set()

    return {
        match.group(1)
        for line in result.stdout.splitlines()
        if (match := re.match(r"^\s*[A-Z\.]{6}\s+(\S+)", line))
    }


def ffmpeg_input_capability_counts(ffmpeg_path: str) -> tuple[int, int]:
    def run_listing(option: str) -> str:
        try:
            result = subprocess.run(
                [ffmpeg_path, "-hide_banner", option],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                creationflags=windows_creation_flags(),
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return result.stdout

    demuxers = {
        match.group(1)
        for line in run_listing("-demuxers").splitlines()
        if (match := re.match(r"^\s*D\s+(\S+)", line))
    }
    video_decoders = {
        match.group(1)
        for line in run_listing("-decoders").splitlines()
        if (match := re.match(r"^\s*V[A-Z\.]{5}\s+(\S+)", line))
    }
    return len(demuxers), len(video_decoders)


def validate_profile_definitions() -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    allowed_label_mismatches = {("mpg", "mpeg")}

    for profile in BUILTIN_PROFILES:
        profile_id = str(profile.get("id", "")).strip()
        name = str(profile.get("name", "Unnamed profile"))
        extension = str(profile.get("extension", "")).lower().lstrip(".")
        format_label = str(profile.get("format_label", "")).lower()

        if not profile_id:
            errors.append(f"{name}: missing profile ID")
        elif profile_id in seen_ids:
            errors.append(f"{name}: duplicate profile ID {profile_id}")
        seen_ids.add(profile_id)

        if not re.fullmatch(r"[a-z0-9]+", extension):
            errors.append(f"{name}: invalid extension {extension!r}")
        if format_label != extension and (extension, format_label) not in allowed_label_mismatches:
            errors.append(
                f"{name}: label {format_label.upper()} does not match .{extension}"
            )

        for field in ("video_codec", "audio_codec", "quality_value"):
            if field not in profile:
                errors.append(f"{name}: missing {field}")

        if profile.get("profile_type") == "device":
            supported = DEVICE_PROFILE_CONTAINERS.get(profile_id)
            if supported is None:
                errors.append(f"{name}: no compatibility mapping")
            elif extension not in supported:
                errors.append(
                    f"{name}: .{extension} is outside the documented container list"
                )

    return errors


def _profile_recipe_key(profile: dict[str, Any]) -> tuple[Any, ...]:
    extra_args = profile.get("extra_output_args", [])
    return (
        str(profile.get("extension", "")).lower(),
        str(profile.get("video_codec", "")),
        str(profile.get("audio_codec", "")),
        str(profile.get("quality_option", "")),
        int(profile.get("quality_value", 0)),
        str(profile.get("preset", "")),
        str(profile.get("pixel_format", "")),
        int(profile.get("audio_channels", 0)),
        tuple(str(value) for value in extra_args if isinstance(extra_args, list)),
    )


def test_profile_recipe(
    ffmpeg_path: str,
    ffprobe_path: str,
    profile: dict[str, Any],
    directory: Path,
) -> tuple[bool, str]:
    extension = str(profile.get("extension", "mp4")).lower().lstrip(".")
    output_path = directory / f"profile_test.{extension}"
    video_codec = str(profile.get("video_codec", "libx264"))
    audio_codec = str(profile.get("audio_codec", "aac"))

    command = [
        ffmpeg_path,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=320x180:r=25:d=1.0",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=44100:cl=stereo",
        "-t",
        "1.0",
        "-shortest",
        "-c:v",
        video_codec,
    ]

    quality_option = str(profile.get("quality_option", ""))
    if quality_option:
        command.extend([quality_option, str(int(profile.get("quality_value", 20)))])

    preset = str(profile.get("preset", ""))
    if preset and video_codec in {"libx264", "libx265"}:
        command.extend(["-preset", preset])

    pixel_format = str(profile.get("pixel_format", ""))
    if pixel_format:
        command.extend(["-pix_fmt", pixel_format])

    if audio_codec.lower() == "none":
        command.append("-an")
    else:
        command.extend(["-c:a", audio_codec])
        channels = int(profile.get("audio_channels", 0))
        if channels:
            command.extend(["-ac", str(channels)])

    extra_args = profile.get("extra_output_args", [])
    if isinstance(extra_args, list):
        command.extend(str(value) for value in extra_args)
    command.append(str(output_path))

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            creationflags=windows_creation_flags(),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)

    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        return False, detail[-1] if detail else "FFmpeg returned an error."

    try:
        info = probe_media(output_path, ffprobe_path)
    except RuntimeError as exc:
        return False, str(exc)

    expected_video = target_codec_name(video_codec)
    expected_audio = target_codec_name(audio_codec)
    if expected_video and info.get("video_codec") != expected_video:
        return False, f"created {info.get('video_codec')}, expected {expected_video}"
    if expected_audio not in {"", "none"} and info.get("audio_codec") != expected_audio:
        return False, f"created {info.get('audio_codec')}, expected {expected_audio}"
    return True, "encoded and validated"


def test_builtin_output_profiles(
    ffmpeg_path: str,
    ffprobe_path: str,
) -> tuple[int, list[str]]:
    recipes: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for profile in BUILTIN_PROFILES:
        recipes.setdefault(_profile_recipe_key(profile), []).append(profile)

    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="neuromedia_profile_test_") as temporary:
        root = Path(temporary)
        for index, profiles in enumerate(recipes.values(), start=1):
            recipe_directory = root / str(index)
            recipe_directory.mkdir()
            success, detail = test_profile_recipe(
                ffmpeg_path,
                ffprobe_path,
                profiles[0],
                recipe_directory,
            )
            if not success:
                names = ", ".join(str(profile.get("name")) for profile in profiles)
                failures.append(f"{names}: {detail}")

    return len(recipes), failures


def test_unicode_subtitle_rendering(ffmpeg_path: str) -> tuple[bool, str]:
    if not ffmpeg_has_filter(ffmpeg_path, "subtitles"):
        return False, "The subtitles/libass filter is unavailable."

    with tempfile.TemporaryDirectory(prefix="neuromedia_subtitle_test_") as temporary:
        root = Path(temporary)
        subtitle_path = root / "آزمایش_زیرنویس.srt"
        output_path = root / "subtitle_test.avi"
        subtitle_path.write_text(
            "1\n00:00:00,000 --> 00:00:00,500\nEnglish subtitle test\nآزمایش زیرنویس فارسی\n",
            encoding="utf-8-sig",
        )
        filter_value = (
            "subtitles="
            f"filename='{escape_subtitles_filter_path(subtitle_path)}':"
            "charenc=UTF-8:"
            "force_style='FontName=Arial,FontSize=24'"
        )
        command = [
            ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=320x180:r=25:d=0.6",
            "-vf",
            filter_value,
            "-t",
            "0.6",
            "-an",
            "-c:v",
            "mpeg4",
            "-q:v",
            "5",
            str(output_path),
        ]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                creationflags=windows_creation_flags(),
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, str(exc)

        if result.returncode != 0 or not output_path.is_file():
            lines = [line for line in result.stderr.splitlines() if line.strip()]
            return False, lines[-1] if lines else "Subtitle rendering failed."
        return True, "English and Persian Unicode subtitles rendered successfully."


def test_directory_write(path: Path) -> tuple[bool, str]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix="neuromedia_write_test_",
            suffix=".tmp",
            dir=path,
            delete=False,
        ) as handle:
            test_path = Path(handle.name)
            handle.write(b"NeuroMedia Prep")
        test_path.unlink()
    except OSError as exc:
        return False, str(exc)
    return True, "Write test passed."

def total_physical_memory_bytes() -> int | None:
    if os.name == "nt":
        try:
            import ctypes

            class MemoryStatusEx(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            status = MemoryStatusEx()
            status.dwLength = ctypes.sizeof(status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return int(status.ullTotalPhys)
        except (AttributeError, OSError):
            return None

    try:
        page_size = int(os.sysconf("SC_PAGE_SIZE"))
        page_count = int(os.sysconf("SC_PHYS_PAGES"))
    except (AttributeError, OSError, TypeError, ValueError):
        return None
    return page_size * page_count if page_size > 0 and page_count > 0 else None


LOGO_ASSET_NAMES = (
    "neuromedia_prep_logo_light.png",
    "neuromedia_prep_logo.svg",
    "neuromedia_prep_logo.png",
    "logo.svg",
    "logo.png",
)


APP_ICON_ASSET_NAMES = (
    "neuromedia_prep_app_icon.ico",
    "neuromedia_prep_app_icon.png",
    "neuromedia_prep_icon_light.png",
    "app_icon.ico",
    "app_icon.png",
)


def find_asset(names: tuple[str, ...]) -> Path | None:

    roots = (
        app_directory() / "assets",
        app_directory(),
    )

    for root in roots:
        for name in names:
            candidate = root / name

            if candidate.is_file():
                return candidate.resolve()

    return None


def find_logo_asset() -> Path | None:
    return find_asset(LOGO_ASSET_NAMES)


def find_app_icon_asset() -> Path | None:
    return find_asset(APP_ICON_ASSET_NAMES)


def brand_icon() -> QIcon:

    asset = find_app_icon_asset()

    if asset is None:
        return QIcon()

    return QIcon(str(asset))


def apply_window_branding(window: QWidget) -> None:
    icon = brand_icon()
    if not icon.isNull():
        window.setWindowIcon(icon)


def create_brand_mark(
    parent: QWidget | None = None,
    width: int = 58,
    height: int | None = None,
) -> QLabel:

    if height is None:
        height = width

    label = QLabel(parent)
    label.setObjectName("BrandMark")
    label.setFixedSize(width, height)
    label.setAlignment(
        Qt.AlignmentFlag.AlignLeft
        | Qt.AlignmentFlag.AlignVCenter
    )

    logo_asset = find_logo_asset()
    icon = QIcon(str(logo_asset)) if logo_asset else QIcon()

    if icon.isNull():
        label.setText("NM")
        label.setProperty("hasLogo", False)
        label.setToolTip(
            "Logo placeholder. Add an accepted logo file inside assets."
        )
    else:
        pixmap = icon.pixmap(
            max(1, width - 4),
            max(1, height - 4),
        )

        label.setPixmap(pixmap)
        label.setProperty("hasLogo", True)
        label.setToolTip(APP_NAME)

    return label


def repolish(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def set_widget_state(widget: QWidget, state: str) -> None:
    widget.setProperty("state", state)
    repolish(widget)


def application_stylesheet() -> str:
    return r"""
    QWidget {
        color: #1F2933;
        font-size: 10pt;
    }
    QMainWindow, QDialog, QWidget#AppRoot {
        background: #F4F6F8;
    }
    QToolTip {
        color: #FFFFFF;
        background: #1F2937;
        border: 1px solid #374151;
        padding: 6px;
    }
    QFrame#HeaderCard, QFrame#Card, QFrame#WorkflowBar, QFrame#OutputStrip {
        background: #FFFFFF;
        border: 1px solid #D8DEE6;
        border-radius: 10px;
    }
    QFrame#HeaderCard {
        border-color: #CDD7E4;
    }
    QLabel#BrandMark {
        background: #E8EEFF;
        color: #315BC7;
        border: 1px solid #C9D6FF;
        border-radius: 13px;
        font-size: 16pt;
        font-weight: 800;
    }
    QLabel#BrandMark[hasLogo="true"] {
        background: transparent;
        border: none;
    }
    QLabel#AppTitle {
        color: #182230;
        font-size: 19pt;
        font-weight: 750;
    }
    QLabel#AppSubtitle, QLabel#CardDescription, QLabel#MutedText {
        color: #667085;
    }
    QLabel#CardTitle {
        color: #182230;
        font-size: 12.5pt;
        font-weight: 700;
    }
    QLabel#MediaSummary, QLabel#PlanSummary, QLabel#ProcessTitle {
        color: #27364A;
        font-weight: 650;
    }
    QLabel#ProcessDetail, QLabel#ProcessMetrics, QLabel#CurrentFile {
        color: #667085;
    }
    QFrame#InsetPanel, QFrame#InlinePanel, QFrame#TransportBar {
        border-radius: 8px;
    }
    QFrame#InsetPanel, QFrame#InlinePanel {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
    }
    QFrame#TransportBar {
        background: #181C24;
        border: 1px solid #252C38;
    }
    QFrame#TransportBar QLabel {
        color: #E5E7EB;
    }
    QPushButton {
        min-height: 32px;
        padding: 0 13px;
        border-radius: 7px;
        border: 1px solid #CBD5E1;
        background: #FFFFFF;
        color: #27364A;
        font-weight: 600;
    }
    QPushButton:hover {
        background: #F8FAFC;
        border-color: #94A3B8;
    }
    QPushButton:pressed {
        background: #EEF2F7;
    }
    QPushButton:disabled {
        color: #98A2B3;
        background: #F2F4F7;
        border-color: #E4E7EC;
    }
    QPushButton[role="primary"] {
        color: #FFFFFF;
        background: #356AE6;
        border-color: #356AE6;
        font-weight: 700;
    }
    QPushButton[role="primary"]:hover {
        background: #2F5FD0;
        border-color: #2F5FD0;
    }
    QPushButton[role="danger"] {
        color: #B42318;
        background: #FFF6F5;
        border-color: #FDA29B;
    }
    QPushButton[role="ghost"] {
        background: transparent;
        border-color: transparent;
        color: #475467;
    }
    QPushButton[role="transport"] {
        color: #F8FAFC;
        background: #252C38;
        border-color: #3A4352;
        min-height: 30px;
    }
    QPushButton[role="transport"]:hover {
        background: #303949;
    }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        min-height: 32px;
        padding: 0 8px;
        border: 1px solid #CBD5E1;
        border-radius: 7px;
        background: #FFFFFF;
        selection-background-color: #C9D6FF;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border: 2px solid #6B8AFD;
    }
    QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled,
    QDoubleSpinBox:disabled {
        color: #98A2B3;
        background: #F2F4F7;
        border-color: #E4E7EC;
    }
    QComboBox::drop-down {
        width: 26px;
        border: none;
    }
    QCheckBox, QRadioButton {
        spacing: 8px;
        min-height: 26px;
    }
    QCheckBox::indicator, QRadioButton::indicator {
        width: 17px;
        height: 17px;
    }
    QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
        background: #FFFFFF;
        border: 1px solid #98A2B3;
    }
    QCheckBox::indicator:checked {
        background: #356AE6;
        border: 1px solid #356AE6;
    }
    QRadioButton::indicator:unchecked, QRadioButton::indicator:checked {
        border-radius: 9px;
    }
    QRadioButton::indicator:checked {
        background: #356AE6;
        border: 4px solid #DCE5FF;
    }
    QTableWidget {
        background: #FFFFFF;
        alternate-background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        gridline-color: #E7ECF2;
        selection-background-color: #E8EEFF;
        selection-color: #1F2933;
    }
    QTableWidget::item {
        padding: 7px;
    }
    QHeaderView::section {
        color: #475467;
        background: #F8FAFC;
        border: none;
        border-bottom: 1px solid #D8DEE6;
        padding: 8px;
        font-weight: 700;
    }
    QPlainTextEdit {
        color: #D8DEE9;
        background: #171B22;
        border: 1px solid #303846;
        border-radius: 8px;
        padding: 8px;
        font-family: Consolas, "Courier New", monospace;
    }
    QProgressBar {
        min-height: 14px;
        max-height: 14px;
        border: none;
        border-radius: 7px;
        background: #E7ECF2;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        border-radius: 7px;
        background: #356AE6;
    }
    QSlider::groove:horizontal {
        height: 5px;
        background: #CBD5E1;
        border-radius: 2px;
    }
    QSlider::sub-page:horizontal {
        background: #6B8AFD;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        width: 16px;
        margin: -6px 0;
        border-radius: 8px;
        background: #356AE6;
        border: 2px solid #FFFFFF;
    }
    QFrame#TransportBar QSlider::groove:horizontal {
        background: #3A4352;
    }
    QLabel#StatusBadge, QLabel#ReadinessSummary {
        padding: 5px 10px;
        border-radius: 11px;
        font-weight: 700;
    }
    QLabel#StatusBadge[state="idle"], QLabel#ReadinessSummary[state="neutral"] {
        color: #475467;
        background: #EEF2F6;
        border: 1px solid #D8DEE6;
    }
    QLabel#StatusBadge[state="running"] {
        color: #1D4ED8;
        background: #DBEAFE;
        border: 1px solid #BFDBFE;
    }
    QLabel#StatusBadge[state="success"], QLabel#ReadinessSummary[state="success"] {
        color: #166534;
        background: #DCFCE7;
        border: 1px solid #BBF7D0;
    }
    QLabel#StatusBadge[state="warning"], QLabel#ReadinessSummary[state="warning"] {
        color: #854D0E;
        background: #FEF3C7;
        border: 1px solid #FDE68A;
    }
    QLabel#StatusBadge[state="error"], QLabel#ReadinessSummary[state="error"] {
        color: #991B1B;
        background: #FEE2E2;
        border: 1px solid #FECACA;
    }
    QFrame#WorkflowStep {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        background: #F8FAFC;
    }
    QFrame#WorkflowStep[state="complete"] {
        border-color: #BBF7D0;
        background: #F0FDF4;
    }
    QFrame#WorkflowStep[state="current"] {
        border-color: #B6C7FF;
        background: #EEF3FF;
    }
    QLabel#WorkflowNumber {
        min-width: 25px;
        max-width: 25px;
        min-height: 25px;
        max-height: 25px;
        border-radius: 12px;
        color: #475467;
        background: #E7ECF2;
        font-weight: 800;
    }
    QFrame#WorkflowStep[state="complete"] QLabel#WorkflowNumber {
        color: #FFFFFF;
        background: #18864B;
    }
    QFrame#WorkflowStep[state="current"] QLabel#WorkflowNumber {
        color: #FFFFFF;
        background: #356AE6;
    }
    QLabel#WorkflowTitle {
        font-weight: 700;
        color: #344054;
    }
    QLabel#WorkflowDetail {
        color: #667085;
        font-size: 9pt;
    }
    QScrollArea {
        border: none;
        background: transparent;
    }
    QScrollBar:vertical {
        width: 12px;
        margin: 2px;
        background: transparent;
    }
    QScrollBar::handle:vertical {
        min-height: 36px;
        border-radius: 5px;
        background: #C5CDD8;
    }
    QScrollBar::handle:vertical:hover {
        background: #98A2B3;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        height: 0;
        background: transparent;
    }
    QScrollBar:horizontal {
        height: 12px;
        margin: 2px;
        background: transparent;
    }
    QScrollBar::handle:horizontal {
        min-width: 36px;
        border-radius: 5px;
        background: #C5CDD8;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        width: 0;
        background: transparent;
    }
    """


class CardFrame(QFrame):

    def __init__(
        self,
        title: str,
        description: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(18, 16, 18, 17)
        self.outer_layout.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("CardTitle")
        self.outer_layout.addWidget(heading)
        if description:
            description_label = QLabel(description)
            description_label.setObjectName("CardDescription")
            description_label.setWordWrap(True)
            self.outer_layout.addWidget(description_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 2, 0, 0)
        self.content_layout.setSpacing(10)
        self.outer_layout.addLayout(self.content_layout)

    def add_layout(self, layout: Any, stretch: int = 0) -> None:
        self.content_layout.addLayout(layout, stretch)

    def add_widget(self, widget: QWidget, stretch: int = 0) -> None:
        self.content_layout.addWidget(widget, stretch)


class WorkflowStep(QFrame):

    def __init__(
        self,
        number: int,
        title: str,
        detail: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.number = number
        self.setObjectName("WorkflowStep")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        self.number_label = QLabel(str(number))
        self.number_label.setObjectName("WorkflowNumber")
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.number_label)

        labels = QVBoxLayout()
        labels.setContentsMargins(0, 0, 0, 0)
        labels.setSpacing(0)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("WorkflowTitle")
        self.detail_label = QLabel(detail)
        self.detail_label.setObjectName("WorkflowDetail")
        labels.addWidget(self.title_label)
        labels.addWidget(self.detail_label)
        layout.addLayout(labels, 1)
        self.set_state("pending", detail)

    def set_state(self, state: str, detail: str | None = None) -> None:
        self.setProperty("state", state)
        self.number_label.setText("✓" if state == "complete" else str(self.number))
        if detail is not None:
            self.detail_label.setText(detail)
        repolish(self)


class DurationEdit(QLineEdit):

    valueChanged = Signal()

    def __init__(self, seconds: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.set_seconds(seconds)
        self.setPlaceholderText("HH:MM:SS")
        self.setMaximumWidth(120)
        self.setToolTip(
            "Enter SS, MM:SS, or HH:MM:SS. For example, 1 becomes 00:00:01."
        )
        self.editingFinished.connect(self._normalize)
        self.textEdited.connect(lambda _text: self.valueChanged.emit())

    def _normalize(self) -> None:
        try:
            self.set_seconds(parse_time_text(self.text()))
        except ValueError:
            return
        self.valueChanged.emit()

    def seconds(self) -> int:
        return parse_time_text(self.text())

    def set_seconds(self, seconds: float) -> None:
        self.setText(format_time(int(max(0, seconds))))


class NoWheelSpinBox(QSpinBox):

    def wheelEvent(self, event: Any) -> None:
        event.ignore()


class NoWheelDoubleSpinBox(QDoubleSpinBox):

    def wheelEvent(self, event: Any) -> None:
        event.ignore()


class NoWheelComboBox(QComboBox):

    def wheelEvent(self, event: Any) -> None:
        event.ignore()


class FirstRunDialog(QDialog):
    def __init__(self, settings: QSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.checks: list[dict[str, str]] = []
        self.subtitle_burn_in_result: tuple[bool, str] | None = None
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION} Setup")
        apply_window_branding(self)
        self.resize(860, 680)
        self.setMinimumSize(760, 580)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        header = QFrame()
        header.setObjectName("HeaderCard")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 12, 15, 12)
        header_layout.addWidget(create_brand_mark(header, 50))
        heading = QVBoxLayout()
        title = QLabel("First-run system check")
        title.setObjectName("AppTitle")
        description = QLabel(
            "NeuroMedia Prep will verify its media tools, output profiles, "
            "subtitle renderer, memory, and working storage before opening the main window."
        )
        description.setObjectName("AppSubtitle")
        description.setWordWrap(True)
        heading.addWidget(title)
        heading.addWidget(description)
        header_layout.addLayout(heading, 1)
        root.addWidget(header)

        locations = CardFrame(
            "Required locations",
            "The bundled media tools are detected automatically. Change a path only "
            "when using a separate FFmpeg installation.",
        )
        form = QFormLayout()

        configured_output = str(settings.value("output_root", "")).strip()
        if configured_output:
            default_output = configured_output
        else:
            videos = Path.home() / "Videos"
            default_output = str((videos if videos.exists() else Path.home()) / APP_NAME)
        self.output_edit = QLineEdit(default_output)
        self.output_edit.textChanged.connect(self._invalidate_checks)
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit, 1)
        output_button = QPushButton("Browse…")
        output_button.clicked.connect(self._browse_output)
        output_row.addWidget(output_button)
        form.addRow("Output directory:", output_row)

        ffmpeg_detected = locate_binary(
            "ffmpeg",
            str(settings.value("ffmpeg_path", "")),
        )
        self.ffmpeg_edit = QLineEdit(ffmpeg_detected or "")
        self.ffmpeg_edit.textChanged.connect(self._invalidate_checks)
        ffmpeg_row = QHBoxLayout()
        ffmpeg_row.addWidget(self.ffmpeg_edit, 1)
        ffmpeg_button = QPushButton("Browse…")
        ffmpeg_button.clicked.connect(
            lambda: self._browse_executable(self.ffmpeg_edit, "Select ffmpeg")
        )
        ffmpeg_row.addWidget(ffmpeg_button)
        form.addRow("FFmpeg:", ffmpeg_row)

        ffprobe_detected = locate_binary(
            "ffprobe",
            str(settings.value("ffprobe_path", "")),
        )
        self.ffprobe_edit = QLineEdit(ffprobe_detected or "")
        self.ffprobe_edit.textChanged.connect(self._invalidate_checks)
        ffprobe_row = QHBoxLayout()
        ffprobe_row.addWidget(self.ffprobe_edit, 1)
        ffprobe_button = QPushButton("Browse…")
        ffprobe_button.clicked.connect(
            lambda: self._browse_executable(self.ffprobe_edit, "Select ffprobe")
        )
        ffprobe_row.addWidget(ffprobe_button)
        form.addRow("FFprobe:", ffprobe_row)
        locations.add_layout(form)
        root.addWidget(locations)

        results = CardFrame(
            "System check",
            "At least 10 GB free space is recommended in the selected output location. "
            "Each processing job is checked again and is blocked if its estimated "
            "output cannot fit.",
        )
        self.summary_label = QLabel("Ready to run checks.")
        self.summary_label.setObjectName("ReadinessSummary")
        set_widget_state(self.summary_label, "neutral")
        results.add_widget(self.summary_label)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Status", "Check", "Result"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        results.add_widget(self.table, 1)
        root.addWidget(results, 1)

        buttons = QHBoxLayout()
        self.run_button = QPushButton("Run checks")
        self.run_button.clicked.connect(self._run_checks)
        buttons.addWidget(self.run_button)
        buttons.addStretch()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(cancel_button)
        self.start_button = QPushButton("Start NeuroMedia Prep")
        self.start_button.setProperty("role", "primary")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self._save_and_accept)
        buttons.addWidget(self.start_button)
        root.addLayout(buttons)

        QTimer.singleShot(0, self._run_checks)

    def _invalidate_checks(self, _text: str = "") -> None:
        if not hasattr(self, "start_button"):
            return
        self.start_button.setEnabled(False)
        self.summary_label.setText("Paths changed. Run the system checks again.")
        set_widget_state(self.summary_label, "neutral")

    def _browse_output(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self,
            "Choose output directory",
            self.output_edit.text().strip() or str(Path.home()),
        )
        if selected:
            self.output_edit.setText(selected)
            self.start_button.setEnabled(False)

    def _browse_executable(self, edit: QLineEdit, title: str) -> None:
        file_filter = (
            "Executable (*.exe);;All files (*.*)"
            if os.name == "nt"
            else "All files (*)"
        )
        selected, _ = QFileDialog.getOpenFileName(
            self,
            title,
            edit.text().strip() or str(app_directory()),
            file_filter,
        )
        if selected:
            edit.setText(selected)
            self.start_button.setEnabled(False)

    def _append_check(self, status: str, name: str, result: str) -> None:
        self.checks.append({"status": status, "name": name, "result": result})
        self._render_checks()
        QApplication.processEvents()

    def _render_checks(self) -> None:
        palette = {
            "green": ("✓ Ready", "#DCFCE7", "#166534"),
            "yellow": ("△ Review", "#FEF3C7", "#854D0E"),
            "red": ("× Blocked", "#FEE2E2", "#991B1B"),
        }
        self.table.setRowCount(len(self.checks))
        for row, check in enumerate(self.checks):
            status_text, background, foreground = palette[check["status"]]
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setBackground(QBrush(QColor(background)))
            status_item.setForeground(QBrush(QColor(foreground)))
            font = status_item.font()
            font.setBold(True)
            status_item.setFont(font)
            self.table.setItem(row, 0, status_item)

            name_item = QTableWidgetItem(check["name"])
            name_font = name_item.font()
            name_font.setBold(True)
            name_item.setFont(name_font)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, QTableWidgetItem(check["result"]))
            self.table.setRowHeight(row, 46)

        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, max(105, self.table.columnWidth(0)))
        self.table.setColumnWidth(1, max(165, self.table.columnWidth(1)))

    def _run_checks(self) -> None:
        self.checks = []
        self.subtitle_burn_in_result = None
        self.table.setRowCount(0)
        self.start_button.setEnabled(False)
        self.run_button.setEnabled(False)
        self.summary_label.setText("Running system checks…")
        set_widget_state(self.summary_label, "warning")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        try:
            app_root = app_directory()
            if app_root.is_dir() and os.access(app_root, os.R_OK):
                self._append_check(
                    "green",
                    "Application files",
                    f"Application directory is readable: {app_root}",
                )
            else:
                self._append_check(
                    "red",
                    "Application files",
                    f"Application directory is unavailable: {app_root}",
                )

            if os.name == "nt":
                windows_version = sys.getwindowsversion()
                if windows_version.major >= 10:
                    windows_name = "11" if windows_version.build >= 22000 else "10"
                    self._append_check(
                        "green",
                        "Windows version",
                        f"Windows {windows_name} is supported "
                        f"(build {windows_version.build}).",
                    )
                elif (
                    windows_version.major == 6
                    and windows_version.minor in {2, 3}
                ):
                    self._append_check(
                        "yellow",
                        "Windows version",
                        f"Windows {platform.release()} is not officially supported. "
                        "The release is tested on Windows 10 and 11.",
                    )
                else:
                    self._append_check(
                        "red",
                        "Windows version",
                        f"Windows {platform.release()} is not supported by this build. "
                        "Use Windows 10 or Windows 11.",
                    )
            else:
                self._append_check(
                    "yellow",
                    "Operating system",
                    f"{platform.system()} is not a validated release platform.",
                )

            total_memory = total_physical_memory_bytes()
            if total_memory is None:
                self._append_check(
                    "yellow",
                    "System memory",
                    "Installed memory could not be measured.",
                )
            elif total_memory < RECOMMENDED_MEMORY_BYTES:
                self._append_check(
                    "yellow",
                    "System memory",
                    f"{format_bytes(total_memory)} detected. At least "
                    f"{format_bytes(RECOMMENDED_MEMORY_BYTES)} is recommended; "
                    "large Exact-mode jobs may be slow.",
                )
            else:
                self._append_check(
                    "green",
                    "System memory",
                    f"{format_bytes(total_memory)} detected.",
                )

            output_text = self.output_edit.text().strip()
            output_path = Path(output_text).expanduser() if output_text else None
            if output_path is None:
                self._append_check(
                    "red",
                    "Output directory",
                    "Choose an output directory.",
                )
            else:
                writable, detail = test_directory_write(output_path)
                if not writable:
                    self._append_check("red", "Output directory", detail)
                else:
                    self._append_check(
                        "green",
                        "Output directory",
                        f"Writable: {output_path.resolve()}",
                    )
                    try:
                        free_bytes = shutil.disk_usage(output_path).free
                    except OSError as exc:
                        self._append_check(
                            "yellow",
                            "Free space",
                            f"Free space could not be measured: {exc}",
                        )
                    else:
                        if free_bytes < RECOMMENDED_FREE_SPACE_BYTES:
                            self._append_check(
                                "yellow",
                                "Free space",
                                f"{format_bytes(free_bytes)} available. "
                                f"{format_bytes(RECOMMENDED_FREE_SPACE_BYTES)} or more "
                                "is recommended. The app can still open, but a job "
                                "will be blocked when its estimated output cannot fit.",
                            )
                        else:
                            self._append_check(
                                "green",
                                "Free space",
                                f"{format_bytes(free_bytes)} available. The 10 GB "
                                "recommendation is satisfied.",
                            )

            ffmpeg_path = self.ffmpeg_edit.text().strip()
            ffprobe_path = self.ffprobe_edit.text().strip()
            ffmpeg_ok = False
            ffprobe_ok = False

            if ffmpeg_path and Path(ffmpeg_path).is_file():
                ffmpeg_ok, version = tool_version(ffmpeg_path)
                self._append_check(
                    "green" if ffmpeg_ok else "red",
                    "FFmpeg",
                    f"{version}\n{ffmpeg_path}",
                )
            else:
                self._append_check(
                    "red",
                    "FFmpeg",
                    "ffmpeg.exe was not found. Keep it beside the app, in bin, "
                    "or select it above.",
                )

            if ffmpeg_ok:
                demuxer_count, decoder_count = ffmpeg_input_capability_counts(
                    ffmpeg_path
                )
                if demuxer_count and decoder_count:
                    self._append_check(
                        "green",
                        "Video input support",
                        f"The file picker accepts every extension. This FFmpeg build "
                        f"provides {demuxer_count} input demuxers and "
                        f"{decoder_count} video decoders.",
                    )
                else:
                    self._append_check(
                        "red",
                        "Video input support",
                        "FFmpeg did not report usable input demuxers and video decoders.",
                    )

            if ffprobe_path and Path(ffprobe_path).is_file():
                ffprobe_ok, version = tool_version(ffprobe_path)
                self._append_check(
                    "green" if ffprobe_ok else "red",
                    "FFprobe",
                    f"{version}\n{ffprobe_path}",
                )
            else:
                self._append_check(
                    "red",
                    "FFprobe",
                    "ffprobe.exe was not found. Keep it beside the app, in bin, "
                    "or select it above.",
                )

            profile_errors = validate_profile_definitions()
            if profile_errors:
                self._append_check(
                    "red",
                    "Built-in profile definitions",
                    "; ".join(profile_errors),
                )
            else:
                self._append_check(
                    "green",
                    "Built-in profile definitions",
                    f"{len(DEVICE_PROFILES)} device presets and "
                    f"{len(FORMAT_PROFILES)} format presets match their documented "
                    "container choices and declared encoding settings.",
                )

            if ffmpeg_ok:
                self.subtitle_burn_in_result = test_unicode_subtitle_rendering(
                    ffmpeg_path
                )
                subtitle_ok, subtitle_detail = self.subtitle_burn_in_result
                self._append_check(
                    "green" if subtitle_ok else "yellow",
                    "Subtitle burn-in",
                    (
                        subtitle_detail
                        if subtitle_ok
                        else subtitle_detail
                        + " The app can still be used, but permanent subtitle "
                        "burn-in will remain unavailable until this is fixed."
                    ),
                )

            if ffmpeg_ok and ffprobe_ok and not profile_errors:
                recipe_count, profile_failures = test_builtin_output_profiles(
                    ffmpeg_path,
                    ffprobe_path,
                )
                if profile_failures:
                    self._append_check(
                        "red",
                        "Output profile test",
                        " | ".join(profile_failures),
                    )
                else:
                    self._append_check(
                        "green",
                        "Output profile test",
                        f"All {recipe_count} unique built-in encoding recipes were "
                        "created and validated with FFprobe.",
                    )

            missing_assets = []
            if find_logo_asset() is None:
                missing_assets.append("header logo")
            if find_app_icon_asset() is None:
                missing_assets.append("application icon")
            if missing_assets:
                self._append_check(
                    "yellow",
                    "Brand assets",
                    "Missing optional " + " and ".join(missing_assets) + ".",
                )
            else:
                self._append_check(
                    "green",
                    "Brand assets",
                    "Header logo and application icon were found.",
                )

            test_key = "_setup_write_test"
            self.settings.setValue(test_key, datetime.now().isoformat())
            self.settings.sync()
            settings_ok = self.settings.status() == QSettings.Status.NoError
            self.settings.remove(test_key)
            self.settings.sync()
            self._append_check(
                "green" if settings_ok else "red",
                "Settings storage",
                "Application settings can be saved."
                if settings_ok
                else "Application settings could not be written.",
            )

        finally:
            QApplication.restoreOverrideCursor()
            self.run_button.setEnabled(True)

        red_count = sum(check["status"] == "red" for check in self.checks)
        yellow_count = sum(check["status"] == "yellow" for check in self.checks)
        if red_count:
            self.summary_label.setText(
                f"Setup blocked: {red_count} item(s) must be fixed. "
                f"{yellow_count} item(s) need review."
            )
            set_widget_state(self.summary_label, "error")
            self.start_button.setEnabled(False)
        elif yellow_count:
            self.summary_label.setText(
                f"System ready with {yellow_count} non-blocking warning(s)."
            )
            set_widget_state(self.summary_label, "warning")
            self.start_button.setEnabled(True)
        else:
            self.summary_label.setText("System ready. All first-run checks passed.")
            set_widget_state(self.summary_label, "success")
            self.start_button.setEnabled(True)

    def _save_and_accept(self) -> None:
        if any(check["status"] == "red" for check in self.checks):
            QMessageBox.warning(
                self,
                APP_NAME,
                "Run the checks and resolve all blocked items first.",
            )
            return

        warnings = [
            f"{check['name']}: {check['result']}"
            for check in self.checks
            if check["status"] == "yellow"
        ]
        if warnings:
            answer = QMessageBox.question(
                self,
                APP_NAME,
                "The system check found non-blocking warnings:\n\n• "
                + "\n• ".join(warnings)
                + "\n\nContinue to NeuroMedia Prep?",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        output_path = Path(self.output_edit.text().strip()).expanduser().resolve()
        self.settings.setValue("output_root", str(output_path))
        self.settings.setValue("ffmpeg_path", self.ffmpeg_edit.text().strip())
        self.settings.setValue("ffprobe_path", self.ffprobe_edit.text().strip())
        if self.subtitle_burn_in_result is not None:
            subtitle_ok, subtitle_detail = self.subtitle_burn_in_result
            self.settings.setValue("subtitle_burn_in_test_passed", subtitle_ok)
            self.settings.setValue("subtitle_burn_in_test_detail", subtitle_detail)
            self.settings.setValue(
                "subtitle_burn_in_test_ffmpeg",
                self.ffmpeg_edit.text().strip(),
            )
        self.settings.setValue(SETUP_VERSION_KEY, APP_VERSION.split(".", 1)[0])
        self.settings.sync()
        if self.settings.status() != QSettings.Status.NoError:
            QMessageBox.critical(
                self,
                APP_NAME,
                "The setup results could not be saved.",
            )
            return
        self.accept()


class SettingsDialog(QDialog):

    def __init__(self, settings: QSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle(f"{APP_NAME} Settings")
        self.setMinimumWidth(650)

        layout = QVBoxLayout(self)
        explanation = QLabel(
            "Each processing run creates a timestamped movie folder inside the "
            "default output directory."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        form = QFormLayout()
        self.output_edit = QLineEdit(str(settings.value("output_root", "")))
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit, 1)
        output_browse = QPushButton("Browse…")
        output_browse.clicked.connect(self._browse_output)
        output_row.addWidget(output_browse)
        form.addRow("Default output directory:", output_row)

        self.ffmpeg_edit = QLineEdit(str(settings.value("ffmpeg_path", "")))
        ffmpeg_row = QHBoxLayout()
        ffmpeg_row.addWidget(self.ffmpeg_edit, 1)
        ffmpeg_browse = QPushButton("Browse…")
        ffmpeg_browse.clicked.connect(
            lambda: self._browse_executable(self.ffmpeg_edit, "Select ffmpeg")
        )
        ffmpeg_row.addWidget(ffmpeg_browse)
        form.addRow("FFmpeg (optional override):", ffmpeg_row)

        self.ffprobe_edit = QLineEdit(str(settings.value("ffprobe_path", "")))
        ffprobe_row = QHBoxLayout()
        ffprobe_row.addWidget(self.ffprobe_edit, 1)
        ffprobe_browse = QPushButton("Browse…")
        ffprobe_browse.clicked.connect(
            lambda: self._browse_executable(self.ffprobe_edit, "Select ffprobe")
        )
        ffprobe_row.addWidget(ffprobe_browse)
        form.addRow("FFprobe (optional override):", ffprobe_row)

        layout.addLayout(form)

        hint = QLabel(
            "Leave FFmpeg fields empty to detect executables beside the app, "
            "inside its bin folder, or on PATH."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666;")
        layout.addWidget(hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_output(self) -> None:
        starting = self.output_edit.text().strip() or str(Path.home())
        selected = QFileDialog.getExistingDirectory(
            self,
            "Choose default output directory",
            starting,
        )
        if selected:
            self.output_edit.setText(selected)

    def _browse_executable(self, edit: QLineEdit, title: str) -> None:
        file_filter = "Executable (*.exe);;All files (*.*)" if os.name == "nt" else "All files (*)"
        selected, _ = QFileDialog.getOpenFileName(
            self,
            title,
            edit.text().strip() or str(app_directory()),
            file_filter,
        )
        if selected:
            edit.setText(selected)

    def _save(self) -> None:
        output_text = self.output_edit.text().strip()
        if not output_text:
            QMessageBox.warning(self, APP_NAME, "Choose a default output directory.")
            return

        output_path = Path(output_text).expanduser()
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.critical(
                self,
                APP_NAME,
                f"The output directory could not be created:\n{exc}",
            )
            return
        if not output_path.is_dir():
            QMessageBox.warning(self, APP_NAME, "The output location is not a directory.")
            return

        for label, field in (
            ("FFmpeg", self.ffmpeg_edit),
            ("FFprobe", self.ffprobe_edit),
        ):
            configured = field.text().strip()
            if configured and not Path(configured).is_file():
                QMessageBox.warning(
                    self,
                    APP_NAME,
                    f"The selected {label} executable does not exist.",
                )
                return

        self.settings.setValue("output_root", str(output_path.resolve()))
        self.settings.setValue("ffmpeg_path", self.ffmpeg_edit.text().strip())
        self.settings.setValue("ffprobe_path", self.ffprobe_edit.text().strip())
        self.settings.sync()
        self.accept()


class ProfileDialog(QDialog):

    def __init__(
        self,
        profile: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.profile = dict(profile or {})
        self.setWindowTitle("Custom Output Profile")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit(str(self.profile.get("name", "")))
        form.addRow("Profile name:", self.name_edit)

        self.extension_combo = NoWheelComboBox()
        self.extension_combo.setEditable(True)
        self.extension_combo.addItems(["mp4", "webm", "avi", "mkv", "mov", "wmv", "mpg"])
        self.extension_combo.setCurrentText(str(self.profile.get("extension", "mp4")))
        form.addRow("Output extension:", self.extension_combo)

        self.video_codec_combo = NoWheelComboBox()
        self.video_codec_combo.setEditable(True)
        self.video_codec_combo.addItems(
            ["libx264", "libx265", "libvpx-vp9", "mpeg4", "wmv2", "mpeg2video"]
        )
        self.video_codec_combo.setCurrentText(
            str(self.profile.get("video_codec", "libx264"))
        )
        form.addRow("FFmpeg video encoder:", self.video_codec_combo)

        self.audio_codec_combo = NoWheelComboBox()
        self.audio_codec_combo.setEditable(True)
        self.audio_codec_combo.addItems(
            ["aac", "libopus", "libmp3lame", "ac3", "wmav2", "mp2", "none"]
        )
        self.audio_codec_combo.setCurrentText(
            str(self.profile.get("audio_codec", "aac"))
        )
        form.addRow("FFmpeg audio encoder:", self.audio_codec_combo)

        self.quality_option_combo = NoWheelComboBox()
        self.quality_option_combo.addItem("CRF", "-crf")
        self.quality_option_combo.addItem("Video quality scale", "-q:v")
        self.quality_option_combo.addItem("No quality option", "")
        current_quality = str(self.profile.get("quality_option", "-crf"))
        quality_index = self.quality_option_combo.findData(current_quality)
        self.quality_option_combo.setCurrentIndex(max(0, quality_index))
        form.addRow("Quality method:", self.quality_option_combo)

        self.quality_value_spin = NoWheelSpinBox()
        self.quality_value_spin.setRange(0, 63)
        self.quality_value_spin.setValue(int(self.profile.get("quality_value", 20)))
        form.addRow("Quality value:", self.quality_value_spin)

        self.preset_combo = NoWheelComboBox()
        self.preset_combo.addItems(
            ["", "ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow"]
        )
        self.preset_combo.setCurrentText(str(self.profile.get("preset", "medium")))
        form.addRow("Encoder preset:", self.preset_combo)

        self.width_spin = NoWheelSpinBox()
        self.width_spin.setRange(0, 7680)
        self.width_spin.setSpecialValueText("Keep source")
        self.width_spin.setValue(int(self.profile.get("max_width", 1920)))
        form.addRow("Maximum width:", self.width_spin)

        self.height_spin = NoWheelSpinBox()
        self.height_spin.setRange(0, 4320)
        self.height_spin.setSpecialValueText("Keep source")
        self.height_spin.setValue(int(self.profile.get("max_height", 1080)))
        form.addRow("Maximum height:", self.height_spin)

        layout.addLayout(form)

        warning = QLabel(
            "Custom encoders and extensions are passed to FFmpeg as separate "
            "arguments. NeuroMedia Prep will report unsupported combinations."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #666;")
        layout.addWidget(warning)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate(self) -> None:
        name = self.name_edit.text().strip()
        extension = self.extension_combo.currentText().strip().lower().lstrip(".")
        video_codec = self.video_codec_combo.currentText().strip()
        audio_codec = self.audio_codec_combo.currentText().strip()
        safe_token = re.compile(r"^[A-Za-z0-9_.+-]+$")

        if not name:
            QMessageBox.warning(self, APP_NAME, "Enter a profile name.")
            return
        if not extension or not safe_token.fullmatch(extension):
            QMessageBox.warning(self, APP_NAME, "Enter a valid output extension.")
            return
        if not video_codec or not safe_token.fullmatch(video_codec):
            QMessageBox.warning(self, APP_NAME, "Enter a valid FFmpeg video encoder.")
            return
        if not audio_codec or not safe_token.fullmatch(audio_codec):
            QMessageBox.warning(self, APP_NAME, "Enter a valid FFmpeg audio encoder.")
            return

        self.accept()

    def result_profile(self) -> dict[str, Any]:
        identifier = str(self.profile.get("id") or f"custom_{datetime.now().timestamp()}")
        video_codec = self.video_codec_combo.currentText().strip()
        pixel_format = "yuv420p" if video_codec in {"libx264", "libx265", "mpeg4"} else ""
        return {
            "id": identifier,
            "name": self.name_edit.text().strip(),
            "builtin": False,
            "extension": self.extension_combo.currentText().strip().lower().lstrip("."),
            "video_codec": video_codec,
            "audio_codec": self.audio_codec_combo.currentText().strip(),
            "quality_option": str(self.quality_option_combo.currentData() or ""),
            "quality_value": self.quality_value_spin.value(),
            "preset": self.preset_combo.currentText(),
            "max_width": self.width_spin.value(),
            "max_height": self.height_spin.value(),
            "pixel_format": pixel_format,
            "audio_channels": 2,
            "external_subtitles": True,
            "profile_type": "custom",
            "format_label": self.extension_combo.currentText().strip().upper(),
            "extra_output_args": [],
        }


class NaturalCutDialog(QDialog):

    PREVIEW_RADIUS_MS = 4_000

    def __init__(
        self,
        boundaries: list[dict[str, Any]],
        video_path: Path,
        video_duration_seconds: float,
        subtitle_cues: list[dict[str, Any]] | None = None,
        subtitle_offset_seconds: float = 0.0,
        subtitle_style: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.boundaries = boundaries
        self.video_path = video_path
        self.subtitle_cues = list(subtitle_cues or [])
        self.subtitle_offset_seconds = float(subtitle_offset_seconds)
        self.subtitle_style = dict(subtitle_style or {})
        self.known_duration_ms = max(0, int(video_duration_seconds * 1000))
        self.slider_is_down = False
        self.preview_end_ms: int | None = None
        self.pending_seek_ms: int | None = None

        self.setWindowTitle("Natural Cut Points")
        apply_window_branding(self)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.resize(1240, 780)
        self.setMinimumSize(960, 650)

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.75)
        self.player.positionChanged.connect(self._player_position_changed)
        self.player.durationChanged.connect(self._player_duration_changed)
        self.player.playbackStateChanged.connect(self._playback_state_changed)
        self.player.mediaStatusChanged.connect(self._media_status_changed)
        self.player.errorOccurred.connect(self._player_error)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        header = QFrame()
        header.setObjectName("HeaderCard")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 13, 16, 13)
        header_layout.setSpacing(12)
        header_layout.addWidget(create_brand_mark(header, 46))
        heading_column = QVBoxLayout()
        title = QLabel("Natural Cut Points")
        title.setObjectName("AppTitle")
        description = QLabel(
            "Review and adjust every internal session boundary. The main window "
            "remains locked until these changes are applied or cancelled."
        )
        description.setObjectName("AppSubtitle")
        description.setWordWrap(True)
        heading_column.addWidget(title)
        heading_column.addWidget(description)
        header_layout.addLayout(heading_column, 1)
        self.workspace_badge = QLabel(f"{len(boundaries)} boundaries")
        self.workspace_badge.setObjectName("StatusBadge")
        set_widget_state(self.workspace_badge, "running")
        header_layout.addWidget(self.workspace_badge)
        root.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        preview_card = CardFrame(
            "Cut preview",
            "Scrub freely or play an eight-second window around the selected cut.",
        )
        self.video_widget = QVideoWidget()
        self.video_widget.setObjectName("VideoSurface")
        self.video_widget.setMinimumHeight(390)
        self.video_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.video_widget.setStyleSheet(
            "background: #101319; border: 1px solid #252C38; border-radius: 8px;"
        )
        self.video_widget.installEventFilter(self)
        self.player.setVideoOutput(self.video_widget)
        preview_card.add_widget(self.video_widget, 1)

        self.subtitle_preview_label = QLabel(self.video_widget)
        self.subtitle_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_preview_label.setWordWrap(True)
        self.subtitle_preview_label.setTextFormat(Qt.TextFormat.PlainText)
        self.subtitle_preview_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self.subtitle_preview_label.hide()
        self._apply_subtitle_style()

        transport_frame = QFrame()
        transport_frame.setObjectName("TransportBar")
        transport = QHBoxLayout(transport_frame)
        transport.setContentsMargins(9, 7, 9, 7)
        transport.setSpacing(7)

        self.seek_back_button = QPushButton("−5 s")
        self.seek_back_button.setProperty("role", "transport")
        self.seek_back_button.clicked.connect(lambda: self._seek_relative(-5_000))
        transport.addWidget(self.seek_back_button)

        self.play_button = QPushButton("Play")
        self.play_button.setProperty("role", "transport")
        self.play_button.setFixedWidth(78)
        self.play_button.clicked.connect(self._toggle_playback)
        transport.addWidget(self.play_button)

        self.seek_forward_button = QPushButton("+5 s")
        self.seek_forward_button.setProperty("role", "transport")
        self.seek_forward_button.clicked.connect(lambda: self._seek_relative(5_000))
        transport.addWidget(self.seek_forward_button)

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, self.known_duration_ms)
        self.position_slider.sliderPressed.connect(self._slider_pressed)
        self.position_slider.sliderReleased.connect(self._slider_released)
        self.position_slider.sliderMoved.connect(self._slider_moved)
        transport.addWidget(self.position_slider, 1)

        self.player_time_label = QLabel(
            f"00:00:00 / {format_time(self.known_duration_ms / 1000)}"
        )
        self.player_time_label.setMinimumWidth(145)
        transport.addWidget(self.player_time_label)
        preview_card.add_widget(transport_frame)
        splitter.addWidget(preview_card)

        cuts_card = CardFrame(
            "Boundary candidates",
            "Select a boundary, then move between nearby scene changes or subtitle gaps.",
        )
        self.selected_cut_label = QLabel("No cut selected.")
        self.selected_cut_label.setObjectName("PlanSummary")
        self.selected_cut_label.setWordWrap(True)
        cuts_card.add_widget(self.selected_cut_label)

        legend = QLabel(
            "Blue: scene change   •   Green: subtitle gap   •   Gray: planned fallback"
        )
        legend.setObjectName("MutedText")
        legend.setWordWrap(True)
        cuts_card.add_widget(legend)

        self.table = QTableWidget(len(boundaries), 5)
        self.table.setObjectName("NaturalCutTable")
        self.table.setHorizontalHeaderLabels(
            ["Cut", "Planned", "Selected", "Source", "Change"]
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        cuts_card.add_widget(self.table, 1)

        navigation = QGridLayout()
        navigation.setHorizontalSpacing(8)
        navigation.setVerticalSpacing(8)
        self.earlier_button = QPushButton("← Earlier candidate")
        self.earlier_button.clicked.connect(lambda: self._move_candidate(-1))
        navigation.addWidget(self.earlier_button, 0, 0)

        self.later_button = QPushButton("Later candidate →")
        self.later_button.clicked.connect(lambda: self._move_candidate(1))
        navigation.addWidget(self.later_button, 0, 1)

        self.jump_button = QPushButton("Jump to selected")
        self.jump_button.clicked.connect(self._jump_selected)
        navigation.addWidget(self.jump_button, 1, 0)

        self.preview_button = QPushButton("Preview around cut")
        self.preview_button.setProperty("role", "primary")
        self.preview_button.setToolTip(
            "Play four seconds before and four seconds after the selected cut."
        )
        self.preview_button.clicked.connect(self._preview_selected)
        navigation.addWidget(self.preview_button, 1, 1)
        cuts_card.add_layout(navigation)
        splitter.addWidget(cuts_card)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([720, 480])
        root.addWidget(splitter, 1)

        actions = QHBoxLayout()
        actions.addStretch()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        actions.addWidget(cancel_button)
        apply_button = QPushButton("Apply cut points")
        apply_button.setProperty("role", "primary")
        apply_button.clicked.connect(self.accept)
        actions.addWidget(apply_button)
        root.addLayout(actions)

        self._refresh_rows()
        self.player.setSource(QUrl.fromLocalFile(str(video_path.resolve())))
        if boundaries:
            self.table.selectRow(0)
        else:
            self._selection_changed()

    def eventFilter(self, watched: Any, event: QEvent) -> bool:
        if watched is self.video_widget and event.type() == QEvent.Type.Resize:
            self._position_subtitle_preview()
            self.subtitle_preview_label.raise_()
        return super().eventFilter(watched, event)

    def _apply_subtitle_style(self) -> None:
        font_family = str(self.subtitle_style.get("font", "Arial"))
        font_size = int(self.subtitle_style.get("size", 24))
        text_color = str(self.subtitle_style.get("text_color", "#FFFFFF"))
        outline_color = str(self.subtitle_style.get("outline_color", "#000000"))
        self.subtitle_preview_label.setStyleSheet(
            f"color: {text_color}; background-color: rgba(0, 0, 0, 165); "
            f"font-family: '{font_family}'; font-size: {font_size}px; "
            f"font-weight: 600; border: 2px solid {outline_color}; "
            "border-radius: 6px; padding: 7px;"
        )
        self._position_subtitle_preview()

    def _position_subtitle_preview(self) -> None:
        margin = 24
        label_height = min(140, max(60, self.video_widget.height() // 4))
        placement = str(self.subtitle_style.get("placement", "bottom"))
        if placement == "top":
            y_position = margin
        elif placement == "center":
            y_position = (self.video_widget.height() - label_height) // 2
        else:
            y_position = self.video_widget.height() - label_height - margin
        self.subtitle_preview_label.setGeometry(
            margin,
            max(0, y_position),
            max(0, self.video_widget.width() - (margin * 2)),
            label_height,
        )

    def _selected_row(self) -> int:
        rows = self.table.selectionModel().selectedRows()
        return rows[0].row() if rows else -1

    def _selected_candidate(self) -> dict[str, Any] | None:
        row = self._selected_row()
        if row < 0:
            return None
        boundary = self.boundaries[row]
        candidates = boundary.get("candidates") or []
        if not candidates:
            return None
        index = min(
            max(0, int(boundary.get("selected_index", 0))),
            len(candidates) - 1,
        )
        boundary["selected_index"] = index
        return candidates[index]

    @staticmethod
    def _candidate_display(kind: str) -> tuple[str, str, str]:
        lowered = kind.lower()
        if "scene" in lowered and "subtitle" in lowered:
            return "SCENE + GAP", "#EDE9FE", "#6D28D9"
        if "scene" in lowered:
            return "SCENE", "#DBEAFE", "#1D4ED8"
        if "subtitle" in lowered:
            return "SUBTITLE GAP", "#DCFCE7", "#166534"
        return "PLANNED", "#EEF2F6", "#475467"

    def _refresh_rows(self) -> None:
        for row, boundary in enumerate(self.boundaries):
            candidates = boundary.get("candidates") or []
            index = int(boundary.get("selected_index", 0))
            index = min(max(0, index), max(0, len(candidates) - 1))
            boundary["selected_index"] = index
            candidate = candidates[index] if candidates else {
                "time": boundary["planned"],
                "kind": "planned time",
            }
            change = float(candidate["time"]) - float(boundary["planned"])
            source_text, source_background, source_foreground = self._candidate_display(
                str(candidate["kind"])
            )
            values = (
                f"{row + 1:02d}",
                format_time(float(boundary["planned"]), True),
                format_time(float(candidate["time"]), True),
                source_text,
                f"{change:+.3f} s",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if column == 3:
                    item.setBackground(QBrush(QColor(source_background)))
                    item.setForeground(QBrush(QColor(source_foreground)))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                elif column == 4:
                    magnitude = abs(change)
                    if magnitude <= 2:
                        background, foreground = "#DCFCE7", "#166534"
                    elif magnitude <= 10:
                        background, foreground = "#FEF3C7", "#854D0E"
                    else:
                        background, foreground = "#FEE2E2", "#991B1B"
                    item.setBackground(QBrush(QColor(background)))
                    item.setForeground(QBrush(QColor(foreground)))
                self.table.setItem(row, column, item)
            self.table.setRowHeight(row, 42)
        self.table.resizeColumnsToContents()

    def _selection_changed(self) -> None:
        row = self._selected_row()
        if row < 0:
            for button in (
                self.earlier_button,
                self.later_button,
                self.jump_button,
                self.preview_button,
            ):
                button.setEnabled(False)
            self.selected_cut_label.setText("No cut selected.")
            return

        boundary = self.boundaries[row]
        candidates = boundary.get("candidates") or []
        index = min(
            max(0, int(boundary.get("selected_index", 0))),
            max(0, len(candidates) - 1),
        )
        boundary["selected_index"] = index
        self.earlier_button.setEnabled(bool(candidates) and index > 0)
        self.later_button.setEnabled(bool(candidates) and index + 1 < len(candidates))
        self.jump_button.setEnabled(bool(candidates))
        self.preview_button.setEnabled(bool(candidates))

        candidate = self._selected_candidate()
        if candidate:
            change = float(candidate["time"]) - float(boundary["planned"])
            self.selected_cut_label.setText(
                f"Cut {row + 1:02d}  •  {format_time(float(candidate['time']), True)}  •  "
                f"{candidate['kind']}  •  {change:+.3f} s from plan"
            )
            self._jump_selected()

    def _move_candidate(self, direction: int) -> None:
        row = self._selected_row()
        if row < 0:
            return
        boundary = self.boundaries[row]
        candidates = boundary.get("candidates") or []
        if not candidates:
            return
        current = int(boundary.get("selected_index", 0))
        boundary["selected_index"] = min(
            max(0, current + direction),
            len(candidates) - 1,
        )
        self._refresh_rows()
        self.table.selectRow(row)
        self._selection_changed()

    def _jump_selected(self) -> None:
        candidate = self._selected_candidate()
        if not candidate:
            return
        self.preview_end_ms = None
        self.player.pause()
        self._set_position(int(max(0.0, float(candidate["time"])) * 1000))

    def _preview_selected(self) -> None:
        candidate = self._selected_candidate()
        if not candidate:
            return
        cut_ms = int(max(0.0, float(candidate["time"])) * 1000)
        start_ms = max(0, cut_ms - self.PREVIEW_RADIUS_MS)
        duration_ms = self._duration_ms()
        self.preview_end_ms = min(
            duration_ms if duration_ms > 0 else cut_ms + self.PREVIEW_RADIUS_MS,
            cut_ms + self.PREVIEW_RADIUS_MS,
        )
        self._set_position(start_ms)
        self.player.play()

    def _toggle_playback(self) -> None:
        self.preview_end_ms = None
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _seek_relative(self, milliseconds: int) -> None:
        self.preview_end_ms = None
        self._set_position(self.player.position() + milliseconds)

    def _set_position(self, position_ms: int) -> None:
        duration = self._duration_ms()
        target = max(0, int(position_ms))
        if duration > 0:
            target = min(duration, target)
        self.pending_seek_ms = target
        self.player.setPosition(target)
        self.position_slider.setValue(target)
        self._update_player_time(target)
        self._update_subtitle_preview(target)

    def _duration_ms(self) -> int:
        return self.player.duration() if self.player.duration() > 0 else self.known_duration_ms

    def _player_position_changed(self, position: int) -> None:
        if self.pending_seek_ms is not None and abs(position - self.pending_seek_ms) <= 250:
            self.pending_seek_ms = None
        if not self.slider_is_down:
            self.position_slider.setValue(position)
        self._update_player_time(position)
        self._update_subtitle_preview(position)
        if self.preview_end_ms is not None and position >= self.preview_end_ms:
            self.preview_end_ms = None
            self.player.pause()

    def _player_duration_changed(self, duration: int) -> None:
        if duration > 0:
            self.known_duration_ms = duration
            self.position_slider.setRange(0, duration)
        self._update_player_time(self.player.position())

    def _media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status in {
            QMediaPlayer.MediaStatus.LoadedMedia,
            QMediaPlayer.MediaStatus.BufferedMedia,
        } and self.pending_seek_ms is not None:
            self.player.setPosition(self.pending_seek_ms)

    def _playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        self.play_button.setText(
            "Pause" if state == QMediaPlayer.PlaybackState.PlayingState else "Play"
        )

    def _slider_pressed(self) -> None:
        self.slider_is_down = True
        self.preview_end_ms = None

    def _slider_released(self) -> None:
        self.slider_is_down = False
        self._set_position(self.position_slider.value())

    def _slider_moved(self, position: int) -> None:
        self._update_player_time(position)
        self._update_subtitle_preview(position)

    def _update_player_time(self, position: int) -> None:
        total = self._duration_ms()
        self.player_time_label.setText(
            f"{format_time(position / 1000)} / {format_time(total / 1000)}"
        )

    def _update_subtitle_preview(self, position_ms: int) -> None:
        position = position_ms / 1000
        active = [
            str(cue["text"])
            for cue in self.subtitle_cues
            if (
                float(cue["start"]) + self.subtitle_offset_seconds
                <= position
                < float(cue["end"]) + self.subtitle_offset_seconds
            )
        ]
        if not active:
            self.subtitle_preview_label.clear()
            self.subtitle_preview_label.hide()
            return

        preview_text = html.unescape(re.sub(r"<[^>]+>", "", "\n".join(active)))
        self.subtitle_preview_label.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
            if contains_rtl_text(preview_text)
            else Qt.LayoutDirection.LeftToRight
        )
        self.subtitle_preview_label.setText(preview_text)
        self.subtitle_preview_label.show()
        self.subtitle_preview_label.raise_()

    def _player_error(self, _error: QMediaPlayer.Error, error_string: str) -> None:
        if error_string:
            self.selected_cut_label.setText(
                f"Preview warning: {error_string}. FFmpeg can still process the video."
            )

    def choices(self) -> dict[float, float]:
        result: dict[float, float] = {}
        for boundary in self.boundaries:
            candidates = boundary.get("candidates") or []
            if candidates:
                index = min(
                    max(0, int(boundary.get("selected_index", 0))),
                    len(candidates) - 1,
                )
                candidate = candidates[index]
                result[round(float(boundary["planned"]), 3)] = float(candidate["time"])
        return result

    def done(self, result: int) -> None:
        self.player.stop()
        super().done(result)


class MainWindow(QMainWindow):

    def __init__(self, settings: QSettings) -> None:
        super().__init__()
        self.settings = settings
        self.input_path: Path | None = None
        self.input_info: dict[str, Any] | None = None
        self.subtitle_path: Path | None = None
        self.subtitle_cues: list[dict[str, Any]] = []
        self.subtitle_encoding = ""
        self.subtitle_font_family = "Arial"
        self.subtitle_text_color = "#FFFFFF"
        self.subtitle_outline_color = "#000000"
        self.natural_cut_choices: dict[float, float] = {}
        self.natural_cut_boundaries: list[dict[str, Any]] = []
        self.readiness_results: list[dict[str, str]] = []
        self.last_output_directory: Path | None = None
        self.current_job_directory: Path | None = None
        self.manifest: dict[str, Any] = {}
        self.segments: list[dict[str, float]] = []
        self.current_segment_index = 0
        self.completed_duration = 0.0
        self.total_processing_duration = 0.0
        self.stdout_buffer = ""
        self.stderr_buffer = ""
        self.is_processing = False
        self.cancel_requested = False
        self.current_partial_path: Path | None = None
        self.current_final_path: Path | None = None
        self.current_burn_subtitle_path: Path | None = None
        self.current_subtitle_cue_count = 0
        self.processing_started_at: datetime | None = None
        self.processing_visual_state = "idle"

        self.ffmpeg_path: str | None = None
        self.ffprobe_path: str | None = None
        self.encoder_names: set[str] | None = None
        self.subtitle_filter_available: bool | None = None
        self.subtitle_render_test_result: tuple[bool, str] | None = None
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.process.readyReadStandardOutput.connect(self._read_process_stdout)
        self.process.readyReadStandardError.connect(self._read_process_stderr)
        self.process.finished.connect(self._process_finished)

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.75)
        self.player.positionChanged.connect(self._player_position_changed)
        self.player.durationChanged.connect(self._player_duration_changed)
        self.player.playbackStateChanged.connect(self._playback_state_changed)
        self.player.errorOccurred.connect(self._player_error)
        self.slider_is_down = False
        self.processing_ui_timer = QTimer(self)
        self.processing_ui_timer.setInterval(1000)
        self.processing_ui_timer.timeout.connect(self._refresh_processing_visuals)

        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        apply_window_branding(self)
        self.resize(1120, 820)
        self.setMinimumSize(900, 680)
        self._build_ui()
        self._refresh_binary_paths()
        self._refresh_output_root()
        self._load_profiles()
        self._update_controls()

    # ------------------------------- UI setup -------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("AppRoot")
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 17, 20, 18)
        root.setSpacing(13)

        header_card = QFrame()
        header_card.setObjectName("HeaderCard")

        header = QHBoxLayout(header_card)
        header.setContentsMargins(16, 6, 16, 6)
        header.setSpacing(10)

        self.logo_label = create_brand_mark(
            header_card,
            width=320,
            height=80,
        )
        header.addWidget(
            self.logo_label,
            0,
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
        )

        header.addStretch(1)

        self.open_button = QPushButton("Open Video")
        self.open_button.setProperty("role", "primary")

        self.open_button.clicked.connect(self._choose_video)
        header.addWidget(self.open_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self._open_settings)
        header.addWidget(self.settings_button)

        root.addWidget(header_card)

        workflow_frame = QFrame()
        workflow_frame.setObjectName("WorkflowBar")
        workflow_layout = QHBoxLayout(workflow_frame)
        workflow_layout.setContentsMargins(10, 9, 10, 9)
        workflow_layout.setSpacing(8)
        workflow_specs = (
            (1, "Source", "Choose a video"),
            (2, "Subtitles", "Optional"),
            (3, "Sessions", "Set timing"),
            (4, "Output", "Choose target"),
            (5, "Process", "Prepare files"),
        )
        self.workflow_steps: dict[str, WorkflowStep] = {}
        for number, step_title, detail in workflow_specs:
            step = WorkflowStep(number, step_title, detail)
            self.workflow_steps[step_title.lower()] = step
            workflow_layout.addWidget(step, 1)
        root.addWidget(workflow_frame)

        output_frame = QFrame()
        output_frame.setObjectName("OutputStrip")
        output_layout = QHBoxLayout(output_frame)
        output_layout.setContentsMargins(12, 8, 12, 8)
        output_label = QLabel("Default output")
        output_label.setObjectName("MutedText")
        output_layout.addWidget(output_label)
        self.output_root_label = QLabel()
        self.output_root_label.setObjectName("MediaSummary")
        self.output_root_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        output_layout.addWidget(self.output_root_label, 1)
        root.addWidget(output_frame)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        body = QVBoxLayout(scroll_content)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(12)

        preview_card = CardFrame(
            "Video preview",
            "Review the source and align subtitles before defining session boundaries.",
        )
        self.video_widget = QVideoWidget()
        self.video_widget.setObjectName("VideoSurface")
        self.video_widget.setMinimumHeight(370)
        self.video_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.video_widget.setStyleSheet(
            "background: #101319; border: 1px solid #252C38; border-radius: 8px;"
        )
        self.video_widget.installEventFilter(self)
        self.player.setVideoOutput(self.video_widget)

        self.subtitle_preview_label = QLabel(self.video_widget)
        self.subtitle_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_preview_label.setWordWrap(True)
        self.subtitle_preview_label.setTextFormat(Qt.TextFormat.PlainText)
        self.subtitle_preview_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        self.subtitle_preview_label.hide()
        preview_card.add_widget(self.video_widget, 1)

        transport_frame = QFrame()
        transport_frame.setObjectName("TransportBar")
        transport = QHBoxLayout(transport_frame)
        transport.setContentsMargins(9, 7, 9, 7)
        transport.setSpacing(7)
        self.seek_back_button = QPushButton("−10 s")
        self.seek_back_button.setProperty("role", "transport")
        self.seek_back_button.clicked.connect(lambda: self._seek_relative(-10_000))
        transport.addWidget(self.seek_back_button)
        self.play_button = QPushButton("Play")
        self.play_button.setProperty("role", "transport")
        self.play_button.setFixedWidth(82)
        self.play_button.clicked.connect(self._toggle_playback)
        transport.addWidget(self.play_button)
        self.seek_forward_button = QPushButton("+10 s")
        self.seek_forward_button.setProperty("role", "transport")
        self.seek_forward_button.clicked.connect(lambda: self._seek_relative(10_000))
        transport.addWidget(self.seek_forward_button)
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderPressed.connect(self._slider_pressed)
        self.position_slider.sliderReleased.connect(self._slider_released)
        self.position_slider.sliderMoved.connect(self._slider_moved)
        transport.addWidget(self.position_slider, 1)
        self.player_time_label = QLabel("00:00:00 / 00:00:00")
        self.player_time_label.setMinimumWidth(145)
        transport.addWidget(self.player_time_label)
        preview_card.add_widget(transport_frame)

        self.input_info_label = QLabel("Open a local video to begin.")
        self.input_info_label.setObjectName("MediaSummary")
        self.input_info_label.setWordWrap(True)
        self.input_info_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        preview_card.add_widget(self.input_info_label)

        subtitle_file_panel = QFrame()
        subtitle_file_panel.setObjectName("InlinePanel")
        subtitle_controls = QHBoxLayout(subtitle_file_panel)
        subtitle_controls.setContentsMargins(10, 8, 10, 8)
        subtitle_controls.addWidget(QLabel("Subtitle file"))
        self.subtitle_path_label = QLabel("None selected")
        self.subtitle_path_label.setObjectName("MutedText")
        self.subtitle_path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        subtitle_controls.addWidget(self.subtitle_path_label, 1)
        self.open_subtitle_button = QPushButton("Choose Subtitle…")
        self.open_subtitle_button.clicked.connect(self._choose_subtitle)
        subtitle_controls.addWidget(self.open_subtitle_button)
        self.clear_subtitle_button = QPushButton("Clear")
        self.clear_subtitle_button.setProperty("role", "ghost")
        self.clear_subtitle_button.clicked.connect(self._clear_subtitle)
        subtitle_controls.addWidget(self.clear_subtitle_button)
        preview_card.add_widget(subtitle_file_panel)
        body.addWidget(preview_card)

        subtitle_card = CardFrame(
            "Subtitle timing and output",
            "Synchronize cues first. Enable burn-in to reveal permanent subtitle styling.",
        )
        subtitle_timing = QGridLayout()
        subtitle_timing.setHorizontalSpacing(8)
        subtitle_timing.setVerticalSpacing(8)
        subtitle_timing.addWidget(QLabel("Timing offset"), 0, 0)
        self.subtitle_minus_10_button = QPushButton("−10 s")
        self.subtitle_minus_10_button.clicked.connect(
            lambda: self._change_subtitle_offset(-10.0)
        )
        subtitle_timing.addWidget(self.subtitle_minus_10_button, 0, 1)
        self.subtitle_minus_5_button = QPushButton("−5 s")
        self.subtitle_minus_5_button.clicked.connect(
            lambda: self._change_subtitle_offset(-5.0)
        )
        subtitle_timing.addWidget(self.subtitle_minus_5_button, 0, 2)
        self.subtitle_offset_back_button = QPushButton("◀")
        self.subtitle_offset_back_button.setToolTip(
            "Hold to move subtitles earlier by 0.1 second per step."
        )
        self.subtitle_offset_back_button.setAutoRepeat(True)
        self.subtitle_offset_back_button.setAutoRepeatDelay(350)
        self.subtitle_offset_back_button.setAutoRepeatInterval(80)
        self.subtitle_offset_back_button.clicked.connect(
            lambda: self._change_subtitle_offset(-0.1)
        )
        subtitle_timing.addWidget(self.subtitle_offset_back_button, 0, 3)
        self.subtitle_offset_spin = NoWheelDoubleSpinBox()
        self.subtitle_offset_spin.setObjectName("NoSpinButtons")
        self.subtitle_offset_spin.setRange(-3600.0, 3600.0)
        self.subtitle_offset_spin.setDecimals(3)
        self.subtitle_offset_spin.setSingleStep(0.1)
        self.subtitle_offset_spin.setSuffix(" s")

        self.subtitle_offset_spin.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons
        )

        self.subtitle_offset_spin.valueChanged.connect(self._subtitle_offset_changed)
        subtitle_timing.addWidget(self.subtitle_offset_spin, 0, 4)
        self.subtitle_offset_forward_button = QPushButton("▶")
        self.subtitle_offset_forward_button.setToolTip(
            "Hold to move subtitles later by 0.1 second per step."
        )
        self.subtitle_offset_forward_button.setAutoRepeat(True)
        self.subtitle_offset_forward_button.setAutoRepeatDelay(350)
        self.subtitle_offset_forward_button.setAutoRepeatInterval(80)
        self.subtitle_offset_forward_button.clicked.connect(
            lambda: self._change_subtitle_offset(0.1)
        )
        subtitle_timing.addWidget(self.subtitle_offset_forward_button, 0, 5)
        self.subtitle_plus_5_button = QPushButton("+5 s")
        self.subtitle_plus_5_button.clicked.connect(
            lambda: self._change_subtitle_offset(5.0)
        )
        subtitle_timing.addWidget(self.subtitle_plus_5_button, 0, 6)
        self.subtitle_plus_10_button = QPushButton("+10 s")
        self.subtitle_plus_10_button.clicked.connect(
            lambda: self._change_subtitle_offset(10.0)
        )
        subtitle_timing.addWidget(self.subtitle_plus_10_button, 0, 7)
        subtitle_timing.setColumnStretch(4, 1)
        subtitle_card.add_layout(subtitle_timing)

        self.burn_subtitles_checkbox = QCheckBox(
            "Burn subtitles permanently into the video (Exact mode)"
        )
        self.burn_subtitles_checkbox.setToolTip(
            "Burn-in permanently renders the selected subtitles into each video. "
            "Enabling it automatically selects Exact mode."
        )
        self.burn_subtitles_checkbox.toggled.connect(self._burn_subtitles_changed)
        subtitle_card.add_widget(self.burn_subtitles_checkbox)

        self.subtitle_appearance_frame = QFrame()
        self.subtitle_appearance_frame.setObjectName("InsetPanel")
        appearance_layout = QGridLayout(self.subtitle_appearance_frame)
        appearance_layout.setContentsMargins(12, 10, 12, 10)
        appearance_layout.setHorizontalSpacing(9)
        appearance_layout.setVerticalSpacing(9)

        font_label = QLabel("Font")
        font_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )
        appearance_layout.addWidget(font_label, 0, 0)

        self.subtitle_font_button = QPushButton(self.subtitle_font_family)
        self.subtitle_font_button.clicked.connect(self._choose_subtitle_font)
        appearance_layout.addWidget(self.subtitle_font_button, 0, 1)

        size_label = QLabel("Size")
        size_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )
        appearance_layout.addWidget(size_label, 0, 2)

        self.subtitle_size_spin = NoWheelSpinBox()
        self.subtitle_size_spin.setRange(8, 96)
        self.subtitle_size_spin.setValue(24)
        self.subtitle_size_spin.setSingleStep(1)

        self.subtitle_size_spin.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.PlusMinus
        )

        self.subtitle_size_spin.setFixedWidth(110)

        self.subtitle_size_spin.valueChanged.connect(
            self._update_subtitle_style
        )
        appearance_layout.addWidget(self.subtitle_size_spin, 0, 3)

        placement_label = QLabel("Placement")
        placement_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )
        appearance_layout.addWidget(placement_label, 0, 4)

        self.subtitle_placement_combo = NoWheelComboBox()
        self.subtitle_placement_combo.addItem("Bottom", "bottom")
        self.subtitle_placement_combo.addItem("Center", "center")
        self.subtitle_placement_combo.addItem("Top", "top")
        self.subtitle_placement_combo.setMinimumWidth(150)
        self.subtitle_placement_combo.currentIndexChanged.connect(
            self._update_subtitle_style
        )
        appearance_layout.addWidget(
            self.subtitle_placement_combo,
            0,
            5,
        )



        text_colour_label = QLabel("Text colour")
        text_colour_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )
        appearance_layout.addWidget(text_colour_label, 1, 0)

        self.subtitle_text_color_button = QPushButton()
        self.subtitle_text_color_button.clicked.connect(
            lambda: self._choose_subtitle_color("text")
        )
        appearance_layout.addWidget(
            self.subtitle_text_color_button,
            1,
            1,
        )

        outline_colour_label = QLabel("Outline colour")
        outline_colour_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )
        appearance_layout.addWidget(outline_colour_label, 1, 4)

        self.subtitle_outline_color_button = QPushButton()
        self.subtitle_outline_color_button.clicked.connect(
            lambda: self._choose_subtitle_color("outline")
        )
        appearance_layout.addWidget(
            self.subtitle_outline_color_button,
            1,
            5,
        )



        self.subtitle_unicode_label = QLabel(
            "Unicode and right-to-left text are supported in preview. "
            "Confirm that the selected font contains every required character."
        )
        self.subtitle_unicode_label.setObjectName("MutedText")
        self.subtitle_unicode_label.setWordWrap(True)
        appearance_layout.addWidget(
            self.subtitle_unicode_label,
            2,
            0,
            1,
            6,
        )


        appearance_layout.setColumnStretch(0, 0)
        appearance_layout.setColumnStretch(1, 3)
        appearance_layout.setColumnStretch(2, 0)
        appearance_layout.setColumnStretch(3, 0)
        appearance_layout.setColumnStretch(4, 0)
        appearance_layout.setColumnStretch(5, 2)
        subtitle_card.add_widget(self.subtitle_appearance_frame)
        body.addWidget(subtitle_card)

        timing_card = CardFrame(
            "Trim and session timing",
            "Define the usable range, session length, overlap, and optional natural cuts.",
        )
        timing_layout = QGridLayout()
        timing_layout.setHorizontalSpacing(10)
        timing_layout.setVerticalSpacing(9)
        timing_layout.addWidget(QLabel("Start at"), 0, 0)
        self.trim_start_edit = DurationEdit(0)
        self.trim_start_edit.valueChanged.connect(self._timing_changed)
        timing_layout.addWidget(self.trim_start_edit, 0, 1)
        self.set_start_button = QPushButton("Set from player")
        self.set_start_button.clicked.connect(self._set_start_from_player)
        timing_layout.addWidget(self.set_start_button, 0, 2)
        timing_layout.addWidget(QLabel("End at"), 1, 0)
        self.trim_end_edit = DurationEdit(0)
        self.trim_end_edit.valueChanged.connect(self._timing_changed)
        timing_layout.addWidget(self.trim_end_edit, 1, 1)
        self.set_end_button = QPushButton("Set from player")
        self.set_end_button.clicked.connect(self._set_end_from_player)
        timing_layout.addWidget(self.set_end_button, 1, 2)
        timing_layout.addWidget(QLabel("Session duration"), 0, 3)
        self.session_duration_combo = NoWheelComboBox()
        for minutes in (20, 30, 40, 45, 60):
            label = f"{minutes} minutes"
            if minutes == 40:
                label += " (default)"
            self.session_duration_combo.addItem(label, minutes * 60)
        self.session_duration_combo.addItem("Custom…", None)
        self.session_duration_combo.setCurrentIndex(2)
        self.session_duration_combo.currentIndexChanged.connect(
            self._session_duration_changed
        )
        timing_layout.addWidget(self.session_duration_combo, 0, 4)
        self.custom_duration_edit = DurationEdit(40 * 60)
        self.custom_duration_edit.setVisible(False)
        self.custom_duration_edit.valueChanged.connect(self._timing_changed)
        timing_layout.addWidget(self.custom_duration_edit, 1, 4)
        timing_layout.addWidget(QLabel("Overlap"), 2, 0)
        self.overlap_mode_combo = NoWheelComboBox()
        self.overlap_mode_combo.addItem("None", "none")
        self.overlap_mode_combo.addItem("Custom…", "custom")
        self.overlap_mode_combo.addItem("Auto — equal-length sessions", "auto")
        self.overlap_mode_combo.currentIndexChanged.connect(
            self._overlap_mode_changed
        )
        timing_layout.addWidget(self.overlap_mode_combo, 2, 1, 1, 2)
        self.custom_overlap_edit = DurationEdit(5 * 60)
        self.custom_overlap_edit.setVisible(False)
        self.custom_overlap_edit.valueChanged.connect(self._timing_changed)
        timing_layout.addWidget(self.custom_overlap_edit, 2, 3, 1, 2)
        self.natural_cut_checkbox = QCheckBox(
            "Prefer natural scene/subtitle cut points"
        )
        self.natural_cut_checkbox.toggled.connect(self._natural_cut_toggled)
        timing_layout.addWidget(self.natural_cut_checkbox, 3, 0, 1, 2)
        self.review_cuts_button = QPushButton("Find / review cut points…")
        self.review_cuts_button.clicked.connect(self._review_natural_cuts)
        timing_layout.addWidget(self.review_cuts_button, 3, 2)
        self.natural_cut_status_label = QLabel("Off")
        self.natural_cut_status_label.setObjectName("MutedText")
        self.natural_cut_status_label.setWordWrap(True)
        timing_layout.addWidget(self.natural_cut_status_label, 3, 3, 1, 2)
        timing_layout.setColumnStretch(4, 1)
        timing_card.add_layout(timing_layout)

        self.plan_summary_label = QLabel("No video loaded.")
        self.plan_summary_label.setObjectName("PlanSummary")
        self.plan_summary_label.setWordWrap(True)
        timing_card.add_widget(self.plan_summary_label)
        self.segment_table = QTableWidget(0, 4)
        self.segment_table.setHorizontalHeaderLabels(
            ["Session", "Start", "End", "Duration"]
        )
        self.segment_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.segment_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.segment_table.setAlternatingRowColors(True)
        self.segment_table.verticalHeader().setVisible(False)
        self.segment_table.horizontalHeader().setStretchLastSection(True)
        self.segment_table.setMaximumHeight(230)
        timing_card.add_widget(self.segment_table)
        body.addWidget(timing_card)

        output_card = CardFrame(
            "Output profile and cutting mode",
            "Choose the target system or format, then select speed or exactness.",
        )
        output_layout = QGridLayout()
        output_layout.setHorizontalSpacing(9)
        output_layout.setVerticalSpacing(10)
        output_layout.addWidget(QLabel("Target system or format"), 0, 0)
        self.profile_combo = NoWheelComboBox()
        self.profile_combo.currentIndexChanged.connect(self._profile_changed)
        output_layout.addWidget(self.profile_combo, 0, 1, 1, 3)
        self.new_profile_button = QPushButton("New…")
        self.new_profile_button.clicked.connect(self._new_profile)
        output_layout.addWidget(self.new_profile_button, 0, 4)
        self.edit_profile_button = QPushButton("Edit…")
        self.edit_profile_button.clicked.connect(self._edit_profile)
        output_layout.addWidget(self.edit_profile_button, 0, 5)
        self.delete_profile_button = QPushButton("Delete")
        self.delete_profile_button.setProperty("role", "danger")
        self.delete_profile_button.clicked.connect(self._delete_profile)
        output_layout.addWidget(self.delete_profile_button, 0, 6)
        self.fast_mode_radio = QRadioButton("Fast — stream copy")
        self.fast_mode_radio.setToolTip(
            "No quality loss, but codecs must already match and cuts may move to keyframes."
        )
        output_layout.addWidget(self.fast_mode_radio, 1, 1, 1, 2)
        self.exact_mode_radio = QRadioButton("Exact — re-encode")
        self.exact_mode_radio.setChecked(True)
        self.exact_mode_radio.setToolTip(
            "Precise cuts and profile-compatible output. Processing takes longer."
        )
        output_layout.addWidget(self.exact_mode_radio, 1, 3, 1, 2)
        self.fast_mode_radio.toggled.connect(self._cutting_mode_changed)
        self.exact_mode_radio.toggled.connect(self._cutting_mode_changed)
        self.profile_details_label = QLabel()
        self.profile_details_label.setObjectName("MutedText")
        self.profile_details_label.setWordWrap(True)
        output_layout.addWidget(self.profile_details_label, 2, 0, 1, 7)
        output_layout.setColumnStretch(3, 1)
        output_card.add_layout(output_layout)
        body.addWidget(output_card)

        readiness_card = CardFrame(
            "Readiness check",
            "Resolve blocked items and review warnings before starting the job.",
        )
        self.readiness_summary_label = QLabel("Choose a video to begin.")
        self.readiness_summary_label.setObjectName("ReadinessSummary")
        self.readiness_summary_label.setWordWrap(True)
        set_widget_state(self.readiness_summary_label, "neutral")
        readiness_card.add_widget(self.readiness_summary_label)
        self.readiness_table = QTableWidget(0, 3)
        self.readiness_table.setObjectName("ReadinessTable")
        self.readiness_table.setHorizontalHeaderLabels(
            ["Status", "Check", "Result"]
        )
        self.readiness_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.readiness_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.readiness_table.setAlternatingRowColors(True)
        self.readiness_table.setWordWrap(True)
        self.readiness_table.verticalHeader().setVisible(False)
        self.readiness_table.horizontalHeader().setStretchLastSection(True)
        self.readiness_table.setMaximumHeight(340)
        readiness_card.add_widget(self.readiness_table)
        body.addWidget(readiness_card)

        self.process_card = CardFrame(
            "Processing",
            "Progress, validation, output location, and technical details appear here.",
        )
        process_header = QHBoxLayout()
        process_title_column = QVBoxLayout()
        process_title_column.setSpacing(2)
        self.status_label = QLabel("Ready to prepare")
        self.status_label.setObjectName("ProcessTitle")
        self.process_detail_label = QLabel(
            "Open a video and review the readiness check before processing."
        )
        self.process_detail_label.setObjectName("ProcessDetail")
        self.process_detail_label.setWordWrap(True)
        process_title_column.addWidget(self.status_label)
        process_title_column.addWidget(self.process_detail_label)
        process_header.addLayout(process_title_column, 1)
        self.process_state_badge = QLabel("Idle")
        self.process_state_badge.setObjectName("StatusBadge")
        set_widget_state(self.process_state_badge, "idle")
        process_header.addWidget(self.process_state_badge)
        self.process_card.add_layout(process_header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.process_card.add_widget(self.progress_bar)

        process_info_panel = QFrame()
        process_info_panel.setObjectName("InsetPanel")
        process_info_layout = QVBoxLayout(process_info_panel)
        process_info_layout.setContentsMargins(11, 8, 11, 8)
        process_info_layout.setSpacing(3)
        self.current_file_label = QLabel("Current file: —")
        self.current_file_label.setObjectName("CurrentFile")
        self.current_file_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.process_metrics_label = QLabel("Session: —   •   Elapsed: 00:00:00")
        self.process_metrics_label.setObjectName("ProcessMetrics")
        process_info_layout.addWidget(self.current_file_label)
        process_info_layout.addWidget(self.process_metrics_label)
        self.process_card.add_widget(process_info_panel)

        process_buttons = QHBoxLayout()
        self.log_toggle_button = QPushButton("Show technical log")
        self.log_toggle_button.setProperty("role", "ghost")
        self.log_toggle_button.clicked.connect(self._toggle_log_visibility)
        process_buttons.addWidget(self.log_toggle_button)
        process_buttons.addStretch()
        self.open_output_button = QPushButton("Open Output Folder")
        self.open_output_button.clicked.connect(self._open_output_folder)
        process_buttons.addWidget(self.open_output_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setProperty("role", "danger")
        self.cancel_button.clicked.connect(self._cancel_processing)
        process_buttons.addWidget(self.cancel_button)
        self.process_button = QPushButton("Prepare Video")
        self.process_button.setProperty("role", "primary")
        self.process_button.clicked.connect(self._start_processing)
        self.process_button.setDefault(True)
        process_buttons.addWidget(self.process_button)
        self.process_card.add_layout(process_buttons)

        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumBlockCount(1000)
        self.log_edit.setMaximumHeight(170)
        self.log_edit.setPlaceholderText("Processing details and errors appear here.")
        self.log_edit.setVisible(False)
        self.process_card.add_widget(self.log_edit)
        body.addWidget(self.process_card)

        body.addStretch()
        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)
        self.setCentralWidget(central)
        self._update_subtitle_style()
        self._update_workflow_navigation()
        self._refresh_processing_visuals()

    def _toggle_log_visibility(self) -> None:
        visible = not self.log_edit.isVisible()
        self.log_edit.setVisible(visible)
        self.log_toggle_button.setText(
            "Hide technical log" if visible else "Show technical log"
        )

    def _set_processing_state(
        self,
        state: str,
        title: str,
        detail: str = "",
    ) -> None:
        self.processing_visual_state = state
        self.status_label.setText(title)
        if detail:
            self.process_detail_label.setText(detail)
        badge_text = {
            "idle": "Idle",
            "running": "Processing",
            "success": "Complete",
            "warning": "Attention",
            "error": "Failed",
        }.get(state, state.title())
        self.process_state_badge.setText(badge_text)
        set_widget_state(self.process_state_badge, state)
        self._refresh_processing_visuals()

    def _refresh_processing_visuals(self) -> None:
        if not hasattr(self, "process_metrics_label"):
            return
        if self.is_processing:
            elapsed_seconds = 0
            if self.processing_started_at is not None:
                elapsed_seconds = max(
                    0,
                    int((datetime.now() - self.processing_started_at).total_seconds()),
                )
            percent = max(0, self.progress_bar.value())
            remaining_text = "calculating"
            if 0 < percent < 100 and elapsed_seconds > 0:
                remaining_seconds = int(elapsed_seconds * (100 - percent) / percent)
                remaining_text = format_time(remaining_seconds)
            session_number = min(self.current_segment_index + 1, len(self.segments))
            self.process_metrics_label.setText(
                f"Session: {session_number or '—'} of {len(self.segments) or '—'}   •   "
                f"Elapsed: {format_time(elapsed_seconds)}   •   Remaining: {remaining_text}"
            )
            current_name = self.current_final_path.name if self.current_final_path else "—"
            self.current_file_label.setText(f"Current file: {current_name}")
        elif self.processing_visual_state == "success" and self.last_output_directory:
            self.process_metrics_label.setText(
                f"Created {len(self.segments)} session(s)   •   Progress: 100%"
            )
            self.current_file_label.setText(
                f"Output: {self.last_output_directory}"
            )
        else:
            self.process_metrics_label.setText("Session: —   •   Elapsed: 00:00:00")
            if self.last_output_directory:
                self.current_file_label.setText(
                    f"Last output: {self.last_output_directory}"
                )
            else:
                self.current_file_label.setText("Current file: —")

    def _update_workflow_navigation(self) -> None:
        if not hasattr(self, "workflow_steps"):
            return
        loaded = self.input_path is not None and self.input_info is not None
        has_subtitles = bool(self.subtitle_cues)
        has_sessions = bool(self.segments)
        has_profile = self.current_profile() is not None if hasattr(self, "profile_combo") else False
        blocked = any(
            check.get("status") == "red" for check in self.readiness_results
        )

        self.workflow_steps["source"].set_state(
            "complete" if loaded else "current",
            self.input_path.name if loaded and self.input_path else "Choose a video",
        )
        if not loaded:
            subtitle_state, subtitle_detail = "pending", "Optional"
        elif has_subtitles:
            subtitle_state, subtitle_detail = "complete", f"{len(self.subtitle_cues)} cues"
        else:
            subtitle_state, subtitle_detail = "complete", "No subtitles"
        self.workflow_steps["subtitles"].set_state(subtitle_state, subtitle_detail)

        session_state = "complete" if has_sessions else ("current" if loaded else "pending")
        session_detail = f"{len(self.segments)} planned" if has_sessions else "Set timing"
        self.workflow_steps["sessions"].set_state(session_state, session_detail)

        output_state = "complete" if loaded and has_profile else ("current" if loaded else "pending")
        profile = self.current_profile() if has_profile else None
        output_detail = str(profile.get("name")) if profile else "Choose target"
        self.workflow_steps["output"].set_state(output_state, output_detail)

        if self.is_processing:
            process_state, process_detail = "current", "In progress"
        elif self.processing_visual_state == "success":
            process_state, process_detail = "complete", "Files created"
        elif loaded and has_sessions and has_profile and not blocked:
            process_state, process_detail = "current", "Ready"
        else:
            process_state, process_detail = "pending", "Prepare files"
        self.workflow_steps["process"].set_state(process_state, process_detail)

    # ------------------------------ basic state -----------------------------

    def _refresh_binary_paths(
        self,
        force_capability_refresh: bool = False,
    ) -> None:
        previous_ffmpeg = self.ffmpeg_path

        self.ffmpeg_path = locate_binary(
            "ffmpeg",
            str(self.settings.value("ffmpeg_path", "")),
        )
        self.ffprobe_path = locate_binary(
            "ffprobe",
            str(self.settings.value("ffprobe_path", "")),
        )

        if force_capability_refresh or self.ffmpeg_path != previous_ffmpeg:
            self.encoder_names = None
            self.subtitle_filter_available = None
            self.subtitle_render_test_result = None

    def _refresh_output_root(self) -> None:
        output_root = str(self.settings.value("output_root", ""))
        self.output_root_label.setText(output_root or "Not configured")
        self.output_root_label.setToolTip(output_root)
        if hasattr(self, "readiness_table"):
            self._refresh_readiness()

    def _custom_profiles(self) -> list[dict[str, Any]]:
        raw = str(self.settings.value("custom_profiles", "[]"))
        try:
            profiles = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if not isinstance(profiles, list):
            return []
        return [profile for profile in profiles if isinstance(profile, dict)]

    def _save_custom_profiles(self, profiles: list[dict[str, Any]]) -> None:
        self.settings.setValue(
            "custom_profiles",
            json.dumps(profiles, ensure_ascii=False),
        )
        self.settings.sync()

    def _load_profiles(self, select_id: str | None = None) -> None:
        previous_id = select_id
        if previous_id is None and self.profile_combo.count():
            current = self.current_profile()
            previous_id = str(current.get("id", "")) if current else ""

        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for profile in DEVICE_PROFILES:
            name = str(profile.get("name", "Unnamed profile"))
            format_label = str(
                profile.get("format_label") or profile.get("extension", "")
            ).upper()
            self.profile_combo.addItem(f"{name} — {format_label}", profile)
        self.profile_combo.insertSeparator(self.profile_combo.count())
        for profile in FORMAT_PROFILES:
            self.profile_combo.addItem(str(profile.get("name", "Unnamed profile")), profile)
        custom_profiles = self._custom_profiles()
        if custom_profiles:
            self.profile_combo.insertSeparator(self.profile_combo.count())
        for profile in custom_profiles:
            self.profile_combo.addItem(str(profile.get("name", "Unnamed profile")), profile)
        self.profile_combo.blockSignals(False)

        desired_id = previous_id or str(
            self.settings.value("last_profile_id", "format_mp4")
        )
        selected = False
        for index in range(self.profile_combo.count()):
            profile = self.profile_combo.itemData(index)
            if isinstance(profile, dict) and str(profile.get("id")) == desired_id:
                self.profile_combo.setCurrentIndex(index)
                selected = True
                break
        if not selected:
            for index in range(self.profile_combo.count()):
                profile = self.profile_combo.itemData(index)
                if isinstance(profile, dict) and profile.get("id") == "format_mp4":
                    self.profile_combo.setCurrentIndex(index)
                    break
        self._profile_changed()

    def current_profile(self) -> dict[str, Any] | None:
        profile = self.profile_combo.currentData()
        return dict(profile) if isinstance(profile, dict) else None

    def _profile_changed(self, _index: int = -1) -> None:
        profile = self.current_profile()
        if not profile:
            self.profile_details_label.clear()
            return
        self.settings.setValue("last_profile_id", str(profile.get("id", "")))
        resolution = "source resolution"
        if int(profile.get("max_width", 0)) and int(profile.get("max_height", 0)):
            resolution = (
                f"up to {profile['max_width']}×{profile['max_height']}"
            )
        audio = str(profile.get("audio_codec", "none"))
        format_label = str(
            profile.get("format_label")
            or profile.get("extension", "")
        ).upper()
        details = (
            f"{format_label} (.{profile.get('extension', '')}) • "
            f"{profile.get('video_codec', '')} video • {audio} audio • {resolution}"
        )
        if profile.get("profile_type") == "device":
            details += " • documented container compatibility preset"
        self.profile_details_label.setText(details)
        is_custom = not bool(profile.get("builtin", False))
        self.edit_profile_button.setEnabled(is_custom and not self.is_processing)
        self.delete_profile_button.setEnabled(is_custom and not self.is_processing)
        if hasattr(self, "readiness_table"):
            self._refresh_readiness()

    def _update_controls(self) -> None:
        loaded = self.input_path is not None and self.input_info is not None
        idle = not self.is_processing
        self.open_button.setEnabled(idle)
        self.settings_button.setEnabled(idle)
        self.play_button.setEnabled(loaded)
        self.seek_back_button.setEnabled(loaded)
        self.seek_forward_button.setEnabled(loaded)
        self.position_slider.setEnabled(loaded)
        self.open_subtitle_button.setEnabled(loaded and idle)
        self.clear_subtitle_button.setEnabled(
            bool(self.subtitle_cues) and loaded and idle
        )
        subtitle_ready = bool(self.subtitle_cues) and loaded and idle
        for control in (
            self.subtitle_minus_10_button,
            self.subtitle_minus_5_button,
            self.subtitle_offset_back_button,
            self.subtitle_offset_spin,
            self.subtitle_offset_forward_button,
            self.subtitle_plus_5_button,
            self.subtitle_plus_10_button,
        ):
            control.setEnabled(subtitle_ready)
        self.burn_subtitles_checkbox.setEnabled(subtitle_ready)

        style_enabled = (
            subtitle_ready
            and self.exact_mode_radio.isChecked()
            and self.burn_subtitles_checkbox.isChecked()
        )
        self.subtitle_appearance_frame.setVisible(
            bool(self.subtitle_cues) and self.burn_subtitles_checkbox.isChecked()
        )
        self.subtitle_font_button.setEnabled(style_enabled)
        self.subtitle_size_spin.setEnabled(style_enabled)
        self.subtitle_placement_combo.setEnabled(style_enabled)
        self.subtitle_text_color_button.setEnabled(style_enabled)
        self.subtitle_outline_color_button.setEnabled(style_enabled)
        self.trim_start_edit.setEnabled(loaded and idle)
        self.trim_end_edit.setEnabled(loaded and idle)
        self.set_start_button.setEnabled(loaded and idle)
        self.set_end_button.setEnabled(loaded and idle)
        self.session_duration_combo.setEnabled(loaded and idle)
        self.custom_duration_edit.setEnabled(loaded and idle)
        self.overlap_mode_combo.setEnabled(loaded and idle)
        self.custom_overlap_edit.setEnabled(loaded and idle)
        self.natural_cut_checkbox.setEnabled(loaded and idle)
        self.review_cuts_button.setEnabled(
            loaded
            and idle
            and self.natural_cut_checkbox.isChecked()
            and len(self.segments) > 1
        )
        self.profile_combo.setEnabled(idle)
        self.new_profile_button.setEnabled(idle)
        self.fast_mode_radio.setEnabled(
            idle and not self.burn_subtitles_checkbox.isChecked()
        )
        self.exact_mode_radio.setEnabled(idle)
        self.process_button.setEnabled(loaded and idle)
        self.cancel_button.setEnabled(self.is_processing)
        self.open_output_button.setEnabled(
            idle
            and self.last_output_directory is not None
            and self.last_output_directory.exists()
        )
        self._profile_changed()
        self._update_workflow_navigation()
        self._refresh_processing_visuals()

    # ---------------------------- settings/profile --------------------------

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh_output_root()
            self._refresh_binary_paths(force_capability_refresh=True)
            self.status_label.setText("Settings saved.")
            self._refresh_readiness()

    def _new_profile(self) -> None:
        dialog = ProfileDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        profile = dialog.result_profile()
        profiles = self._custom_profiles()
        profiles.append(profile)
        self._save_custom_profiles(profiles)
        self._load_profiles(str(profile["id"]))

    def _edit_profile(self) -> None:
        current = self.current_profile()
        if not current or current.get("builtin"):
            return
        dialog = ProfileDialog(current, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        replacement = dialog.result_profile()
        profiles = self._custom_profiles()
        profiles = [
            replacement if str(item.get("id")) == str(current.get("id")) else item
            for item in profiles
        ]
        self._save_custom_profiles(profiles)
        self._load_profiles(str(replacement["id"]))

    def _delete_profile(self) -> None:
        current = self.current_profile()
        if not current or current.get("builtin"):
            return
        answer = QMessageBox.question(
            self,
            APP_NAME,
            f"Delete the custom profile “{current.get('name', '')}”?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        profiles = [
            item
            for item in self._custom_profiles()
            if str(item.get("id")) != str(current.get("id"))
        ]
        self._save_custom_profiles(profiles)
        self._load_profiles("format_mp4")

    # ------------------------------- preview --------------------------------

    def eventFilter(self, watched: Any, event: QEvent) -> bool:
        if (
            watched is self.video_widget
            and event.type() == QEvent.Type.Resize
            and hasattr(self, "subtitle_preview_label")
        ):
            self._position_subtitle_preview()
            self.subtitle_preview_label.raise_()

        return super().eventFilter(watched, event)

    def _position_subtitle_preview(self) -> None:
        margin = 24
        label_height = min(140, max(60, self.video_widget.height() // 4))
        placement = str(self.subtitle_placement_combo.currentData() or "bottom")
        if placement == "top":
            y_position = margin
        elif placement == "center":
            y_position = (self.video_widget.height() - label_height) // 2
        else:
            y_position = self.video_widget.height() - label_height - margin
        self.subtitle_preview_label.setGeometry(
            margin,
            max(0, y_position),
            max(0, self.video_widget.width() - (margin * 2)),
            label_height,
        )

    def _subtitle_offset_seconds(self) -> float:
        return float(self.subtitle_offset_spin.value())

    def _change_subtitle_offset(self, change: float) -> None:
        self.subtitle_offset_spin.setValue(
            self.subtitle_offset_spin.value() + change
        )

    def _subtitle_offset_changed(self, _value: float = 0.0) -> None:
        self.natural_cut_choices = {}
        self.natural_cut_boundaries = []
        if self.natural_cut_checkbox.isChecked():
            self.natural_cut_status_label.setText(
                "Timing changed — review cut points again."
            )
        self._update_subtitle_preview(self.player.position())
        self._update_segment_plan()

    def _cutting_mode_changed(self, _checked: bool = False) -> None:
        if (
            self.fast_mode_radio.isChecked()
            and self.burn_subtitles_checkbox.isChecked()
        ):
            self.burn_subtitles_checkbox.blockSignals(True)
            self.burn_subtitles_checkbox.setChecked(False)
            self.burn_subtitles_checkbox.blockSignals(False)
            self._update_subtitle_style()
        self._update_controls()
        self._refresh_readiness()

    def _burn_subtitles_changed(self, checked: bool) -> None:
        if checked and not self.exact_mode_radio.isChecked():
            self.exact_mode_radio.setChecked(True)
        self._update_subtitle_style()
        self._update_controls()
        self._refresh_readiness()

    def _choose_subtitle_font(self) -> None:
        initial = QFont(self.subtitle_font_family, self.subtitle_size_spin.value())
        font, accepted = QFontDialog.getFont(
            initial,
            self,
            "Choose subtitle font",
        )
        if not accepted:
            return
        self.subtitle_font_family = font.family()
        if font.pointSize() > 0:
            self.subtitle_size_spin.setValue(font.pointSize())
        self._update_subtitle_style()

    def _choose_subtitle_color(self, target: str) -> None:
        current = (
            self.subtitle_text_color
            if target == "text"
            else self.subtitle_outline_color
        )
        color = QColorDialog.getColor(
            QColor(current),
            self,
            "Choose subtitle colour",
        )
        if not color.isValid():
            return
        if target == "text":
            self.subtitle_text_color = color.name().upper()
        else:
            self.subtitle_outline_color = color.name().upper()
        self._update_subtitle_style()

    def _update_subtitle_style(self, _index: int = -1) -> None:
        if not hasattr(self, "subtitle_preview_label"):
            return
        size = self.subtitle_size_spin.value()
        family = self.subtitle_font_family.replace('"', "")
        self.subtitle_font_button.setText(family)
        self.subtitle_preview_label.setStyleSheet(
            "QLabel {"
            f"color: {self.subtitle_text_color};"
            "background-color: rgba(0, 0, 0, 155);"
            f"font-family: \"{family}\";"
            f"font-size: {size}px;"
            "font-weight: 600;"
            f"border: 2px solid {self.subtitle_outline_color};"
            "border-radius: 4px;"
            "padding: 7px;"
            "}"
        )
        for button, color in (
            (self.subtitle_text_color_button, self.subtitle_text_color),
            (self.subtitle_outline_color_button, self.subtitle_outline_color),
        ):
            foreground = "#000000" if QColor(color).lightness() > 150 else "#FFFFFF"
            button.setText(color)
            button.setStyleSheet(
                f"background-color: {color}; color: {foreground};"
            )
        self._position_subtitle_preview()
        if hasattr(self, "readiness_table"):
            self._refresh_readiness()

    def _choose_video(self) -> None:
        starting = str(self.settings.value("last_input_directory", str(Path.home())))
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Open local video",
            starting,
            VIDEO_FILTER,
        )
        if selected:
            self._load_video(Path(selected))

    def _load_video(self, path: Path) -> None:
        self._refresh_binary_paths()
        if not self.ffprobe_path:
            QMessageBox.critical(
                self,
                APP_NAME,
                "FFprobe was not found. Place ffprobe.exe beside the application "
                "or select it in Settings.",
            )
            return
        self.status_label.setText("Reading video information…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            info = probe_media(path, self.ffprobe_path)
        except RuntimeError as exc:
            QMessageBox.critical(
                self,
                APP_NAME,
                f"Could not open the video:\n\n{exc}",
            )
            self.status_label.setText("Could not read video.")
            return
        finally:
            QApplication.restoreOverrideCursor()

        self.player.stop()
        self.input_path = path.resolve()
        self.input_info = info
        self.natural_cut_choices = {}
        self.natural_cut_boundaries = []
        self.natural_cut_checkbox.setChecked(False)
        self._clear_subtitle()
        self.settings.setValue(
            "last_input_directory",
            str(path.resolve().parent),
        )
        self.trim_start_edit.set_seconds(0)
        self.trim_end_edit.set_seconds(math.floor(info["duration"]))
        self.player.setSource(QUrl.fromLocalFile(str(self.input_path)))
        self.position_slider.setRange(0, int(info["duration"] * 1000))

        fps = f"{info['frame_rate']:.3f}".rstrip("0").rstrip(".")
        audio = info["audio_codec"] or "no audio"
        self.input_info_label.setText(
            f"{self.input_path.name}  •  {format_time(info['duration'])}  •  "
            f"{info['width']}×{info['height']}  •  {fps or '?'} fps  •  "
            f"{info['video_codec']} video / {audio}"
        )
        self._set_processing_state(
            "idle",
            "Video loaded",
            "Review subtitles, session timing, output profile, and readiness checks.",
        )
        self.progress_bar.setValue(0)
        self.log_edit.clear()
        self._update_segment_plan()
        self._update_controls()

    def _choose_subtitle(self) -> None:
        if not self.input_path:
            return

        starting = str(
            self.settings.value(
                "last_subtitle_directory",
                str(self.input_path.parent),
            )
        )

        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Choose subtitle",
            starting,
            "Subtitle files (*.srt *.vtt);;All files (*.*)",
        )

        if not selected:
            return

        path = Path(selected).resolve()

        try:
            _text, encoding = decode_subtitle_file(path)
            cues = read_subtitle_file(path)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(
                self,
                APP_NAME,
                f"Could not read the subtitle:\n\n{exc}",
            )
            return

        self.subtitle_path = path
        self.subtitle_cues = cues
        self.subtitle_encoding = encoding
        self.subtitle_path_label.setText(path.name)
        self.subtitle_path_label.setToolTip(str(path))
        self.settings.setValue(
            "last_subtitle_directory",
            str(path.parent),
        )
        self.status_label.setText(
            f"Subtitle loaded: {len(cues)} cues."
        )
        self._update_subtitle_preview(self.player.position())
        self._update_controls()
        self._refresh_readiness()

    def _clear_subtitle(self) -> None:
        self.subtitle_path = None
        self.subtitle_cues = []
        self.subtitle_encoding = ""

        if hasattr(self, "subtitle_offset_spin"):
            self.subtitle_offset_spin.blockSignals(True)
            self.subtitle_offset_spin.setValue(0.0)
            self.subtitle_offset_spin.blockSignals(False)
        if hasattr(self, "burn_subtitles_checkbox"):
            self.burn_subtitles_checkbox.blockSignals(True)
            self.burn_subtitles_checkbox.setChecked(False)
            self.burn_subtitles_checkbox.blockSignals(False)

        if hasattr(self, "subtitle_path_label"):
            self.subtitle_path_label.setText("None selected")
            self.subtitle_path_label.setToolTip("")

        if hasattr(self, "subtitle_preview_label"):
            self.subtitle_preview_label.clear()
            self.subtitle_preview_label.hide()

        if hasattr(self, "clear_subtitle_button"):
            self._update_controls()
        if hasattr(self, "readiness_table"):
            self._refresh_readiness()

    def _update_subtitle_preview(self, position_ms: int) -> None:
        position = position_ms / 1000
        offset = self._subtitle_offset_seconds()

        active = [
            str(cue["text"])
            for cue in self.subtitle_cues
            if (
                float(cue["start"]) + offset
                <= position
                < float(cue["end"]) + offset
            )
        ]

        if not active:
            self.subtitle_preview_label.clear()
            self.subtitle_preview_label.hide()
            return

        preview_text = "\n".join(active)
        preview_text = re.sub(r"<[^>]+>", "", preview_text)
        preview_text = html.unescape(preview_text)
        self.subtitle_preview_label.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
            if contains_rtl_text(preview_text)
            else Qt.LayoutDirection.LeftToRight
        )
        self.subtitle_preview_label.setText(preview_text)
        self.subtitle_preview_label.show()
        self.subtitle_preview_label.raise_()

    def _toggle_playback(self) -> None:
        if not self.input_path:
            return
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        self.play_button.setText(
            "Pause"
            if state == QMediaPlayer.PlaybackState.PlayingState
            else "Play"
        )

    def _player_position_changed(self, position: int) -> None:
        if not self.slider_is_down:
            self.position_slider.setValue(position)

        self._update_player_time(position)
        self._update_subtitle_preview(position)

    def _player_duration_changed(self, duration: int) -> None:
        if duration > 0:
            self.position_slider.setRange(0, duration)
        self._update_player_time(self.player.position())

    def _update_player_time(self, position: int) -> None:
        total = self.player.duration()
        if total <= 0 and self.input_info:
            total = int(self.input_info["duration"] * 1000)
        self.player_time_label.setText(
            f"{format_time(position / 1000)} / {format_time(total / 1000)}"
        )

    def _slider_pressed(self) -> None:
        self.slider_is_down = True

    def _slider_released(self) -> None:
        self.slider_is_down = False
        self.player.setPosition(self.position_slider.value())

    def _slider_moved(self, position: int) -> None:
        self._update_player_time(position)
        self._update_subtitle_preview(position)

    def _seek_relative(self, milliseconds: int) -> None:
        target = max(
            0,
            min(self.player.duration(), self.player.position() + milliseconds),
        )
        self.player.setPosition(target)

    def _player_error(
        self,
        _error: QMediaPlayer.Error,
        error_string: str,
    ) -> None:
        if error_string and self.input_path:
            self.log_edit.appendPlainText(
                "Preview warning: "
                f"{error_string}\nFFmpeg may still be able to process this video."
            )

    def _set_start_from_player(self) -> None:
        self.trim_start_edit.set_seconds(self.player.position() // 1000)
        self._timing_changed()

    def _set_end_from_player(self) -> None:
        self.trim_end_edit.set_seconds(self.player.position() // 1000)
        self._timing_changed()

    # --------------------------- segment planning ---------------------------

    def _timing_changed(self) -> None:
        if self.natural_cut_choices:
            self.natural_cut_choices = {}
            self.natural_cut_boundaries = []
            self.natural_cut_status_label.setText(
                "Timing changed — review cut points again."
            )
        self._update_segment_plan()

    def _session_duration_changed(self, _index: int = -1) -> None:
        custom = self.session_duration_combo.currentData() is None
        self.custom_duration_edit.setVisible(custom)
        self._timing_changed()

    def _overlap_mode_changed(self, _index: int = -1) -> None:
        custom = self.overlap_mode_combo.currentData() == "custom"
        self.custom_overlap_edit.setVisible(custom)
        self._timing_changed()

    def _natural_cut_toggled(self, checked: bool) -> None:
        if not checked:
            self.natural_cut_choices = {}
            self.natural_cut_boundaries = []
            self.natural_cut_status_label.setText("Off")
            self._update_segment_plan()
            self._update_controls()
            return
        self.natural_cut_status_label.setText("Not analyzed yet.")
        self._update_segment_plan()
        self._update_controls()
        if self.input_info and len(self.segments) > 1:
            QTimer.singleShot(0, self._review_natural_cuts)

    def _base_segment_plan(self) -> list[dict[str, float]]:
        if not self.input_info:
            return []
        try:
            start, end, session, overlap_mode, overlap = self._timing_values()
        except ValueError:
            return []
        duration = float(self.input_info["duration"])
        if start < 0 or end <= start or start >= duration:
            return []
        if session <= 0:
            return []
        if overlap_mode == "custom" and not 0 <= overlap < session:
            return []
        return build_segments(
            start,
            min(end, duration),
            session,
            overlap_mode,
            overlap,
        )

    def _internal_cut_times(
        self,
        segments: list[dict[str, float]],
    ) -> list[float]:
        if not segments:
            return []
        first = float(segments[0]["start"])
        last = float(segments[-1]["end"])
        values: set[float] = set()
        for segment in segments:
            for key in ("start", "end"):
                value = round(float(segment[key]), 3)
                if value > first + 0.001 and value < last - 0.001:
                    values.add(value)
        return sorted(values)

    def _review_natural_cuts(self) -> None:
        if not self.input_path or not self.input_info:
            return
        self._refresh_binary_paths()
        if not self.ffmpeg_path:
            QMessageBox.critical(
                self,
                APP_NAME,
                "FFmpeg is required to find natural scene changes.",
            )
            return
        base_segments = self._base_segment_plan()
        boundaries = self._internal_cut_times(base_segments)
        if not boundaries:
            QMessageBox.information(
                self,
                APP_NAME,
                "This session plan has no internal cut points.",
            )
            return

        self.player.pause()
        self.status_label.setText("Finding natural cut points…")
        self.natural_cut_status_label.setText("Analyzing nearby scenes…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        analyzed: list[dict[str, Any]] = []
        try:
            for number, planned in enumerate(boundaries, start=1):
                self.natural_cut_status_label.setText(
                    f"Analyzing cut {number} of {len(boundaries)}…"
                )
                QApplication.processEvents()
                kinds_by_time: dict[float, set[str]] = {}
                for value in subtitle_gap_candidates(
                    self.subtitle_cues,
                    planned,
                    60.0,
                    self._subtitle_offset_seconds(),
                ):
                    kinds_by_time.setdefault(value, set()).add("subtitle gap")
                for value in detect_scene_change_candidates(
                    self.input_path,
                    self.ffmpeg_path,
                    planned,
                ):
                    kinds_by_time.setdefault(value, set()).add("scene change")

                candidates = [
                    {
                        "time": value,
                        "kind": " + ".join(sorted(kinds)),
                    }
                    for value, kinds in sorted(kinds_by_time.items())
                    if abs(value - planned) <= 60.0
                ]
                if not candidates:
                    candidates = [{"time": planned, "kind": "planned time"}]

                preferred = self.natural_cut_choices.get(round(planned, 3))
                if preferred is None:
                    selected_index = min(
                        range(len(candidates)),
                        key=lambda index: abs(
                            float(candidates[index]["time"]) - planned
                        ),
                    )
                else:
                    selected_index = min(
                        range(len(candidates)),
                        key=lambda index: abs(
                            float(candidates[index]["time"]) - preferred
                        ),
                    )
                analyzed.append(
                    {
                        "planned": planned,
                        "candidates": candidates,
                        "selected_index": selected_index,
                    }
                )
        finally:
            QApplication.restoreOverrideCursor()

        dialog = NaturalCutDialog(
            boundaries=analyzed,
            video_path=self.input_path,
            video_duration_seconds=float(self.input_info["duration"]),
            subtitle_cues=self.subtitle_cues,
            subtitle_offset_seconds=self._subtitle_offset_seconds(),
            subtitle_style={
                "font": self.subtitle_font_family,
                "size": self.subtitle_size_spin.value(),
                "text_color": self.subtitle_text_color,
                "outline_color": self.subtitle_outline_color,
                "placement": str(
                    self.subtitle_placement_combo.currentData() or "bottom"
                ),
            },
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            if not self.natural_cut_choices:
                self.natural_cut_checkbox.blockSignals(True)
                self.natural_cut_checkbox.setChecked(False)
                self.natural_cut_checkbox.blockSignals(False)
                self.natural_cut_status_label.setText("Off")
            self.status_label.setText("Natural cut review cancelled.")
            self._update_segment_plan()
            self._update_controls()
            return

        self.natural_cut_boundaries = analyzed
        self.natural_cut_choices = dialog.choices()
        adjusted = sum(
            1
            for planned, selected in self.natural_cut_choices.items()
            if abs(planned - selected) > 0.001
        )
        self.natural_cut_status_label.setText(
            f"{len(self.natural_cut_choices)} cut point(s), "
            f"{adjusted} moved."
        )
        self.status_label.setText("Natural cut points applied.")
        self._update_segment_plan()
        self._update_controls()

    def _apply_natural_cut_choices(
        self,
        segments: list[dict[str, float]],
    ) -> list[dict[str, float]]:
        if not self.natural_cut_checkbox.isChecked() or not self.natural_cut_choices:
            return segments
        adjusted: list[dict[str, float]] = []
        for segment in segments:
            start = self.natural_cut_choices.get(
                round(float(segment["start"]), 3),
                float(segment["start"]),
            )
            end = self.natural_cut_choices.get(
                round(float(segment["end"]), 3),
                float(segment["end"]),
            )
            if end <= start + 0.25:
                start = float(segment["start"])
                end = float(segment["end"])
            adjusted.append(
                {
                    "start": start,
                    "end": end,
                    "duration": end - start,
                }
            )
        return adjusted

    def _session_seconds(self) -> int:
        selected = self.session_duration_combo.currentData()

        if selected is not None:
            return int(selected)

        return self.custom_duration_edit.seconds()

    def _overlap_seconds(self) -> int:
        if self.overlap_mode_combo.currentData() == "custom":
            return self.custom_overlap_edit.seconds()

        return 0

    def _timing_values(self) -> tuple[int, int, int, str, int]:
        return (
            self.trim_start_edit.seconds(),
            self.trim_end_edit.seconds(),
            self._session_seconds(),
            str(self.overlap_mode_combo.currentData()),
            self._overlap_seconds(),
        )

    def _update_segment_plan(self) -> None:
        self.segment_table.setRowCount(0)
        self.segments = []

        if not self.input_info:
            self.plan_summary_label.setText("No video loaded.")
            if hasattr(self, "readiness_table"):
                self._refresh_readiness()
            return

        try:
            (
                start,
                end,
                session_seconds,
                overlap_mode,
                overlap_seconds,
            ) = self._timing_values()
        except ValueError:
            self.plan_summary_label.setText(
                "Enter valid trim, session, and overlap times."
            )
            self._refresh_readiness()
            return

        duration = float(self.input_info["duration"])

        if start < 0 or end <= start:
            self.plan_summary_label.setText(
                "The end time must be later than the start time."
            )
            self._refresh_readiness()
            return

        if start >= duration or end > duration + 1:
            self.plan_summary_label.setText(
                f"Trim points must be inside the "
                f"{format_time(duration)} video."
            )
            self._refresh_readiness()
            return

        if session_seconds <= 0:
            self.plan_summary_label.setText(
                "Session duration must be greater than zero."
            )
            self._refresh_readiness()
            return

        if (
            overlap_mode == "custom"
            and (overlap_seconds < 0 or overlap_seconds >= session_seconds)
        ):
            self.plan_summary_label.setText(
                "Custom overlap must be shorter than the "
                "session duration."
            )
            self._refresh_readiness()
            return

        end = min(end, duration)

        base_segments = build_segments(
            start,
            end,
            session_seconds,
            overlap_mode,
            overlap_seconds,
        )
        self.segments = self._apply_natural_cut_choices(base_segments)

        usable = end - start
        total_overlap = max(
            0.0,
            sum(
                segment["duration"]
                for segment in self.segments
            )
            - usable,
        )

        natural_text = ""
        if self.natural_cut_checkbox.isChecked():
            natural_text = (
                "  •  Natural cuts: applied"
                if self.natural_cut_choices
                else "  •  Natural cuts: review needed"
            )
        self.plan_summary_label.setText(
            f"Usable video: {format_time(usable)}  •  "
            f"Output sessions: {len(self.segments)}  •  "
            f"Total repeated overlap: "
            f"{format_time(total_overlap)}"
            f"{natural_text}"
        )

        self.segment_table.setRowCount(len(self.segments))

        for row, segment in enumerate(self.segments):
            values = (
                f"{row + 1:02d}",
                format_time(segment["start"]),
                format_time(segment["end"]),
                format_time(segment["duration"]),
            )

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.segment_table.setItem(
                    row,
                    column,
                    item,
                )

        self.segment_table.resizeColumnsToContents()
        if hasattr(self, "review_cuts_button"):
            self.review_cuts_button.setEnabled(
                not self.is_processing
                and self.natural_cut_checkbox.isChecked()
                and len(self.segments) > 1
            )
        self._refresh_readiness()

    # ------------------------------ processing ------------------------------

    def _load_ffmpeg_capabilities(self) -> None:
        if not self.ffmpeg_path:
            self.encoder_names = set()
            self.subtitle_filter_available = False
            return

        if self.subtitle_filter_available is None:
            self.subtitle_filter_available = ffmpeg_has_filter(
                self.ffmpeg_path,
                "subtitles",
            )
        if self.encoder_names is None:
            try:
                result = subprocess.run(
                    [self.ffmpeg_path, "-hide_banner", "-encoders"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=20,
                    creationflags=windows_creation_flags(),
                    check=False,
                )
                self.encoder_names = {
                    match.group(1)
                    for line in result.stdout.splitlines()
                    if (
                        match := re.match(
                            r"^\s*[A-Z\.]{6}\s+(\S+)",
                            line,
                        )
                    )
                }
            except (OSError, subprocess.TimeoutExpired):
                self.encoder_names = set()

    def _collect_readiness_checks(self) -> list[dict[str, str]]:
        checks: list[dict[str, str]] = []

        def add(status: str, name: str, result: str) -> None:
            checks.append(
                {"status": status, "name": name, "result": result}
            )

        if not self.input_path or not self.input_info:
            add("yellow", "Video", "Choose a video to run the readiness check.")
            return checks

        self._refresh_binary_paths()
        if self.ffmpeg_path and self.ffprobe_path:
            add("green", "FFmpeg executable", self.ffmpeg_path)
            add("green", "FFprobe executable", self.ffprobe_path)
        else:
            missing = []
            if not self.ffmpeg_path:
                missing.append("FFmpeg")
            if not self.ffprobe_path:
                missing.append("FFprobe")
            add(
                "red",
                "Media tools",
                f"{' and '.join(missing)} must be configured before processing.",
            )

        info = self.input_info
        add(
            "green",
            "Source video",
            f"{format_time(info['duration'])}, "
            f"{info['width']}×{info['height']}, "
            f"{info['video_codec']} video.",
        )

        average_rate = float(info.get("average_frame_rate") or 0)
        real_rate = float(info.get("real_frame_rate") or 0)
        if (
            average_rate > 0
            and real_rate > 0
            and abs(average_rate - real_rate) > max(0.05, average_rate * 0.01)
        ):
            add(
                "yellow",
                "Frame timing",
                "Variable frame-rate timing may make Fast cuts less precise; "
                "Exact mode is safer.",
            )
        elif float(info.get("frame_rate") or 0) > 60.01:
            add(
                "yellow",
                "Frame timing",
                f"{info['frame_rate']:.2f} fps is unusually high for older "
                "feedback players.",
            )
        else:
            add(
                "green",
                "Frame timing",
                f"{float(info.get('frame_rate') or 0):.3f} fps appears regular.",
            )

        transfer = str(info.get("color_transfer") or "").lower()
        if transfer in {"smpte2084", "arib-std-b67"}:
            add(
                "yellow",
                "Colour range",
                "The source is HDR. Legacy outputs may look washed out because "
                "automatic HDR tone mapping is not applied.",
            )
        else:
            add("green", "Colour range", "No HDR transfer was detected.")

        field_order = str(info.get("field_order") or "").lower()
        if field_order not in {"", "unknown", "progressive"}:
            add(
                "yellow",
                "Scan type",
                f"The source is {field_order}; motion may show interlacing lines.",
            )
        else:
            add("green", "Scan type", "Progressive or ordinary scan detected.")

        if info.get("audio_codec"):
            channels = int(info.get("audio_channels") or 0)
            if channels > 2:
                add(
                    "yellow",
                    "Audio",
                    f"{channels}-channel audio will be converted to stereo in "
                    "Exact mode.",
                )
            else:
                add(
                    "green",
                    "Audio",
                    f"{info['audio_codec']} audio, "
                    f"{channels or '?'} channel(s).",
                )
        else:
            add(
                "yellow",
                "Audio",
                "No audio stream was found; the output will be silent.",
            )

        profile = self.current_profile()
        if not profile:
            add("red", "Target", "Choose a target system or output format.")
        else:
            add(
                "green",
                "Target",
                f"{profile.get('name')} → "
                f"{str(profile.get('format_label') or profile.get('extension')).upper()}, "
                f"{profile.get('video_codec')} / {profile.get('audio_codec')}.",
            )

            if self.ffmpeg_path:
                self._load_ffmpeg_capabilities()
                required_encoders = {
                    str(profile.get("video_codec", "")),
                    str(profile.get("audio_codec", "")),
                } - {"", "none"}
                unavailable = sorted(
                    encoder
                    for encoder in required_encoders
                    if self.encoder_names is not None
                    and encoder not in self.encoder_names
                )
                if unavailable and self.exact_mode_radio.isChecked():
                    add(
                        "red",
                        "Encoders",
                        "This FFmpeg build lacks: " + ", ".join(unavailable) + ".",
                    )
                else:
                    add(
                        "green",
                        "Encoders",
                        "The selected output encoders are available.",
                    )

            if self.fast_mode_radio.isChecked():
                mismatch: list[str] = []
                expected_video = target_codec_name(
                    str(profile.get("video_codec", ""))
                )
                expected_audio = target_codec_name(
                    str(profile.get("audio_codec", ""))
                )
                if expected_video and info.get("video_codec") != expected_video:
                    mismatch.append(
                        f"video is {info.get('video_codec')}, needs {expected_video}"
                    )
                if (
                    info.get("audio_codec")
                    and expected_audio not in {"", "none"}
                    and info.get("audio_codec") != expected_audio
                ):
                    mismatch.append(
                        f"audio is {info.get('audio_codec')}, needs {expected_audio}"
                    )
                max_width = int(profile.get("max_width", 0))
                max_height = int(profile.get("max_height", 0))
                if max_width and int(info.get("width", 0)) > max_width:
                    mismatch.append(
                        f"width {info.get('width')} exceeds {max_width}"
                    )
                if max_height and int(info.get("height", 0)) > max_height:
                    mismatch.append(
                        f"height {info.get('height')} exceeds {max_height}"
                    )
                expected_pixel = str(profile.get("pixel_format") or "")
                if (
                    expected_pixel
                    and info.get("pixel_format")
                    and info.get("pixel_format") != expected_pixel
                ):
                    mismatch.append(
                        f"pixel format is {info.get('pixel_format')}, "
                        f"needs {expected_pixel}"
                    )
                target_channels = int(profile.get("audio_channels", 0))
                if (
                    target_channels
                    and int(info.get("audio_channels", 0)) > target_channels
                ):
                    mismatch.append(
                        f"audio has {info.get('audio_channels')} channels, "
                        f"target uses {target_channels}"
                    )
                if mismatch:
                    add(
                        "red",
                        "Cutting mode",
                        "Fast mode cannot change " + "; ".join(mismatch) + ".",
                    )
                else:
                    add(
                        "green",
                        "Cutting mode",
                        "Fast stream copy matches the selected profile; cut "
                        "times may move to nearby keyframes.",
                    )
            else:
                add(
                    "green",
                    "Cutting mode",
                    "Exact mode will convert codecs, resolution, pixel format, "
                    "and channel count as needed.",
                )

        if not self.segments:
            add("red", "Session plan", "The trim and session times are not valid.")
        else:
            add(
                "green",
                "Session plan",
                f"{len(self.segments)} output session(s), "
                f"{format_time(sum(s['duration'] for s in self.segments))} "
                "of output.",
            )

        if self.natural_cut_checkbox.isChecked():
            if len(self.segments) <= 1:
                add(
                    "green",
                    "Natural cuts",
                    "Only one session is planned, so no internal cut is needed.",
                )
            elif not self.natural_cut_choices:
                add(
                    "red",
                    "Natural cuts",
                    "Find and review the natural cut points before processing.",
                )
            else:
                add(
                    "green",
                    "Natural cuts",
                    f"{len(self.natural_cut_choices)} reviewed cut point(s) "
                    "will be used.",
                )

        if not self.subtitle_cues:
            add("green", "Subtitles", "No subtitle file selected.")
        else:
            if self.subtitle_encoding in {"utf-8-sig", "utf-16"}:
                add(
                    "green",
                    "Subtitle text",
                    f"{len(self.subtitle_cues)} Unicode cue(s) loaded.",
                )
            else:
                add(
                    "yellow",
                    "Subtitle text",
                    f"{self.subtitle_encoding} text will be rewritten as Unicode "
                    "UTF-8 for output.",
                )

            shifted_first = min(
                float(cue["start"]) for cue in self.subtitle_cues
            ) + self._subtitle_offset_seconds()
            shifted_last = max(
                float(cue["end"]) for cue in self.subtitle_cues
            ) + self._subtitle_offset_seconds()
            if shifted_first < 0 or shifted_last > float(info["duration"]) + 0.5:
                add(
                    "yellow",
                    "Subtitle timing",
                    "The selected offset moves some cues outside the video; "
                    "those portions will be clipped.",
                )
            else:
                add(
                    "green",
                    "Subtitle timing",
                    f"Offset {self._subtitle_offset_seconds():+.3f} s remains "
                    "inside the video.",
                )

            has_rtl = any(
                contains_rtl_text(str(cue["text"]))
                for cue in self.subtitle_cues
            )
            if has_rtl:
                add(
                    "yellow",
                    "Right-to-left text",
                    f"RTL preview is active. Confirm that {self.subtitle_font_family} "
                    "contains the required characters.",
                )

            if self.burn_subtitles_checkbox.isChecked():
                if self.fast_mode_radio.isChecked():
                    add(
                        "red",
                        "Subtitle output",
                        "Burning subtitles requires Exact mode.",
                    )
                elif self.subtitle_filter_available is False:
                    add(
                        "red",
                        "Subtitle output",
                        "The active FFmpeg did not expose the subtitles/libass filter. "
                        f"Active executable: {self.ffmpeg_path or 'not found'}",
                    )
                elif not self.ffmpeg_path:
                    add(
                        "red",
                        "Subtitle output",
                        "FFmpeg is unavailable, so subtitle burn-in cannot be used.",
                    )
                else:
                    if self.subtitle_render_test_result is None:
                        self.subtitle_render_test_result = (
                            test_unicode_subtitle_rendering(self.ffmpeg_path)
                        )
                    subtitle_ok, subtitle_detail = self.subtitle_render_test_result
                    if subtitle_ok:
                        add(
                            "green",
                            "Subtitle output",
                            "Subtitles will be permanently rendered into every video. "
                            + subtitle_detail,
                        )
                    else:
                        add(
                            "red",
                            "Subtitle output",
                            "Permanent subtitle burn-in is unavailable: "
                            + subtitle_detail,
                        )
            elif profile and not bool(profile.get("external_subtitles", True)):
                add(
                    "yellow",
                    "Subtitle output",
                    f"{profile.get('name')} may not load an external SRT "
                    "automatically; burn-in is safer.",
                )
            else:
                add(
                    "green",
                    "Subtitle output",
                    "A matching UTF-8 SRT will be written beside every video.",
                )

        root_text = str(self.settings.value("output_root", "")).strip()
        if not root_text:
            add("red", "Output directory", "Choose an output directory in Settings.")
        else:
            root = Path(root_text).expanduser()
            existing = root
            while not existing.exists() and existing != existing.parent:
                existing = existing.parent
            if not existing.exists() or not existing.is_dir():
                add(
                    "red",
                    "Output directory",
                    "The selected output location is unavailable.",
                )
            elif not os.access(existing, os.W_OK):
                add(
                    "red",
                    "Output directory",
                    "The selected output location is not writable.",
                )
            else:
                add(
                    "green",
                    "Output directory",
                    str(root),
                )
                total_seconds = sum(
                    float(segment["duration"]) for segment in self.segments
                )
                estimate = estimate_output_bytes(info, total_seconds)
                try:
                    free_bytes = shutil.disk_usage(existing).free
                except OSError:
                    free_bytes = 0
                if free_bytes and free_bytes < estimate:
                    add(
                        "red",
                        "Disk space",
                        f"Needs about {format_bytes(estimate)}, but only "
                        f"{format_bytes(free_bytes)} is available. Output may "
                        "be incomplete or corrupt.",
                    )
                elif free_bytes and (
                    free_bytes < estimate * 1.25
                    or free_bytes - estimate < 2 * 1024**3
                ):
                    add(
                        "yellow",
                        "Disk space",
                        f"About {format_bytes(estimate)} is needed and "
                        f"{format_bytes(free_bytes)} is available; free space "
                        "will be tight.",
                    )
                elif free_bytes:
                    add(
                        "green",
                        "Disk space",
                        f"About {format_bytes(estimate)} is needed; "
                        f"{format_bytes(free_bytes)} is available.",
                    )
                else:
                    add(
                        "yellow",
                        "Disk space",
                        "Free space could not be measured.",
                    )

                profile_extension = (
                    str(profile.get("extension", "mp4"))
                    if profile
                    else "mp4"
                )
                sample_name = (
                    safe_filename(self.input_path.stem)
                    + "_session_99."
                    + profile_extension
                )
                projected = root / (
                    safe_filename(self.input_path.stem)
                    + "_YYYYMMDD_HHMMSS"
                ) / sample_name
                if os.name == "nt" and len(str(projected)) >= 240:
                    add(
                        "yellow",
                        "Output path",
                        "The projected Windows path is very long; choose a "
                        "shorter output directory or movie name.",
                    )

        return checks

    def _refresh_readiness(self, *_args: Any) -> None:
        if not hasattr(self, "readiness_table"):
            return
        checks = self._collect_readiness_checks()
        self.readiness_results = checks
        self.readiness_table.setRowCount(len(checks))
        palette = {
            "green": ("✓ Ready", "#DCFCE7", "#166534"),
            "yellow": ("△ Review", "#FEF3C7", "#854D0E"),
            "red": ("× Blocked", "#FEE2E2", "#991B1B"),
        }
        for row, check in enumerate(checks):
            status_text, background, foreground = palette[check["status"]]
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setBackground(QBrush(QColor(background)))
            status_item.setForeground(QBrush(QColor(foreground)))
            status_font = status_item.font()
            status_font.setBold(True)
            status_item.setFont(status_font)
            self.readiness_table.setItem(row, 0, status_item)

            name_item = QTableWidgetItem(check["name"])
            name_font = name_item.font()
            name_font.setBold(True)
            name_item.setFont(name_font)
            self.readiness_table.setItem(row, 1, name_item)

            result_item = QTableWidgetItem(check["result"])
            self.readiness_table.setItem(row, 2, result_item)
            self.readiness_table.setRowHeight(row, 44)

        self.readiness_table.resizeColumnsToContents()
        self.readiness_table.setColumnWidth(0, max(105, self.readiness_table.columnWidth(0)))
        self.readiness_table.setColumnWidth(1, max(145, self.readiness_table.columnWidth(1)))

        if not self.input_path or not self.input_info:
            self.readiness_summary_label.setText(
                "Choose a video to run the full readiness check."
            )
            set_widget_state(self.readiness_summary_label, "neutral")
            self._update_workflow_navigation()
            return

        red_count = sum(1 for check in checks if check["status"] == "red")
        yellow_count = sum(1 for check in checks if check["status"] == "yellow")
        green_count = sum(1 for check in checks if check["status"] == "green")
        if red_count:
            self.readiness_summary_label.setText(
                f"Blocked: {red_count} problem(s) require attention. "
                f"{yellow_count} warning(s), {green_count} ready check(s)."
            )
            set_widget_state(self.readiness_summary_label, "error")
        elif yellow_count:
            self.readiness_summary_label.setText(
                f"Ready with review: {yellow_count} warning(s), "
                f"{green_count} ready check(s)."
            )
            set_widget_state(self.readiness_summary_label, "warning")
        else:
            self.readiness_summary_label.setText(
                f"Ready to process: all {green_count} checks passed."
            )
            set_widget_state(self.readiness_summary_label, "success")
        self._update_workflow_navigation()

    def _preflight(self) -> tuple[dict[str, Any], Path] | None:
        if not self.input_path or not self.input_info:
            QMessageBox.warning(self, APP_NAME, "Open a video first.")
            return None
        self._refresh_binary_paths()
        profile = self.current_profile()
        if not profile:
            QMessageBox.warning(self, APP_NAME, "Choose an output profile.")
            return None

        self._update_segment_plan()
        if not self.segments:
            QMessageBox.warning(self, APP_NAME, "The session plan is not valid.")
            return None

        self._refresh_readiness()
        blocked = [
            check["result"]
            for check in self.readiness_results
            if check["status"] == "red"
        ]
        if blocked:
            QMessageBox.critical(
                self,
                APP_NAME,
                "The readiness check found problems that must be fixed:\n\n• "
                + "\n• ".join(blocked),
            )
            return None
        warnings = [
            check["result"]
            for check in self.readiness_results
            if check["status"] == "yellow"
        ]
        if warnings:
            answer = QMessageBox.question(
                self,
                APP_NAME,
                "The readiness check found items to review:\n\n• "
                + "\n• ".join(warnings)
                + "\n\nContinue anyway?",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return None

        root_text = str(self.settings.value("output_root", "")).strip()
        root = Path(root_text).expanduser()
        try:
            root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.critical(
                self,
                APP_NAME,
                f"The output directory is unavailable:\n{exc}",
            )
            return None

        return profile, root

    def _start_processing(self) -> None:
        preflight = self._preflight()
        if not preflight:
            return
        profile, root = preflight
        assert self.input_path is not None

        try:
            job_directory = unique_directory(root, self.input_path.stem)
        except OSError as exc:
            QMessageBox.critical(
                self,
                APP_NAME,
                f"Could not create the timestamped output folder:\n{exc}",
            )
            return

        self.player.pause()
        self.current_job_directory = job_directory
        self.last_output_directory = job_directory
        self.current_segment_index = 0
        self.completed_duration = 0.0
        self.total_processing_duration = sum(
            segment["duration"] for segment in self.segments
        )
        self.is_processing = True
        self.cancel_requested = False
        self.processing_started_at = datetime.now()
        self.processing_ui_timer.start()
        self.progress_bar.setValue(0)
        self.log_edit.clear()

        mode = "fast" if self.fast_mode_radio.isChecked() else "exact"
        self.manifest = {
            "application": APP_NAME,
            "application_version": APP_VERSION,
            "status": "processing",
            "started_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "input": {
                "path": str(self.input_path),
                "duration_seconds": self.input_info["duration"],
                "format": self.input_info["format_name"],
                "video_codec": self.input_info["video_codec"],
                "audio_codec": self.input_info["audio_codec"],
                "resolution": [
                    self.input_info["width"],
                    self.input_info["height"],
                ],
            },
            "trim": {
                "start_seconds": self.segments[0]["start"],
                "end_seconds": self.segments[-1]["end"],
            },
            "overlap": {
                "mode": str(
                    self.overlap_mode_combo.currentData()
                ),
                "custom_seconds": self._overlap_seconds(),
            },
            "natural_cut_points": {
                "enabled": self.natural_cut_checkbox.isChecked(),
                "choices_seconds": [
                    {
                        "planned": planned,
                        "selected": selected,
                    }
                    for planned, selected in sorted(
                        self.natural_cut_choices.items()
                    )
                ],
            },
            "subtitle": (
                {
                    "source_path": str(self.subtitle_path),
                    "source_encoding": self.subtitle_encoding,
                    "timing_offset_seconds": self._subtitle_offset_seconds(),
                    "output": (
                        "burned-in"
                        if self.burn_subtitles_checkbox.isChecked()
                        else "external_srt"
                    ),
                    "style": {
                        "font": self.subtitle_font_family,
                        "size": self.subtitle_size_spin.value(),
                        "text_color": self.subtitle_text_color,
                        "outline_color": self.subtitle_outline_color,
                        "placement": str(
                            self.subtitle_placement_combo.currentData()
                        ),
                    },
                }
                if self.subtitle_path
                else None
            ),
            "cutting_mode": mode,
            "profile": profile,
            "readiness_check": self.readiness_results,
            "output_directory": str(job_directory),
            "segments": [],
        }
        if not self._persist_manifest():
            self.is_processing = False
            self.processing_ui_timer.stop()
            self._set_processing_state(
                "error",
                "Could not create the job manifest",
                "Check output permissions and available disk space.",
            )
            self._update_controls()
            QMessageBox.critical(
                self,
                APP_NAME,
                "The timestamped folder was created, but the job manifest could "
                "not be written. Check output permissions and free disk space.",
            )
            return
        self._append_log(f"Output folder: {job_directory}")
        self._append_log(
            f"Starting {len(self.segments)} session(s) in {mode} mode."
        )
        self._set_processing_state(
            "running",
            "Starting processing…",
            f"Preparing {len(self.segments)} session(s) in {mode} mode.",
        )
        self._update_controls()
        QTimer.singleShot(0, self._start_next_segment)

    def _start_next_segment(self) -> None:
        if self.cancel_requested:
            self._finish_cancelled()
            return
        if self.current_segment_index >= len(self.segments):
            self._finish_successfully()
            return
        assert self.current_job_directory is not None
        assert self.input_path is not None
        assert self.ffmpeg_path is not None

        profile = self.current_profile()
        if not profile:
            self._fail_job("The selected output profile is no longer available.")
            return
        segment = self.segments[self.current_segment_index]
        extension = str(profile.get("extension", "mp4")).lower().lstrip(".")
        movie_name = safe_filename(self.input_path.stem)
        final_name = (
            f"{movie_name}_session_{self.current_segment_index + 1:02d}.{extension}"
        )
        final_path = self.current_job_directory / final_name
        partial_path = final_path.with_name(
            f"{final_path.stem}.partial{final_path.suffix}"
        )
        self.current_final_path = final_path
        self.current_partial_path = partial_path
        self.current_burn_subtitle_path = None
        self.current_subtitle_cue_count = 0
        self.stdout_buffer = ""
        self.stderr_buffer = ""

        if self.subtitle_cues and self.burn_subtitles_checkbox.isChecked():
            burn_path = self.current_job_directory / (
                f".session_{self.current_segment_index + 1:02d}_burn.srt"
            )
            try:
                cue_count = write_segment_subtitles(
                    burn_path,
                    self.subtitle_cues,
                    segment["start"],
                    segment["end"],
                    self._subtitle_offset_seconds(),
                )
            except OSError as exc:
                self._fail_job(
                    f"Could not prepare subtitles for burn-in: {exc}"
                )
                return
            if cue_count:
                self.current_burn_subtitle_path = burn_path
                self.current_subtitle_cue_count = cue_count
            else:
                try:
                    burn_path.unlink(missing_ok=True)
                except OSError:
                    pass

        arguments = self._build_ffmpeg_arguments(segment, profile, partial_path)
        self._append_log(
            f"Session {self.current_segment_index + 1:02d}: "
            f"{format_time(segment['start'])} → {format_time(segment['end'])}"
        )
        self._set_processing_state(
            "running",
            f"Preparing session {self.current_segment_index + 1} of {len(self.segments)}…",
            f"Source range: {format_time(segment['start'])} to {format_time(segment['end'])}.",
        )
        self.process.setProgram(self.ffmpeg_path)
        self.process.setArguments(arguments)
        self.process.start()
        if not self.process.waitForStarted(5000):
            self._fail_job(
                "FFmpeg could not be started. Check its path in Settings."
            )

    def _build_ffmpeg_arguments(
        self,
        segment: dict[str, float],
        profile: dict[str, Any],
        output_path: Path,
    ) -> list[str]:
        assert self.input_path is not None
        arguments = [
            "-hide_banner",
            "-y",
            "-loglevel",
            "warning",
            "-progress",
            "pipe:1",
            "-nostats",
            "-ss",
            ffmpeg_time(segment["start"]),
            "-i",
            str(self.input_path),
            "-t",
            ffmpeg_time(segment["duration"]),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-sn",
            "-dn",
        ]

        if self.fast_mode_radio.isChecked():
            arguments.extend(["-c", "copy", "-avoid_negative_ts", "make_zero"])
            if str(profile.get("audio_codec", "")).lower() == "none":
                arguments.append("-an")
        else:
            video_codec = str(profile.get("video_codec", "libx264"))
            audio_codec = str(profile.get("audio_codec", "aac"))
            arguments.extend(["-c:v", video_codec])
            video_filters: list[str] = []

            quality_option = str(profile.get("quality_option", ""))
            if quality_option:
                arguments.extend(
                    [quality_option, str(int(profile.get("quality_value", 20)))]
                )

            preset = str(profile.get("preset", ""))
            if preset and video_codec in {"libx264", "libx265"}:
                arguments.extend(["-preset", preset])

            max_width = int(profile.get("max_width", 0))
            max_height = int(profile.get("max_height", 0))
            if max_width > 0 and max_height > 0:
                scale_filter = (
                    f"scale=w='min(iw,{max_width})':h='min(ih,{max_height})':"
                    "force_original_aspect_ratio=decrease:force_divisible_by=2"
                )
                video_filters.append(scale_filter)

            if self.current_burn_subtitle_path:
                placement = str(
                    self.subtitle_placement_combo.currentData() or "bottom"
                )
                alignment = {"bottom": 2, "center": 5, "top": 8}.get(
                    placement,
                    2,
                )
                margin = 28 if placement in {"bottom", "top"} else 0
                font_name = re.sub(
                    r"[,']+",
                    " ",
                    self.subtitle_font_family,
                ).strip() or "Arial"
                force_style = (
                    f"FontName={font_name},"
                    f"FontSize={self.subtitle_size_spin.value()},"
                    f"PrimaryColour={ass_color(self.subtitle_text_color)},"
                    f"OutlineColour={ass_color(self.subtitle_outline_color)},"
                    "BorderStyle=1,Outline=2,Shadow=0,"
                    f"Alignment={alignment},MarginV={margin}"
                )
                subtitle_filter = (
                    "subtitles="
                    f"filename='{escape_subtitles_filter_path(self.current_burn_subtitle_path)}':"
                    "charenc=UTF-8:"
                    f"force_style='{force_style}'"
                )
                video_filters.append(subtitle_filter)

            if video_filters:
                arguments.extend(["-vf", ",".join(video_filters)])

            pixel_format = str(profile.get("pixel_format", ""))
            if pixel_format:
                arguments.extend(["-pix_fmt", pixel_format])

            if audio_codec.lower() == "none":
                arguments.append("-an")
            else:
                arguments.extend(["-c:a", audio_codec])
                audio_channels = int(profile.get("audio_channels", 0))
                if audio_channels > 0:
                    arguments.extend(["-ac", str(audio_channels)])

            extra_args = profile.get("extra_output_args", [])
            if isinstance(extra_args, list):
                arguments.extend(str(value) for value in extra_args)

        arguments.append(str(output_path))
        return arguments

    def _read_process_stdout(self) -> None:
        data = bytes(self.process.readAllStandardOutput()).decode(
            "utf-8",
            errors="replace",
        )
        self.stdout_buffer += data
        lines = self.stdout_buffer.splitlines(keepends=True)
        if lines and not lines[-1].endswith(("\n", "\r")):
            self.stdout_buffer = lines.pop()
        else:
            self.stdout_buffer = ""
        for raw_line in lines:
            line = raw_line.strip()
            if line.startswith("out_time_us="):
                try:
                    microseconds = int(line.split("=", 1)[1])
                except ValueError:
                    continue
                self._update_processing_progress(microseconds / 1_000_000)

    def _read_process_stderr(self) -> None:
        data = bytes(self.process.readAllStandardError()).decode(
            "utf-8",
            errors="replace",
        )
        self.stderr_buffer += data
        if len(self.stderr_buffer) > 100_000:
            self.stderr_buffer = self.stderr_buffer[-100_000:]

    def _update_processing_progress(self, current_seconds: float) -> None:
        if not self.segments or self.total_processing_duration <= 0:
            return
        current_duration = self.segments[self.current_segment_index]["duration"]
        completed = self.completed_duration + min(current_seconds, current_duration)
        percent = int((completed / self.total_processing_duration) * 95)
        self.progress_bar.setValue(max(0, min(95, percent)))
        self._refresh_processing_visuals()

    def _process_finished(
        self,
        exit_code: int,
        _exit_status: QProcess.ExitStatus,
    ) -> None:
        self._read_process_stdout()
        self._read_process_stderr()
        self._remove_burn_subtitle()
        if not self.is_processing:
            return
        if self.cancel_requested:
            self._finish_cancelled()
            return
        if exit_code != 0:
            self._fail_job(self._friendly_ffmpeg_error())
            return
        if not self.current_partial_path or not self.current_partial_path.exists():
            self._fail_job("FFmpeg finished but did not create the expected output.")
            return

        self._set_processing_state(
            "running",
            f"Validating session {self.current_segment_index + 1}…",
            "Checking duration, codecs, resolution, pixel format, and audio.",
        )
        QApplication.processEvents()
        profile = self.current_profile()
        if not profile:
            self._fail_job("The output profile is unavailable during validation.")
            return
        segment = self.segments[self.current_segment_index]
        errors, output_info = self._validate_output(
            self.current_partial_path,
            segment,
            profile,
        )
        if errors:
            self._fail_job(
                "Output validation failed:\n• " + "\n• ".join(errors)
            )
            return

        assert self.current_final_path is not None
        try:
            os.replace(
                self.current_partial_path,
                self.current_final_path,
            )
        except OSError as exc:
            self._fail_job(
                f"Could not finalize the output file: {exc}"
            )
            return

        subtitle_file_name: str | None = None
        subtitle_cue_count = self.current_subtitle_cue_count

        if (
            self.subtitle_cues
            and not self.burn_subtitles_checkbox.isChecked()
        ):
            subtitle_output_path = (
                self.current_final_path.with_suffix(".srt")
            )

            try:
                subtitle_cue_count = write_segment_subtitles(
                    subtitle_output_path,
                    self.subtitle_cues,
                    segment["start"],
                    segment["end"],
                    self._subtitle_offset_seconds(),
                )
            except OSError as exc:
                self._fail_job(
                    f"Could not write the segment subtitle: {exc}"
                )
                return

            subtitle_file_name = subtitle_output_path.name

        self.manifest["segments"].append(
            {
                "number": self.current_segment_index + 1,
                "source_start_seconds": segment["start"],
                "source_end_seconds": segment["end"],
                "planned_duration_seconds": segment["duration"],
                "file_name": self.current_final_path.name,
                "subtitle_file_name": subtitle_file_name,
                "subtitle_cue_count": subtitle_cue_count,
                "subtitles_burned_in": (
                    bool(self.subtitle_cues)
                    and self.burn_subtitles_checkbox.isChecked()
                ),
                "validation": {
                    "status": "passed",
                    "duration_seconds": output_info["duration"],
                    "format": output_info["format_name"],
                    "video_codec": output_info["video_codec"],
                    "audio_codec": output_info["audio_codec"],
                    "resolution": [
                        output_info["width"],
                        output_info["height"],
                    ],
                },
            }
        )
        assert self.current_job_directory is not None
        self._persist_manifest()
        self._append_log(
            f"Validated: {self.current_final_path.name} "
            f"({format_time(output_info['duration'])})"
        )
        self.completed_duration += segment["duration"]
        self.current_segment_index += 1
        QTimer.singleShot(0, self._start_next_segment)

    def _validate_output(
        self,
        path: Path,
        segment: dict[str, float],
        profile: dict[str, Any],
    ) -> tuple[list[str], dict[str, Any]]:
        assert self.ffprobe_path is not None
        errors: list[str] = []
        try:
            info = probe_media(path, self.ffprobe_path)
        except RuntimeError as exc:
            return [f"FFprobe could not read the result: {exc}"], {}

        if path.stat().st_size <= 0:
            errors.append("The output file is empty.")

        tolerance = 10.0 if self.fast_mode_radio.isChecked() else 1.5
        duration_difference = abs(info["duration"] - segment["duration"])
        if duration_difference > tolerance:
            errors.append(
                "Duration differs from the plan by "
                f"{duration_difference:.2f} seconds."
            )

        expected_video = target_codec_name(str(profile.get("video_codec", "")))
        expected_audio = target_codec_name(str(profile.get("audio_codec", "")))
        if expected_video and info["video_codec"] != expected_video:
            errors.append(
                f"Video codec is {info['video_codec']}, expected {expected_video}."
            )
        if (
            expected_audio
            and expected_audio != "none"
            and self.input_info
            and self.input_info.get("audio_codec")
            and info["audio_codec"] != expected_audio
        ):
            errors.append(
                f"Audio codec is {info['audio_codec'] or 'missing'}, "
                f"expected {expected_audio}."
            )
        if expected_audio == "none" and info["audio_codec"]:
            errors.append("The profile requires no audio, but an audio stream is present.")

        expected_pixel_format = str(profile.get("pixel_format") or "")
        if (
            expected_pixel_format
            and info.get("pixel_format")
            and info["pixel_format"] != expected_pixel_format
        ):
            errors.append(
                f"Pixel format is {info['pixel_format']}, "
                f"expected {expected_pixel_format}."
            )

        expected_channels = int(profile.get("audio_channels", 0))
        if (
            expected_channels
            and info.get("audio_codec")
            and int(info.get("audio_channels", 0)) != expected_channels
        ):
            errors.append(
                f"Audio has {info.get('audio_channels')} channels, "
                f"expected {expected_channels}."
            )

        max_width = int(profile.get("max_width", 0))
        max_height = int(profile.get("max_height", 0))
        if max_width and info["width"] > max_width:
            errors.append(f"Width exceeds the profile maximum of {max_width}.")
        if max_height and info["height"] > max_height:
            errors.append(f"Height exceeds the profile maximum of {max_height}.")

        return errors, info

    def _friendly_ffmpeg_error(self) -> str:
        text = self.stderr_buffer.strip()
        lowered = text.lower()
        if "no space left on device" in lowered:
            return "The output drive is full."
        if "permission denied" in lowered:
            return "Permission was denied while reading or writing a file."
        if "unknown encoder" in lowered:
            return (
                "The selected FFmpeg encoder is unavailable. "
                "Edit the output profile or use another FFmpeg build."
            )
        if "invalid argument" in lowered:
            return (
                "FFmpeg rejected the selected format or codec combination. "
                "Try a built-in profile or Exact mode."
            )
        lines = [line for line in text.splitlines() if line.strip()]
        detail = "\n".join(lines[-10:])
        return detail or "FFmpeg stopped with an unknown error."

    def _cancel_processing(self) -> None:
        if not self.is_processing or self.cancel_requested:
            return
        answer = QMessageBox.question(
            self,
            APP_NAME,
            "Cancel this job? Completed session files will be kept.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.cancel_requested = True
        self.cancel_button.setEnabled(False)
        self._set_processing_state(
            "warning",
            "Cancelling…",
            "FFmpeg is being stopped. Completed session files will be kept.",
        )
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            QTimer.singleShot(3000, self._kill_process_if_running)
        else:
            self._finish_cancelled()

    def _kill_process_if_running(self) -> None:
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()

    def _remove_partial(self) -> None:
        if self.current_partial_path and self.current_partial_path.exists():
            try:
                self.current_partial_path.unlink()
            except OSError:
                pass
        self._remove_burn_subtitle()

    def _remove_burn_subtitle(self) -> None:
        if (
            self.current_burn_subtitle_path
            and self.current_burn_subtitle_path.exists()
        ):
            try:
                self.current_burn_subtitle_path.unlink()
            except OSError:
                pass
        self.current_burn_subtitle_path = None

    def _finish_cancelled(self) -> None:
        if not self.is_processing:
            return
        self._remove_partial()
        self.manifest["status"] = "cancelled"
        self.manifest["finished_at"] = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
        if self.current_job_directory:
            self._persist_manifest()
        self._append_log("Job cancelled. Completed session files were kept.")
        self.processing_ui_timer.stop()
        self._set_processing_state(
            "warning",
            "Processing cancelled",
            "Completed session files were kept in the job folder.",
        )
        self.is_processing = False
        self.cancel_requested = False
        self._update_controls()

    def _fail_job(self, message: str) -> None:
        if not self.is_processing:
            return
        self._remove_partial()
        self.manifest["status"] = "failed"
        self.manifest["error"] = message
        self.manifest["finished_at"] = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
        if self.current_job_directory:
            self._persist_manifest()
        self._append_log(f"ERROR: {message}")
        self.processing_ui_timer.stop()
        self._set_processing_state(
            "error",
            "Processing failed",
            message.splitlines()[0] if message else "FFmpeg stopped unexpectedly.",
        )
        self.is_processing = False
        self.cancel_requested = False
        self._update_controls()
        QMessageBox.critical(self, APP_NAME, message)

    def _finish_successfully(self) -> None:
        self.manifest["status"] = "completed"
        self.manifest["finished_at"] = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
        if self.current_job_directory:
            self._persist_manifest()
        self.processing_ui_timer.stop()
        self.progress_bar.setValue(100)
        self._set_processing_state(
            "success",
            f"Completed {len(self.segments)} session(s)",
            "Every output passed FFprobe validation.",
        )
        self._append_log("All session files passed FFprobe validation.")
        self.is_processing = False
        self._update_controls()
        QMessageBox.information(
            self,
            APP_NAME,
            f"Video preparation completed successfully.\n\n"
            f"Output folder:\n{self.current_job_directory}",
        )

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_edit.appendPlainText(f"[{timestamp}] {message}")

    def _persist_manifest(self) -> bool:
        if not self.current_job_directory:
            return False
        try:
            atomic_write_json(
                self.current_job_directory / "job_manifest.json",
                self.manifest,
            )
            return True
        except OSError as exc:
            self._append_log(f"WARNING: Could not write job manifest: {exc}")
            return False

    def _open_output_folder(self) -> None:
        if self.last_output_directory and self.last_output_directory.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.last_output_directory)))

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self.is_processing:
            event.accept()
            return
        answer = QMessageBox.question(
            self,
            APP_NAME,
            "A video is still being processed. Cancel it and close the application?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            event.ignore()
            return
        self.cancel_requested = True
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
            self.process.waitForFinished(3000)
        self._remove_partial()
        if self.current_job_directory:
            self.manifest["status"] = "cancelled"
            self.manifest["finished_at"] = datetime.now().astimezone().isoformat(
                timespec="seconds"
            )
            self._persist_manifest()
        event.accept()


def first_run_setup(settings: QSettings) -> bool:
    completed_major = str(settings.value(SETUP_VERSION_KEY, "")).strip()
    current_major = APP_VERSION.split(".", 1)[0]
    if completed_major == current_major:
        return True

    dialog = FirstRunDialog(settings)
    return dialog.exec() == QDialog.DialogCode.Accepted


def main() -> int:
    QCoreApplication.setOrganizationName(ORGANIZATION_NAME)
    QCoreApplication.setApplicationName(APP_NAME)
    QCoreApplication.setApplicationVersion(APP_VERSION)
    app = QApplication(sys.argv)
    app.setApplicationDisplayName(APP_NAME)
    app.setStyle("Fusion")
    if os.name == "nt":
        app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(application_stylesheet())
    icon = brand_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)

    settings = QSettings()
    if not first_run_setup(settings):
        return 1

    window = MainWindow(settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

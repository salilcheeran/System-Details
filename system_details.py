"""Small standalone laptop configuration and performance dashboard."""

from __future__ import annotations

import ctypes
import math
import os
import platform
import shutil
import tkinter as tk
from datetime import datetime


APP_BG = "#101820"
PANEL_BG = "#182630"
TEXT = "#eef6f5"
MUTED = "#9db0b0"
ACCENT = "#70d6c0"
WARNING = "#f5c36a"


class MemoryStatus(ctypes.Structure):
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


def bytes_to_gb(value: int) -> str:
    return f"{value / (1024 ** 3):.1f} GB"


def memory_details() -> tuple[int, int, int]:
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if os.name == "nt" and ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return status.dwMemoryLoad, status.ullTotalPhys, status.ullAvailPhys
    return 0, 0, 0


def cpu_times() -> tuple[int, int, int, int]:
    class FileTime(ctypes.Structure):
        _fields_ = [("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]

    idle = FileTime()
    kernel = FileTime()
    user = FileTime()
    if os.name == "nt" and ctypes.windll.kernel32.GetSystemTimes(
        ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)
    ):
        def as_int(item: FileTime) -> int:
            return (item.high << 32) | item.low

        return as_int(idle), as_int(kernel), as_int(user), 0
    return 0, 0, 0, 0


def cpu_percent(previous: tuple[int, int, int, int] | None) -> tuple[float, tuple[int, int, int, int]]:
    current = cpu_times()
    if not previous or current[1] == 0:
        return 0.0, current
    idle_delta = current[0] - previous[0]
    total_delta = (current[1] + current[2]) - (previous[1] + previous[2])
    return (max(0.0, min(100.0, (1 - idle_delta / total_delta) * 100)) if total_delta else 0.0), current


def drive_details() -> tuple[str, float]:
    usage = shutil.disk_usage(os.path.abspath(os.sep))
    used = usage.used / usage.total * 100 if usage.total else 0
    return bytes_to_gb(usage.total), used


class SystemDetailsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("System Details")
        self.root.geometry("768x480")
        self.root.minsize(680, 400)
        self.root.configure(bg=APP_BG)
        self.root.resizable(False, False)
        self.previous_cpu: tuple[int, int, int, int] | None = None
        self.view_title = tk.StringVar(value="Overview")
        self.status_text = tk.StringVar(value="Ready")
        self._build_ui()
        self._refresh_performance()

    def _build_ui(self) -> None:
        header = tk.Frame(self.root, bg=APP_BG)
        header.pack(fill="x", padx=22, pady=(18, 8))
        self._draw_gear(header)
        title_box = tk.Frame(header, bg=APP_BG)
        title_box.pack(side="left", padx=(12, 0))
        tk.Label(title_box, text="SYSTEM DETAILS", font=("Segoe UI", 16, "bold"), fg=TEXT, bg=APP_BG).pack(anchor="w")
        tk.Label(title_box, textvariable=self.view_title, font=("Segoe UI", 9), fg=ACCENT, bg=APP_BG).pack(anchor="w")

        developer_label = tk.Label(
            header,
            text="Developed by: Salil Cheeran",
            font=("Segoe UI", 9, "bold"),
            fg=ACCENT,
            bg=APP_BG,
        )
        developer_label.pack(side="right", anchor="n", pady=(6, 0))

        content_shell = tk.Frame(self.root, bg=APP_BG)
        content_shell.pack(fill="both", expand=True, padx=22, pady=(0, 14))
        self.content_canvas = tk.Canvas(content_shell, bg=PANEL_BG, highlightthickness=1, highlightbackground="#2a3d45")
        self.content_canvas.pack(side="left", fill="both", expand=True)
        self.content_scrollbar = tk.Scrollbar(content_shell, orient="vertical", command=self.content_canvas.yview)
        self.content_scrollbar.pack(side="right", fill="y")
        self.content_canvas.configure(yscrollcommand=self.content_scrollbar.set)
        self.content = tk.Frame(self.content_canvas, bg=PANEL_BG)
        self.content_window = self.content_canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", self._update_scroll_region)
        self.content_canvas.bind("<Configure>", self._resize_content)
        self.content_canvas.bind_all("<MouseWheel>", self._scroll_content)
        self._show_overview()

        footer = tk.Frame(self.root, bg=APP_BG)
        footer.pack(fill="x", padx=22, pady=(0, 18))
        self._button(footer, "Configuration", self._show_configuration).pack(side="left", expand=True, fill="x", padx=(0, 5))
        self._button(footer, "Performance", self._show_performance).pack(side="left", expand=True, fill="x", padx=5)
        self._button(footer, "Exit", self.root.destroy, accent=False).pack(side="left", expand=True, fill="x", padx=(5, 0))

    def _draw_gear(self, parent: tk.Widget) -> None:
        canvas = tk.Canvas(parent, width=44, height=44, bg=APP_BG, highlightthickness=0)
        canvas.pack(side="left")
        for angle in range(0, 360, 45):
            radians = math.radians(angle)
            canvas.create_line(22, 22, 22 + math.cos(radians) * 17, 22 + math.sin(radians) * 17, fill=ACCENT, width=7)
        canvas.create_oval(10, 10, 34, 34, fill=ACCENT, outline=ACCENT)
        canvas.create_oval(17, 17, 27, 27, fill=APP_BG, outline=APP_BG)

    def _button(self, parent: tk.Widget, label: str, command: object, accent: bool = True) -> tk.Button:
        return tk.Button(parent, text=label, command=command, font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                         padx=6, pady=8, bg=ACCENT if accent else "#263840", fg=APP_BG if accent else TEXT,
                         activebackground="#9ae8d7" if accent else "#344a53", activeforeground=APP_BG,
                         cursor="hand2")

    def _clear_content(self, title: str) -> None:
        for child in self.content.winfo_children():
            child.destroy()
        self.view_title.set(title)
        self.content_canvas.yview_moveto(0)

    def _update_scroll_region(self, _event: tk.Event[tk.Misc]) -> None:
        self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))

    def _resize_content(self, event: tk.Event[tk.Misc]) -> None:
        self.content_canvas.itemconfigure(self.content_window, width=event.width)

    def _scroll_content(self, event: tk.Event[tk.Misc]) -> None:
        if self.content_canvas.winfo_exists():
            self.content_canvas.yview_scroll(-int(event.delta / 120), "units")

    def _show_overview(self) -> None:
        self._clear_content("Overview")
        tk.Label(self.content, text="A quiet look at this machine.", font=("Segoe UI", 15, "bold"), fg=TEXT, bg=PANEL_BG).pack(anchor="w", padx=20, pady=(22, 4))
        tk.Label(self.content, text="Use the controls below to inspect configuration or watch live performance.", font=("Segoe UI", 9), fg=MUTED, bg=PANEL_BG).pack(anchor="w", padx=20)
        tk.Label(self.content, textvariable=self.status_text, font=("Segoe UI", 9), fg=WARNING, bg=PANEL_BG).pack(anchor="w", padx=20, pady=(28, 0))

    def _line(self, label: str, value: str) -> None:
        row = tk.Frame(self.content, bg=PANEL_BG)
        row.pack(fill="x", padx=20, pady=3)
        tk.Label(row, text=label, width=15, anchor="w", font=("Segoe UI", 9), fg=MUTED, bg=PANEL_BG).pack(side="left")
        tk.Label(row, text=value, anchor="w", font=("Segoe UI", 9, "bold"), fg=TEXT, bg=PANEL_BG).pack(side="left", fill="x", expand=True)

    def _show_configuration(self) -> None:
        self._clear_content("Configuration")
        self._line("Operating system", f"{platform.system()} {platform.release()}")
        self._line("Computer", platform.node() or "Unavailable")
        self._line("Processor", platform.processor() or platform.machine())
        _, total, available = memory_details()
        self._line("Memory", f"{bytes_to_gb(total)} total, {bytes_to_gb(available)} available" if total else "Unavailable")
        total_disk, used_disk = drive_details()
        self._line("System drive", f"{total_disk}, {used_disk:.0f}% used")
        self._line("Python", platform.python_version())
        self._line("Checked", datetime.now().strftime("%H:%M:%S"))

    def _show_performance(self) -> None:
        self._clear_content("Live Performance")
        self._render_performance()

    def _render_performance(self) -> None:
        load, _, _ = memory_details()
        cpu, self.previous_cpu = cpu_percent(self.previous_cpu)
        total_disk, used_disk = drive_details()
        self._line("CPU", f"{cpu:5.1f}% active")
        self._line("Memory", f"{load}% in use")
        self._line("Storage", f"{used_disk:.0f}% used of {total_disk}")
        self._line("Updated", datetime.now().strftime("%H:%M:%S"))
        self.status_text.set("Live readings refresh every second")

    def _refresh_performance(self) -> None:
        if self.view_title.get() == "Live Performance":
            self._show_performance()
        self.root.after(1000, self._refresh_performance)


def main() -> None:
    root = tk.Tk()
    SystemDetailsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
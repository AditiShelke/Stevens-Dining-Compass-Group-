"""
Stevens Dining — Heatmap Generator API
Accepts an Excel workbook (multi-sheet), generates a heatmap PNG per sheet,
returns a ZIP file containing all PNGs.

POST /generate
  Body: multipart/form-data  with field "file" = .xlsx
  Returns: application/zip

GET /health
  Returns: {"status": "ok"}
"""

from flask import Flask, request, jsonify, send_file
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — required on server
import matplotlib.pyplot as plt
import matplotlib as mpl
import io
import zipfile
import traceback

app = Flask(__name__)

# ── Per-venue config ────────────────────────────────────────────────────────
# Maps lowercase sheet name keywords → time order + title suffix
VENUE_CONFIG = {
    "pierce": {
        "time_order": [
            "7:00AM","8:00AM","9:00AM","10:00AM","11:00AM",
            "12:00PM","1:00PM","2:00PM","3:00PM","4:00PM",
            "5:00PM","6:00PM","7:00PM","8:00PM","9:00PM"
        ],
        "has_notes": False,   # Pierce only has 4 columns
        "skip_rows": 1,
    },
    "zaro": {
        "time_order": [
            "8:00AM","9:00AM","10:00AM","11:00AM",
            "12:00PM","1:00PM","2:00PM","3:00PM","4:00PM"
        ],
        "has_notes": True,
        "skip_rows": 0,
    },
    "create": {
        "time_order": [
            "8:00AM","9:00AM","10:00AM","11:00AM",
            "12:00PM","1:00PM","2:00PM","3:00PM","4:00PM",
            "5:00PM","6:00PM","7:00PM"
        ],
        "has_notes": True,
        "skip_rows": 0,
    },
    "cannon": {
        "time_order": [
            "8:00AM","9:00AM","10:00AM","11:00AM",
            "12:00PM","1:00PM","2:00PM","3:00PM","4:00PM",
            "5:00PM","6:00PM","7:00PM","8:00PM"
        ],
        "has_notes": True,
        "skip_rows": 0,
    },
    "yella": {
        "time_order": [
            "10:00AM","11:00AM","12:00PM","1:00PM","2:00PM",
            "3:00PM","4:00PM","5:00PM","6:00PM","7:00PM","8:00PM"
        ],
        "has_notes": True,
        "skip_rows": 0,
    },
    "taco": {
        "time_order": [
            "11:00AM","12:00PM","1:00PM","2:00PM","3:00PM",
            "4:00PM","5:00PM","6:00PM","7:00PM","8:00PM"
        ],
        "has_notes": True,
        "skip_rows": 0,
    },
    "pom": {
        "time_order": [
            "8:00AM","9:00AM","10:00AM","11:00AM",
            "12:00PM","1:00PM","2:00PM","3:00PM","4:00PM",
            "5:00PM","6:00PM","7:00PM"
        ],
        "has_notes": True,
        "skip_rows": 0,
    },
    "honey": {
        "time_order": [
            "8:00AM","9:00AM","10:00AM","11:00AM",
            "12:00PM","1:00PM","2:00PM","3:00PM","4:00PM",
            "5:00PM","6:00PM","7:00PM"
        ],
        "has_notes": True,
        "skip_rows": 0,
    },
    "piccola": {
        "time_order": [
            "11:00AM","12:00PM","1:00PM","2:00PM","3:00PM",
            "4:00PM","5:00PM","6:00PM","7:00PM","8:00PM"
        ],
        "has_notes": True,
        "skip_rows": 0,
    },
    "late": {
        "time_order": [
            "8:00PM","8:15PM","8:30PM","8:45PM",
            "9:00PM","9:15PM","9:30PM"
        ],
        "has_notes": True,
        "skip_rows": 0,
    },
}

DEFAULT_CONFIG = {
    "time_order": [
        "7:00AM","8:00AM","9:00AM","10:00AM","11:00AM",
        "12:00PM","1:00PM","2:00PM","3:00PM","4:00PM",
        "5:00PM","6:00PM","7:00PM","8:00PM","9:00PM"
    ],
    "has_notes": True,
    "skip_rows": 0,
}


def get_config(sheet_name: str) -> dict:
    name = sheet_name.lower()
    for key, cfg in VENUE_CONFIG.items():
        if key in name:
            return cfg
    return DEFAULT_CONFIG


def load_sheet(xl: pd.ExcelFile, sheet_name: str, cfg: dict) -> pd.DataFrame:
    """Load one sheet and return a clean DataFrame."""
    if cfg["skip_rows"] > 0:
        df = pd.read_excel(xl, sheet_name=sheet_name, skiprows=cfg["skip_rows"], header=None)
        df = df.iloc[:, :4]
        df.columns = ["Weekday", "Date", "Time", "Transactions"]
    else:
        df = pd.read_excel(xl, sheet_name=sheet_name)
        if cfg["has_notes"] and df.shape[1] >= 5:
            df = df.iloc[:, :5]
            df.columns = ["Weekday", "Date", "Time", "Transactions", "Notes"]
        else:
            df = df.iloc[:, :4]
            df.columns = ["Weekday", "Date", "Time", "Transactions"]

    df["Date_dt"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Transactions"] = pd.to_numeric(df["Transactions"], errors="coerce").fillna(0)
    df["Time"] = df["Time"].astype(str).str.strip()

    # Critical: use Weekday column from data, NOT strftime (off-by-one bug)
    df["DayLabel"] = df["Weekday"].astype(str).str[:3] + " " + df["Date_dt"].dt.strftime("%m/%d")
    df = df.dropna(subset=["Date_dt"])
    return df


def generate_heatmap(df: pd.DataFrame, title: str, time_order: list) -> bytes:
    """Generate heatmap PNG from df, return bytes."""
    # Filter open days only
    daily_totals = df.groupby("DayLabel")["Transactions"].sum()
    open_days = daily_totals[daily_totals > 0].index.tolist()
    df = df[df["DayLabel"].isin(open_days)]

    if df.empty:
        raise ValueError("No open days found in this sheet")

    pivot = df.pivot_table(
        index="Time",
        columns="DayLabel",
        values="Transactions",
        aggfunc="sum",
        fill_value=0
    )

    available_times = [t for t in time_order if t in pivot.index]
    if not available_times:
        available_times = pivot.index.tolist()
    pivot = pivot.reindex(index=available_times)

    # Sort columns by date
    def sort_key(label):
        try:
            parts = label.split()
            return pd.to_datetime(parts[1] + "/2000", format="%m/%d/%Y")
        except Exception:
            return pd.Timestamp("2000-01-01")

    day_order = sorted(pivot.columns, key=sort_key)
    pivot = pivot[day_order]

    cmap = mpl.colormaps.get_cmap("YlOrRd").copy()
    cmap.set_bad("lightgray")

    annot = pivot.map(lambda x: f"{int(x)}" if x > 0 else "")

    fig_width = max(14, len(pivot.columns) * 0.85)
    fig_height = max(8, len(pivot.index) * 0.55)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    sns.heatmap(
        pivot,
        ax=ax,
        cmap=cmap,
        linewidths=0.5,
        linecolor="white",
        annot=annot,
        fmt="",
        cbar_kws={"label": "Transactions", "shrink": 0.8},
        square=False,
        robust=True,
        annot_kws={"size": 8}
    )

    ax.set_title(title, fontsize=15, weight="bold", pad=18)
    ax.set_xlabel("Day / Date", fontsize=11, weight="bold")
    ax.set_ylabel("Time of Day", fontsize=11, weight="bold")

    if len(pivot.columns) > 15:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
    else:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha="center", fontsize=10)

    ax.set_yticklabels(ax.get_yticklabels(), fontsize=10)

    cbar = ax.collections[0].colorbar
    cbar.set_label("Transactions", fontsize=11, weight="bold")

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Stevens Dining Heatmap API"})


@app.route("/generate", methods=["POST"])
def generate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Use field name 'file'."}), 400

    uploaded = request.files["file"]
    if not uploaded.filename.endswith((".xlsx", ".xls")):
        return jsonify({"error": "File must be .xlsx or .xls"}), 400

    try:
        file_bytes = io.BytesIO(uploaded.read())
        xl = pd.ExcelFile(file_bytes)
        sheet_names = xl.sheet_names

        zip_buf = io.BytesIO()
        results = []

        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for sheet in sheet_names:
                try:
                    cfg = get_config(sheet)
                    df = load_sheet(xl, sheet, cfg)

                    # Derive month/year from data for title
                    month_label = ""
                    if not df["Date_dt"].dropna().empty:
                        first_date = df["Date_dt"].dropna().iloc[0]
                        month_label = first_date.strftime("%B %Y")

                    title = f"{sheet.upper()} — {month_label}\nTransaction Heatmap (Open Days Only)"
                    png_bytes = generate_heatmap(df, title, cfg["time_order"])

                    safe_name = sheet.replace(" ", "_").replace("/", "-")
                    filename = f"{safe_name}_heatmap.png"
                    zf.writestr(filename, png_bytes)
                    results.append({"sheet": sheet, "status": "ok", "file": filename})

                except Exception as e:
                    results.append({"sheet": sheet, "status": "error", "error": str(e)})

        zip_buf.seek(0)

        response = send_file(
            zip_buf,
            mimetype="application/zip",
            as_attachment=True,
            download_name="dining_heatmaps.zip"
        )
        # Include summary in headers so n8n can log it
        response.headers["X-Results"] = str(results)
        return response

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

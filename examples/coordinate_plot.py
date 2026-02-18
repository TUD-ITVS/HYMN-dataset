from pathlib import Path

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import pandas as pd

TECHNOLOGIES = ["reference"]  # e.g. ["uwb", "ble", ...] or "reference" for reference location

CRS = {
    "LOCAL": ["X_LOCAL", "Y_LOCAL", "Z_LOCAL"],
    "ECEF": ["X_ECEF", "Y_ECEF", "Z_ECEF"],
    "UTM": ["E", "N", "U"]
}

# Map technology -> a substring used in point column names.
TECH_COLUMN_HINTS = {
    "reference": ["CENTER"],
    "uwb": ["UWB"],
    "ble": ["BLE"],
    "nr5g": ["NR5G"],
    "wifi": ["WIFI"],
    "wlan": ["WLAN"],
    "gnss": ["GNSS"],
}

def _color_for(technology: str, default: str = "k") -> str:
    """Stable per-technology colors using Matplotlib's default prop cycle."""
    if not technology:
        return default
    tech = technology.lower()
    if tech in (TECHNOLOGIES or []):
        return f"C{(TECHNOLOGIES or []).index(tech)}"
    return default


def _anchor_technology_from_point_id(point_id: str) -> str | None:
    if not isinstance(point_id, str) or not point_id:
        return None
    # Common pattern: BLE_01, UWB_03, NR5G_02, WLAN_03 ...
    prefix = point_id.split("_")[0].strip().lower()
    return prefix or None


def _shared_anchor_id_from_point_id(point_id: str) -> str | None:
    """Return a shared anchor id like '03' for BLE_03 / UWB_03.

    If no numeric suffix can be parsed, returns None.
    """
    if not isinstance(point_id, str) or not point_id:
        return None
    parts = point_id.split("_")
    if len(parts) < 2:
        return None
    suffix = parts[-1].strip()
    # Most files use 2-digit suffixes (01..), but accept any digits.
    return suffix if suffix.isdigit() else None


BASE = Path(__file__).resolve().parents[1]
ANCHOR_PATH = BASE / "data" / "reference" / "pickle" / "anchor_coordinates.pkl"
POINT_PATH = BASE / "data" / "reference" / "pickle" / "point_coordinates.pkl"


def _filter_technology(df: pd.DataFrame) -> pd.DataFrame:
    if TECHNOLOGIES is None or "technology" not in df.columns:
        return df
    return df[df["technology"].isin(TECHNOLOGIES)].copy()


def _filter_crs(df: pd.DataFrame, in_crs: str) -> pd.DataFrame:
    cols = CRS.get(in_crs)
    # return all columns which have CRS[in_crs] in header, but also get something like X_LOCAL_CENTER
    filtered_cols = [col for col in df.columns if any(c in col for c in cols)]
    # keep technology for later filtering (if present)
    if "technology" in df.columns:
        filtered_cols = ["technology"] + filtered_cols
    # keep point_id for labeling
    if "point_id" in df.columns and "point_id" not in filtered_cols:
        filtered_cols = ["point_id"] + filtered_cols
    return df[filtered_cols].copy()


def _get_xy(df: pd.DataFrame):
    candidates = [
        ("X_LOCAL", "Y_LOCAL"),
    ]
    for x_col, y_col in candidates:
        # if column names have candidates in header, but use anything like X_LOCAL_CENTER, Y_LOCAL_CENTER
        x_candidates = [col for col in df.columns if x_col in col]
        y_candidates = [col for col in df.columns if y_col in col]
        if x_candidates and y_candidates:
            # pick the first match for each to return 1D series
            return df[x_candidates[0]], df[y_candidates[0]], (x_candidates[0], y_candidates[0])


def _get_xy_for_technology(points_df: pd.DataFrame, technology: str):
    """Extract X/Y series from the wide points dataframe for a specific technology.

    Expected patterns include:
      - X_LOCAL_<TECH>, Y_LOCAL_<TECH>
      - X_LOCAL_<TECH><suffix> (e.g., UWB1/UWB2)
    """
    hints = TECH_COLUMN_HINTS.get(technology.lower(), [technology.upper()])

    # Look for X/Y columns that contain both axis prefix and any hint.
    x_cols = [c for c in points_df.columns if "X_LOCAL" in c and any(h in c.upper() for h in hints)]
    y_cols = [c for c in points_df.columns if "Y_LOCAL" in c and any(h in c.upper() for h in hints)]

    if not x_cols or not y_cols:
        return None

    # Keep order stable and pair with common suffix where possible
    x_cols = sorted(x_cols)
    y_cols = sorted(y_cols)

    # If there are multiple matches (e.g., UWB1/UWB2), take the first pair.
    return points_df[x_cols[0]], points_df[y_cols[0]], (x_cols[0], y_cols[0])


def _annotate_points_once(ax: plt.Axes, points_df: pd.DataFrame, technology: str):
    """Annotate each point_id exactly once based on the requested technology columns."""
    if "point_id" not in points_df.columns:
        return

    xy = _get_xy_for_technology(points_df, technology)
    if xy is None:
        return

    x_s, y_s, _ = xy

    # points_df is wide with one row per point_id; annotate each row once
    for pid, x, y in zip(points_df["point_id"].astype(str), x_s, y_s):
        if pd.isna(x) or pd.isna(y):
            continue
        ax.annotate(
            pid,
            (x, y),
            textcoords="offset points",
            xytext=(6, -10),
            ha="left",
            va="top",
            color="blue",
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.65),
        )


def main():
    anchors_raw = pd.read_pickle(ANCHOR_PATH)
    points_raw = pd.read_pickle(POINT_PATH)

    anchors_raw = _filter_crs(anchors_raw, "LOCAL")
    points_raw = _filter_crs(points_raw, "LOCAL")

    ax = plt.gca()
    # fontsize for all text in the plot
    plt.rcParams.update({"font.size": 12})
    ax.grid(True, linestyle="--", color="0.75")


    # Anchors: color by technology encoded in point_id (e.g., BLE_01 -> ble) and label them.
    ax_x, ax_y, ax_cols = _get_xy(anchors_raw)

    ax.scatter(0, 0, marker="d", s=100, label="Origin", color="red")
    # text for origin
    ax.text(0, 0, "Tachymeter", color="red")

    labeled_shared_ids: set[str] = set()

    if "point_id" in anchors_raw.columns:
        for _, row in anchors_raw.iterrows():
            pid = row.get("point_id")
            tech = _anchor_technology_from_point_id(pid)
            c = _color_for(tech, default="k")

            x = row[ax_cols[0]]
            y = row[ax_cols[1]]

            # plot each anchor to allow per-point color
            ax.scatter(x, y, marker="^", s=70, c=c,
                       label=f"Anchors ({tech})" if tech else "Anchors")

            # Label policy:
            # - If multiple technologies share same numeric suffix, label only once as 'anchor_XX'
            # - If suffix can't be parsed, or it's a single-tech anchor, label with full point_id
            shared_id = _shared_anchor_id_from_point_id(pid) if isinstance(pid, str) else None

            label_text = None
            if shared_id is None:
                label_text = str(pid)
            else:
                # Count how many anchors share this suffix
                same_suffix = anchors_raw["point_id"].astype(str).str.endswith(f"_{shared_id}").sum()
                if same_suffix > 1:
                    if shared_id not in labeled_shared_ids:
                        labeled_shared_ids.add(shared_id)
                        label_text = f"Multi-Anchor_{shared_id}"
                else:
                    label_text = str(pid)

            if label_text:
                # More consistent label placement: offset in screen coords + small white background
                ax.annotate(
                    label_text,
                    (x, y),
                    textcoords="offset points",
                    xytext=(8, 8),
                    ha="left",
                    va="bottom",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75),
                )
    else:
        ax.scatter(ax_x, ax_y, marker="^", s=70, label="Anchors", c="k")

    last_px_cols = None
    for idx, t in enumerate(TECHNOLOGIES or []):
        if "technology" in points_raw.columns:
            points = points_raw[points_raw["technology"].eq(t)]
            xy = _get_xy(points)
        else:
            xy = _get_xy_for_technology(points_raw, t)

        if xy is None:
            continue

        px_x, px_y, px_cols = xy
        last_px_cols = px_cols
        ax.scatter(px_x, px_y, marker="o", s=50, label=f"Points ({t})", c=_color_for(t, default=f"C{idx}"))

        # annotate point names once per point
        _annotate_points_once(ax, points_raw, t)

    # De-duplicate legend entries
    handles, labels = ax.get_legend_handles_labels()

    # Show only one anchor symbol in the legend (keep plot as-is)
    anchor_handle = mlines.Line2D([], [], color="k", marker="^", linestyle="None", markersize=12, label="Anchors")

    seen = set()
    uniq_handles = []
    uniq_labels = []
    for h, l in zip(handles, labels):
        if l in seen:
            continue
        # Drop per-technology anchor legend labels like "Anchors (ble)"
        if isinstance(l, str) and l.lower().startswith("anchors ("):
            continue
        seen.add(l)
        uniq_handles.append(h)
        uniq_labels.append(l)

    # Insert the generic anchor entry if we actually plotted anchors
    if "point_id" in anchors_raw.columns and len(anchors_raw) > 0:
        # put it after Origin if Origin exists, otherwise at the front
        insert_at = 1 if "Origin" in uniq_labels else 0
        uniq_handles.insert(insert_at, anchor_handle)
        uniq_labels.insert(insert_at, "Anchors")

    # Axis labels: prefer anchor columns, fall back to last plotted points
    ax.set_xlabel("X_LOCAL [m]")
    ax.set_ylabel("Y_LOCAL [m]")

    ax.legend(uniq_handles, uniq_labels)
    ax.set_aspect("equal", adjustable="box")
    plt.tight_layout()
    plt.savefig("coordinate_plot.png", dpi=300)
    plt.show()


if __name__ == "__main__":

    main()

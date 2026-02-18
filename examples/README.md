# Examples

This folder contains small, self-contained scripts that show how to work with the processed HYMΝ dataset.

> Paths in these examples are written to be run from the **repository root**.

## `example_iterator.py`

Purpose:
- Shows how to **iterate** over the merged dataset using the `Dataset` helper class.
- Demonstrates how the merged file (`data/processed/<backend>/merged.*`) can be used to look up the matching rows for each technology (`wifi`, `uwb`, `ble`, `gnss`, `nr5g`).
- Includes an example evaluation function: **WiFi ranging error** against geometric ground truth.

### Example evaluation: WiFi ranging error
`example_calculate_wifi_ranging_error(measurement)`:
- loads reference geometry from:
  - `data/reference/pickle/point_coordinates.pkl` (WiFi sensor reference position per `point_id`)
  - `data/reference/pickle/anchor_coordinates.pkl` (anchor positions, uses `WIFI_01..WIFI_06`)
- computes the **true range** as Euclidean distance between the reference point and the anchor
- compares it to the **measured ranges** in the WiFi data
- returns a `DataFrame` with `measured_range`, `true_range`, and `error = measured - true`


## `coordinate_plot.py`

Purpose:
- Gives a **geometric overview of the scene** in **local coordinates**.
- Plots **anchor coordinates** and **measurement point coordinates** from the reference files.
- Useful as a quick sanity check for coordinate systems, anchor layout, and point naming.

Data sources:
- `data/reference/pickle/anchor_coordinates.pkl`
- `data/reference/pickle/point_coordinates.pkl`

Adaptations:
- You can control what gets plotted by editing the `TECHNOLOGIES` variable near the top of the script (e.g., `"uwb"`, `"wifi"`, `"ble"`, or `"reference"`).

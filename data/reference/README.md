# Reference Data

This directory contains reference information for anchors, measurement points, and timing. 

## Coordinate Reference Systems

| Name                                        | Axes / Units        | Description                                                                                                                                          |
|:--------------------------------------------|:--------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| **Local Cartesian Coordinates**             | $X, Y, Z$ [m]       | Local tangent plane coordinates centered at the tachymeter station. Requires an affine transformation for geodetic alignment.                        |
| **UTM33N / ETRS89** EPSG:25833              | $E, N$ [m], $h$ [m] | Projected coordinates ($E$=Easting, $N$=Northing) and ellipsoidal height ($h$). Standard for regional mapping and GIS integration in Central Europe. |
| **ECEF / WGS84** EPSG:4978                  | $X, Y, Z$ [m]       | Earth-Centered, Earth-Fixed 3D Cartesian coordinates. The primary frame used for GNSS orbital calculations and satellite positioning.                |

### Local to Global Transformation (UTM33N)
The transformation from the **Local Cartesian** system to **UTM33N (EPSG:25833)** is a 2D rigid body transformation (rotation and translation) applied to the horizontal components:

$$
\begin{bmatrix} E_{utm} \\ N_{utm} \end{bmatrix} = \mathbf{R} \begin{bmatrix} x_{local} \\ y_{local} \end{bmatrix} + \mathbf{t}
$$

**Parameters:**

$$\mathbf{R} = \begin{bmatrix} -0.84645628 & 0.53245822 \\ -0.53245822 & -0.84645628 \end{bmatrix}$$

$$\mathbf{t} = \begin{bmatrix} 361620.04024452 \\ 5715157.13887458 \end{bmatrix}$$

*Note: All units are in meters. The up component of the transformation matrix is zero as the local coordinate system is aligned with the horizontal plane.*

## Anchor Coordinates (`anchor_coordinates.*`)

This file contains the coordinates of the anchors used for BLE, WiFi, and UWB technologies.

**Anchor Coordinate Rationale:**
The anchors are installed at fixed positions within the environment. In several cases, multiple anchors (e.g., a BLE beacon, a WiFi access point, and a UWB anchor) are mounted at the same horizontal position but at different heights. This is reflected in the coordinates where the Easting (E) and Northing (N) values are identical, but the Up (U) value (vertical component) is shifted.

## Point Coordinates (`point_coordinates.*`)

This file provides the ground-truth coordinates for each measurement point (`point_id`).

**Measurement Plate Setup:**
During the data collection, all sensors were mounted on a specialized measurement plate. Because the sensors (GNSS antenna, NR5G UE, UWB/BLE tags, WiFi smartphone) are physically spaced out on this plate, each sensor has a slightly different ground-truth position for the same `point_id`.

The `point_coordinates.csv` file includes:
- **X_LOCAL_[TECH], ...**: The reference coordinates for each specific sensor/technology on the plate.
- **X_LOCAL_CENTER, Y_LOCAL_CENTER, Z_LOCAL_CENTER**: The central reference point of the measurement plate.

This ensures that the ground-truth data is highly accurate for each individual sensor.

## Time Reference (`time_reference.csv`)

This file defines the temporal boundaries for each measurement run.

**Time Reference Rationale:**
For each `point_id`, the `time_reference.csv` specifies the `start_time` and `end_time` (in both local time and UTC). These timestamps determine the exact duration during which the sensors were stationary at that specific point and valid measurements were being recorded. This is used to filter the raw data streams to match the ground-truth positions.

import marimo

__generated_with = "0.16.5"
app = marimo.App(width="full", app_title="Laser altimetry from orbit")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    return mo, np, plt


@app.cell
def _(mo):
    mo.md(
        r"""
    # Laser altimetry from orbit
    Connect a satellite's orbit to a laser pulse, then assemble repeated height profiles into global coverage.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 1 · Choose the circular orbit

    For orbital radius $r=r_e+h$, Newtonian gravity gives

    $$v=\sqrt{\frac{\mu}{r}}, \qquad
    T=\frac{2\pi r}{v}=2\pi r\sqrt{\frac{r}{\mu}}.$$

    Increasing altitude makes the satellite **slower**, but gives it a **longer path**;
    both effects increase the period.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    altitude_km = mo.ui.slider(
        150,
        40000,
        step=10,
        value=570,
        label="Orbital altitude h (km)",
        show_value=True,
        full_width=True,
    )
    return (altitude_km,)


@app.cell
def _(altitude_km, np):
    earth_radius_m = 6_378_140.0
    mu_m3_s2 = 3.986004e14
    light_speed_m_s = 299_792_458.0
    earth_day_s = 86_400.0
    orbit_radius_m = earth_radius_m + altitude_km.value * 1000.0
    orbital_speed_m_s = np.sqrt(mu_m3_s2 / orbit_radius_m)
    orbital_period_s = 2 * np.pi * orbit_radius_m / orbital_speed_m_s
    orbits_per_day = earth_day_s / orbital_period_s
    return (
        earth_day_s,
        earth_radius_m,
        light_speed_m_s,
        mu_m3_s2,
        orbital_period_s,
        orbital_speed_m_s,
        orbits_per_day,
    )


@app.cell
def _(
    altitude_km,
    earth_radius_m,
    mo,
    mu_m3_s2,
    np,
    orbital_period_s,
    orbital_speed_m_s,
    orbits_per_day,
    plt,
):
    _moon_distance_from_center_km = 384_400.0
    _moon_altitude_km = _moon_distance_from_center_km - earth_radius_m / 1000
    _altitudes = np.linspace(150, 1.05 * _moon_altitude_km, 1200)
    _radii = earth_radius_m + 1000 * _altitudes
    _speeds = np.sqrt(mu_m3_s2 / _radii) / 1000
    _periods = 2 * np.pi * np.sqrt(_radii**3 / mu_m3_s2) / 60
    _moon_speed = np.sqrt(mu_m3_s2 / (_moon_distance_from_center_km * 1000)) / 1000
    _moon_period_min = 2 * np.pi * np.sqrt((_moon_distance_from_center_km * 1000) ** 3 / mu_m3_s2) / 60

    _fig, (_speed_ax, _period_ax) = plt.subplots(1, 2, figsize=(10.8, 4.35), layout="constrained")
    _speed_ax.plot(_altitudes, _speeds, color="#147d92", lw=2.7)
    _period_ax.plot(_altitudes, _periods, color="#d97706", lw=2.7)
    _speed_ax.scatter(altitude_km.value, orbital_speed_m_s / 1000, color="#147d92", s=70, zorder=4)
    _period_ax.scatter(altitude_km.value, orbital_period_s / 60, color="#d97706", s=70, zorder=4)
    _speed_ax.scatter(_moon_altitude_km, _moon_speed, marker="o", s=85, color="0.18", zorder=5)
    _period_ax.scatter(_moon_altitude_km, _moon_period_min, marker="o", s=85, color="0.18", zorder=5)
    for _axis in (_speed_ax, _period_ax):
        _axis.axvline(altitude_km.value, color="0.45", lw=1, ls="--")
        _axis.axvline(35_786, color="0.55", lw=1, ls=":")
        _axis.grid(alpha=0.2)
        _axis.set_xlim(_altitudes[0], _altitudes[-1])
    _speed_ax.set(
        title=r"Speed falls as $1/\sqrt{r}$",
        xlabel="Altitude above Earth's equator (km)",
        ylabel="Orbital velocity (km/s)",
    )
    _period_ax.set(
        title=r"Period grows as $r^{3/2}$",
        xlabel="Altitude above Earth's equator (km)",
        ylabel="Orbital period (minutes)",
    )
    _period_ax.annotate(
        "geosynchronous\naltitude",
        xy=(35_786, 1436),
        xytext=(29_000, 1050),
        arrowprops={"arrowstyle": "->", "color": "0.35"},
        ha="center",
        color="0.3",
    )
    _speed_ax.annotate(
        "Moon",
        xy=(_moon_altitude_km, _moon_speed),
        xytext=(-8, 14),
        textcoords="offset points",
        ha="right",
        weight="bold",
    )
    _period_ax.annotate(
        "Moon\n27.3 days",
        xy=(_moon_altitude_km, _moon_period_min),
        xytext=(-8, -28),
        textcoords="offset points",
        ha="right",
        weight="bold",
    )
    plt.close(_fig)

    _hours = int(orbital_period_s // 3600)
    _minutes = int((orbital_period_s % 3600) // 60)
    _seconds = int(round(orbital_period_s % 60))
    _period_text = (
        f"{_hours} h {_minutes} min"
        if _hours
        else f"{_minutes} min {_seconds} s"
    )
    _readout = mo.md(
        fr"""
        ### At {altitude_km.value:,} km

        | Quantity | Value |
        |:--|--:|
        | Orbit radius $r$ | ${earth_radius_m / 1000 + altitude_km.value:,.0f}\ \mathrm{{km}}$ |
        | Speed $v$ | ${orbital_speed_m_s / 1000:.3f}\ \mathrm{{km/s}}$ |
        | Period $T$ | **{_period_text}** |
        | Orbits per 24 h | ${orbits_per_day:.2f}$ |

        The dotted reference is geosynchronous altitude. The Moon is marked at its
        average distance of **384,400 km from Earth's center**. The notes' 570 km
        example rounds to **7.6 km/s**, **1 h 36 min**, and **15 orbits per day**.
        """
    )
    mo.vstack(
        [
            altitude_km,
            mo.hstack([mo.as_html(_fig), _readout], widths=[3, 2], align="center", wrap=True),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 2 · Turn a pulse delay into a terrain profile

    The pulse travels **down and back**, so its total path is $2R$. If $t$ is the
    measured round-trip time,

    $$R=\frac{ct}{2}, \qquad z_{\mathrm{surface}}=h-R.$$

    That is where the factor of two comes from. Pulse rate controls along-track
    spacing; clock precision controls height precision.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    pulse_rate_hz = mo.ui.slider(
        1,
        30,
        step=1,
        value=6,
        label="Laser pulse rate (pulses/s)",
        show_value=True,
        full_width=True,
    )
    timing_precision_ns = mo.ui.slider(
        1.0,
        100.0,
        step=1.0,
        value=30.0,
        label="Clock uncertainty σt (ns)",
        show_value=True,
        full_width=True,
    )
    return pulse_rate_hz, timing_precision_ns


@app.cell
def _(
    altitude_km,
    light_speed_m_s,
    np,
    orbital_speed_m_s,
    pulse_rate_hz,
    timing_precision_ns,
):
    profile_length_km = 40.0
    sample_spacing_m = orbital_speed_m_s / pulse_rate_hz.value
    profile_x_km = np.arange(0, profile_length_km + 1e-9, sample_spacing_m / 1000)
    sample_count = len(profile_x_km)

    def terrain_elevation_m(x_km):
        _base = 130 + 45 * np.sin(2 * np.pi * x_km / 14)
        _hill = 720 * np.exp(-0.5 * ((x_km - 23) / 4.1) ** 2)
        _ridge = 260 * np.exp(-0.5 * ((x_km - 33) / 2.0) ** 2)
        return _base + _hill + _ridge

    true_surface_m = terrain_elevation_m(profile_x_km)
    true_range_m = altitude_km.value * 1000 - true_surface_m
    true_delay_s = 2 * true_range_m / light_speed_m_s
    _rng = np.random.default_rng(11)
    timing_error_s = timing_precision_ns.value * 1e-9 * _rng.standard_normal(sample_count)
    measured_delay_s = true_delay_s + timing_error_s
    measured_surface_m = altitude_km.value * 1000 - light_speed_m_s * measured_delay_s / 2
    height_precision_m = light_speed_m_s * timing_precision_ns.value * 1e-9 / 2
    nominal_delay_ms = 2 * altitude_km.value * 1000 / light_speed_m_s * 1000
    return (
        height_precision_m,
        measured_surface_m,
        nominal_delay_ms,
        profile_length_km,
        profile_x_km,
        sample_spacing_m,
        terrain_elevation_m,
        true_surface_m,
    )


@app.cell(hide_code=True)
def _(mo, profile_x_km):
    pulse_step = mo.ui.number(
        start=1,
        stop=len(profile_x_km),
        step=1,
        value=1,
        label=f"Selected pulse (1–{len(profile_x_km)})",
    )
    return (pulse_step,)


@app.cell
def _(
    height_precision_m,
    measured_surface_m,
    mo,
    nominal_delay_ms,
    np,
    plt,
    profile_length_km,
    profile_x_km,
    pulse_rate_hz,
    pulse_step,
    sample_spacing_m,
    terrain_elevation_m,
    timing_precision_ns,
    true_surface_m,
):
    _dense_x = np.linspace(0, profile_length_km, 900)
    _dense_surface = terrain_elevation_m(_dense_x)
    _fig, _axes = plt.subplots(2, 1, figsize=(10.5, 6.5), sharex=True, layout="constrained")

    # Panel 1 makes pulse cadence spatial: every gold line is one emitted pulse.
    _track_height = float(np.max(_dense_surface) + 260)
    _active_index = min(max(int(pulse_step.value) - 1, 0), len(profile_x_km) - 1)
    _active_x = profile_x_km[_active_index]
    _active_ground = true_surface_m[_active_index]
    _active_measurement = measured_surface_m[_active_index]
    _height_error_m = measured_surface_m - true_surface_m
    _axes[0].plot(_dense_x, _dense_surface, color="0.25", lw=2.1)
    _axes[0].axhline(_track_height, color="#147d92", lw=2.4, label="satellite track")
    _axes[0].vlines(
        profile_x_km,
        true_surface_m,
        _track_height,
        color="#d97706",
        lw=0.75,
        alpha=0.65,
    )
    _axes[0].scatter(profile_x_km, true_surface_m, s=25, color="#d97706", zorder=3, label="pulse footprint")
    _axes[0].vlines(
        _active_x,
        _active_ground,
        _track_height,
        color="#ef4444",
        linewidth=3,
        zorder=6,
        label=f"selected pulse {pulse_step.value:.0f}",
    )
    _axes[0].scatter(
        [_active_x],
        [_active_ground],
        s=120,
        facecolor="none",
        edgecolor="#ef4444",
        linewidth=2.2,
        zorder=5,
    )
    _axes[0].set(
        ylabel="Elevation (m)",
        title=f"{pulse_rate_hz.value} pulses/s → one footprint every {sample_spacing_m:.0f} m",
        ylim=(0, _track_height + 90),
    )
    _axes[0].legend(loc="upper left", ncols=2)
    _axes[0].grid(alpha=0.18)

    # Panel 2 shows the measured profile and the uncertainty attached to each point.
    _axes[1].plot(_dense_x, _dense_surface, color="0.25", lw=2.1, label="actual terrain")
    _axes[1].errorbar(
        profile_x_km,
        measured_surface_m,
        yerr=height_precision_m,
        fmt="o",
        ms=5,
        color="#147d92",
        ecolor="#ef4444",
        elinewidth=2.8,
        capsize=0,
        barsabove=True,
        alpha=0.9,
        label=r"measured height; vertical line = ± $1\sigma_h$",
    )
    _axes[1].scatter(
        [_active_x],
        [_active_measurement],
        s=120,
        facecolor="none",
        edgecolor="#ef4444",
        linewidth=2.2,
        zorder=5,
        label="selected measurement",
    )
    _axes[1].set(
        xlabel="Distance along satellite track (km)",
        ylabel="Elevation (m)",
        title=f"Each pulse becomes one height estimate; bars show ±{height_precision_m:.2f} m (1σ)",
    )
    _axes[1].legend(loc="upper left", ncols=2)
    _axes[1].grid(alpha=0.18)
    plt.close(_fig)

    _rms_error = float(np.sqrt(np.mean((measured_surface_m - true_surface_m) ** 2)))
    _summary = mo.md(
        fr"""
        **What the controls imply**

        - Nominal round-trip delay: **{nominal_delay_ms:.3f} ms**
        - Time between pulses: **{1 / pulse_rate_hz.value:.3f} s**
        - Distance flown between pulses: **{sample_spacing_m:.1f} m**
        - $1\sigma$ range uncertainty: **{height_precision_m:.3f} m** for {timing_precision_ns.value:.0f} ns timing
        - Simulated profile RMS error: **{_rms_error:.3f} m**
        - Selected pulse {pulse_step.value:.0f}: **{_active_x:.2f} km** along track,
          measured error **{_height_error_m[_active_index]:+.2f} m**

        **Pulse rate changes horizontal sampling density. Clock uncertainty changes vertical
        accuracy.** The vertical bars in the second plot show ±$1\sigma_h$ around every
        height estimate. The absolute round-trip delay is still about {nominal_delay_ms:.3f} ms.
        """
    )
    _controls = mo.hstack(
        [pulse_rate_hz, timing_precision_ns, pulse_step],
        widths=[2, 2, 1],
        align="end",
        wrap=True,
    )
    mo.vstack([_controls, mo.as_html(_fig), mo.callout(_summary, kind="neutral")])
    return


@app.cell(hide_code=True)
def _(mo):
    _intro = mo.md(
        r"""
        ## 3 · Sweep profiles across the rotating Earth

        One pass produces a line profile. Repeated passes become a 2-D raster because
        Earth rotates beneath the orbital plane. Compare the two idealized orientations
        from the notes, change the orbit height, then extend the time window. The final
        altitude preset has a circular-orbit period of exactly 24 hours.
        """
    )
    orbit_orientation = mo.ui.radio(
        options={"Equatorial orbit": 0.0, "Polar orbit": 90.0},
        value="Polar orbit",
        label="Orbital plane",
    )
    coverage_hours = mo.ui.slider(
        0,
        48,
        step=1,
        value=0,
        label="Elapsed mission time (hours)",
        show_value=True,
        full_width=True,
    )
    globe_altitude_km = mo.ui.slider(
        steps=[300, 400, 570, 800, 1000, 1500, 2000, 3000, 5000, 8000, 12000, 20000, 30000, 35863],
        value=570,
        label="Orbit altitude (km; final step = 24 h)",
        show_value=True,
        full_width=True,
    )
    view_azimuth = mo.ui.slider(
        -180,
        180,
        step=5,
        value=-60,
        label="Globe rotation (degrees)",
        show_value=True,
        full_width=True,
    )
    view_elevation = mo.ui.slider(
        5,
        75,
        step=5,
        value=25,
        label="Camera elevation (degrees)",
        show_value=True,
        full_width=True,
    )
    mo.vstack([_intro])
    return (
        coverage_hours,
        globe_altitude_km,
        orbit_orientation,
        view_azimuth,
        view_elevation,
    )


@app.cell
def _(
    coverage_hours,
    earth_day_s,
    earth_radius_m,
    globe_altitude_km,
    mo,
    mu_m3_s2,
    np,
    orbit_orientation,
    plt,
    view_azimuth,
    view_elevation,
):
    _globe_orbit_radius_m = earth_radius_m + globe_altitude_km.value * 1000
    _globe_orbital_period_s = 2 * np.pi * np.sqrt(_globe_orbit_radius_m**3 / mu_m3_s2)
    _duration_s = coverage_hours.value * 3600.0
    _time = np.linspace(0, _duration_s, max(500, coverage_hours.value * 180))
    _inclination = np.radians(orbit_orientation.value)
    _orbital_phase = 2 * np.pi * _time / _globe_orbital_period_s
    _earth_angle = 2 * np.pi * _time / earth_day_s

    # Circular orbit in an inertial plane, rotated into the Earth-fixed frame.
    _x_i = np.cos(_orbital_phase)
    _y_i = np.sin(_orbital_phase) * np.cos(_inclination)
    _z_i = np.sin(_orbital_phase) * np.sin(_inclination)
    _x_ecef = np.cos(_earth_angle) * _x_i + np.sin(_earth_angle) * _y_i
    _y_ecef = -np.sin(_earth_angle) * _x_i + np.cos(_earth_angle) * _y_i
    ground_lat_deg = np.degrees(np.arcsin(np.clip(_z_i, -1, 1)))
    ground_lon_deg = np.degrees(np.arctan2(_y_ecef, _x_ecef))

    # Display the scene in inertial space at the final time. Historical
    # footprints remain attached to the Earth as it rotates to its current angle.
    _current_earth_angle = _earth_angle[-1]
    _track_x = np.cos(_current_earth_angle) * _x_ecef - np.sin(_current_earth_angle) * _y_ecef
    _track_y = np.sin(_current_earth_angle) * _x_ecef + np.cos(_current_earth_angle) * _y_ecef
    _track_z = _z_i

    _orientation_name = "Polar orbit" if orbit_orientation.value == 90.0 else "Equatorial orbit"

    _fig = plt.figure(figsize=(9.2, 7.2), layout="constrained")
    _ax = _fig.add_subplot(111, projection="3d", computed_zorder=False)

    # Use the camera direction for explicit visibility tests. Matplotlib's
    # automatic 3D sorting treats each surface/line as a whole artist.
    _view_elev_rad = np.radians(view_elevation.value)
    _view_azim_rad = np.radians(view_azimuth.value)
    _camera_direction = np.array(
        [
            np.cos(_view_elev_rad) * np.cos(_view_azim_rad),
            np.cos(_view_elev_rad) * np.sin(_view_azim_rad),
            np.sin(_view_elev_rad),
        ]
    )

    # Draw a spherical Earth and a geographic graticule.
    _surface_lon = np.linspace(0, 2 * np.pi, 100)
    _surface_lat = np.linspace(-np.pi / 2, np.pi / 2, 55)
    _lon_grid, _lat_grid = np.meshgrid(_surface_lon, _surface_lat)
    _sphere_x = np.cos(_lat_grid) * np.cos(_lon_grid)
    _sphere_y = np.cos(_lat_grid) * np.sin(_lon_grid)
    _sphere_z = np.sin(_lat_grid)
    _ax.plot_surface(
        _sphere_x,
        _sphere_y,
        _sphere_z,
        color="#72b7d2",
        alpha=0.58,
        linewidth=0,
        antialiased=True,
        shade=True,
        zorder=1,
    )

    def _visible_above_earth(_x, _y, _z):
        _depth = (
            _x * _camera_direction[0]
            + _y * _camera_direction[1]
            + _z * _camera_direction[2]
        )
        _distance_from_view_axis_sq = _x**2 + _y**2 + _z**2 - _depth**2
        _occulted = (_depth < 0) & (_distance_from_view_axis_sq < 1.001**2)
        return (
            np.where(_occulted, np.nan, _x),
            np.where(_occulted, np.nan, _y),
            np.where(_occulted, np.nan, _z),
        )

    _grid_radius = 1.003
    for _latitude_deg in np.arange(-60, 61, 30):
        _latitude_rad = np.radians(_latitude_deg)
        _latitude_x = _grid_radius * np.cos(_latitude_rad) * np.cos(_surface_lon)
        _latitude_y = _grid_radius * np.cos(_latitude_rad) * np.sin(_surface_lon)
        _latitude_z = np.full_like(_surface_lon, _grid_radius * np.sin(_latitude_rad))
        _latitude_x, _latitude_y, _latitude_z = _visible_above_earth(
            _latitude_x, _latitude_y, _latitude_z
        )
        _ax.plot(
            _latitude_x,
            _latitude_y,
            _latitude_z,
            color="white",
            alpha=0.42,
            lw=0.7,
            zorder=2,
        )
    _meridian_lat = np.linspace(-np.pi , np.pi , 100)
    for _longitude_deg in np.arange(0, 360, 30):
        _longitude_rad = np.radians(_longitude_deg) + _current_earth_angle
        _meridian_x = _grid_radius * np.cos(_meridian_lat) * np.cos(_longitude_rad)
        _meridian_y = _grid_radius * np.cos(_meridian_lat) * np.sin(_longitude_rad)
        _meridian_z = _grid_radius * np.sin(_meridian_lat)
        _meridian_x, _meridian_y, _meridian_z = _visible_above_earth(
            _meridian_x, _meridian_y, _meridian_z
        )
        _ax.plot(
            _meridian_x,
            _meridian_y,
            _meridian_z,
            color="white",
            alpha=0.38,
            lw=0.65,
            zorder=2,
        )
    _prime_lon = _current_earth_angle
    _prime_x = 1.008 * np.cos(_meridian_lat) * np.cos(_prime_lon)
    _prime_y = 1.008 * np.cos(_meridian_lat) * np.sin(_prime_lon)
    _prime_z = 1.008 * np.sin(_meridian_lat)
    _prime_x, _prime_y, _prime_z = _visible_above_earth(_prime_x, _prime_y, _prime_z)
    _ax.plot(
        _prime_x,
        _prime_y,
        _prime_z,
        color="#74C365",
        alpha=0.95,
        lw=2,
        label="prime meridian",
        zorder=3,
    )
    _prime_marker_x = 1.015 * np.cos(_prime_lon)
    _prime_marker_y = 1.015 * np.sin(_prime_lon)
    _prime_marker_depth = (
        _prime_marker_x * _camera_direction[0]
        + _prime_marker_y * _camera_direction[1]
    )
    _prime_marker_perp_sq = 1.015**2 - _prime_marker_depth**2
    if not (_prime_marker_depth < 0 and _prime_marker_perp_sq < 1.001**2):
        _ax.scatter(
            [_prime_marker_x],
            [_prime_marker_y],
            [0],
            s=38,
            color="#74C365",
            marker="x",
            depthshade=False,
            zorder=3,
        )

    # Lift the ground track slightly above the sphere so it remains legible.
    _track_radius = 1.018
    _track_depth = _track_radius * (
        _track_x * _camera_direction[0]
        + _track_y * _camera_direction[1]
        + _track_z * _camera_direction[2]
    )
    _track_distance_from_view_axis_sq = _track_radius**2 - _track_depth**2
    _track_occulted = (_track_depth < 0) & (_track_distance_from_view_axis_sq < 1.003**2)
    _ax.plot(
        np.where(_track_occulted, np.nan, _track_radius * _track_x),
        np.where(_track_occulted, np.nan, _track_radius * _track_y),
        np.where(_track_occulted, np.nan, _track_radius * _track_z),
        color="#075985",
        lw=1.1,
        alpha=0.95,
        label="laser ground track",
        zorder=4,
    )

    # Draw the satellite's fixed circular orbit in inertial space.
    _orbit_radius_scale = _globe_orbit_radius_m / earth_radius_m
    _orbit_curve_phase = np.linspace(0, 2 * np.pi, 720)
    _orbit_x_i = np.cos(_orbit_curve_phase)
    _orbit_y_i = np.sin(_orbit_curve_phase) * np.cos(_inclination)
    _orbit_z_i = np.sin(_orbit_curve_phase) * np.sin(_inclination)

    # Matplotlib's translucent 3D surfaces do not depth-sort lines reliably.
    # Remove only the orbit samples that are actually occulted by Earth's disk.
    _orbit_x = _orbit_radius_scale * _orbit_x_i
    _orbit_y = _orbit_radius_scale * _orbit_y_i
    _orbit_z = _orbit_radius_scale * _orbit_z_i
    _depth_along_view = (
        _orbit_x * _camera_direction[0]
        + _orbit_y * _camera_direction[1]
        + _orbit_z * _camera_direction[2]
    )
    _distance_from_view_axis_sq = _orbit_radius_scale**2 - _depth_along_view**2
    _orbit_occulted = (_depth_along_view < 0) & (_distance_from_view_axis_sq < 1.003**2)
    _visible_orbit_x = np.where(_orbit_occulted, np.nan, _orbit_x)
    _visible_orbit_y = np.where(_orbit_occulted, np.nan, _orbit_y)
    _visible_orbit_z = np.where(_orbit_occulted, np.nan, _orbit_z)

    _satellite_x = _orbit_radius_scale * _x_i[-1]
    _satellite_y = _orbit_radius_scale * _y_i[-1]
    _satellite_z = _orbit_radius_scale * _z_i[-1]
    _subpoint_x = _track_radius * _track_x[-1]
    _subpoint_y = _track_radius * _track_y[-1]
    _subpoint_z = _track_radius * _track_z[-1]

    def _point_is_occulted(_x, _y, _z):
        _depth = (
            _x * _camera_direction[0]
            + _y * _camera_direction[1]
            + _z * _camera_direction[2]
        )
        _perpendicular_distance_sq = _x**2 + _y**2 + _z**2 - _depth**2
        return bool(_depth < 0 and _perpendicular_distance_sq < 1.001**2)

    _satellite_alpha = 0.18 if _point_is_occulted(_satellite_x, _satellite_y, _satellite_z) else 1.0
    _subpoint_alpha = 0.18 if _point_is_occulted(_subpoint_x, _subpoint_y, _subpoint_z) else 1.0
    _ax.plot(
        [_subpoint_x, _satellite_x],
        [_subpoint_y, _satellite_y],
        [_subpoint_z, _satellite_z],
        color="#ef4444",
        lw=2.3,
        label="nadir laser",
        zorder=8,
    )
    _ax.scatter(
        [_satellite_x],
        [_satellite_y],
        [_satellite_z],
        s=115,
        marker="D",
        color="#facc15",
        edgecolor="#4c1d95",
        linewidth=1.2,
        depthshade=False,
        alpha=_satellite_alpha,
        label="satellite",
        zorder=9,
    )
    _ax.scatter(
        [_subpoint_x],
        [_subpoint_y],
        [_subpoint_z],
        s=95,
        color="#f59e0b",
        edgecolor="white",
        linewidth=1.1,
        depthshade=False,
        alpha=_subpoint_alpha,
        label="current sub-satellite point",
        zorder=9,
    )
    _plot_limit = max(1.12, 1.08 * _orbit_radius_scale)
    _ax.set(
        xlim=(-_plot_limit, _plot_limit),
        ylim=(-_plot_limit, _plot_limit),
        zlim=(-_plot_limit, _plot_limit),
        title=f"{_orientation_name} at {globe_altitude_km.value:,.0f} km · rotating Earth · {coverage_hours.value} h",
    )
    _ax.plot(
        _visible_orbit_x,
        _visible_orbit_y,
        _visible_orbit_z,
        color="#7c3aed",
        lw=2,
        ls="--",
        alpha=0.9,
        label="satellite orbit",
        zorder=7,
    )
    _ax.set_box_aspect((1, 1, 1))
    _ax.view_init(elev=view_elevation.value, azim=view_azimuth.value)
    _ax.set_axis_off()
    _ax.legend(loc="upper left")
    plt.close(_fig)

    _revolutions = _duration_s / _globe_orbital_period_s
    _period_hours = _globe_orbital_period_s / 3600
    _latitude_span = float(np.max(ground_lat_deg) - np.min(ground_lat_deg))
    if globe_altitude_km.value == 35863 and orbit_orientation.value == 0.0:
        _explanation = (
            "At the 24-hour altitude, an equatorial satellite co-rotates with Earth: "
            "its orbit is a circle in space while its ground point remains fixed."
        )
    elif orbit_orientation.value == 90.0:
        _explanation = (
            "A polar orbit reaches both poles. Rotation shifts each successive pass in longitude, "
            "so parallel height profiles can build a global map."
        )
    else:
        _explanation = (
            "An equatorial orbit remains at 0° latitude. It repeatedly surveys an equatorial belt "
            "rather than the full globe."
        )
    _globe_controls = mo.vstack(
        [
            mo.md("### Globe controls"),
            orbit_orientation,
            globe_altitude_km,
            coverage_hours,
            view_azimuth,
            view_elevation,
        ],
        gap=1.5,
    )
    mo.vstack(
        [
            mo.hstack(
                [_globe_controls, mo.as_html(_fig)],
                widths=[1, 3],
                align="center",
                wrap=True,
                gap=2,
            ),
            mo.callout(
                mo.md(
                    f"**Orbital period {_period_hours:.2f} h · {_revolutions:.2f} revolutions shown · "
                    f"{_latitude_span:.0f}° latitude span.** {_explanation}"
                ),
                kind="info",
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Put the system together

    1. **Orbital mechanics** determines speed, period, and where the satellite points.
    2. **Pulse timing** turns each round trip into one range estimate.
    3. **Along-track motion** arranges those estimates into a height profile.
    4. **Earth's rotation plus a polar orbit** shifts later profiles across longitude,
       assembling a 2-D topographic raster.

    The model is intentionally idealized: it treats Earth as a sphere and omits orbit
    perturbations, atmosphere, clouds, off-nadir pointing, geolocation error, surface
    reflectivity, and the finite laser footprint. Those are the next ingredients in a
    real altimetry mission.

    Built with [marimo](https://docs.marimo.io/). Open the notebook in edit mode to
    inspect or change every equation.
    """
    )
    return


if __name__ == "__main__":
    app.run()

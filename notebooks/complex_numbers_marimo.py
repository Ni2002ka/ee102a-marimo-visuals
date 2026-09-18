import marimo

__generated_with = "0.16.5"
app = marimo.App(width="full", app_title="Complex numbers, seen geometrically")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    return mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Complex numbers, geometrically!

    Build a number in Cartesian form, watch Euler's relation convert it to polar form, then use the same geometry to understand arithmetic and roots.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    _intro = mo.md(
        r"""
    ## 1 · One number, two coordinate systems

    Choose $z=x+jy$. Its distance from the origin is $|z|=\sqrt{x^2+y^2}$ and its
    angle is $\angle z=\operatorname{atan2}(y,x)$. Euler's relation
    $e^{j\theta}=\cos\theta+j\sin\theta$ then gives $z=|z|e^{j\angle z}$.
    """
    )
    x = mo.ui.slider(-4.0, 4.0, step=0.1, value=3.0, label="Real part  x", show_value=True, full_width=True)
    y = mo.ui.slider(-4.0, 4.0, step=0.1, value=2.0, label="Imaginary part  y", show_value=True, full_width=True)
    mo.vstack([_intro, mo.hstack([x, y], widths="equal", wrap=True)])
    return x, y


@app.cell
def _(np, x, y):
    z = complex(x.value, y.value)
    magnitude = abs(z)
    phase = np.angle(z) if magnitude > 1e-12 else 0.0
    return magnitude, phase, z


@app.cell
def _(magnitude, mo, np, phase, plt, z):
    _limit = max(4.5, magnitude + 0.8)
    _fig, _ax = plt.subplots(figsize=(7.4, 5.4), layout="constrained")
    _ax.axhline(0, color="0.55", lw=0.8)
    _ax.axvline(0, color="0.55", lw=0.8)
    _ax.grid(True, alpha=0.2)
    _ax.quiver(0, 0, z.real, z.imag, angles="xy", scale_units="xy", scale=1, color="#0072b2", width=0.009, label="$z$")
    _ax.quiver(0, 0, z.real, -z.imag, angles="xy", scale_units="xy", scale=1, color="#d55e00", width=0.006, alpha=0.8, label="$z^*$")
    _ax.plot([z.real, z.real], [0, z.imag], color="#0072b2", ls=":", lw=1)
    _ax.plot([0, z.real], [z.imag, z.imag], color="#0072b2", ls=":", lw=1)
    if magnitude > 1e-12:
        _arc_radius = min(1.15, 0.34 * magnitude)
        _arc_angles = np.linspace(0, phase, 100)
        _ax.plot(_arc_radius * np.cos(_arc_angles), _arc_radius * np.sin(_arc_angles), color="#009e73", lw=2)
        _label_angle = phase / 2
        _ax.text(1.25 * _arc_radius * np.cos(_label_angle), 1.25 * _arc_radius * np.sin(_label_angle), r"$\theta$", color="#007a58", ha="center", va="center")
    _ax.scatter([z.real, z.real], [z.imag, -z.imag], c=["#0072b2", "#d55e00"], s=45, zorder=3)
    _ax.annotate("z", (z.real, z.imag), xytext=(7, 7), textcoords="offset points")
    _ax.annotate("z*", (z.real, -z.imag), xytext=(7, -13), textcoords="offset points")
    _ax.set(xlim=(-_limit, _limit), ylim=(-_limit, _limit), aspect="equal", xlabel="Re", ylabel="Im", title="Cartesian components, polar vector, and conjugate")
    _ax.legend(loc="upper left")
    plt.close(_fig)

    _phase_deg = np.degrees(phase)
    _cartesian = f"{z.real:.1f} {'+' if z.imag >= 0 else '−'} j{abs(z.imag):.1f}"
    _conjugate = f"{z.real:.1f} {'−' if z.imag >= 0 else '+'} j{abs(z.imag):.1f}"
    _note = "The origin has zero magnitude; its phase is undefined (shown here as 0°)." if magnitude <= 1e-12 else "Conjugation reflects the point across the real axis: magnitude stays fixed and phase changes sign."
    _values = mo.md(
        fr"""
        | Description | Value |
        |:--|--:|
        | Cartesian form | $z={_cartesian}$ |
        | Polar form | $z={magnitude:.3f}e^{{j({_phase_deg:.1f}^\circ)}}$ |
        | Conjugate | $z^*={_conjugate}$ |

        {_note}
        """
    )
    mo.hstack([mo.as_html(_fig), _values], widths=[3, 2], align="center", wrap=True)
    return


@app.cell(hide_code=True)
def _(mo):
    _intro = mo.md(
        r"""
    ## 2 · Arithmetic becomes geometry

    Choose a second number $w=|w|e^{j\angle w}$. Multiplication multiplies magnitudes
    and adds phases; division divides magnitudes and subtracts phases. A reciprocal is
    the special case $1/w$: invert the magnitude and negate the phase.
    """
    )
    w_magnitude = mo.ui.slider(0.25, 3.0, step=0.05, value=1.5, label="|w|", show_value=True, full_width=True)
    w_phase_deg = mo.ui.slider(-180, 180, step=5, value=45, label="∠w (degrees)", show_value=True, full_width=True)
    operation = mo.ui.radio(options=["Multiply  z · w", "Divide  z / w", "Reciprocal  1 / w"], value="Multiply  z · w", label="Operation")
    mo.vstack([_intro, mo.hstack([w_magnitude, w_phase_deg], widths="equal", wrap=True), operation])
    return operation, w_magnitude, w_phase_deg


@app.cell
def _(np, operation, w_magnitude, w_phase_deg, z):
    w_phase = np.radians(w_phase_deg.value)
    w = w_magnitude.value * np.exp(1j * w_phase)
    if operation.value == "Multiply  z · w":
        result = z * w
        result_name = "z · w"
        rule = "multiply magnitudes; add phases"
    elif operation.value == "Divide  z / w":
        result = z / w
        result_name = "z / w"
        rule = "divide magnitudes; subtract phases"
    else:
        result = 1 / w
        result_name = "1 / w"
        rule = "invert the magnitude; negate the phase"
    return result, rule, w


@app.cell
def _(mo, np, operation, plt, result, rule, w, z):
    _blue, _green, _orange = "#0072b2", "#009e73", "#d55e00"

    def _draw_vector(_ax, _value, _name, _color, *, _style="solid", _alpha=1.0):
        if _style == "dashed":
            _ax.plot(
                [0, _value.real], [0, _value.imag],
                color=_color, lw=2, ls="--", alpha=_alpha, label=_name,
            )
        else:
            _ax.quiver(
                0, 0, _value.real, _value.imag,
                angles="xy", scale_units="xy", scale=1,
                color=_color, width=0.008, alpha=_alpha, label=_name,
            )
        _ax.scatter(_value.real, _value.imag, color=_color, s=42, alpha=_alpha, zorder=3)

    def _draw_arc(_ax, _start, _stop, _radius, _label):
        _angles = np.linspace(_start, _stop, 100)
        _ax.plot(_radius * np.cos(_angles), _radius * np.sin(_angles), color=_orange, lw=2)
        _middle = (_start + _stop) / 2
        _ax.text(
            1.16 * _radius * np.cos(_middle),
            1.16 * _radius * np.sin(_middle),
            _label, color=_orange, ha="center", va="center",
        )

    _fig, _ax = plt.subplots(figsize=(7.4, 5.4), layout="constrained")
    _ax.axhline(0, color="0.55", lw=0.8)
    _ax.axvline(0, color="0.55", lw=0.8)
    _ax.grid(True, alpha=0.2)
    _z_phase = np.angle(z) if abs(z) > 1e-12 else 0.0
    _w_phase = np.angle(w)

    if operation.value == "Multiply  z · w":
        _scaled_w = abs(z) * w
        _draw_vector(_ax, z, "$z$ (multiplier)", _blue)
        _draw_vector(_ax, w, "$w$ (start)", _green)
        if abs(z) > 1e-12:
            _draw_vector(_ax, _scaled_w, "$|z|w$ (scale)", _green, _style="dashed", _alpha=0.55)
            _draw_arc(_ax, _w_phase, _w_phase + _z_phase, min(0.65 * max(abs(result), 1), 1.5), r"$+\angle z$")
        _draw_vector(_ax, result, "$zw$ (scale, then rotate)", _orange)
        _title = "Multiply: scale w by |z|, then rotate by ∠z"
        _details = mo.md(
            fr"""
            **$z\,w$: {rule}**

            Magnitude: ${abs(z):.3f}\times {abs(w):.3f}={abs(result):.3f}$

            Phase: ${np.degrees(_z_phase):.1f}^\circ+{np.degrees(_w_phase):.1f}^\circ
            ={np.degrees(_z_phase + _w_phase):.1f}^\circ$

            The dashed green vector is the scaling step. The orange arc is the rotation step.
            """
        )
        _values = [z, w, _scaled_w, result]
    elif operation.value == "Divide  z / w":
        _scaled_z = z / abs(w)
        _draw_vector(_ax, z, "$z$ (start)", _blue)
        _draw_vector(_ax, w, "$w$ (divisor)", _green)
        _draw_vector(_ax, _scaled_z, "$z/|w|$ (scale)", _blue, _style="dashed", _alpha=0.55)
        if abs(z) > 1e-12:
            _draw_arc(_ax, _z_phase, _z_phase - _w_phase, min(0.65 * max(abs(result), 1), 1.5), r"$-\angle w$")
        _draw_vector(_ax, result, "$z/w$ (scale, then rotate)", _orange)
        _title = "Divide: scale z by 1/|w|, then rotate by −∠w"
        _details = mo.md(
            fr"""
            **$z/w$: {rule}**

            Magnitude: ${abs(z):.3f}/{abs(w):.3f}={abs(result):.3f}$

            Phase: ${np.degrees(_z_phase):.1f}^\circ-{np.degrees(_w_phase):.1f}^\circ
            ={np.degrees(_z_phase - _w_phase):.1f}^\circ$

            The dashed blue vector is the scaling step. The orange arc is the opposite rotation.
            """
        )
        _values = [z, w, _scaled_z, result]
    else:
        _unit_circle = plt.Circle((0, 0), 1, fill=False, color="0.55", ls="--", lw=1)
        _ax.add_patch(_unit_circle)
        _draw_vector(_ax, w, "$w$", _green)
        _draw_vector(_ax, result, "$1/w$", _orange)
        _reflection = np.conjugate(w)
        _ax.plot([0, _reflection.real], [0, _reflection.imag], color=_green, ls=":", lw=1.5, alpha=0.7, label="$w^*$ direction")
        _draw_arc(_ax, _w_phase, -_w_phase, min(0.62, 0.45 * max(abs(w), abs(result))), r"$\theta\to-\theta$")
        _title = "Reciprocal: reflect the angle and invert the radius"
        _details = mo.md(
            fr"""
            **$1/w$: {rule}**

            Radius: $1/{abs(w):.3f}={abs(result):.3f}$

            Phase: $-{np.degrees(_w_phase):.1f}^\circ={np.degrees(np.angle(result)):.1f}^\circ$

            $$\frac{{1}}{{w}}=\frac{{w^*}}{{|w|^2}}$$

            The dotted ray shows the reflected direction; the dashed circle marks unit magnitude.
            """
        )
        _values = [w, result, 1 + 0j, -1 + 0j, 1j, -1j]

    _limit = max(1.6, *(abs(_value) + 0.8 for _value in _values))
    _ax.set(xlim=(-_limit, _limit), ylim=(-_limit, _limit), aspect="equal", xlabel="Re", ylabel="Im", title=_title)
    _ax.legend(loc="upper left")
    plt.close(_fig)

    mo.hstack([mo.as_html(_fig), _details], widths=[3, 2], align="center", wrap=True)
    return


@app.cell(hide_code=True)
def _(mo):
    _intro = mo.md(
        r"""
    ## 3 · All of the Nth roots

    If $z=|z|e^{j\theta}$, its $N$ distinct roots are
    $$r_k=|z|^{1/N}e^{j(\theta+2\pi k)/N},\qquad k=0,\ldots,N-1.$$
    They lie at equal angular spacings of $2\pi/N$. Raising any one to the $N$th
    power returns to $z$.
    """
    )
    degree = mo.ui.slider(2, 10, step=1, value=4, label="Root degree  N", show_value=True, full_width=True)
    mo.vstack([_intro, degree])
    return (degree,)


@app.cell(hide_code=True)
def _(degree, mo):
    root_index = mo.ui.slider(0, degree.value - 1, step=1, value=0, label="Inspect root index  k", show_value=True, full_width=True)
    root_index
    return (root_index,)


@app.cell
def _(degree, magnitude, np, phase, root_index):
    N = degree.value
    k = min(root_index.value, N - 1)
    if magnitude <= 1e-12:
        roots = np.array([0j])
        k = 0
    else:
        roots = magnitude ** (1 / N) * np.exp(1j * (phase + 2 * np.pi * np.arange(N)) / N)
    selected_root = roots[k]
    return N, k, roots, selected_root


@app.cell
def _(N, k, magnitude, mo, np, phase, plt, roots, selected_root, z):
    _radius = max(1.4, (abs(roots[0]) if len(roots) else 0) + 0.55)
    _fig, _ax = plt.subplots(figsize=(7.4, 5.4), layout="constrained")
    _ax.axhline(0, color="0.55", lw=0.8)
    _ax.axvline(0, color="0.55", lw=0.8)
    _ax.grid(True, alpha=0.2)
    if magnitude > 1e-12:
        _circle = plt.Circle((0, 0), abs(roots[0]), fill=False, color="0.55", ls="--", lw=1)
        _ax.add_patch(_circle)
        _root0_phase = np.angle(roots[0])
        _angle_radius = min(0.48 * abs(roots[0]), 0.7)
        _angle_values = np.linspace(0, _root0_phase, 80)
    for _idx, _root in enumerate(roots):
        _color = "#d55e00" if _idx == k else "#0072b2"
        _ax.quiver(0, 0, _root.real, _root.imag, angles="xy", scale_units="xy", scale=1, color=_color, width=0.007, alpha=1 if _idx == k else 0.72)
        _ax.scatter(_root.real, _root.imag, color=_color, s=70 if _idx == k else 42, zorder=3)
        _ax.annotate(f"k={_idx}", (_root.real, _root.imag), xytext=(6, 6), textcoords="offset points")
    if magnitude > 1e-12:
        _angle_middle = _root0_phase / 2
        _arc_mid_x = _angle_radius * np.cos(_angle_middle)
        _arc_mid_y = _angle_radius * np.sin(_angle_middle)
        _normal_sign = 1 if _root0_phase >= 0 else -1
        _normal_angle = _angle_middle + _normal_sign * np.pi / 2
        _label_offset = 0.28
        _label_x = _arc_mid_x + _label_offset * np.cos(_normal_angle)
        _label_y = _arc_mid_y + _label_offset * np.sin(_normal_angle)
        _ax.plot(_angle_radius * np.cos(_angle_values), _angle_radius * np.sin(_angle_values), color="#009e73", lw=2.5, zorder=5)
        _ax.annotate(
            fr"$\angle r_0={np.degrees(_root0_phase):.1f}^\circ$",
            xy=(_arc_mid_x, _arc_mid_y), xytext=(_label_x, _label_y),
            arrowprops=dict(arrowstyle="<-", color="#007a58", lw=1),
            color="#007a58", ha="center", va="center", zorder=6,
        )
    _ax.set(xlim=(-_radius, _radius), ylim=(-_radius, _radius), aspect="equal", xlabel="Re", ylabel="Im", title=f"The {N}th roots of z")
    plt.close(_fig)

    _raised = selected_root ** N
    _error = abs(_raised - z)
    _selected_phase = np.degrees(np.angle(selected_root))
    _target_phase = np.degrees(phase)
    _root_note = (
        "For $z=0$, every displayed branch collapses to the single root 0."
        if magnitude <= 1e-12
        else f"Neighboring roots are separated by ${360/N:.1f}^\\circ$."
    )
    _details = mo.md(
        fr"""
        **Target:** $z={z.real:.3f}{z.imag:+.3f}j={magnitude:.3f}e^{{j({_target_phase:.1f}^\circ)}}$

        **Selected root $r_{k}$**

        $|r_{k}|=|z|^{{1/{N}}}={abs(selected_root):.4f}$

        $\angle r_{k}=({_target_phase:.1f}^\circ+360^\circ\cdot{k})/{N}={_selected_phase:.1f}^\circ$

        **Returned value:** $r_{k}^{{{N}}}={_raised.real:.3f}{_raised.imag:+.3f}j$

        **Return error:** $\left|r_{k}^{{{N}}}-z\right|={_error:.2e}$

        This error is the distance from the returned value $r_k^N$ to the target $z$; it should be near zero, up to floating-point roundoff.

        {_root_note}
        """
    )
    mo.hstack([mo.as_html(_fig), _details], widths=[3, 2], align="center", wrap=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    **What to remember**

    - Cartesian form makes addition natural; polar form makes multiplication, division, and powers natural.
    - Conjugation reflects across the real axis: $|z^*|=|z|$ and $\angle z^*=-\angle z$.
    - Multiplication adds angles; division subtracts them.
    - An $N$th-root problem has $N$ equally spaced solutions unless the target is zero.

    Based on the EE 102A complex-numbers appendix. Built with [marimo](https://docs.marimo.io/).
    """
    )
    return


if __name__ == "__main__":
    app.run()

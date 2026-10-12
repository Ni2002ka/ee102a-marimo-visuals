import marimo

__generated_with = "0.16.5"
app = marimo.App(width="full", app_title="Filter by editing the spectrum")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    return mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Filter by editing the spectrum
    Keep the slow wave, isolate the fast ripples, or mix your own output.
    Each frequency has a **gain**: 0 removes it, 1 keeps it, and 2 doubles it.

    $$x(t)=\cos(2\pi t)+0.1\cos(2\pi\cdot10t)+0.1\cos(2\pi\cdot30t).$$

    **Predict first:** if you remove the 1 Hz component, will the output become
    smoother or more rapidly varying?
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mode = mo.ui.dropdown(
        ["All frequencies", "Low-pass", "High-pass", "Band-pass", "Custom gains"],
        value="All frequencies", label="Filter",
    )
    cutoff = mo.ui.slider(0, 35, value=5, step=1, label="Cutoff (Hz)", show_value=True)
    band = mo.ui.range_slider(0, 35, value=[5, 15], step=1, label="Passband (Hz)", show_value=True)
    keep1 = mo.ui.checkbox(value=True, label="Keep 1 Hz")
    keep10 = mo.ui.checkbox(value=True, label="Keep 10 Hz")
    keep30 = mo.ui.checkbox(value=True, label="Keep 30 Hz")
    gain1 = mo.ui.slider(0, 2, value=1, step=0.1, label="1 Hz gain", show_value=True)
    gain10 = mo.ui.slider(0, 2, value=1, step=0.1, label="10 Hz gain", show_value=True)
    gain30 = mo.ui.slider(0, 2, value=1, step=0.1, label="30 Hz gain", show_value=True)
    zoom_output = mo.ui.checkbox(value=False, label="Fit output vertical scale to remaining signal")
    mo.hstack([mode, zoom_output], justify="start", wrap=True)
    return (
        band,
        cutoff,
        gain1,
        gain10,
        gain30,
        keep1,
        keep10,
        keep30,
        mode,
        zoom_output,
    )


@app.cell(hide_code=True)
def _(band, cutoff, gain1, gain10, gain30, keep1, keep10, keep30, mo, mode):
    if mode.value in ("Low-pass", "High-pass"):
        _controls = mo.vstack([
            cutoff,
            mo.md("Low-pass keeps frequency magnitudes **at or below** the cutoff; high-pass keeps those **above** it."),
        ])
    elif mode.value == "Band-pass":
        _controls = mo.vstack([band, mo.md("The passband applies to frequency magnitude |f|; both endpoints are included.")])
    elif mode.value == "Custom gains":
        _controls = mo.hstack([
            mo.vstack([keep1, gain1]), mo.vstack([keep10, gain10]), mo.vstack([keep30, gain30]),
        ], wrap=True)
    else:
        _controls = mo.md("All three components pass unchanged. Choose a filter to start removing frequencies.")
    _controls
    return


@app.cell
def _(np):
    frequencies = np.array([1.0, 10.0, 30.0])
    amplitudes = np.array([1.0, 0.1, 0.1])
    time = np.linspace(0, 2, 4001)
    components = amplitudes[:, None] * np.cos(2 * np.pi * frequencies[:, None] * time)
    original = components.sum(axis=0)

    def filter_gains(kind, freq, edge, interval, custom):
        if kind == "Low-pass":
            return (freq <= edge).astype(float)
        if kind == "High-pass":
            return (freq > edge).astype(float)
        if kind == "Band-pass":
            return ((freq >= interval[0]) & (freq <= interval[1])).astype(float)
        if kind == "Custom gains":
            return np.asarray(custom, dtype=float)
        return np.ones_like(freq)
    return amplitudes, components, filter_gains, frequencies, original, time


@app.cell
def _(
    amplitudes,
    band,
    components,
    cutoff,
    filter_gains,
    frequencies,
    gain1,
    gain10,
    gain30,
    keep1,
    keep10,
    keep30,
    mode,
):
    gains = filter_gains(
        mode.value, frequencies, cutoff.value, band.value,
        [gain1.value * keep1.value, gain10.value * keep10.value, gain30.value * keep30.value],
    )
    output_amplitudes = amplitudes * gains
    filtered_components = components * gains[:, None]
    output = filtered_components.sum(axis=0)
    power_ratio = (output_amplitudes @ output_amplitudes) / (amplitudes @ amplitudes)
    return gains, output, output_amplitudes, power_ratio


@app.cell(hide_code=True)
def _(
    amplitudes,
    band,
    cutoff,
    filter_gains,
    frequencies,
    gains,
    mo,
    mode,
    np,
    original,
    output,
    output_amplitudes,
    plt,
    time,
    zoom_output,
):
    _colors = ["#2563eb", "#d97706", "#a855f7"]
    _fig, _axes = plt.subplots(2, 2, figsize=(14, 7), layout="constrained")
    _input, _response, _result, _spectrum = _axes.flat
    _input.plot(time, original, color="#475569", lw=1.4)
    _input.set(title="1 · Original signal", xlabel="Time (s)", ylabel="Amplitude", xlim=(0, 2), ylim=(-2.5, 2.5))

    if mode.value != "Custom gains":
        _f = np.sort(np.unique(np.r_[np.linspace(-35, 35, 2801), cutoff.value, -cutoff.value, band.value, -np.asarray(band.value)]))
        _h = filter_gains(mode.value, np.abs(_f), cutoff.value, band.value, [])
        _response.step(_f, _h, where="mid", color="#94a3b8", lw=1.4)
    for _f0, _gain, _color in zip(np.r_[-frequencies[::-1], frequencies], np.r_[gains[::-1], gains], _colors[::-1] + _colors):
        _response.vlines(_f0, 0, _gain, color=_color, lw=3)
        _response.scatter([_f0], [_gain], color=_color, s=55, zorder=3)
        _response.annotate(f"{_gain:g}×", (_f0, _gain), xytext=(0, 9), textcoords="offset points", ha="center")
    _response.set(title="2 · Filter gain at each frequency", xlabel="Frequency (Hz)", ylabel="Gain", xlim=(-35, 35), ylim=(-0.12, 2.4), xticks=[-30, -10, 0, 10, 30])

    _result.plot(time, output, color="#0d9488", lw=1.5)
    _limit = max(0.05, float(np.max(np.abs(output))) * 1.15) if zoom_output.value else 2.5
    _result.set(title="3 · Reconstructed output" + (" (scale fitted)" if zoom_output.value else " (same scale as input)"), xlabel="Time (s)", ylabel="Amplitude", xlim=(0, 2), ylim=(-_limit, _limit))
    if not np.any(gains):
        _result.text(0.5, 0.85, "No components remain: y(t) = 0", transform=_result.transAxes, ha="center")
    _signed_frequencies = np.r_[-frequencies[::-1], frequencies]
    _input_coefficients = np.r_[amplitudes[::-1], amplitudes] / 2
    _output_coefficients = np.r_[output_amplitudes[::-1], output_amplitudes] / 2
    _bar_offset = 0.3 * np.sign(_signed_frequencies)
    _spectrum.bar(_signed_frequencies - _bar_offset, _input_coefficients, width=0.6, color="#cbd5e1", label="Input")
    _spectrum.bar(_signed_frequencies + _bar_offset, _output_coefficients, width=0.6, color=_colors[::-1] + _colors, label="Output")
    _spectrum.set(title="4 · Two-sided Fourier coefficients", xlabel="Frequency (Hz)", ylabel=r"Coefficient magnitude $|c_k|$", xlim=(-35, 35), xticks=[-30, -10, 0, 10, 30], ylim=(0, 1.15))
    _spectrum.legend(frameon=False)
    for _ax in _axes.flat:
        _ax.grid(axis="y", alpha=0.18)
        _ax.spines[["top", "right"]].set_visible(False)
        _ax.spines["left"].set_position("zero")
        _ax.spines["bottom"].set_position("zero")
        # Keep axis labels outside the data even when the spines cross inside it.
        _ax.xaxis.set_label_coords(0.5, -0.10)
        _ax.yaxis.set_label_coords(-0.08, 0.5)
    plt.close(_fig)
    mo.as_html(_fig)
    return


@app.cell(hide_code=True)
def _(frequencies, gains, mo, output_amplitudes, power_ratio):
    _terms = [
        rf"{_a:g}\cos(2\pi\cdot{_f:g}t)"
        for _f, _a in zip(frequencies, output_amplitudes) if _a > 0
    ]
    _equation = " + ".join(_terms) or "0"
    mo.md(rf"""
    $$y(t)={_equation}.$$

    **Components remaining:** {int((gains > 0).sum())} of 3 ·
    **Output / input average power:** {100 * power_ratio:.2f}%

    The bars show two-sided Fourier coefficient magnitudes, not power.
    Each cosine of amplitude $A$ contributes $A/2$ at each of $+f$ and $-f$.
    Average power is $P=\sum_k |c_k|^2$, summed over **both sides**, with no extra factor of 1/2.
    Custom gains above 1 can make the output power exceed the input power.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Try these three experiments
    1. **Keep the slow wave:** choose **Low-pass**, cutoff **5 Hz**.
       The ripples disappear and the 1 Hz cosine remains.
    2. **Keep only the ripples:** choose **High-pass**, cutoff **5 Hz**.
       Turn on **Fit output vertical scale** to inspect the smaller 10 Hz and 30 Hz waves.
    3. **Isolate one component:** choose **Band-pass**, bounds **5–15 Hz**.
       Then use **Custom gains** to remove, attenuate, or amplify individual components.

    ### Why this works
    For each component, $B_k=H(f_k)A_k$; reconstruct by adding
    $B_k\cos(2\pi f_k t)$. The ideal filters here have real, nonnegative gains,
    so the surviving components keep their original phase.

    This is an ideal Fourier-series component-selection demo, not a causal
    circuit simulation. The graphs show two periods of the signal. 

    The spectrum shows both positive and negative frequencies. The 1 Hz cosine
    contributes coefficients of 0.5 at ±1 Hz; the smaller cosines contribute
    0.05 at ±10 Hz and ±30 Hz. Each control changes both members of a pair.
    Filter cutoffs apply to $|f|$, so the response is symmetric about zero.
    """
    )
    return


if __name__ == "__main__":
    app.run()

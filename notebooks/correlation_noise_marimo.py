import marimo

__generated_with = "0.16.5"
app = marimo.App(width="full", app_title="Find a signal buried in noise")


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
    # Find a signal buried in noise
    A descending ramp pulse is hidden in a noisy recording. Slide a known
    template across the recording, multiply, and add: **correlation measures
    how strongly the signal matches at each location**.

    We add independent, zero-mean Gaussian noise to each sample:
    $x[n]=s[n]+\sigma z[n]$, where $z[n]\sim\mathcal{N}(0,1)$.


    **Try first:** move the template to where you think the pulse starts.
    Then reveal the correlation curve. Can it find a pulse you can barely see?
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    noise_level = mo.ui.slider(0, 4, step=0.1, value=1.5, label="Noise amplitude (RMS)", show_value=True)
    pulse_start = mo.ui.slider(0.5, 7, step=0.05, value=3.5, label="True pulse start (s)", show_value=True)
    pulse_width = mo.ui.slider(0.2, 2, step=0.05, value=1, label="Pulse duration (s)", show_value=True)
    template_shape = mo.ui.dropdown(["Descending ramp (matched)", "Ascending ramp", "Rectangle"], value="Descending ramp (matched)", label="Template shape")
    width_ratio = mo.ui.slider(0.5, 1.5, step=0.1, value=1, label="Template / pulse duration", show_value=True)
    scan = mo.ui.slider(0, 7, step=0.01, value=2, label="Slide template to (s)", show_value=True, full_width=True)
    reveal = mo.ui.checkbox(value=False, label="Reveal clean signal, correlation, and estimate")
    mo.vstack([
        noise_level,
        mo.hstack([pulse_start, pulse_width], wrap=True),
        mo.hstack([template_shape, width_ratio], wrap=True),
        scan, reveal,
        mo.md(r"""
        The slider sets $\sigma$, the noise standard deviation (its theoretical RMS).
        About 68% of noise values fall within $\pm\sigma$, and 95% within
        $\pm2\sigma$; occasional larger values are possible.

        At the default amplitude **1.5**, about 95% of noise values lie between
        **−3 and +3**, compared with the pulse's peak of **1**. Noise power is
        $\sigma^2$. Setting the amplitude to **0** removes the noise.
        The random pattern stays fixed: moving this slider scales the same noise
        so you can compare results. Samples are independent at 200 samples/s
        (discrete white noise); a finite recording's measured RMS can differ slightly.
        """),
    ])
    return (
        noise_level,
        pulse_start,
        pulse_width,
        reveal,
        scan,
        template_shape,
        width_ratio,
    )


@app.cell
def _(np):
    sample_rate = 200
    dt = 1 / sample_rate
    time = np.arange(2000) * dt

    def make_template(length, shape):
        fraction = np.arange(length) / length
        if shape == "Ascending ramp":
            return (np.arange(length) + 1) / length
        if shape == "Rectangle":
            return np.ones(length)
        return 1 - fraction

    def locate_pulse(recording, template):
        # Full-overlap placements only: no wraparound or partial-template edges.
        # Dividing by template energy makes a noise-free exact match score 1.
        return np.correlate(recording, template, mode="valid") / np.dot(template, template)
    return dt, locate_pulse, make_template, sample_rate, time


@app.cell
def _(
    dt,
    locate_pulse,
    make_template,
    noise_level,
    np,
    pulse_start,
    pulse_width,
    sample_rate,
    scan,
    template_shape,
    time,
    width_ratio,
):
    pulse_samples = int(round(pulse_width.value * sample_rate))
    start_index = int(round(pulse_start.value * sample_rate))
    clean = np.zeros_like(time)
    clean[start_index:start_index + pulse_samples] = make_template(pulse_samples, "Descending ramp (matched)")
    noise = np.random.default_rng(7).normal(size=len(time))
    recording = clean + noise_level.value * noise
    template_samples = int(round(pulse_samples * width_ratio.value))
    template = make_template(template_samples, template_shape.value)
    scores = locate_pulse(recording, template)
    clean_scores = locate_pulse(clean, template)
    lags = np.arange(len(scores)) * dt
    estimate_index = int(np.argmax(scores))
    estimate = lags[estimate_index]
    scan_index = int(round(scan.value * sample_rate))
    shifted = np.zeros_like(time)
    shifted[scan_index:scan_index + template_samples] = template
    product = recording * shifted
    return (
        clean,
        clean_scores,
        estimate,
        estimate_index,
        lags,
        product,
        recording,
        scan_index,
        scores,
        shifted,
    )


@app.cell(hide_code=True)
def _(
    clean,
    clean_scores,
    estimate,
    estimate_index,
    lags,
    mo,
    plt,
    product,
    recording,
    reveal,
    scan,
    scan_index,
    scores,
    shifted,
    time,
):
    _fig, _axes = plt.subplots(2, 2, figsize=(14, 7.5), layout="constrained")
    _signal, _template_ax, _product_ax, _corr = _axes.flat
    _signal.plot(time, recording, color="#64748b", lw=0.65, label="Noisy recording")
    if reveal.value:
        _signal.plot(time, clean, color="#2563eb", lw=2, label="Clean pulse")
    _signal.set(title="1 · Can you spot the pulse?", xlabel="Time (s)", ylabel="Amplitude", xlim=(0, 10))
    _signal.legend(loc="upper right", frameon=False)

    _template_ax.plot(time, shifted, color="#d97706", lw=2)
    _template_ax.axvline(scan.value, color="#d97706", ls="--", alpha=0.5)
    _template_ax.set(title=f"2 · Template placed at {scan.value:.2f} s", xlabel="Time (s)", ylabel="Template amplitude", xlim=(0, 10), ylim=(-0.15, 1.25))

    _product_ax.plot(time, product, color="#475569", lw=0.65)
    _product_ax.fill_between(time, 0, product, where=product >= 0, color="#0d9488", alpha=0.5, label="Positive contribution")
    _product_ax.fill_between(time, 0, product, where=product < 0, color="#e11d48", alpha=0.5, label="Negative contribution")
    _product_ax.set(title=f"3 · Multiply and sum: score = {scores[scan_index]:.3f}", xlabel="Time (s)", ylabel="Recording × template", xlim=(0, 10))
    _product_ax.legend(loc="upper right", frameon=False, fontsize=8)

    if reveal.value:
        _corr.plot(lags, scores, color="#0d9488", lw=1.5, label="Noisy recording")
        _corr.plot(lags, clean_scores, color="#2563eb", lw=1, ls="--", label="Noise-free reference")
        _corr.scatter([estimate], [scores[estimate_index]], color="#a855f7", zorder=4, label=f"Maximum: {estimate:.2f} s")
        _corr.scatter([scan.value], [scores[scan_index]], color="#d97706", zorder=4, label="Your template position")
        _corr.legend(loc="upper right", frameon=False, fontsize=8)
    else:
        _corr.text(0.5, 0.55, "Move the template and watch the score.\nThen check ‘Reveal’ to scan every location.", transform=_corr.transAxes, ha="center", va="center", color="#475569")
        _corr.set_ylim(-0.2, 1.4)
    _corr.set(title="4 · Correlation across all full-overlap placements", xlabel="Template start / lag (s)", ylabel="Correlation / template energy", xlim=(0, 10))
    for _ax in _axes.flat:
        _ax.grid(axis="y", alpha=0.18)
        _ax.spines[["top", "right"]].set_visible(False)
        _ax.spines["left"].set_position("zero")
        _ax.spines["bottom"].set_position("zero")
        _ax.xaxis.set_label_coords(0.5, -0.10)
        _ax.yaxis.set_label_coords(-0.09, 0.5)
    plt.close(_fig)
    mo.as_html(_fig)
    return


@app.cell(hide_code=True)
def _(
    estimate,
    mo,
    pulse_start,
    reveal,
    scan_index,
    scores,
    template_shape,
    width_ratio,
):
    if reveal.value:
        _note = "Matched shape and duration." if template_shape.value == "Descending ramp (matched)" and width_ratio.value == 1 else "Mismatched template: its peak can shift away from the true start."
        _summary = mo.md(f"**True start:** {pulse_start.value:.2f} s · **Estimated start:** {estimate:.2f} s · **Absolute error:** {abs(estimate - pulse_start.value):.3f} s\n\n{_note} Noise can shift the peak or cause a false match; the maximum is an estimate, not a guarantee.")
    else:
        _summary = mo.md(f"**Score at your template position:** {scores[scan_index]:.3f}. Try to make it larger, then reveal the result.")
    _summary
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Experiments
    1. **Find the hidden ramp.** Keep the matched template and reveal the result.
       Increase the noise amplitude until the estimate becomes unreliable.
    2. **Use the wrong shape.** Switch to an ascending ramp or rectangle. Does
       the peak still locate the start? Set noise to zero to isolate template mismatch.
    3. **Change duration.** With a matched template and duration ratio of 1,
       compare short and long pulses at the same noise level. A longer pulse
       collects more matching samples.

    ### What the score means
    Let $x[n]$ be the recording and $h[n]$ the real template starting at zero
    (zero outside its $M$ samples). **Moving the template right by $\ell$ samples
    gives $h[n-\ell]$**. The minus sign means a right shift.

    Ordinary cross-correlation adds the pointwise products:
    $$C[\ell]=\sum_n x[n]h[n-\ell].$$
    The demo divides this by the template's energy to normalize the score:
    $$E_h=\sum_{m=0}^{M-1}h[m]^2,\qquad
    \mathrm{score}[\ell]=\frac{C[\ell]}{E_h}.$$

    1. **Shift:** move the template right to the candidate start.
    2. **Multiply:** multiply each recording sample by the shifted template.
       Plot 3 shows these products; green contributions are positive and red are negative.
    3. **Add:** sum all those products to obtain $C[\ell]$.
    4. **Scale:** divide by $E_h$, the sum of squared template values.
       This denominator stays constant as you slide the template.

    **Why a perfect match scores 1:** when the recording segment equals the
    template, the numerator is $\sum h[m]^2=E_h$, so the score is $E_h/E_h=1$.
    A segment equal to $A h[m]$ scores $A$: twice the template's height scores 2.
    Noise perturbs this value. This is **not Pearson correlation** and the score
    is **not bounded by −1 and 1**. The largest score gives the estimated start.

    Independent, zero-mean noise tends to cancel in the sum; a matching pulse
    adds consistently. For noise standard deviation $\sigma$, the score's noise
    standard deviation at one placement is $\sigma/\sqrt{\sum_n h[n]^2}$.
    Scanning many locations still creates opportunities for false peaks. Try increasing noise RMS to see this effect.
    The 200 samples/s rate is fixed throughout this demo.
    """
    )
    return


if __name__ == "__main__":
    app.run()

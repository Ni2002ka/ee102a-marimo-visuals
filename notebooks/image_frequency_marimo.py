import marimo

__generated_with = "0.16.5"
app = marimo.App(width="full", app_title="An image in the frequency domain")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from PIL import Image
    from pathlib import Path
    from io import BytesIO
    import sys
    return BytesIO, Image, Path, mo, np, plt, sys


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # From organ pipes to spatial frequencies
    A photograph is a signal $I[y,x]$. Its Fourier transform describes **how quickly
    brightness changes across space**, measured in cycles per pixel—not sound frequency.

    Follow a row, inspect the 2D spectrum, then keep or remove frequencies and reconstruct the image.
    """
    )
    return


@app.cell
async def _(BytesIO, Image, Path, np, sys):
    if sys.platform == "emscripten":
        # The Pages workflow publishes shared assets beside notebook folders.
        from pyodide.http import pyfetch
        _response = await pyfetch("https://ni2002ka.github.io/ee102a-marimo-visuals/assets/organ_pipes.png")
        if not _response.ok:
            raise RuntimeError(f"Could not load the photograph: HTTP {_response.status}")
        _image_source = BytesIO(await _response.bytes())
    else:
        _image_source = Path(__file__).resolve().parent.parent / "assets/organ_pipes.png"
    original = Image.open(_image_source).convert("RGB")
    photo = original.crop((85, 46, 1425, 936)).resize((640, 424), Image.Resampling.LANCZOS)
    rgb = np.asarray(photo, dtype=float) / 255.0
    gray = rgb @ np.array([0.2126, 0.7152, 0.0722])
    height, width = gray.shape
    return gray, height, photo, width


@app.cell(hide_code=True)
def _(height, mo):
    _intro = mo.md("## 1 · Read the picture as a signal\nThe photograph is resized to 640 × 424 pixels and converted to grayscale using weighted RGB. Move the row down to the pipe mouths to see the signal change.")
    row = mo.ui.slider(0, height - 1, value=height // 3, step=1, label="Image row", show_value=True, full_width=True)
    mo.vstack([_intro, row])
    return (row,)


@app.cell
def _(gray, mo, np, photo, plt, row, width):
    _fig, _ax = plt.subplots(1, 3, figsize=(15, 3.8), layout="constrained")
    _ax[0].imshow(photo)
    _ax[0].axhline(row.value, color="#00c3bc", lw=2)
    _ax[0].set(title="Input Picture", xlabel="x (pixels)", ylabel="y (pixels)")
    _signal = gray[row.value]
    _ax[1].plot(_signal, color="#008b8b", lw=1)
    _ax[1].set(title=f"Intensity along row {row.value}", xlabel="x (pixels)", ylabel="Grayscale intensity", ylim=(0, 1))
    _amplitude = np.abs(np.fft.rfft(_signal - _signal.mean())) / width
    _ax[2].plot(np.fft.rfftfreq(width), _amplitude, color="#ab6500")
    _ax[2].set(title="Row spectrum (mean removed)", xlabel="Horizontal frequency (cycles/pixel)", ylabel="|FFT| / width", xlim=(0, .15))
    plt.close(_fig)
    mo.vstack([mo.as_html(_fig), mo.md("**Try:** compare an upper row with one near the bottom. More details lead to higher frequencies getting mixed in.")])
    return


@app.cell(hide_code=True)
def _(mo):
    _intro = mo.md(r"""
    ## 2 · Transform both dimensions
    $$F[v,u]=\sum_{y=0}^{H-1}\sum_{x=0}^{W-1} I[y,x]\,e^{-2\pi i(ux/W+vy/H)}.$$
    Each complex coefficient has **magnitude** (strength) and **phase** (alignment).
    `fftshift` moves zero frequency to the center; it does not change the transform's information.
    We display `log1p(abs(S))` so weaker components are visible.

    **Vertical pipes produce a horizontal band:** brightness varies strongly across x, but less along y.
    The central DC coefficient is the sum of all intensities. Opposite frequencies have equal magnitude
    because the image is real. Pipe mouths, shading, edges, and the crop boundaries add other components.
    """)
    remove_mean = mo.ui.checkbox(value=False, label="Remove mean brightness (DC)")
    zoom = mo.ui.slider(.025, .5, step=.025, value=.125, label="Spectrum half-width (cycles/pixel)", show_value=True)
    mo.vstack([_intro, mo.hstack([remove_mean, zoom], wrap=True)])
    return remove_mean, zoom


@app.cell
def _(gray, height, np, remove_mean, width):
    input_image = gray - gray.mean() if remove_mean.value else gray.copy()
    S = np.fft.fftshift(np.fft.fft2(input_image))
    fx = np.fft.fftshift(np.fft.fftfreq(width))
    fy = np.fft.fftshift(np.fft.fftfreq(height))
    magnitude = np.log1p(np.abs(S))
    return S, fx, fy, input_image, magnitude


@app.cell
def _(fx, fy, input_image, magnitude, mo, plt, zoom):
    _fig, _ax = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    _ax[0].imshow(input_image, cmap="gray")
    _ax[0].set(title="Input to the FFT (after selected preprocessing)", xlabel="x (pixels)", ylabel="y (pixels)")
    _dx, _dy = fx[1]-fx[0], fy[1]-fy[0]
    _extent = (fx[0]-_dx/2, fx[-1]+_dx/2, fy[-1]+_dy/2, fy[0]-_dy/2)
    _im = _ax[1].imshow(magnitude, cmap="magma", extent=_extent, interpolation="nearest")
    _ax[1].set(xlim=(-zoom.value, zoom.value), ylim=(zoom.value, -zoom.value), title="Centered 2D log-magnitude", xlabel="fx (cycles/pixel)", ylabel="fy (cycles/pixel)")
    _ax[1].plot(0, 0, '+', color='cyan', ms=10)
    _fig.colorbar(_im, ax=_ax[1], label="log(1 + |S|)")
    plt.close(_fig)
    mo.as_html(_fig)
    return


@app.cell(hide_code=True)
def _(mo):
    _intro = mo.md("## 3 · Keep frequencies and transform back\nStart with low-pass filtering and increase the cutoff: coarse shading becomes recognizable pipes, then sharp detail. Switch to high-pass to isolate fast changes. ‘All frequencies’ recovers the selected FFT input.")
    filter_mode = mo.ui.dropdown(["Low-pass", "High-pass", "All frequencies"], value="Low-pass", label="Filter")
    cutoff = mo.ui.slider(.005, .71, step=.005, value=.04, label="Radial cutoff (cycles/pixel)", show_value=True, full_width=True)
    mo.vstack([_intro, mo.hstack([filter_mode, cutoff], widths=[1, 3])])
    return cutoff, filter_mode


@app.cell
def _(S, cutoff, filter_mode, fx, fy, input_image, np):
    radius = np.hypot(fy[:, None], fx[None, :])
    mask = np.ones_like(radius, dtype=bool)
    if filter_mode.value == "Low-pass":
        mask = radius <= cutoff.value
    elif filter_mode.value == "High-pass":
        mask = radius > cutoff.value
    filtered = S * mask
    reconstruction = np.fft.ifft2(np.fft.ifftshift(filtered)).real
    retained_energy = np.sum(np.abs(filtered)**2) / np.sum(np.abs(S)**2)
    round_trip_error = np.max(np.abs(np.fft.ifft2(np.fft.ifftshift(S)).real - input_image))
    return mask, reconstruction, retained_energy, round_trip_error


@app.cell
def _(
    filter_mode,
    fx,
    fy,
    input_image,
    magnitude,
    mask,
    mo,
    np,
    plt,
    reconstruction,
    retained_energy,
    round_trip_error,
    zoom,
):
    _fig, _ax = plt.subplots(1, 3, figsize=(15, 4), layout="constrained")
    _ax[0].imshow(input_image, cmap="gray", vmin=0, vmax=1)
    _ax[0].set_title("FFT input (display clipped to 0–1)")
    # Align the FFT and mask at their exact frequency-bin centers.
    _dx, _dy = fx[1] - fx[0], fy[1] - fy[0]
    _extent = (fx[0] - _dx/2, fx[-1] + _dx/2, fy[-1] + _dy/2, fy[0] - _dy/2)
    _ax[1].imshow(magnitude, cmap="magma", extent=_extent, interpolation="nearest")
    # Transparent where kept; dim rejected bins without hiding their structure.
    _overlay = np.zeros((*mask.shape, 4))
    _overlay[..., 3] = (~mask) * 0.78
    _ax[1].imshow(_overlay, extent=_extent, interpolation="nearest")
    if mask.any() and not mask.all():
        _ax[1].contour(fx, fy, mask.astype(float), levels=[0.5], colors=["cyan"], linewidths=1)
    _ax[1].set(
        title="FFT + mask: dimmed = removed",
        xlabel="fx (cycles/pixel)", ylabel="fy (cycles/pixel)",
        xlim=(-zoom.value, zoom.value), ylim=(zoom.value, -zoom.value),
    )
    if filter_mode.value == "High-pass":
        _bound = max(float(np.abs(reconstruction).max()), 1e-12)
        _im = _ax[2].imshow(reconstruction, cmap="RdBu_r", vmin=-_bound, vmax=_bound)
        _fig.colorbar(_im, ax=_ax[2], label="Signed intensity")
        _ax[2].set_title("High-pass result (signed)")
    else:
        _ax[2].imshow(reconstruction, cmap="gray", vmin=0, vmax=1)
        _ax[2].set_title("Reconstruction (display clipped to 0–1)")
    for _axis in [_ax[0], _ax[2]]:
        _axis.set(xlabel="x (pixels)", ylabel="y (pixels)")
    plt.close(_fig)
    mo.vstack([mo.as_html(_fig), mo.md(f"**Spectral energy retained:** {retained_energy:.1%} · **Full FFT round-trip error:** {round_trip_error:.2e}\n\nReconstruction uses the **complex coefficients**, including phase—not the log-magnitude picture. Energy includes DC unless mean removal is selected. A sharp cutoff can create ringing near edges.")])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    **What to remember:** 
    * position in the spectrum encodes direction and rate of variation
    * magnitude encodes strength
    * phase locates those patterns in the image (positional shift)
    * The DFT assumes the image repeats at its boundaries; Removing the mean and windowing therefore change what we recover. 
    * To transform color, process each channel separately.

    Built with [marimo](https://docs.marimo.io/). The Python cells are editable in notebook mode.
    """
    )
    return


if __name__ == "__main__":
    app.run()

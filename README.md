# Visualizing concepts from EE102A using Marimo

Interactive demos for signals, images, and frequency-domain intuition.
Uses the same notebook-per-page GitHub Pages setup as [cvxpy-marimo-visuals](https://github.com/Ni2002ka/cvxpy-marimo-visuals).

## Demos

- [Find a signal buried in noise](https://ni2002ka.github.io/ee102a-marimo-visuals/correlation_noise_marimo/): slide a ramp template through a noisy recording, reveal its correlation peak, and explore noise, duration, and template mismatch.
- [Fourier filtering](https://ni2002ka.github.io/ee102a-marimo-visuals/fourier_filtering_marimo/): edit the gains of the handout's 1, 10, and 30 Hz components; compare low-pass, high-pass, band-pass, and custom filters with linked time and frequency plots.
- [Complex numbers](https://ni2002ka.github.io/ee102a-marimo-visuals/complex_numbers_marimo/): connect Cartesian and polar form, explore conjugation and arithmetic geometrically, and inspect every Nth root.
- [Image → frequency domain](https://ni2002ka.github.io/ee102a-marimo-visuals/image_frequency_marimo/): inspect an image row, explore its 2D FFT, overlay frequency masks, and reconstruct with low-pass or high-pass filters.
- [Laser altimetry from orbit](https://ni2002ka.github.io/ee102a-marimo-visuals/laser_altimeter_marimo/): connect circular-orbit mechanics, pulse time-of-flight, sampled terrain profiles, and equatorial versus polar ground coverage.
- [All demos](https://ni2002ka.github.io/ee102a-marimo-visuals/)

## Run locally

Using the existing conda environment:

```sh
conda run -n dev-test marimo edit notebooks/image_frequency_marimo.py
```

Or install the dependencies in your preferred Python environment:

```sh
python -m pip install -r requirements.txt
marimo edit notebooks/image_frequency_marimo.py
```

Use `marimo run` instead of `marimo edit` for the app view. The root-level `image_frequency_marimo.py` is a compatibility symlink to the same notebook.

Run the Fourier filtering playground:

```sh
conda run -n dev-test marimo run notebooks/fourier_filtering_marimo.py
```

## Publish a new demo

1. Add a marimo `.py` notebook to `notebooks/`.
2. Put shared images or other input files in `assets/`.
3. Push to `main`. GitHub Actions exports every notebook with `marimo export html-wasm`, regenerates the demo index, and deploys GitHub Pages.
4. Add the demo link to this README.

A notebook named `example.py` is served at `https://ni2002ka.github.io/ee102a-marimo-visuals/example/`.
Python runs in the visitor's browser via Pyodide. This demo requires no backend server. The first visit downloads the Python runtime and dependencies.

For browser-compatible file access, follow the image-loading cell: load the published `https://ni2002ka.github.io/ee102a-marimo-visuals/assets/<file>` URL asynchronously with `pyfetch` in Pyodide, and use a notebook-relative filesystem path locally. The workflow copies `assets/` into the published site. Use Pyodide-compatible dependencies.

# The paper

`main.tex` and the files it inputs are the source; `main.pdf` is the compiled paper. The text is
licensed CC BY 4.0.

## Rebuilding it

The figures are drawn from `figdata/*.csv`, which `make_figures.py` writes from the event logs in
`data/`. From the repo root:

```bash
python paper/make_figures.py
```

```bash
docker build -t agent-names-paper paper
```

```bash
docker run --rm -v "$PWD/paper:/work" -w /work agent-names-paper latexmk -pdf main.tex
```

The image is the official `texlive/texlive:latest-medium` plus the few packages it lacks
(see `Dockerfile`).

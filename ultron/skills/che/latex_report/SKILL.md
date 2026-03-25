---
name: LaTeX Report Generator
description: Generate professional LaTeX lab reports and technical documents for chemical engineering
---

# LaTeX Report Generator Skill

## Trigger Patterns
- "create lab report"
- "write LaTeX report"
- "generate technical document"
- "make PDF report"
- "format report"

## Steps
1. **Gather data** — Collect experimental data, calculations, and observations
2. **Select template** — Lab report, research paper, or technical memo
3. **Structure document** — Title, abstract, introduction, theory, procedure, results, discussion, conclusion
4. **Write LaTeX** — Use proper packages: `amsmath`, `graphicx`, `booktabs`, `siunitx`
5. **Add figures** — Use matplotlib/plotly to generate, embed via `\includegraphics`
6. **Add tables** — Use `booktabs` for professional formatting
7. **Compile** — Use GitHub Actions with `texlive-full` for compilation
8. **Store** — Upload PDF to Fast.io, send download link via Discord

## Example
```latex
\documentclass[12pt]{article}
\usepackage{amsmath,graphicx,booktabs,siunitx}
\title{Experiment 3: Vapor-Liquid Equilibrium of Ethanol-Water}
\author{Ghost — SVNIT Surat}
\begin{document}
\maketitle
\section{Objective}
To determine the VLE data for ethanol-water system at 1 atm.
\end{document}
```

## Common Pitfalls
- Missing packages in preamble causing compilation errors
- Not escaping special characters (%, &, #, _)
- Using bitmap images instead of vector (PDF/SVG)
- Incorrect `siunitx` formatting for engineering units

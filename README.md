# Viveka 2.0 – AI Club, CFI, IIT Madras

Application submission for the **Viveka 2.0** Project Member role at the AI Club, CFI, IIT Madras.

---

## Repository Structure

```
.
├── solution.py              # ARC-AGI puzzle solver (Problem 2.1)
├── sudoku_starter.py        # Baseline Sudoku transformer – autoregressive, 1D sinusoidal PE
├── sudoku_masked.py         # Sudoku transformer – masked / masked-iterative decoding
├── sudoku_positional.py     # Sudoku transformer – Sudoku-aware positional embeddings
└── data/
    ├── train/               # ARC-AGI JSON training tasks
    ├── test/                # ARC-AGI JSON test tasks
    └── sudoku.csv           # Kaggle Sudoku dataset (puzzle, solution columns)
```

---

## Problem 2.1 – ARC-AGI Puzzle Solver (`solution.py`)

A rule-based Python solver for two ARC-AGI task types. Takes JSON input in the standard ARC-AGI dataset format and outputs the predicted grid.

### How it works

The solver auto-detects which of the two problem types it's dealing with and routes accordingly.

**Type 1 – Repeating pattern reconstruction** (non-square grids)

The input is a tall or wide grid containing a repeating coloured pattern separated by delimiter rows/columns of 1s. The solver:
1. Splits the figure on delimiter rows/columns (`splitter`).
2. Extracts the base pattern, repetition count, shape colour, and background colour (`type1_scanner`).
3. Reconstructs the output by tiling the pattern the correct number of times (`type1_constructor`).
4. Handles both vertical and horizontal orientations via `transpose`.

**Type 2 – Shape completion inside green boxes** (square grids)

The input contains partially drawn coloured shapes and one or more green rectangular frames. The solver:
1. Detects checkerboard/alternating colour pairs and collapses them to a single colour for processing (`collapse_patterns` / `restore_patterns`).
2. Finds all green box components via flood-fill (`extract_shapes_and_boxes`).
3. Completes broken shape outlines by merging bounding boxes of same-colour components.
4. Overlays the completed shapes onto the grid and crops the interior of each green box as the output (`overlay_and_crop`, `fill_boxes_from_x`).
5. Restores the original alternating colour patterns in the output (`restore_patterns`).

### Usage

```
data/
  train/   ← ARC-AGI JSON files
  test/    ← ARC-AGI JSON files
```

Prints correctness on training examples and predictions for test cases.

---

## Problem 2.2 – Sudoku Transformer

Three training scripts experimenting with different decoding strategies and positional encodings for a transformer trained to solve Sudoku. All use the [Kaggle Sudoku dataset](https://www.kaggle.com/datasets/bryanpark/sudoku) (`data/sudoku.csv`) — 50,000 train / 10,000 validation puzzles (81-character strings).

### Shared architecture

- **Vocabulary:** 12 tokens — digits 1–9, blank (0), BOS (10), EOS (11)
- **Model:** `SudokuTransformer` with token embedding + positional encoding + transformer blocks + linear head
- **Training:** Adam optimizer, CrossEnttropyLoss, CosineAnnealingLR scheduler
- **Metrics:** Per-token accuracy on train and validation sets, best model saved to `results/`

---

### `sudoku_starter.py` — Baseline (Encoder-Decoder, Autoregressive)

Standard encoder-decoder transformer with 1D sinusoidal positional encoding and autoregressive decoding.

- **Decoding:** Left-to-right autoregressive (`generate_autoregressive`) starting from a BOS token.
- **Default config:** 8 layers, d_model=128, lr=5e-4, 100 epochs.
- **Output:** `results/depth_experiment_results.csv`

---

### `sudoku_masked.py` — Masked Decoding (Encoder-Only)

Replaces the encoder-decoder with a **TransformerEncoder only** (no decoder). Treats solving as a masked token prediction task — more natural for Sudoku since all positions are known upfront.

Two decoding modes (set via `METHOD`):

- `"masked"` — Single forward pass, predict all blanks at once (`generate_masked`).
- `"masked_iterative"` — Multiple forward passes; blanks are filled iteratively and re-fed into the model (`generate_masked_iterative`). More robust for hard puzzles.

- **Default config:** 8 layers, d_model=64, lr=1e-3, 50 epochs.
- **Output:** `results/masked_results.csv` or `results/masked_iterative_results.csv`

---

### `sudoku_positional.py` — Sudoku-Aware Positional Embeddings

Same encoder-decoder architecture as the baseline but replaces 1D sinusoidal PE with **`SudokuPositionalEmbedding`** — separate learned embeddings for row (0–8), column (0–8), and 3×3 box (0–8) indices for each of the 81 cells, summed together.

Hypothesis: encoding Sudoku's grid structure (rows, columns, boxes) directly into position representations should help the model learn constraints more easily than a flat 1D encoding.

Toggle via `USE_SUDOKU_POSITIONAL = True/False`.

- **Default config:** 8 layers, d_model=64, lr=1e-3, 50 epochs.
- **Output:** `results/sudoku_positional_results.csv` or `results/standard_positional_results.csv`

---

## Requirements

```bash
pip install torch pandas
```

GPU recommended (Kaggle P100 or equivalent). Reduce `batch_size` if you run out of memory.

---

## Results

All experiment results are saved as CSVs under `results/` with columns: layers, d_model, learning_rate, train_acc, val_acc, best_val_acc, loss, runtime_sec. Best model weights per experiment are saved as `.pth` files.

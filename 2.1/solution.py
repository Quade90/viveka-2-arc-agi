from collections import Counter
import json
import os

def splitter(fig, delimiter):
    """Splits fig into sections based on delimiter.
    Parameters:
    - fig: 2D list representing the figure to split
    - delimiter: represents the delimiter variable
    Returns:
    - List of lists, where each inner list represents a section of the figure
    """
    info = [[]]
    for item in fig:
        if item == delimiter:
            info.append([])
        else:
            info[-1].append(item)
    return info

def type1_scanner(fig):
    """Scans a figure of the first type to extract shape info.
    Parameters:
    - fig: 2D list representing the figure to scan
    Returns:
    - List of extracted shape information
    """
    delimiter = [1 for _ in range(len(fig[0]))]
    info = splitter(fig, delimiter)

    info[0] = info[0][1:-1]
    info[0] = [x[1:-1] for x in info[0]] # capture the repeating pattern

    info[1] = [sum(x) for x in info[1]] # number of repitions of the pattern
    info[1] = sum(info[1])//6

    info[2] = info[2][0][0] # colour of the shape

    info[3] = info[3][0][0] # background colour

    return info

def type1_constructor(info):
    """Constructs the output figure for the first type based on extracted info.
    Parameters:
    - info: List of extracted shape information
    Returns:
    - 2D list representing the constructed figure
    """
    shape_coloured = []
    for i in info[0]:
        row = [info[2] if x != 0 else info[3] for x in i]
        shape_coloured.append(row)

    shape = []
    for _ in range(info[1]):
        for k in shape_coloured:
            shape.append(k)
        sep = [info[3] for _ in range(len(info[0][0]))]
        shape.append(sep)

    shape.pop()

    return shape

def transpose(fig):
    """Transposes a 2D list (matrix).
    Parameters:
    - fig: 2D list to transpose
    Returns:
    - Transposed 2D list
    """
    return [list(row) for row in zip(*fig)]

def type2_construct(fig):
    """Constructs the output figure for the second type based on the input figure.
    Parameters:
    - fig: 2D list representing the input figure
    Returns:
    - 2D list representing the constructed figure
    - 2D list representing the original figure with shapes extracted
    """
    tp = transpose(fig)
    border = fig[0] + fig[-1] + tp[0] + tp[-1] # get border pixels
    bg = Counter(border).most_common(1)[0][0]

    shape_fig = [
        [None if cell == bg or cell == 3 else cell for cell in row]
        for row in fig
    ]

    result = [row[:] for row in shape_fig]

    rows = len(shape_fig)
    cols = len(shape_fig[0])

    visited = set()

    for r in range(rows):
        for c in range(cols):

            if shape_fig[r][c] is None or (r, c) in visited:
                continue

            component = []
            stack = [(r, c)]
            colour = shape_fig[r][c]

            if colour == 3:
                continue

            while stack:
                x, y = stack.pop()

                if (x, y) in visited:
                    continue

                if not (0 <= x < rows and 0 <= y < cols):
                    continue

                if shape_fig[x][y] != colour:
                    continue

                visited.add((x, y))
                component.append((x, y))

                stack.extend([
                    (x + 1, y),
                    (x - 1, y),
                    (x, y + 1),
                    (x, y - 1)
                ])

            # Bounding box of the shape 
            min_r = min(r for r, c in component)
            max_r = max(r for r, c in component)

            min_c = min(c for r, c in component)
            max_c = max(c for r, c in component)

            top_pattern = shape_fig[min_r][min_c:max_c + 1]

            stripe = []
            for x in top_pattern:
                if x is not None and x not in stripe:
                    stripe.append(x)

            if not stripe:
                continue
            
            # Reconstruct top and bottom borders
            for c in range(min_c, max_c + 1):
                colour = top_pattern[c - min_c]

                if colour is None:
                    colour = stripe[(c - min_c) % len(stripe)]

                result[min_r][c] = colour
                result[max_r][c] = colour

            # Reconstruct left and right borders
            for r2 in range(min_r, max_r + 1):
                colour = stripe[(r2 - min_r) % len(stripe)]

                result[r2][min_c] = colour
                result[r2][max_c] = colour

    return result, fig

def fill_boxes_from_x(shape_fig_complete, fig, green=3):
    """Fills the interiors of green boxes in the figure based on the most common non-green colour inside each box.
    Parameters:    
    - shape_fig_complete: 2D list representing the figure with completed shapes
    - fig: 2D list representing the original figure
    - green: The value representing the green colour (default is 3)
    Returns:    
    - 2D list representing the figure with filled green boxes
    """
    rows = len(fig)
    cols = len(fig[0])

    visited = set()
    
    # Find green boxes and fill them
    for r in range(rows):
        for c in range(cols):

            if fig[r][c] != green or (r, c) in visited:
                continue

            component = []
            stack = [(r, c)]

            # DFS to find all connected green pixels
            while stack:
                i, j = stack.pop()

                if (i, j) in visited:
                    continue

                if not (0 <= i < rows and 0 <= j < cols):
                    continue

                if fig[i][j] != green:
                    continue

                visited.add((i, j))
                component.append((i, j))

                stack.extend([
                    (i + 1, j),
                    (i - 1, j),
                    (i, j + 1),
                    (i, j - 1)
                ])

            min_r = min(r for r, c in component)
            max_r = max(r for r, c in component)

            min_c = min(c for r, c in component)
            max_c = max(c for r, c in component)

            h = max_r - min_r - 1
            w = max_c - min_c - 1

            # fill colour
            fill = None
            counts = Counter()

            for rr in range(min_r + 1, max_r):
                for cc in range(min_c + 1, max_c):
                    if fig[rr][cc] != green:
                        counts[fig[rr][cc]] += 1

            fill = counts.most_common(1)[0][0]

            output = [[fill for _ in range(w)] for _ in range(h)]

            # copy every non-background/non-green pixel
            for rr in range(rows):
                for cc in range(cols):
                    val = shape_fig_complete[rr][cc]

                    if val is None:
                        continue

                    if min_r < rr < max_r and min_c < cc < max_c:
                        output[rr - min_r - 1][cc - min_c - 1] = val

            return output

def extract_shapes_and_boxes(grid):
    """Extracts completed shapes and green boxes from the grid.
    Parameters:
    - grid: 2D list representing the figure to analyze
    Returns:
    - completed_shapes: List of completed shapes
    - green_boxes: List of green boxes
    """
    rows = len(grid)
    cols = len(grid[0])

    border = (
        grid[0] +
        grid[-1] +
        [row[0] for row in grid] +
        [row[-1] for row in grid]
    )

    bg = Counter(border).most_common(1)[0][0]

    visited = set()
    green_boxes = []

    # Find green boxes
    for r in range(rows):
        for c in range(cols):

            if grid[r][c] != 3 or (r, c) in visited:
                continue

            component = []
            stack = [(r, c)]

            while stack:
                x, y = stack.pop()

                if (x, y) in visited:
                    continue

                if not (0 <= x < rows and 0 <= y < cols):
                    continue

                if grid[x][y] != 3:
                    continue

                visited.add((x, y))
                component.append((x, y))

                stack.extend([
                    (x + 1, y),
                    (x - 1, y),
                    (x, y + 1),
                    (x, y - 1)
                ])

            min_r = min(r for r, c in component)
            max_r = max(r for r, c in component)
            min_c = min(c for r, c in component)
            max_c = max(c for r, c in component)

            inside = []

            for rr in range(min_r + 1, max_r):
                for cc in range(min_c + 1, max_c):
                    inside.append(grid[rr][cc])

            fill_colour = bg

            if inside:
                fill_colour = Counter(inside).most_common(1)[0][0]

            green_boxes.append({
                "bbox": (min_r, max_r, min_c, max_c),
                "fill_colour": fill_colour
            })

    # Remove green boxes and background
    work = [row[:] for row in grid]

    for r in range(rows):
        for c in range(cols):
            if work[r][c] == bg:
                work[r][c] = None

    for box in green_boxes:

        min_r, max_r, min_c, max_c = box["bbox"]

        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                work[r][c] = None

    # Find remaining components
    visited = set()
    completed_shapes = []

    for r in range(rows):
        for c in range(cols):

            if work[r][c] is None or (r, c) in visited:
                continue

            colour = work[r][c]

            component = []
            stack = [(r, c)]

            while stack:
                x, y = stack.pop()

                if (x, y) in visited:
                    continue

                if not (0 <= x < rows and 0 <= y < cols):
                    continue

                if work[x][y] != colour:
                    continue

                visited.add((x, y))
                component.append((x, y))

                stack.extend([
                    (x + 1, y),
                    (x - 1, y),
                    (x, y + 1),
                    (x, y - 1)
                ])

            min_r = min(r for r, c in component)
            max_r = max(r for r, c in component)
            min_c = min(c for r, c in component)
            max_c = max(c for r, c in component)

            completed_shapes.append({
                "colour": colour,
                "bbox": (min_r, max_r, min_c, max_c)
            })

    return completed_shapes, green_boxes

def overlay_and_crop(original_grid, completed_grid, green_boxes):
    """Overlays completed shapes onto the original grid and crops out the interiors of green boxes.
    Parameters:
    - original_grid: 2D list representing the original figure
    - completed_grid: 2D list representing the figure with completed shapes
    - green_boxes: List of green boxes
    Returns:
    - List of cropped regions
    """

    rows = len(original_grid)
    cols = len(original_grid[0])

    result = [row[:] for row in original_grid]

    # refill green boxes with their fill colour
    for box in green_boxes:

        min_r, max_r, min_c, max_c = box["bbox"]
        fill_colour = box["fill_colour"]

        for r in range(min_r + 1, max_r):
            for c in range(min_c + 1, max_c):
                result[r][c] = fill_colour

    # overlay completed shapes
    for r in range(rows):
        for c in range(cols):

            if completed_grid[r][c] is not None:
                result[r][c] = completed_grid[r][c]

    outputs = []

    # crop out interiors of green boxes
    for box in green_boxes:

        min_r, max_r, min_c, max_c = box["bbox"]

        crop = []

        for r in range(min_r + 1, max_r):
            crop.append(
                result[r][min_c + 1:max_c]
            )

        outputs.append(crop)

    return outputs

def collapse_patterns(grid):
    """Collapses pairs of colours that form a checkerboard pattern into a single colour.
    Parameters:
    - grid: 2D list representing the figure to analyze
    Returns:
    - new_grid: 2D list representing the figure with collapsed patterns
    - patterns: List of collapsed patterns
    """

    new_grid = [row[:] for row in grid]

    patterns = []

    colours = set()

    for row in grid:
        colours.update(row)

    # Check for pairs of colours that form an alternating pattern
    for a in colours:
        for b in colours:

            if a >= b:
                continue

            found = False

            for r in range(len(grid)):
                for c in range(len(grid[0])):

                    if grid[r][c] != a:
                        continue

                    for dr, dc in [(1,0),(0,1)]:

                        nr = r + dr
                        nc = c + dc

                        if (
                            0 <= nr < len(grid)
                            and
                            0 <= nc < len(grid[0])
                            and
                            grid[nr][nc] == b
                        ):
                            found = True

            if found:

                patterns.append((a,b))

                for r in range(len(grid)):
                    for c in range(len(grid[0])):

                        if new_grid[r][c] in (a,b):
                            new_grid[r][c] = a

    return new_grid, patterns

def restore_patterns(output, patterns):
    """Restores collapsed patterns in the output figure based on the original patterns.
    Parameters:
    - output: 2D list representing the figure with collapsed patterns
    - patterns: List of collapsed patterns
    Returns:
    - 2D list representing the figure with restored patterns
    """

    result = [row[:] for row in output]

    for info in patterns:

        base = info["base"]
        a, b = info["pattern"]

        positions = []

        for r in range(len(result)):
            for c in range(len(result[0])):

                if result[r][c] == base:
                    positions.append((r, c))

        if not positions:
            continue

        anchor_r, anchor_c = positions[0]

        for r, c in positions:

            parity = (
                abs(r - anchor_r)
                + abs(c - anchor_c)
            )

            result[r][c] = (a, b)[parity % 2]

    return result


def solve_grid(fig):
    """Solves the given figure by determining its type and applying the appropriate transformations.
    Parameters:
    - fig: 2D list representing the figure to solve
    Returns:
    - 2D list representing the solved figure
    """

    # Check for type 1 pattern
    if len(fig) != len(fig[0]):
        if len(fig) > len(fig[0]):
            return type1_constructor(type1_scanner(fig))
        else:
            return transpose(
                type1_constructor(
                    type1_scanner(
                        transpose(fig)
                    )
                )
            )

    collapsed_fig = [row[:] for row in fig]

    border = (
        fig[0]
        + fig[-1]
        + [row[0] for row in fig]
        + [row[-1] for row in fig]
    )

    bg = Counter(border).most_common(1)[0][0]

    patterns = []

    colours = set()

    for row in fig:
        colours.update(row)

    # Check for pairs of colours that form an alternating pattern
    for a in colours:

        if a == bg or a == 3:
            continue

        for b in colours:

            if b == bg or b == 3:
                continue

            if a >= b:
                continue

            count_a = sum(row.count(a) for row in fig)
            count_b = sum(row.count(b) for row in fig)

            if count_a < 3 or count_b < 3:
                continue

            adjacent = 0

            for r in range(len(fig)):
                for c in range(len(fig[0])):

                    if fig[r][c] != a:
                        continue

                    for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:

                        nr = r + dr
                        nc = c + dc

                        if (
                            0 <= nr < len(fig)
                            and 0 <= nc < len(fig[0])
                            and fig[nr][nc] == b
                        ):
                            adjacent += 1

            if adjacent >= 3:

                patterns.append({
                    "base": a,
                    "pattern": (a, b)
                })

                for r in range(len(fig)):
                    for c in range(len(fig[0])):

                        if collapsed_fig[r][c] == b:
                            collapsed_fig[r][c] = a

    shapes, green_boxes = extract_shapes_and_boxes(collapsed_fig)

    merged = {}

    # Merge bounding boxes of shapes with the same colour
    for shape in shapes:

        colour = shape["colour"]

        if colour not in merged:
            merged[colour] = list(shape["bbox"])
        else:

            min_r,max_r,min_c,max_c = merged[colour]

            a,b,c,d = shape["bbox"]

            merged[colour] = [
                min(min_r,a),
                max(max_r,b),
                min(min_c,c),
                max(max_c,d)
            ]

    completed_grid = [[None] * len(fig[0]) for _ in range(len(fig))]

    # Reconstruct shapes based on merged bounding boxes
    for colour, bbox in merged.items():

        min_r, max_r, min_c, max_c = bbox

        for c in range(min_c, max_c + 1):
            completed_grid[min_r][c] = colour
            completed_grid[max_r][c] = colour

        for r in range(min_r, max_r + 1):
            completed_grid[r][min_c] = colour
            completed_grid[r][max_c] = colour

    outputs = overlay_and_crop(
        collapsed_fig,
        completed_grid,
        green_boxes
    )

    for i in range(len(outputs)):
        outputs[i] = restore_patterns(
            outputs[i],
            patterns
        )

    return outputs[0]

# ==========================
# TRAIN
# ==========================

for filename in sorted(os.listdir("data/train")):

    if not filename.endswith(".json"):
        continue

    with open(os.path.join("data/train", filename), "r") as f:
        task = json.load(f)

    prediction = solve_grid(task["train"][0]["input"])

    if prediction == task["train"][0]["output"]:
        print(f"{filename}: Correct solution")
    else:
        print(f"{filename}: Incorrect solution")
        print(prediction)


# ==========================
# TEST
# ==========================

print("\n" + "=" * 60)
print("TEST SET PREDICTIONS")
print("=" * 60)

for filename in sorted(os.listdir("data/test")):

    if not filename.endswith(".json"):
        continue

    with open(os.path.join("data/test", filename), "r") as f:
        task = json.load(f)

    prediction = solve_grid(task["test"][0]["input"])

    print(f"\n{filename}")
    print(prediction)
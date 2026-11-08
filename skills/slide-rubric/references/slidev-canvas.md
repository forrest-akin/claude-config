# Slidev Canvas Dimensions

## Default Canvas

Slidev's default canvas is **980 × 551px** (16:9 at canvasWidth 980).

## Safe Areas for SVG Figures

After accounting for slide padding, layout chrome, and the slide title:

### Default Layout (full-width figure)
- **Usable width:** ~900px (40px padding each side)
- **Usable height after title:** ~370px (title takes ~80px, padding takes ~100px)
- **Recommended SVG viewBox:** `viewBox="0 0 850 350"`
- **Maximum SVG viewBox:** `viewBox="0 0 900 380"`

### Two-Column Layout (figure in one column)
- **Usable width per column:** ~420px
- **Usable height after title:** ~370px
- **Recommended SVG viewBox:** `viewBox="0 0 400 350"`

### Center Layout (full-width, no default padding assumptions)
- **Usable width:** ~900px
- **Usable height:** ~450px (no title expected, just content)
- **Recommended SVG viewBox:** `viewBox="0 0 850 420"`

### Full Layout (no padding at all)
- **Usable width:** 980px
- **Usable height:** 551px
- **Recommended SVG viewBox:** `viewBox="0 0 960 530"` (10px safety margin)

## Custom Canvas Sizes

If the user specifies a custom `canvasWidth` or `aspectRatio` in headmatter, recalculate:

```
usable_width = canvasWidth - 80   (40px padding each side)
usable_height = (canvasWidth / aspectRatio) - 180  (title + padding)
svg_viewBox_width = usable_width - 50  (safety margin)
svg_viewBox_height = usable_height - 20  (safety margin)
```

## Embedding Position

Center SVGs in the available space using a flex wrapper:

```html
<div class="flex justify-center items-center" style="margin-top: 1rem;">
  <svg viewBox="0 0 850 350" xmlns="http://www.w3.org/2000/svg">
    ...
  </svg>
</div>
```

The `margin-top: 1rem` provides breathing room below the slide title.

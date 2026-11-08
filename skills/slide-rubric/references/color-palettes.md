# Color Palettes

## Accessibility Rules

- **Minimum contrast ratio 4.5:1** for text on backgrounds. Every palette in `scripts/deck_constants.json` meets this.
- **Never use color alone** to convey meaning. Always pair color with a label, icon, or position.
- **Limit to 3 semantic colors per figure.** If a figure needs Primary, Accent, Danger, AND Success fills, it's communicating too many categories — simplify.

## Applying the Palette

When the user specifies colors (brand colors, theme colors, etc.), map them to the `default` palette's roles:

1. **Primary** → Their main brand color
2. **Accent** → Their secondary/CTA color
3. **Danger/Success** → Keep standard red/green unless they specify otherwise (these are universal)
4. **Neutral** → Derive from primary at 5-10% opacity, or use a light gray
5. **Text** → Calculate contrast: white text on fills darker than #808080, dark text on lighter fills
6. **Border** → Primary at 20% opacity, or a light neutral

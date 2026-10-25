# Color Palettes

## Choosing a Palette

Use ONE palette per presentation. If the user provides brand colors, build a custom palette following the same structure. If no preference is given, use the Default palette.

## Default Palette (Blue + Amber)

Clean, professional, high-contrast. Works on both light and dark slide backgrounds.

```
primary:       #2563EB   (blue — main elements, key concepts)
accent:        #F59E0B   (amber — highlighted/emphasized elements)
danger:        #EF4444   (red — negative, warning, anti-pattern)
success:       #10B981   (green — positive, correct, pro-pattern)
neutral_fill:  #F3F4F6   (light gray — background shapes, secondary)
text_on_dark:  #FFFFFF   (white — text inside Primary/Accent/Danger/Success)
text_on_light: #1F2937   (dark gray — text inside Neutral or standalone)
border:        #E5E7EB   (light border — shape outlines)
connector:     #6B7280   (medium gray — arrows and lines)
```

## Monochrome Palette (for minimal/elegant decks)

```
primary:       #1E293B   (slate-800)
secondary:     #475569   (slate-600)
tertiary:      #94A3B8   (slate-400)
neutral_fill:  #F1F5F9   (slate-100)
text_on_dark:  #FFFFFF
text_on_light: #1E293B
border:        #CBD5E1   (slate-300)
connector:     #64748B   (slate-500)
```

## Warm Palette (for creative/non-corporate decks)

```
primary:       #7C3AED   (violet)
accent:        #F97316   (orange)
danger:        #DC2626   (red-600)
success:       #059669   (emerald-600)
neutral_fill:  #FAF5FF   (violet-50)
text_on_dark:  #FFFFFF
text_on_light: #1F2937
border:        #E9D5FF   (violet-200)
connector:     #6B7280
```

## Accessibility Rules

- **Minimum contrast ratio 4.5:1** for text on backgrounds. All palettes above meet this.
- **Never use color alone** to convey meaning. Always pair color with a label, icon, or position.
- **Limit to 3 semantic colors per figure.** If a figure needs Primary, Accent, Danger, AND Success fills, it's communicating too many categories — simplify.

## Applying the Palette

When the user specifies colors (brand colors, theme colors, etc.), map them to the palette structure:

1. **Primary** → Their main brand color
2. **Accent** → Their secondary/CTA color
3. **Danger/Success** → Keep standard red/green unless they specify otherwise (these are universal)
4. **Neutral** → Derive from primary at 5-10% opacity, or use a light gray
5. **Text** → Calculate contrast: white text on fills darker than #808080, dark text on lighter fills
6. **Border** → Primary at 20% opacity, or a light neutral

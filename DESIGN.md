---
name: Field Intelligence
colors:
  surface: '#111413'
  surface-dim: '#111413'
  surface-bright: '#373a38'
  surface-container-lowest: '#0c0f0e'
  surface-container-low: '#191c1b'
  surface-container: '#1d201f'
  surface-container-high: '#272b29'
  surface-container-highest: '#323534'
  on-surface: '#e1e3e1'
  on-surface-variant: '#bdcabd'
  inverse-surface: '#e1e3e1'
  inverse-on-surface: '#2e3130'
  outline: '#889488'
  outline-variant: '#3e4a40'
  surface-tint: '#70dc96'
  primary: '#7ce8a1'
  on-primary: '#00391c'
  primary-container: '#5fcb87'
  on-primary-container: '#00532c'
  inverse-primary: '#006d3b'
  secondary: '#e4c369'
  on-secondary: '#3d2f00'
  secondary-container: '#6e5700'
  on-secondary-container: '#efce72'
  tertiary: '#d4d2cd'
  on-tertiary: '#31302d'
  tertiary-container: '#b8b6b2'
  on-tertiary-container: '#484744'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#8cf9b0'
  primary-fixed-dim: '#70dc96'
  on-primary-fixed: '#00210e'
  on-primary-fixed-variant: '#00522b'
  secondary-fixed: '#ffe08d'
  secondary-fixed-dim: '#e4c369'
  on-secondary-fixed: '#241a00'
  on-secondary-fixed-variant: '#584400'
  tertiary-fixed: '#e5e2dd'
  tertiary-fixed-dim: '#c8c6c2'
  on-tertiary-fixed: '#1c1c19'
  on-tertiary-fixed-variant: '#474743'
  background: '#111413'
  on-background: '#e1e3e1'
  surface-variant: '#323534'
typography:
  display-hero:
    fontFamily: Plus Jakarta Sans
    fontSize: 44px
    fontWeight: '600'
    lineHeight: 52px
    letterSpacing: -0.03em
  display-hero-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.06em
  label-sm:
    fontFamily: Inter
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.08em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2.5rem
  margin-mobile: 1.25rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style
The design system operates at the confluence of raw agronomic majesty and high-precision computational intelligence. Built for modern agricultural enterprises, autonomous field operators, and agronomists, the aesthetic bridges the tangible earth with ethereal data. It balances an authoritative, high-luxury editorial tone with functional, situational clarity.

The visual style merges tactile glassmorphism with minimalist computational architecture. Translucent, lens-grade mineral surfaces sit suspended over cinematic agronomic macro-views—evoking dawn mist, crystalline morning condensation, and stratified soil textures. High-contrast type choices and luminous, biologically resonant accents ensure urgent field data cuts through ambient outdoor conditions without aesthetic compromise.

## Colors
The palette is rooted in an obsidian-charcoal foundation infused with deep botanical undertones, avoiding standard flat grays or saturated monoculture greens:
- **Base Obsidian Layers**: `#080B0A` (canvas base), `#0E1210` (surface elevated), and `#141916` (surface overlay).
- **Mineral Ivory / Cream**: `#FAF7F2` and `#F4F1E8` provide high-contrast typographic hierarchy and stark, tactile editorial panels against the dark soils.
- **Living Emerald**: Primary accent `#5FCB87` (with active highlight `#82D9A0`) radiates life, active irrigation, and biological vitality.
- **Solar & Environmental Accents**: `#E7C66B` introduces dawn light, solar irradiance, and maturation states; `#F59E0B` handles transitional alerts; `#EF4444` is reserved strictly for operational failure and critical biosecurity threats.

## Typography
Typographic rules follow technical editorial rigor. Headlines rely on Plus Jakarta Sans for structural clarity and refined geometry, while Inter anchors computational telemetry, sensor reads, and deep analytical tables. Display treatments prioritize tight negative letter-spacing paired with generous line height to establish an airy, commanding reading cadence. Sub-labels and technical indicators employ uppercase transformations with wide tracking for legibility across vibration-heavy fieldwork environments.

## Layout & Spacing
The layout implements a 12-column fluid grid system across desktop viewports, condensing to 8 columns on tablet and 4 columns on mobile devices. Standardized outer margins isolate computational instruments from the boundary of the display, framing content like precise optical instrumentation. 

Spacing rhythm emphasizes breathing room around dense data clusters. Sensor matrices and micro-charts rely on tightly bound internal increments (`space-xs` and `space-sm`), while top-level structural panels use expansive margins (`space-xl`) to mirror the scale of wide-open terrain.

## Elevation & Depth
Depth is constructed using physical, optical metaphors rather than drop shadows:
- **Lens Layering**: Interfaces employ high-refraction glassmorphism with 20px to 40px backdrop blurs combined with semi-translucent base tones (`rgba(14, 18, 16, 0.75)`).
- **Edge Illumination**: Boundaries are defined not by harsh strokes, but by directional linear gradients (`1px solid rgba(255, 255, 255, 0.08)` to `rgba(95, 203, 135, 0.2)` on top-lit borders), emulating low-angle morning sunlight grazing an optical filter.
- **Ambient Chromatic Glow**: Elevated cards hovering over interactive satellite or drone feeds project an ultra-diffused, 48px blur colored to match the terrain state (e.g., `#5FCB87` at 6% opacity for healthy canopy tiers).

## Shapes
Geometry uses a controlled 0.5rem base radius (`roundedness: 2`), balancing natural curves with industrial precision:
- Primary panels, monitoring modules, and dashboard viewports utilize `rounded-lg` (1rem) for an organic, tactile enclosure.
- Micro-badges, telemetry pills, and status tags scale to fully rounded capsules to signify dynamic, live-state tracking.
- Interactive fields maintain rigid inner geometry with softer outer silhouettes to emphasize precision touch targets.

## Components
- **Buttons**: Primary actions use high-contrast Ivory (`#FAF7F2`) text over Obsidian with an active Living Emerald illuminated boundary, or solid `#5FCB87` with dark `#080B0A` labels for high-priority actions. Secondary actions use translucent mineral surfaces with 1px top-lit refraction borders.
- **Sensor & Telemetry Chips**: Capsule-shaped components housing live micro-metrics. They pair muted monochrome text with pulsing, glowing indicators (Emerald for optimal hydration, Solar Amber for heat stress, Carmine for soil nitrogen depletion).
- **Data Cards**: Floating glass modules with subtle backdrop blur, separated by hairline borders. Card headers feature high-contrast ivory titles with uppercase secondary metrics in tracking-expanded Inter.
- **Inputs & Field Controls**: Understated recessed obsidian troughs (`#080B0A`) with subtle inset borders. Focused states trigger an outer ambient Emerald aura (`0 0 0 1px #5FCB87`).
- **Selection Controls (Checkboxes & Radios)**: Precision geometric selectors with subtle 1px border framing. Active states fill with emerald and feature crisp mineral-ivory check vectors.
- **Soil & Canopy Spectrograms**: Specialized timeline and telemetry components that layer real-time spectral wave data over deep mineral backdrops, using agricultural gold and living emerald gradient fills.
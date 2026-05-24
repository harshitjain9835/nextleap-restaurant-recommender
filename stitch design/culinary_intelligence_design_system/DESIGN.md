---
name: Culinary Intelligence Design System
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#5b403f'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#5e5e5f'
  on-secondary: '#ffffff'
  secondary-container: '#e3e2e3'
  on-secondary-container: '#646465'
  tertiary: '#006a36'
  on-tertiary: '#ffffff'
  tertiary-container: '#008646'
  on-tertiary-container: '#f6fff4'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#e3e2e3'
  secondary-fixed-dim: '#c7c6c7'
  on-secondary-fixed: '#1a1c1d'
  on-secondary-fixed-variant: '#464748'
  tertiary-fixed: '#7cfca5'
  tertiary-fixed-dim: '#5ede8b'
  on-tertiary-fixed: '#00210d'
  on-tertiary-fixed-variant: '#005229'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 48px
  max-width: 1280px
---

## Brand & Style

The design system is engineered for an **AI-Powered Restaurant Recommendation Engine**, targeting food enthusiasts who value speed, precision, and visual appeal. The brand personality is **Knowledgeable, Vibrant, and Intuitive**, bridging the gap between high-tech data processing and the sensory pleasure of dining.

The design style is **Corporate / Modern** with a lean towards **Minimalism**. It prioritizes high-quality photography and AI-driven insights through a clean, systematic interface. We use expansive whitespace to let vibrant food imagery and red primary accents "pop," creating an appetizing and high-energy environment that feels more curated than traditional crowdsourced platforms.

## Colors

The palette is anchored by an **Appetizing Red**, chosen specifically to stimulate appetite and create urgency in the discovery process. 

- **Primary (#E23744):** Used for primary actions, AI-highlighted features, and critical branding elements.
- **Secondary (#2D2E2F):** A deep charcoal for high-contrast typography and iconography.
- **Tertiary (#05A357):** A "Safe Green" reserved specifically for positive AI match scores, open status indicators, and price-value highlights.
- **Surface (#F8F9FA):** A cool neutral for secondary background layers, card containers, and search inputs to maintain a crisp, hygienic feel.
- **Background (#FFFFFF):** The standard canvas to ensure maximum readability for AI-generated text.

## Typography

This design system utilizes **Inter** across all levels to maintain a systematic, utilitarian aesthetic that remains highly readable. 

The hierarchy is built on **Heavy Weights (700-800)** for headlines to create a strong editorial feel. **Body-lg** is the default for AI-generated restaurant descriptions to reduce eye strain and emphasize the "concierge" quality of the content. Labels use a slightly tracked-out, semi-bold style to differentiate metadata (like "Cuisine" or "Distance") from standard body copy.

## Layout & Spacing

The system follows a **Fluid Grid** model with a 12-column structure for desktop and a 4-column structure for mobile. 

- **Vertical Rhythm:** Built on an 8px baseline grid. Components like cards and list items should use increments of 8px (16, 24, 32) for internal padding.
- **Responsive Behavior:** On mobile, margins tighten to 16px to maximize real estate for imagery. On desktop, the content is capped at 1280px with a centered alignment and 48px margins.
- **Search-First Layout:** The search bar is always globally accessible, either pinned to the header or as a prominent hero element, utilizing a wider 24px gutter to feel expansive.

## Elevation & Depth

We utilize **Tonal Layers** combined with **Low-contrast Outlines** to create a modern, flat-but-layered look.

- **Level 0 (Background):** Pure #FFFFFF for main content areas.
- **Level 1 (Surfaces):** #F8F9FA used for secondary inputs, search bars, and filter chips.
- **Level 2 (Cards):** Use a 1px border of #E9ECEF. Shadows should be avoided for standard states.
- **Level 3 (Interactive/Hover):** Apply an **Ambient Shadow** (0px 8px 24px rgba(0,0,0,0.06)) to indicate lift and interactivity when a user hovers over a restaurant card or clicks a dropdown.

## Shapes

The design system employs **Rounded (0.5rem)** corners as the default for most elements to evoke a friendly, modern tech feel. 

- **Cards & Containers:** Use `rounded-lg` (1rem) to create a distinct frame for food photography.
- **Buttons & Chips:** Use `rounded-xl` or full pill-shapes for filter tags and primary CTAs to distinguish them from structural content.
- **Input Fields:** Use the standard 0.5rem roundedness to maintain a structured, professional appearance.

## Components

- **AI-Curated Badges:** Small, pill-shaped tags using the primary red background with white text. These should feature a "sparkle" icon to denote AI-generated insights.
- **Restaurant Cards:** High-quality imagery occupies the top 60% of the card. The bottom section includes the name in `headline-md`, a "Match Score" in tertiary green, and a condensed list of preference tags.
- **Search Bars:** Large, Level-1 surfaces with 16px internal padding and a prominent search icon. Use `body-lg` for placeholder text.
- **Filter Chips:** Pill-shaped buttons that toggle from #F8F9FA (inactive) to Primary Red (active). Use `label-md` for text.
- **Preference Sliders:** Custom sliders for price and distance, utilizing the Primary Red for the track and a high-contrast white handle with a Level 3 shadow.
- **Action Buttons:** Primary buttons are solid Primary Red. Secondary buttons use a Primary Red outline with transparent backgrounds. Both should be 48px height minimum for mobile accessibility.
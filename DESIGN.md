---
name: EvoFit AI
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#3d4a3d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#6d7b6c'
  outline-variant: '#bccbb9'
  surface-tint: '#006e2f'
  primary: '#006e2f'
  on-primary: '#ffffff'
  primary-container: '#22c55e'
  on-primary-container: '#004b1e'
  inverse-primary: '#4ae176'
  secondary: '#0058be'
  on-secondary: '#ffffff'
  secondary-container: '#2170e4'
  on-secondary-container: '#fefcff'
  tertiary: '#855300'
  on-tertiary: '#ffffff'
  tertiary-container: '#ef9900'
  on-tertiary-container: '#5c3800'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#6bff8f'
  primary-fixed-dim: '#4ae176'
  on-primary-fixed: '#002109'
  on-primary-fixed-variant: '#005321'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#004395'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
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
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  container-padding: 20px
  gutter: 16px
---

## Brand & Style

The design system is anchored in a **Modern Minimalist** aesthetic with a focus on high-performance health and clarity. It targets health-conscious individuals who value efficiency and data-driven insights. The UI should evoke a sense of vitality, precision, and calm encouragement.

By utilizing expansive whitespace and a refined "Startup-quality" finish, the interface avoids the cluttered feel of traditional fitness apps. The emotional response is one of "organized energy"—motivating the user to take action without overwhelming them with complexity. The visual language is clean, breathable, and premium, prioritizing content over decorative chrome.

## Colors

This design system utilizes a vibrant, nature-inspired palette to signal health and progress. 

- **Primary (Emerald Green):** Used for growth, completion states, and main action buttons. It represents vitality and "go" energy.
- **Secondary (Blue):** Employed for informational accents, data visualization, and secondary navigation elements.
- **Accent (Orange):** Reserved for high-attention alerts, metabolic spikes, or "burn" metrics to provide heat and contrast.
- **Background (Light Gray):** The foundation is #F8FAFC, providing a cool, soft canvas that reduces eye strain compared to pure white.
- **Semantic Colors:** Success (Primary), Warning (Orange), Info (Blue), and Error (Red #EF4444).

## Typography

The typography strategy balances character with utility. **Plus Jakarta Sans** (serving as a high-quality alternative to Poppins) provides a modern, geometric feel for headings and labels, offering excellent legibility and a friendly, rounded terminal. 

**Inter** is used for all body copy and technical data to ensure maximum readability at small sizes. 
- Use **SemiBold** for interactive labels and buttons to ensure they pass accessibility standards.
- Maintain generous line heights (1.5x for body) to keep the "spacious" brand promise.
- Data points (calories, weights, times) should use tabular num alignment where possible.

## Layout & Spacing

The layout follows a **Fluid Grid** model optimized for mobile-first interaction. 

- **The 8pt Grid:** All spacing between elements must be a multiple of 4px or 8px.
- **Safe Zones:** A standard horizontal padding of 20px (container-padding) is applied to all screens to ensure content doesn't hit the bezel.
- **One Action Rule:** Each screen should ideally feature one primary Floating Action Button (FAB) or a large fixed bottom button to minimize cognitive load.
- **Touch Targets:** All interactive elements must maintain a minimum 48x48px hit area.
- **Vertical Rhythm:** Use 32px (xl) or 48px (xxl) sections to separate logical groups of information, emphasizing the "spacious" feel.

## Elevation & Depth

This design system uses **Tonal Layers** and **Ambient Shadows** to create a soft, tactile hierarchy.

- **Level 0 (Background):** #F8FAFC. The lowest layer.
- **Level 1 (Cards):** Pure White (#FFFFFF). These use a very soft, diffused shadow (Y: 4px, Blur: 12px, Color: rgba(15, 23, 42, 0.05)) to appear lifted from the background.
- **Level 2 (Interactive/Modals):** These use a more pronounced shadow (Y: 8px, Blur: 24px, Color: rgba(15, 23, 42, 0.08)) to indicate they are temporary or require immediate focus.
- **Interactions:** On press, cards should visually "sink" by reducing shadow spread and scaling slightly (98%) to provide haptic-like visual feedback.

## Shapes

The shape language is consistently **Rounded**, reinforcing the approachable and friendly nature of the brand.

- **Cards:** 16px (rounded-lg) corner radius is the standard for all content containers.
- **Buttons:** Fully pill-shaped (rounded-full) or 12px (rounded-md) depending on context, though pill-shaped is preferred for primary actions to maximize the modern startup feel.
- **Inputs:** 12px corner radius to match the button language.
- **Icons:** Use rounded variants of iconography (e.g., Material Symbols Rounded) with a consistent 2px stroke weight.

## Components

- **Buttons:** 
  - *Primary:* Emerald Green background, White text, SemiBold. 
  - *Secondary:* Ghost style with 1px Blue border or Blue text.
- **Cards:** White background, 16px rounded corners, soft ambient shadow. Cards should never have borders; depth is strictly defined by shadows.
- **Chips/Badges:** Used for workout categories or nutrition tags. These use low-opacity versions of the brand colors (e.g., 10% Green background with 100% Green text).
- **Input Fields:** Large, 56px height for accessibility. Light gray fill (#F1F5F9) that transitions to a 2px Emerald Green border on focus.
- **Progress Bars:** Thick (8px), rounded caps. Use the Primary Emerald for completion and the Background Gray for the track.
- **Lists:** Clean rows with 16px vertical padding, separated by a subtle 1px divider (#F1F5F9) or simply by whitespace within a card.
- **Bottom Sheets:** Use for quick logging (e.g., adding water or a meal). 24px top corner radius, with a subtle drag handle at the top.
# Hermes Platform — Design System

## Brand & Identity

| Attribute | Value |
|-----------|-------|
| Name | Hermes |
| Tagline | Your agent, your way |
| Tone | Clean, capable, trustworthy |
| Audience | B2C — professionals, solopreneurs, small teams |

## Color Palette

```
Primary:        #6C5CE7  (Purple)     — Trust, creativity, premium
Primary Dark:   #5A4BD1  (Deep Purple)
Primary Light:  #A29BFE  (Soft Purple)

Secondary:      #00CEC9  (Teal)       — Action, growth, clarity
Secondary Dark: #00B5B0  (Deep Teal)
Secondary Light:#81ECEC  (Soft Teal)

Background:     #FAFBFC  (Off-white)
Surface:        #FFFFFF  (White)
Surface Alt:    #F1F3F5  (Light Gray)

Text Primary:   #1A1A2E  (Dark Navy)
Text Secondary: #636E72  (Medium Gray)
Text Muted:     #B2BEC3  (Light Gray)

Success:        #00B894  (Green)
Warning:        #FDCB6E  (Amber)
Error:          #E17055  (Coral)
Info:           #74B9FF  (Blue)

Gradient Hero:  linear-gradient(135deg, #6C5CE7 0%, #00CEC9 100%)
```

## Typography

```
Font Family:    Inter (headings) / system-ui (body)

Headings:       H1: 28px Bold
                H2: 22px Bold
                H3: 18px Semibold
                H4: 16px Semibold

Body:           15px Regular
Caption:        13px Regular
Small:          12px Regular

Button:         15px Semibold
```

## Spacing

```
Tiny:    4px
Small:   8px
Medium:  12px
Base:    16px
Large:   24px
XLarge:  32px
XXLarge: 48px

Content padding: 16px (mobile) / 24px (desktop)
```

## Components

### Cards
```
Border-radius: 16px
Shadow: 0 2px 8px rgba(0,0,0,0.06)
Background: White
Padding: 16px
```

### Buttons
```
Primary:   Purple bg, white text, 48px height, 12px padding x 24px, 12px radius
Secondary: White bg, purple text, 1px purple border, 48px height
Ghost:     Transparent, purple text
Danger:    Coral bg, white text
Small:     36px height, 10px padding x 16px, 8px radius
```

### Inputs
```
Height: 48px
Border: 1.5px solid #DFE6E9
Focus:  1.5px solid #6C5CE7
Radius: 12px
Padding: 0 16px
Label:  14px Semibold, 8px margin bottom
Error:  Border turns coral
```

### Bottom Navigation
```
Height: 64px
Background: White
Border-top: 1px solid #F1F3F5
Icons: 24px
Active: Purple
Inactive: #B2BEC3
Label: 11px
```

### Status Indicators
```
Online:  Green dot (8px)
Away:    Amber dot
Offline: Gray dot
Usage:   Linear progress bar, purple fill, 6px height, 12px radius
```

### Sheet / Modal
```
Background: White
Border-radius top: 20px
Drag handle: 32px x 4px gray bar at top
Padding: 16px
Backdrop: Black at 40% opacity
Animation: Slide up from bottom (mobile)
```

## Mobile-First Breakpoints

```
Mobile:  375-428px (primary target)
Tablet:  768px
Desktop: 1024px+
```

## Accessibility

```
Touch targets: min 44px
Contrast ratio: min 4.5:1 for text
Focus indicators: 2px purple outline + 4px offset

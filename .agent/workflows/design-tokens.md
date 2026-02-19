---
description: You are helping the user choose colors and typography for their PyQt application. These design tokens will be used consistently across all screen designs and the application shell.
---

# Design Tokens

You are helping the user choose colors and typography for their product. These design tokens will be used consistently across all screen designs and the application shell.

## Step 1: Check Prerequisites

First, verify that the product overview exists:

Read `/product/product-overview.md` to understand what the product is.

If it doesn't exist:

"Before defining your design system, you'll need to establish your product vision. Please run `/product-vision` first."

Stop here if the prerequisite is missing.

## Step 2: Explain the Process

"Let's define the visual identity for **[Product Name]**.

I'll help you choose:
1. **Colors** — A primary accent, secondary accent, and neutral palette
2. **Typography** — Fonts for headings, body text, and code

These will be applied consistently across all your PyQt screen designs.

Do you have any existing brand colors or fonts in mind, or would you like suggestions?"

Wait for their response.

## Step 3: Choose Colors

Help the user select a color palette. While we can use Tailwind names for communication, these will be converted to QT Stylesheet (QSS) variables.

"For colors, we can pick from standard palettes.

**Primary color** (main accent, buttons, active states):
Common choices: Blue, Indigo, Emerald, Teal, Amber, Rose

**Secondary color** (complementary accent, tags, highlights):
Should complement your primary — often a different hue or a neutral variation

**Neutral color** (backgrounds, text, borders):
Options: Gray, Slate, Zinc, Neutral

Based on [Product Name], I'd suggest:
- **Primary:** [suggestion] — [why it fits]
- **Secondary:** [suggestion] — [why it complements]
- **Neutral:** [suggestion] — [why it works]

What feels right for your product?"

Use AskUserQuestion to gather their preferences if they're unsure.

## Step 4: Choose Typography

Help the user select Fonts that are commonly available or easy to bundle.

"For typography, we should choose fonts that look good on desktop applications.

**Heading font** (titles, section headers):
Popular choices: Segoe UI (Windows standard), Roboto, Open Sans, Montserrat

**Body font** (paragraphs, UI text):
Often the same as heading, or: Segoe UI, Inter, Lato

**Mono font** (code, technical content):
Options: Consolas, Cascadia Code, JetBrains Mono, Fira Code

My suggestions for [Product Name]:
- **Heading:** [suggestion] — [why]
- **Body:** [suggestion] — [why]
- **Mono:** [suggestion] — [why]

What do you prefer?"

## Step 5: Present Final Choices

Once they've made decisions:

"Here's your design system:

**Colors:**
- Primary: `[color]`
- Secondary: `[color]`
- Neutral: `[color]`

**Typography:**
- Heading: [Font Name]
- Body: [Font Name]
- Mono: [Font Name]

Does this look good? Ready to save it?"

## Step 6: Create the Files

Once approved, create two files:

**File 1:** `/product/design-system/colors.json`
```json
{
  "primary": "[color hex or name]",
  "secondary": "[color hex or name]",
  "neutral": "[color hex or name]"
}
```

**File 2:** `/product/design-system/typography.json`
```json
{
  "heading": "[Font Name]",
  "body": "[Font Name]",
  "mono": "[Font Name]"
}
```

## Step 7: Confirm Completion

Let the user know:

"I've saved your design tokens:
- `/product/design-system/colors.json`
- `/product/design-system/typography.json`

**Your palette:**
- Primary: `[color]` — for buttons, links, key actions
- Secondary: `[color]` — for tags, highlights, secondary elements
- Neutral: `[color]` — for backgrounds, text, borders

**Your fonts:**
- [Heading Font] for headings
- [Body Font] for body text
- [Mono Font] for code

These will be used when generating the Stitch.ai prompt and creating PyQt screens.

Next step: Run `/design-shell` to design your application's navigation and layout."

## Important Notes

- Colors can be hex codes or standard names.
- Fonts should be standard system fonts or widely available fonts to ensure they render correctly in the desktop app.
- Design tokens apply to screen designs only.

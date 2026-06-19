{
  "brand": {
    "name": "HelixCortex Labs",
    "attributes": [
      "premium clinical SaaS",
      "scientific / molecular",
      "audit-ready + contestable AI",
      "mission-control clarity",
      "calm, high-trust, high-contrast"
    ],
    "visual_metaphors": [
      "glowing orbital orchestration diagram (center consensus)",
      "molecular dot patterns + helix dividers",
      "anatomical/kinematics overlays (vectors, ROM arcs)",
      "clinical documentation + audit trails"
    ]
  },

  "design_tokens": {
    "notes": [
      "No transparent backgrounds: all surfaces use solid tokens (background/card/popover).",
      "Gradients are decorative only and must stay under 20% viewport (hero/top header band).",
      "Tier colors must feel medical-grade (muted, not neon)."
    ],

    "css_custom_properties": {
      "apply_in": "/app/frontend/src/index.css (replace :root tokens)",
      "light": {
        "--background": "285 33% 98%",
        "--foreground": "255 22% 14%",

        "--card": "0 0% 100%",
        "--card-foreground": "255 22% 14%",

        "--popover": "0 0% 100%",
        "--popover-foreground": "255 22% 14%",

        "--primary": "258 41% 21%",
        "--primary-foreground": "285 33% 98%",

        "--secondary": "285 22% 94%",
        "--secondary-foreground": "258 41% 21%",

        "--muted": "285 18% 93%",
        "--muted-foreground": "255 10% 42%",

        "--accent": "43 44% 58%",
        "--accent-foreground": "258 41% 16%",

        "--destructive": "0 62% 46%",
        "--destructive-foreground": "0 0% 98%",

        "--border": "270 18% 86%",
        "--input": "270 18% 86%",
        "--ring": "43 44% 58%",

        "--chart-1": "258 41% 28%",
        "--chart-2": "43 44% 58%",
        "--chart-3": "196 38% 34%",
        "--chart-4": "142 33% 34%",
        "--chart-5": "28 55% 52%",

        "--radius": "0.75rem",

        "--hc-surface": "285 33% 98%",
        "--hc-surface-2": "285 22% 94%",
        "--hc-ink": "255 22% 14%",
        "--hc-ink-2": "255 10% 42%",
        "--hc-purple-900": "258 41% 21%",
        "--hc-purple-800": "258 44% 28%",
        "--hc-purple-700": "258 46% 34%",
        "--hc-gold": "43 44% 58%",
        "--hc-champagne": "38 36% 72%",

        "--tier-green": "152 33% 34%",
        "--tier-green-bg": "152 33% 94%",
        "--tier-yellow": "42 78% 45%",
        "--tier-yellow-bg": "44 80% 93%",
        "--tier-red": "0 62% 46%",
        "--tier-red-bg": "0 70% 95%",

        "--shadow-1": "0 10px 30px rgba(42,31,74,0.08)",
        "--shadow-2": "0 18px 50px rgba(42,31,74,0.12)",
        "--shadow-inset": "inset 0 1px 0 rgba(255,255,255,0.7)",

        "--focus-ring": "0 0 0 3px rgba(201,169,97,0.35)",
        "--noise-opacity": "0.06"
      },
      "dark_optional": {
        "note": "Only if a dark mode is later required; keep it solid (no gradients).",
        "--background": "258 41% 10%",
        "--foreground": "285 33% 98%",
        "--card": "258 41% 12%",
        "--card-foreground": "285 33% 98%",
        "--primary": "43 44% 58%",
        "--primary-foreground": "258 41% 12%",
        "--border": "258 25% 22%",
        "--ring": "43 44% 58%"
      }
    },

    "gradients_and_textures": {
      "allowed_usage": [
        "Top header band behind page title (max 120px height)",
        "Hero strip on /login only (max 20% viewport)",
        "Decorative orbital glow behind consensus gauge (blurred, non-interactive)"
      ],
      "gradient_recipes": [
        {
          "name": "lavender-cream-band",
          "css": "background: linear-gradient(135deg, #FAF7FB 0%, #F5F0F7 45%, #F2ECF6 100%);"
        },
        {
          "name": "orchid-orbit-glow (decorative overlay)",
          "css": "background: radial-gradient(closest-side, rgba(201,169,97,0.18), rgba(61,43,110,0.06) 55%, rgba(250,247,251,0) 70%);"
        }
      ],
      "noise_overlay": {
        "implementation": "Add a pseudo-element on main app shell: background-image: url(data:image/svg+xml,...noise) OR use CSS repeating-radial-gradient trick; keep opacity var(--noise-opacity).",
        "rule": "Noise must be subtle and never reduce text contrast."
      }
    },

    "spacing_scale": {
      "system": "Tailwind spacing + a few semantic aliases",
      "aliases": {
        "--space-1": "0.25rem",
        "--space-2": "0.5rem",
        "--space-3": "0.75rem",
        "--space-4": "1rem",
        "--space-6": "1.5rem",
        "--space-8": "2rem",
        "--space-10": "2.5rem",
        "--space-12": "3rem"
      },
      "layout_rules": [
        "Dashboard gutters: px-4 sm:px-6 lg:px-8",
        "Card padding: p-4 sm:p-5",
        "Dense tables: py-2.5 px-3 (but keep row height >= 44px for touch)"
      ]
    },

    "radius_and_elevation": {
      "radius": {
        "card": "rounded-xl",
        "button": "rounded-lg",
        "badge": "rounded-full",
        "input": "rounded-md"
      },
      "shadows": {
        "card_default": "shadow-[var(--shadow-1)]",
        "card_hover": "hover:shadow-[var(--shadow-2)]",
        "inset_highlight": "shadow-[var(--shadow-inset)]"
      }
    }
  },

  "typography": {
    "font_pairing": {
      "headings": {
        "google_font": "Fraunces",
        "fallback": "ui-serif, Georgia, Cambria, 'Times New Roman', Times, serif",
        "usage": "All page titles, section headers, agent names"
      },
      "body": {
        "google_font": "Manrope",
        "fallback": "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial",
        "usage": "Body, tables, forms, labels"
      },
      "mono": {
        "google_font": "IBM Plex Mono",
        "usage": "FHIR JSON preview, audit event IDs, hashes"
      }
    },
    "tailwind_application": {
      "note": "Add fonts via <link> in public/index.html or CSS @import; then set body font-family in index.css.",
      "classes": {
        "h1": "font-serif text-4xl sm:text-5xl lg:text-6xl tracking-[-0.02em]",
        "h2": "font-serif text-base md:text-lg text-[hsl(var(--muted-foreground))]",
        "section_title": "font-serif text-xl tracking-[-0.01em]",
        "kpi": "font-sans text-2xl font-semibold tabular-nums",
        "body": "font-sans text-sm sm:text-base leading-relaxed",
        "caption": "text-xs text-[hsl(var(--muted-foreground))]",
        "mono": "font-mono text-xs"
      }
    },
    "numerals": {
      "rule": "Use tabular-nums for σ², γ ratio, confidence %, ROM degrees, timestamps."
    }
  },

  "iconography": {
    "library": "lucide-react (preferred) + FontAwesome CDN if needed",
    "style": [
      "Use line icons, 1.5px–2px stroke",
      "Medical/scientific: Activity, Microscope, Atom, ShieldCheck, FileText, Scale, AlertTriangle",
      "Avoid emoji icons"
    ],
    "tier_icons": {
      "GREEN": "ShieldCheck",
      "YELLOW": "AlertTriangle",
      "RED": "Siren or AlertOctagon"
    }
  },

  "component_system": {
    "component_path": {
      "shadcn_primary": "/app/frontend/src/components/ui",
      "required_components": [
        "button.jsx",
        "card.jsx",
        "badge.jsx",
        "table.jsx",
        "tabs.jsx",
        "dialog.jsx",
        "sheet.jsx",
        "select.jsx",
        "input.jsx",
        "textarea.jsx",
        "form.jsx",
        "separator.jsx",
        "tooltip.jsx",
        "progress.jsx",
        "scroll-area.jsx",
        "calendar.jsx",
        "sonner.jsx"
      ]
    },

    "patterns": {
      "app_shell": {
        "layout": "Left rail (icon+label) + top header (page title + global search + role chip) + content",
        "classes": "min-h-screen bg-[hsl(var(--background))] text-[hsl(var(--foreground))]",
        "left_rail": {
          "classes": "w-64 shrink-0 border-r bg-[hsl(var(--card))]",
          "items": ["Dashboard", "Patients", "Memos", "FHIR", "Audit", "Education", "Me"],
          "micro": "Active item gets left gold bar (w-1) + subtle lavender background"
        },
        "top_header": {
          "classes": "sticky top-0 z-30 border-b bg-[hsl(var(--background))]",
          "band": "Optional 96–120px decorative band using lavender-cream-band gradient behind title only"
        }
      },

      "cards": {
        "base": "rounded-xl border bg-[hsl(var(--card))] shadow-[var(--shadow-1)]",
        "header": "flex items-start justify-between gap-3 p-4 sm:p-5",
        "content": "px-4 pb-4 sm:px-5 sm:pb-5",
        "hover": "transition-shadow duration-200 hover:shadow-[var(--shadow-2)]",
        "no_transition_all": true
      },

      "tier_badges": {
        "use": "badge.jsx",
        "variants": {
          "GREEN": {
            "classes": "bg-[hsl(var(--tier-green-bg))] text-[hsl(var(--tier-green))] border border-[hsl(var(--tier-green))]/20",
            "label": "GREEN — stable"
          },
          "YELLOW": {
            "classes": "bg-[hsl(var(--tier-yellow-bg))] text-[hsl(var(--tier-yellow))] border border-[hsl(var(--tier-yellow))]/25",
            "label": "YELLOW — monitor"
          },
          "RED": {
            "classes": "bg-[hsl(var(--tier-red-bg))] text-[hsl(var(--tier-red))] border border-[hsl(var(--tier-red))]/25",
            "label": "RED — urgent"
          }
        },
        "accessibility": "Always include text label + aria-label; never rely on color alone."
      },

      "agent_cards": {
        "structure": [
          "Header: agent name + confidence chip + last-run timestamp",
          "Body: top 3 findings (bulleted), key biomarkers/metrics, rationale excerpt",
          "Footer: actions (View trace, Compare, Add memo)"
        ],
        "accent": "Each agent gets a subtle left border strip: Chemical=gold, Physical=purple-700, Psychological=teal-muted",
        "classes": "relative overflow-hidden",
        "micro": "On hover: show 'View trace' ghost button; on focus: ring"
      },

      "consensus_variance_gauge": {
        "visual": "Orbital gauge: center value σ² with ring segments; outer orbit dots represent agents; variance animates between states",
        "implementation": {
          "library": "recharts (radial bar) OR custom SVG",
          "recommended": "Custom SVG for precise orbital look",
          "classes": "relative rounded-xl border bg-[hsl(var(--card))] p-4",
          "decorative_glow": "absolute inset-0 pointer-events-none bg-[radial-gradient(...)]"
        },
        "data_points": ["σ²", "θ_safe", "γ ratio", "consensus label"],
        "empty_state": "Show skeleton + 'Run assessment to compute consensus'"
      },

      "dynamic_alert_banner": {
        "placement": "Bottom-right quadrant header + sticky mini-banner at top of patient workspace",
        "content": ["I_alert tier", "reason codes", "recommended next action", "time since last update"],
        "motion": {
          "tier_change": "Animate background tint crossfade (200ms) + number count-up",
          "red_pulse": "Only RED: subtle box-shadow pulse every 2.4s; respect prefers-reduced-motion"
        }
      },

      "hitl_memo_cards": {
        "queue_card": {
          "layout": "Left: patient + tier badge; Middle: memo summary; Right: actions",
          "actions": ["Open", "Approve", "Contest", "Override"],
          "classes": "rounded-xl border bg-[hsl(var(--card))] p-4 hover:shadow-[var(--shadow-2)] transition-shadow duration-200"
        },
        "review_screen": {
          "two_panel": "Left: AI output + evidence; Right: clinician decision + rationale form",
          "decision_controls": "Use RadioGroup + Textarea + Button group",
          "audit_capture": "Decision requires rationale (min 20 chars)"
        }
      },

      "audit_log_table": {
        "use": "table.jsx + scroll-area.jsx",
        "rules": [
          "Sticky header row",
          "Zebra striping using muted background",
          "Right-align numeric columns",
          "Use mono for event_id, request_id"
        ],
        "row": {
          "left": "timestamp + actor",
          "middle": "action + entity",
          "right": "diff summary + integrity hash"
        }
      },

      "fhir_import_export": {
        "import": "Upload JSON -> validate -> show issues list (Alert component) -> preview (mono) -> import",
        "export": "Select patient/encounter -> generate bundle -> download",
        "validation_feedback": "Use Alert with severity + list of JSONPath errors"
      },

      "forms": {
        "use": "form.jsx + input.jsx + textarea.jsx + select.jsx + slider.jsx + calendar.jsx",
        "runner": "Assessment runner uses Tabs: Biomarkers / EMA / Kinematics / Review",
        "synthetic_demo": "Primary button with gold accent; confirm dialog"
      }
    }
  },

  "layout_and_grids": {
    "global": {
      "max_width": "2xl content for reading pages (education), full-width for dashboards",
      "grid": "Use CSS grid with 12 columns on lg; stack on mobile",
      "mobile_first": "All quadrants become vertical stack with sticky alert banner"
    },

    "patient_detail_workspace": {
      "desktop": {
        "grid": "grid grid-cols-1 lg:grid-cols-2 gap-6",
        "quadrants": {
          "top_left": "Chemical Agent",
          "top_right": "Physical Agent + 3D viewer",
          "bottom_left": "Psychological Agent",
          "bottom_right": "Negotiation + σ² gauge + I_alert banner"
        },
        "3d_viewer": {
          "chrome": [
            "Top bar: view presets (Sagittal/Coronal/Axial), playback, reset",
            "Right rail: ROM toggles, velocity vectors toggle, joint markers toggle",
            "Bottom: timeline scrubber"
          ],
          "classes": "rounded-xl border bg-[hsl(var(--card))] overflow-hidden"
        }
      },
      "mobile": {
        "order": ["I_alert banner", "Negotiation", "Physical+3D", "Chemical", "Psychological"],
        "3d": "Lazy-load; show poster skeleton until loaded"
      }
    }
  },

  "page_level_blueprints": {
    "dashboard_clinician": {
      "goal": "Scan alert tiers, prioritize memos, jump into patient workspace fast.",
      "layout": [
        "Top KPI strip (4 cards): Active Patients, RED queue, YELLOW queue, Pending memos",
        "Main split: Left (Patient list table) / Right (Alert queue + Memo queue tabs)",
        "Patient list: search + filters (tier, last updated, clinician)"
      ],
      "key_components": [
        "Card",
        "Table",
        "Tabs",
        "Badge (tier)",
        "Tooltip",
        "Sheet (patient quick view)"
      ],
      "data_testids": [
        "dashboard-kpi-active-patients",
        "dashboard-kpi-red-queue",
        "dashboard-patient-search-input",
        "dashboard-patient-table",
        "dashboard-alert-queue-tab",
        "dashboard-memo-queue-tab"
      ]
    },

    "patient_detail": {
      "goal": "Review multi-agent outputs, inspect kinematics, compute consensus, document decision.",
      "layout": [
        "Sticky patient header: name, MRN, tier badge, last assessment, actions (Run, Export FHIR, Add memo)",
        "Quadrant grid (2x2 on desktop)",
        "Assessment runner as Tabs inside a Sheet/Drawer to avoid leaving context"
      ],
      "key_components": [
        "Card",
        "Tabs",
        "Dialog (confirm run)",
        "Sheet/Drawer (assessment runner)",
        "Progress (compute)",
        "Tooltip"
      ],
      "data_testids": [
        "patient-header-tier-badge",
        "patient-run-assessment-button",
        "patient-export-fhir-button",
        "patient-add-memo-button",
        "patient-chemical-agent-card",
        "patient-physical-agent-card",
        "patient-psychological-agent-card",
        "patient-negotiation-card",
        "patient-kinematics-viewer"
      ]
    },

    "memo_review": {
      "goal": "Contest/approve/override with rationale; preserve audit trail.",
      "layout": [
        "Header: memo status + tier + timestamps",
        "Two-panel: Left (AI memo + evidence + trace snippets) Right (Decision form)",
        "Bottom: Audit timeline (append-only)"
      ],
      "decision_ctas": {
        "primary": "Approve",
        "secondary": "Contest",
        "destructive": "Override"
      },
      "key_components": [
        "Card",
        "RadioGroup",
        "Textarea",
        "Button",
        "Separator",
        "Table (audit timeline)"
      ],
      "data_testids": [
        "memo-review-approve-button",
        "memo-review-contest-button",
        "memo-review-override-button",
        "memo-review-rationale-textarea",
        "memo-review-audit-table"
      ]
    }
  },

  "motion_principles": {
    "library": "framer-motion (recommended for entrance + count-up)",
    "rules": [
      "No universal transition: only transition-shadow, transition-colors, transition-opacity",
      "Hover lift: translate-y-[-1px] only on cards/buttons (not on tables)",
      "Tier transitions: crossfade background tint + subtle ring glow",
      "RED pulse: box-shadow pulse only; disable with prefers-reduced-motion"
    ],
    "micro_interactions": {
      "buttons": "active:scale-[0.98] transition-transform duration-100",
      "inputs": "focus-visible ring using --focus-ring",
      "tables": "row hover uses muted background + left gold indicator"
    }
  },

  "3d_kinematics_viewer": {
    "library": "@react-three/fiber + drei",
    "performance": [
      "Lazy-load route chunk",
      "Use <Canvas frameloop='demand'> when paused",
      "Use simplified skeleton mesh + instanced joint markers"
    ],
    "ui_chrome": {
      "controls": [
        "View preset buttons",
        "Toggle joint markers",
        "Toggle velocity vectors",
        "ROM overlay slider",
        "Reset camera"
      ],
      "empty_state": "If no kinematics: show Card with skeleton placeholder + upload CTA"
    }
  },

  "accessibility": {
    "wcag": "AA",
    "rules": [
      "Tier badges must include text + icon + aria-label",
      "All controls keyboard reachable; visible focus ring",
      "Tables: use proper <th> headers; sortable columns announce sort",
      "Avoid color-only encoding for σ² risk; include labels"
    ]
  },

  "libraries_to_add": {
    "framer_motion": {
      "install": "npm i framer-motion",
      "use_cases": ["card entrance", "tier crossfade", "count-up numbers", "orbital gauge animation"]
    },
    "react_window": {
      "install": "npm i react-window",
      "use_cases": ["virtualize patient list when >50"]
    },
    "recharts_optional": {
      "install": "npm i recharts",
      "use_cases": ["backup for gauge if SVG too custom"]
    }
  },

  "image_urls": {
    "decorative_molecular_texture": [
      {
        "url": "https://images.pexels.com/photos/28886386/pexels-photo-28886386.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "usage": "Very subtle blurred background in /login header band or dashboard top band (opacity 0.06–0.1)"
      },
      {
        "url": "https://images.pexels.com/photos/11042723/pexels-photo-11042723.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "usage": "Optional texture for education module hero strip (keep under 20% viewport)"
      }
    ],
    "clinical_science_hero": [
      {
        "url": "https://images.unsplash.com/photo-1706478106657-1a8d73d82f29?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxOTB8MHwxfHNlYXJjaHwzfHxtZWRpY2FsJTIwbGFiJTIwbWljcm9zY29wZSUyMHB1cnBsZSUyMGdvbGR8ZW58MHx8fHB1cnBsZXwxNzgxODY3MTgyfDA&ixlib=rb-4.1.0&q=85",
        "usage": "Login side panel image (cropped, desaturated, overlay cream)"
      }
    ],
    "anatomy_reference": [
      {
        "url": "https://images.unsplash.com/photo-1658004041869-df5e54b82032?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2ODl8MHwxfHNlYXJjaHwxfHxhbmF0b215JTIwc2tlbGV0b24lMjB4cmF5JTIwcHVycGxlJTIwYmFja2dyb3VuZHxlbnwwfHx8cHVycGxlfDE3ODE4NjcxNzh8MA&ixlib=rb-4.1.0&q=85",
        "usage": "Education module illustration card background (very low opacity)"
      }
    ]
  },

  "instructions_to_main_agent": [
    "Replace /app/frontend/src/index.css :root tokens with the provided HSL values; keep shadcn structure.",
    "Remove CRA default App.css centering patterns; do not use .App { text-align:center }.",
    "Implement tier badges as a small wrapper component around shadcn Badge with explicit aria-label + icon.",
    "Build Patient Detail Workspace as a responsive 2x2 grid on lg and stacked on mobile; keep I_alert banner sticky.",
    "Lazy-load the 3D viewer route/component; show Skeleton while loading.",
    "Every interactive element and key info block must include data-testid in kebab-case.",
    "Use sonner for toasts (success/error on FHIR import/export, memo decisions, assessment run)."
  ],

  "general_ui_ux_design_guidelines_appendix": "<General UI UX Design Guidelines>  \n    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.\n</General UI UX Design Guidelines>"
}

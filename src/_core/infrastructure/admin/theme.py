"""Centralized theme + style system for the NiceGUI admin dashboard (#193).

Single source of truth for admin colors, **style tokens** (radius, shadow,
border treatment), layout metrics, and the helper CSS classes + Quasar
component overrides that every admin page inherits. Replaces the hardcoded
Quasar/Tailwind color classes and inline grid heights that were previously
scattered across the shell and domain pages.

Design (see plan #193 / Codex cross-review):

* The look is driven by CSS custom properties: ``--q-*`` (Quasar brand) and
  ``--admin-*`` (semantic + style) variables, declared under ``:root`` (light)
  and ``.body--dark`` (dark). Quasar's ``body--dark`` toggle flips the whole
  palette with no Python re-render, no reload, and no per-page ``ui.colors()``.
* Multiple **style presets** (``default``, ``linear``, ``shadcn``,
  ``supabase``) bundle a full set of color + style tokens, selected at boot via
  the ``ADMIN_THEME_PALETTE`` setting. The layout structure is identical across
  presets — only the tokens (and thus the CSS-var-driven component look) differ.
* The CSS is injected **once, app-wide** via ``ui.add_css(..., shared=True)`` so
  it reaches every page — including login / setup / error, which never call
  :func:`admin_layout`.
* AG Grid dark theming is **built in** to NiceGUI (a ``body--dark`` observer
  flips ``data-ag-theme-mode``); we only feed it ``--ag-*`` vars for row colors.

Constants here are intentionally **import-free** (no ``from nicegui``); the
nicegui + settings imports are lazy inside :func:`install_admin_theme_css` so
the constants and :func:`build_admin_css` stay testable when the ``admin``
extra is absent.
"""

from __future__ import annotations

from typing import Final

# Uniform empty / null cell rendering (replaces the bare "" used before).
EMPTY_DISPLAY: Final = "—"


class AdminColors:
    """Default brand palette — also the source of the ``default`` preset."""

    PRIMARY: Final = "#1d4ed8"
    SECONDARY: Final = "#475569"
    ACCENT: Final = "#0ea5e9"
    POSITIVE: Final = "#16a34a"
    NEGATIVE: Final = "#dc2626"
    WARNING: Final = "#d97706"
    INFO: Final = "#0284c7"


class AdminVars:
    """Names of the CSS custom properties consumed by the helper classes."""

    # Quasar brand variables (override Quasar's defaults app-wide).
    Q_PRIMARY: Final = "--q-primary"
    Q_SECONDARY: Final = "--q-secondary"
    Q_ACCENT: Final = "--q-accent"
    Q_POSITIVE: Final = "--q-positive"
    Q_NEGATIVE: Final = "--q-negative"
    Q_WARNING: Final = "--q-warning"
    Q_INFO: Final = "--q-info"

    # Semantic surfaces.
    BG: Final = "--admin-bg"
    SURFACE: Final = "--admin-surface"
    BORDER: Final = "--admin-border"
    TEXT_MUTED: Final = "--admin-text-muted"
    HEADER_BG: Final = "--admin-header-bg"
    HEADER_TEXT: Final = "--admin-header-text"
    DRAWER_BG: Final = "--admin-drawer-bg"
    NAV_ACTIVE: Final = "--admin-nav-active"
    SUCCESS_BG: Final = "--admin-success-bg"
    ROW_ALT: Final = "--admin-row-alt"
    ROW_HOVER: Final = "--admin-row-hover"

    # Style tokens (shape/elevation — theme-level, same in light + dark).
    RADIUS: Final = "--admin-radius"
    SHADOW: Final = "--admin-shadow"
    CARD_BORDER: Final = "--admin-card-border"

    # Layout metrics.
    GRID_HEIGHT: Final = "--admin-grid-height"
    GRID_HEIGHT_COMPACT: Final = "--admin-grid-height-compact"
    LABEL_COL_WIDTH: Final = "--admin-label-col-width"


class AdminMetrics:
    """Layout metrics (numbers, not colors)."""

    GRID_ROW_HEIGHT: Final = 44
    GRID_MIN_COL_WIDTH: Final = 120


class AdminClasses:
    """Helper CSS class names (all ``admin-`` prefixed for the AST guard)."""

    HEADER: Final = "admin-header"
    DRAWER: Final = "admin-drawer"
    NAV_ACTIVE: Final = "admin-nav-active"
    ACCENT_ICON: Final = "admin-accent-icon"
    CARD: Final = "admin-card"
    FIELD_LABEL: Final = "admin-field-label"
    FIELD_VALUE: Final = "admin-field-value"
    MUTED: Final = "admin-text-muted"
    EMPTY_VALUE: Final = "admin-empty-value"
    SUCCESS_SURFACE: Final = "admin-success-surface"
    GRID: Final = "admin-grid"
    GRID_COMPACT: Final = "admin-grid-compact"
    PAGINATION: Final = "admin-pagination"
    EMPTY_STATE: Final = "admin-empty-state"
    PRE: Final = "admin-pre"
    HIDDEN: Final = "admin-hidden"


# ── Style presets (#193) ──
#
# Each preset bundles "style" (shape/elevation, theme-level), "light" (:root
# colors) and "dark" (.body--dark colors). Layout metrics are shared. Selected
# at boot via ADMIN_THEME_PALETTE; unknown names fall back to DEFAULT_PALETTE.
DEFAULT_PALETTE: Final = "default"

_LAYOUT_TOKENS: Final = {
    AdminVars.GRID_HEIGHT: "calc(100vh - 240px)",
    AdminVars.GRID_HEIGHT_COMPACT: "calc(100vh - 360px)",
    AdminVars.LABEL_COL_WIDTH: "160px",
}

_PALETTES: Final = {
    # Classic blue — the original corporate look.
    "default": {
        "style": {
            AdminVars.RADIUS: "4px",
            AdminVars.SHADOW: "0 1px 4px rgba(0,0,0,0.12)",
            AdminVars.CARD_BORDER: "none",
        },
        "light": {
            AdminVars.Q_PRIMARY: AdminColors.PRIMARY,
            AdminVars.Q_SECONDARY: AdminColors.SECONDARY,
            AdminVars.Q_ACCENT: AdminColors.ACCENT,
            AdminVars.Q_POSITIVE: AdminColors.POSITIVE,
            AdminVars.Q_NEGATIVE: AdminColors.NEGATIVE,
            AdminVars.Q_WARNING: AdminColors.WARNING,
            AdminVars.Q_INFO: AdminColors.INFO,
            AdminVars.BG: "#f1f5f9",
            AdminVars.SURFACE: "#ffffff",
            AdminVars.BORDER: "#e2e8f0",
            AdminVars.TEXT_MUTED: "#64748b",
            AdminVars.HEADER_BG: AdminColors.PRIMARY,
            AdminVars.HEADER_TEXT: "#ffffff",
            AdminVars.DRAWER_BG: "#eff6ff",
            AdminVars.NAV_ACTIVE: "#1e40af",
            AdminVars.SUCCESS_BG: "#f0fdf4",
            AdminVars.ROW_ALT: "#f8fafc",
            AdminVars.ROW_HOVER: "#eef2ff",
        },
        "dark": {
            AdminVars.BG: "#0b1220",
            AdminVars.SURFACE: "#1e293b",
            AdminVars.BORDER: "#334155",
            AdminVars.TEXT_MUTED: "#94a3b8",
            AdminVars.HEADER_BG: "#1e293b",
            AdminVars.HEADER_TEXT: "#f1f5f9",
            AdminVars.DRAWER_BG: "#0f172a",
            AdminVars.NAV_ACTIVE: "#60a5fa",
            AdminVars.SUCCESS_BG: "#052e16",
            AdminVars.ROW_ALT: "#0f172a",
            AdminVars.ROW_HOVER: "#1e293b",
        },
    },
    # Linear / Vercel — minimal, flat, border-based, indigo accent, light header.
    "linear": {
        "style": {
            AdminVars.RADIUS: "6px",
            AdminVars.SHADOW: "none",
            AdminVars.CARD_BORDER: "1px solid var(--admin-border)",
        },
        "light": {
            AdminVars.Q_PRIMARY: "#5e6ad2",
            AdminVars.Q_SECONDARY: "#6b6f76",
            AdminVars.Q_ACCENT: "#5e6ad2",
            AdminVars.Q_POSITIVE: "#4cb782",
            AdminVars.Q_NEGATIVE: "#eb5757",
            AdminVars.Q_WARNING: "#d99e00",
            AdminVars.Q_INFO: "#4ea7fc",
            AdminVars.BG: "#fbfbfb",
            AdminVars.SURFACE: "#ffffff",
            AdminVars.BORDER: "#ebebed",
            AdminVars.TEXT_MUTED: "#8a8f98",
            AdminVars.HEADER_BG: "#ffffff",
            AdminVars.HEADER_TEXT: "#232529",
            AdminVars.DRAWER_BG: "#fbfbfb",
            AdminVars.NAV_ACTIVE: "#5e6ad2",
            AdminVars.SUCCESS_BG: "#edf7f2",
            AdminVars.ROW_ALT: "#fafafa",
            AdminVars.ROW_HOVER: "#f4f4f5",
        },
        "dark": {
            AdminVars.BG: "#0d0d0f",
            AdminVars.SURFACE: "#161618",
            AdminVars.BORDER: "#232326",
            AdminVars.TEXT_MUTED: "#8a8f98",
            AdminVars.HEADER_BG: "#0d0d0f",
            AdminVars.HEADER_TEXT: "#e6e6e8",
            AdminVars.DRAWER_BG: "#0d0d0f",
            AdminVars.NAV_ACTIVE: "#8b87ff",
            AdminVars.SUCCESS_BG: "#0f2a1f",
            AdminVars.ROW_ALT: "#161618",
            AdminVars.ROW_HOVER: "#1c1c1f",
        },
    },
    # shadcn / Notion — clean light, rounded, soft shadow, near-black primary.
    "shadcn": {
        "style": {
            AdminVars.RADIUS: "12px",
            AdminVars.SHADOW: "0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)",
            AdminVars.CARD_BORDER: "1px solid var(--admin-border)",
        },
        "light": {
            AdminVars.Q_PRIMARY: "#18181b",
            AdminVars.Q_SECONDARY: "#71717a",
            AdminVars.Q_ACCENT: "#6366f1",
            AdminVars.Q_POSITIVE: "#16a34a",
            AdminVars.Q_NEGATIVE: "#ef4444",
            AdminVars.Q_WARNING: "#f59e0b",
            AdminVars.Q_INFO: "#3b82f6",
            AdminVars.BG: "#fafafa",
            AdminVars.SURFACE: "#ffffff",
            AdminVars.BORDER: "#e4e4e7",
            AdminVars.TEXT_MUTED: "#71717a",
            AdminVars.HEADER_BG: "#ffffff",
            AdminVars.HEADER_TEXT: "#18181b",
            AdminVars.DRAWER_BG: "#fafafa",
            AdminVars.NAV_ACTIVE: "#18181b",
            AdminVars.SUCCESS_BG: "#f0fdf4",
            AdminVars.ROW_ALT: "#fafafa",
            AdminVars.ROW_HOVER: "#f4f4f5",
        },
        "dark": {
            AdminVars.BG: "#09090b",
            AdminVars.SURFACE: "#18181b",
            AdminVars.BORDER: "#27272a",
            AdminVars.TEXT_MUTED: "#a1a1aa",
            AdminVars.HEADER_BG: "#09090b",
            AdminVars.HEADER_TEXT: "#fafafa",
            AdminVars.DRAWER_BG: "#09090b",
            AdminVars.NAV_ACTIVE: "#fafafa",
            AdminVars.SUCCESS_BG: "#052e16",
            AdminVars.ROW_ALT: "#18181b",
            AdminVars.ROW_HOVER: "#27272a",
        },
    },
    # Supabase / Stripe — dark header, green accent, clean data tables.
    "supabase": {
        "style": {
            AdminVars.RADIUS: "8px",
            AdminVars.SHADOW: "0 1px 2px rgba(0,0,0,0.08)",
            AdminVars.CARD_BORDER: "1px solid var(--admin-border)",
        },
        "light": {
            AdminVars.Q_PRIMARY: "#3ecf8e",
            AdminVars.Q_SECONDARY: "#64748b",
            AdminVars.Q_ACCENT: "#3ecf8e",
            AdminVars.Q_POSITIVE: "#3ecf8e",
            AdminVars.Q_NEGATIVE: "#ef4444",
            AdminVars.Q_WARNING: "#f59e0b",
            AdminVars.Q_INFO: "#3b82f6",
            AdminVars.BG: "#f8f9fa",
            AdminVars.SURFACE: "#ffffff",
            AdminVars.BORDER: "#e6e8eb",
            AdminVars.TEXT_MUTED: "#6b7280",
            AdminVars.HEADER_BG: "#1c1c1c",
            AdminVars.HEADER_TEXT: "#ededed",
            AdminVars.DRAWER_BG: "#fbfcfd",
            AdminVars.NAV_ACTIVE: "#3ecf8e",
            AdminVars.SUCCESS_BG: "#ecfdf5",
            AdminVars.ROW_ALT: "#f8f9fa",
            AdminVars.ROW_HOVER: "#f0fdf8",
        },
        "dark": {
            AdminVars.BG: "#121212",
            AdminVars.SURFACE: "#1c1c1c",
            AdminVars.BORDER: "#2e2e2e",
            AdminVars.TEXT_MUTED: "#a0a0a0",
            AdminVars.HEADER_BG: "#121212",
            AdminVars.HEADER_TEXT: "#ededed",
            AdminVars.DRAWER_BG: "#1c1c1c",
            AdminVars.NAV_ACTIVE: "#3ecf8e",
            AdminVars.SUCCESS_BG: "#06281d",
            AdminVars.ROW_ALT: "#1c1c1c",
            AdminVars.ROW_HOVER: "#262626",
        },
    },
}

PALETTES: Final = tuple(_PALETTES)


# Palette-independent rules: helper classes + Quasar component overrides that
# read the tokens above. Plain string (literal class/var names) so there are no
# f-string brace-escaping hazards.
_HELPER_CSS: Final = """
/* === Helper classes + Quasar component overrides (token-driven) === */
body, .q-page-container {
  background-color: var(--admin-bg) !important;
}
.admin-header {
  background-color: var(--admin-header-bg) !important;
  color: var(--admin-header-text) !important;
  box-shadow: none !important;
  border-bottom: 1px solid var(--admin-border);
}
.admin-header .q-btn,
.admin-header .q-icon,
.admin-header .q-toolbar__title {
  color: var(--admin-header-text) !important;
}
.admin-drawer {
  background-color: var(--admin-drawer-bg) !important;
  border-right: 1px solid var(--admin-border);
}
.admin-nav-active {
  color: var(--admin-nav-active) !important;
  font-weight: 700;
}
.admin-accent-icon {
  color: var(--admin-nav-active) !important;
}
.admin-field-label {
  width: var(--admin-label-col-width);
  font-weight: 700;
}
.admin-text-muted,
.admin-empty-value {
  color: var(--admin-text-muted);
}
.admin-success-surface {
  background-color: var(--admin-success-bg) !important;
}
.admin-grid {
  width: 100%;
  height: var(--admin-grid-height);
}
.admin-grid-compact {
  width: 100%;
  height: var(--admin-grid-height-compact);
}
/* AG Grid (NiceGUI 3.x quartz theme) reads these CSS custom properties from the
   new theming API — set them on the grid element rather than overriding the
   legacy .ag-row-odd class (which the quartz theme no longer emits). */
.admin-grid,
.admin-grid-compact {
  --ag-odd-row-background-color: var(--admin-row-alt);
  --ag-row-hover-color: var(--admin-row-hover);
  --ag-border-radius: var(--admin-radius);
}
.admin-pagination {
  justify-content: flex-end;
}
.admin-empty-state {
  color: var(--admin-text-muted);
  align-items: center;
  text-align: center;
  padding: 48px 0;
}
.admin-pre {
  white-space: pre-wrap;
}
.admin-hidden {
  display: none;
}
/* Shape/elevation applied to standard Quasar components so every page inherits
   the preset look without per-page styling. */
.q-card {
  border-radius: var(--admin-radius) !important;
  box-shadow: var(--admin-shadow) !important;
  border: var(--admin-card-border) !important;
}
.q-btn {
  border-radius: var(--admin-radius);
}
.q-field--outlined .q-field__control,
.q-field__control {
  border-radius: var(--admin-radius);
}
"""


def _emit_vars(mapping: dict[str, str]) -> str:
    return "\n".join(f"  {name}: {value};" for name, value in mapping.items())


def build_admin_css(palette: str = DEFAULT_PALETTE) -> str:
    """Return the single CSS payload injected app-wide for the admin theme.

    Pure string builder (no nicegui import) so it is unit-testable without the
    ``admin`` extra. Emits ``:root`` (light) + ``.body--dark`` (dark) blocks for
    the selected preset, then the palette-independent helper/component CSS.
    Unknown palette names fall back to :data:`DEFAULT_PALETTE`.
    """
    name = palette if palette in _PALETTES else DEFAULT_PALETTE
    preset = _PALETTES[name]
    root_vars = {**preset["style"], **preset["light"], **_LAYOUT_TOKENS}
    return (
        f"/* === Admin theme (#193) — palette: {name} === */\n"
        ":root {\n" + _emit_vars(root_vars) + "\n}\n"
        ".body--dark {\n" + _emit_vars(preset["dark"]) + "\n}\n" + _HELPER_CSS
    )


_theme_css_installed = False


def install_admin_theme_css() -> None:
    """Inject the admin theme CSS app-wide (once per process).

    Calls ``ui.add_css(..., shared=True)`` so the stylesheet lands in every
    page's ``<head>`` — including login / setup / error which never render
    :func:`admin_layout`. Guarded so repeated ``bootstrap_admin()`` calls (test
    reloads) do not double-inject, mirroring the exception-handler guard in
    ``bootstrap.py``.
    """
    global _theme_css_installed
    if _theme_css_installed:
        return
    from nicegui import ui

    from src._core.config import settings

    ui.add_css(build_admin_css(settings.admin_theme_palette), shared=True)
    _theme_css_installed = True

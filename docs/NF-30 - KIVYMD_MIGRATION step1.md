# KivyMD Migration Guide

## Overview
This document tracks the migration of the TLUM (Teach Language Using Materials) application from Kivy to KivyMD (Material Design v3).

**Migration Status**: IN PROGRESS  
**Start Date**: May 8, 2026  
**Version Target**: KivyMD 0.104.2

---

## Completed Tasks ✓

### Phase 1: Setup & Core Configuration
- ✅ Added `kivymd==0.104.2` to requirements.txt
- ✅ Updated `src/main.py` to use `MDApp` instead of `App`
- ✅ Configured Material Design theme in `__init__`:
  - Primary palette: Blue
  - Accent palette: Cyan
  - Theme style: Light
- ✅ KivyMD installed in virtual environment

### Phase 2: Main Navigation Screen
- ✅ Updated `src/template/main_screen.kv` with MD components:
  - `BoxLayout` → `MDBoxLayout`
  - `TextInput` → `MDTextField` (rectangle mode)
  - `Button` → `MDRaisedButton` / `MDFlatButton`
  - `Label` → `MDLabel`
  - Added Material Design colors via `theme_cls`
  - Improved button sizing and spacing
  - Added breadcrumb navigation with MD buttons

### Phase 3: Dictionary Management Screen
- ✅ Updated `src/template/dictionary_management_screen.kv` with MD components:
  - `BoxLayout` → `MDBoxLayout`
  - `Button` → `MDRaisedButton` / `MDFlatButton`
  - `Label` → `MDLabel`
  - `VocabularyItemWidget` uses `MDBoxLayout` and `MDLabel`
  - Improved visual hierarchy with MD typography

---

## Remaining Tasks 🔄

### Screens Still Needing KivyMD Updates (12 remaining)

1. **src/template/card_screen.kv** - Card-based game screen
2. **src/template/articulation_screen.kv** - Audio-based game
3. **src/template/phonetics_screen.kv** - Phonetics practice
4. **src/template/structure_screen.kv** - Language structure
5. **src/template/store_update_screen.kv** - Store management
6. **src/template/structure_update_screen.kv** - Structure editing
7. **src/template/loading_screen.kv** - Loading screen
8. **src/template/language_screen.kv** - Language selection
9. **src/template/dictionary_screen.kv** - Dictionary view
10. **src/template/vocabulary_add_screen.kv** - Add vocabulary
11. **src/template/category_add_screen.kv** - Add category
12. **src/template/language_pair_add_screen.kv** - Add language pair

---

## KivyMD Component Mapping

### Layout Components
| Kivy | KivyMD | Notes |
|------|--------|-------|
| `BoxLayout` | `MDBoxLayout` | Use `md_bg_color` for background |
| `GridLayout` | `MDGridLayout` | Similar functionality |
| `ScrollView` | `MDScrollView` | Built-in scroll behavior |
| `StackLayout` | `MDStackLayout` | For dynamic layouts |

### Input Components
| Kivy | KivyMD | Notes |
|------|--------|-------|
| `TextInput` | `MDTextField` | Use `mode: "rectangle"` or `"line"` |
| `Button` | `MDRaisedButton` | Elevated button with shadow |
| `Button` | `MDFlatButton` | Flat button without elevation |
| `CheckBox` | `MDCheckbox` | Use `CheckBox` or `MDCheckbox` |
| `Spinner` | `MDDropDownItem` | Dropdown selection |

### Text & Display
| Kivy | KivyMD | Notes |
|------|--------|-------|
| `Label` | `MDLabel` | Use `font_style` for typography |
| `Text` properties | `font_style` | Options: "H1"-"H6", "Button", "Caption", etc. |

### List & Grid
| Kivy | KivyMD | Notes |
|------|--------|-------|
| `RecycleView` | `MDRecycleListItem` or `MDList` | For item-based lists |
| `ListItemWithCheckbox` | `MDListItemTrailingCheckbox` | Checked list items |

---

## Migration Pattern for Each Screen

### Step 1: Update KV Header
Add imports at the top:
```kivy
#:kivy 2.0
#:import MDApp kivymd.app.MDApp
#:import MDBoxLayout kivymd.uix.boxlayout.MDBoxLayout
#:import MDTextField kivymd.uix.textfield.MDTextField
#:import MDRaisedButton kivymd.uix.button.MDRaisedButton
#:import MDFlatButton kivymd.uix.button.MDFlatButton
#:import MDLabel kivymd.uix.label.MDLabel
```

### Step 2: Replace Layout Classes
- `BoxLayout` → `MDBoxLayout`
- Add `md_bg_color: app.theme_cls.bg_light` for backgrounds
- Use `adaptive_height: True` for auto-sizing

### Step 3: Replace Interactive Components
- `TextInput` → `MDTextField` with `mode: "rectangle"`
- `Button` → `MDRaisedButton` (for primary) or `MDFlatButton` (for secondary)
- `Label` → `MDLabel` with appropriate `font_style`

### Step 4: Apply MD Theming
- Use `app.theme_cls.primary_color`, `secondary_color`, etc.
- Apply consistent padding/spacing with `dp()` units
- Use Material Design elevation with shadows

### Step 5: Test
```bash
cd c:\Apps\Git\tlum
.\kivy_venv\Scripts\activate
python -c "from kivy.lang import Builder; Builder.load_file('src/template/screen_name.kv')"
```

---

## Theme Configuration Reference

### Available Theme Properties (in main.py `__init__`)
```python
# Primary color
self.theme_cls.primary_palette = "Blue"      # Color palette name
self.theme_cls.primary_hue = "500"           # Material Design hue

# Accent color  
self.theme_cls.accent_palette = "Cyan"
self.theme_cls.accent_hue = "500"

# Theme style
self.theme_cls.theme_style = "Light"         # or "Dark"

# Available colors in theme_cls
# .primary_color, .secondary_color, .accent_color
# .bg_light, .bg_dark
# .text_color, .divider_color
```

### Material Design Palettes
- Red, Pink, Purple, DeepPurple
- Indigo, Blue, LightBlue, Cyan
- Teal, Green, LightGreen, Lime
- Yellow, Amber, Orange, DeepOrange
- Brown, BlueGrey, Grey

---

## Python Component Updates

### Files That May Need Adjustments
1. **src/component/dictionary_management_screen.py** - ✅ Already updated for MD
2. **Other screen components** - May need MD-specific imports or property updates

### Key Import Changes
```python
# Old
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# New (if needed)
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
```

---

## Testing Checklist

After each screen update:
- [ ] KV file syntax valid
- [ ] All imports present
- [ ] Component type-consistency verified
- [ ] Theme colors applied correctly
- [ ] Navigation works
- [ ] Touch interactions responsive
- [ ] Mobile responsiveness (if applicable)

---

## Known Limitations & Considerations

1. **RecycleView Compatibility**: Some complex RecycleView patterns may need refactoring to use MD list items
2. **Custom Widgets**: Custom widget canvas operations may need adjustment for MD styling
3. **Icon Support**: KivyMD uses Material Design Icons - ensure icon font is available
4. **Mobile**: Test on actual mobile devices (Android/iOS) for responsive behavior
5. **Performance**: MD components may have different performance characteristics than basic Kivy

---

## Resources

- **KivyMD Documentation**: https://kivymd.readthedocs.io/en/latest/
- **Material Design Guidelines**: https://material.io/design
- **Kivy to KivyMD Migration**: Check KivyMD API docs for equivalents

---

## Next Steps

1. **Immediate**: Update remaining 12 KV files following the pattern above
2. **Short-term**: Test app functionality with all MD components
3. **Medium-term**: Refine theme colors and spacing for optimal UX
4. **Long-term**: Consider MD-specific features like Navigation Drawer, Bottom App Bar

---

**Last Updated**: May 8, 2026  
**Migration Lead**: GitHub Copilot  
**Status**: Phase 3 Complete - 14 screens total, 2 updated, 12 remaining

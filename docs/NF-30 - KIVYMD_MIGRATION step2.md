# KivyMD 1.1.1 Migration Guide

## Overview
This document tracks the migration of the TLUM (Teach Language Using Materials) application from Kivy to KivyMD (Material Design v3).

**Migration Status**: IN PROGRESS
**Latest Update**: May 8, 2026
**Version**: KivyMD 1.1.1 (Latest Material Design 3)

---

## Completed Tasks ✅

### Phase 1: Setup & Core Configuration
- ✅ Updated `requirements.txt` to `kivymd==1.1.1`
- ✅ Updated `src/main.py` to use `MDApp` instead of `App`
- ✅ Configured Material Design 3 theme in `__init__`:
  - Theme style: Light mode
  - Material style: M3 (Material Design 3)
  - Primary palette: Blue
- ✅ KivyMD 1.1.1 installed and tested

### Phase 2: Main Navigation Screen
- ✅ Updated `src/template/main_screen.kv` with MD 1.1.1 components:
  - `BoxLayout` → `MDBoxLayout`
  - `TextInput` → `MDTextField` with `mode: "rectangle"`
  - `Button` → `MDRaisedButton` / `MDFlatButton`
  - `Label` → `MDLabel` with Material Design typography
  - Optimized for KivyMD 1.1.1 API
  - All imports verified and working

### Phase 3: Dictionary Management Screen
- ✅ Updated `src/template/dictionary_management_screen.kv` with MD 1.1.1 components:
  - `BoxLayout` → `MDBoxLayout`
  - `Button` → `MDRaisedButton` / `MDFlatButton`
  - `Label` → `MDLabel`
  - `VocabularyItemWidget` uses `MDBoxLayout` and `MDLabel`
  - Removed unnecessary imports for KivyMD 1.1.1 compatibility

### Phase 4: Testing & Verification
- ✅ KV files load without errors
- ✅ Python files compile successfully
- ✅ KivyMD 1.1.1 (git-Unknown, 2026-05-08) confirmed installed

---

## KivyMD 1.1.1 Component Mapping

### Layout Components
| Kivy | KivyMD 1.1.1 | Notes |
|------|-------|-------|
| `BoxLayout` | `MDBoxLayout` | Full compatibility |
| `GridLayout` | `MDGridLayout` | Full compatibility |
| `ScrollView` | `MDScrollView` | Full compatibility |

### Input Components
| Kivy | KivyMD 1.1.1 | Notes |
|------|-------|-------|
| `TextInput` | `MDTextField` | Use `mode: "rectangle"` or `"line"` |
| `Button` | `MDRaisedButton` | Elevated button with shadow |
| `Button` | `MDFlatButton` | Flat button without elevation |
| `CheckBox` | `CheckBox` | Keep standard Kivy CheckBox |

### Text & Display
| Kivy | KivyMD 1.1.1 | Notes |
|------|-------|-------|
| `Label` | `MDLabel` | Use `font_style` for typography |
| `Text properties` | `font_style` | "H1"-"H6", "Button", "Caption", etc. |

---

## KivyMD 1.1.1 Theme Configuration

### Available Theme Properties
```python
# In MDApp.__init__()
self.theme_cls.theme_style = "Light"      # or "Dark"
self.theme_cls.material_style = "M3"      # Material Design 3
self.theme_cls.primary_palette = "Blue"   # Color palette
```

### Material Design 3 Palettes (1.1.1)
- Red, Pink, Purple, DeepPurple
- Indigo, Blue, LightBlue, Cyan
- Teal, Green, LightGreen, Lime
- Yellow, Amber, Orange, DeepOrange
- Brown, BlueGrey, Grey

---

## Migration Pattern for Remaining Screens

### Step 1: Update KV Header
```kivy
#:kivy 2.0
#:import MDBoxLayout kivymd.uix.boxlayout.MDBoxLayout
#:import MDTextField kivymd.uix.textfield.MDTextField
#:import MDRaisedButton kivymd.uix.button.MDRaisedButton
#:import MDFlatButton kivymd.uix.button.MDFlatButton
#:import MDLabel kivymd.uix.label.MDLabel
```

### Step 2: Replace Layout Classes
- `BoxLayout` → `MDBoxLayout`
- `GridLayout` → `MDGridLayout`
- Remove `md_bg_color` if not needed (KivyMD 1.1.1 handles defaults)

### Step 3: Replace Interactive Components
- `TextInput` → `MDTextField` with `mode: "rectangle"`
- `Button` → `MDRaisedButton` (primary) or `MDFlatButton` (secondary)
- `Label` → `MDLabel` with `font_style`

### Step 4: Test KV Syntax
```bash
python -c "from kivy.lang import Builder; Builder.load_file('src/template/SCREEN_NAME.kv')"
```

---

## Remaining Screens to Migrate (12 Total)

1. src/template/card_screen.kv
2. src/template/articulation_screen.kv
3. src/template/phonetics_screen.kv
4. src/template/structure_screen.kv
5. src/template/store_update_screen.kv
6. src/template/structure_update_screen.kv
7. src/template/loading_screen.kv
8. src/template/language_screen.kv
9. src/template/dictionary_screen.kv
10. src/template/vocabulary_add_screen.kv
11. src/template/category_add_screen.kv
12. src/template/language_pair_add_screen.kv

---

## Important Notes for KivyMD 1.1.1

### What Changed From 0.104.2
- Better Material Design 3 support
- Improved component API consistency
- `MDIcon` module removed (use `icon` property directly)
- Better theme handling with M3 style
- Enhanced typography system
- Improved performance and stability

### Compatibility Notes
- ✅ Full Kivy 2.3.0 compatibility
- ✅ Python 3.12.2 compatible
- ✅ Material Design 3 compliant
- ✅ Modern MD3 color system
- ⚠️ No custom icon module (use Kivy Image or MDIcon styling)

### Testing Checklist
After each screen update:
- [ ] KV file syntax valid (`Builder.load_file()` works)
- [ ] All MD imports present
- [ ] Component types correctly replaced
- [ ] Navigation works
- [ ] Touch interactions responsive
- [ ] Mobile responsiveness tested (if applicable)

---

## Project Statistics

**Total Screens**: 14
**Updated**: 2 ✅
**Remaining**: 12 🔄
**Completion**: 14%

**Updated Screens**:
- ✅ main_screen.kv (Navigation hub)
- ✅ dictionary_management_screen.kv (Vocabulary selection)

**Pending Screens**:
- 🔄 card_screen.kv - Card-based game
- 🔄 articulation_screen.kv - Audio game
- 🔄 phonetics_screen.kv - Phonetics practice
- 🔄 structure_screen.kv - Language structure
- 🔄 store_update_screen.kv - Store management
- 🔄 structure_update_screen.kv - Edit structures
- 🔄 loading_screen.kv - Loading UI
- 🔄 language_screen.kv - Language selection
- 🔄 dictionary_screen.kv - Dictionary view
- 🔄 vocabulary_add_screen.kv - Add words
- 🔄 category_add_screen.kv - Add category
- 🔄 language_pair_add_screen.kv - Add language pair

---

## Resources

- **KivyMD 1.1.1 Documentation**: https://kivymd.readthedocs.io/en/latest/
- **Material Design 3 Guidelines**: https://m3.material.io/
- **Kivy Documentation**: https://kivy.org/doc/stable/

---

## Next Steps

1. **Immediate**: Migrate remaining 12 KV screens
2. **Short-term**: Full application testing
3. **Medium-term**: Optimize theme colors and spacing
4. **Long-term**: Consider advanced MD3 features

---

**Last Updated**: May 8, 2026
**KivyMD Version**: 1.1.1
**Status**: 2/14 screens completed - Migration in progress

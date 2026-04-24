# Vocabulary Add Feature

## Overview
This document describes the new vocabulary add feature that allows users to add new words to the SQLite database directly from the application.

## Components Added

### 1. VocabularyAddScreen (`src/component/vocabulary_add_screen.py`)
- New screen component for adding vocabulary items
- Follows Clean Architecture with dependency injection
- Validates required fields (origin, translation)
- Uses the existing `save_vocabulary_items()` repository method

### 2. UI Template (`src/template/vocabulary_add_screen.kv`)
- Form-based interface with the following fields:
  - **Origin** (required): Source language word
  - **Translation** (required): Target language word
  - **Category** (optional): e.g., dictionary, verbs, numbers
  - **Difficulty Level** (optional): 0-10 scale
  - **Sound Path** (optional): Path to audio file
  - **Image Path** (optional): Path to image file
- Save and Cancel buttons with proper translations

### 3. Translations
Added `button_cancel` translations to all language files:
- EN: "Cancel"
- RU: "Отмена"
- BE: "Адмена"
- UK: "Скасувати"

### 4. Integration
- Added to main.py screen manager
- **Add button appears at category level** (after selecting a dictionary)
- Category is pre-filled automatically from selected dictionary
- Integrated with existing SQLite vocabulary repository
- New `add_vocabulary()` method in main_screen.py handles navigation with context

## Usage

1. Navigate to the main screen and select a language pair
2. **Select a dictionary/category** (e.g., "Verbs", "Dictionary", "Numbers")
3. Click the **"Add"** button next to the category (button appears after category selection)
4. The category field will be automatically pre-filled and locked
5. Fill in the required fields (Origin and Translation)
6. Optionally fill in additional fields (Difficulty, Sound, Image paths)
7. Click **"Save"** to add the vocabulary item to the selected category
8. Click **"Cancel"** to return without saving

## UX Improvements (v2)

**Category-Based Workflow:**
- The "Add" button now appears at the category level (not in the header)
- Users must select a dictionary/category before adding words
- Category is automatically pre-filled based on the selected dictionary
- Category field is read-only (displayed but not editable)
- This ensures all new words are properly categorized

**Button Layout:**
- Categories show: **Add (30%)** + **Select (30%)** buttons side-by-side
- Games show: **Play (40%)** button only
- Improved visual hierarchy and clearer user flow

## Technical Details

### Repository Integration
Uses `SQLiteVocabularyRepository.save_vocabulary_items()` with:
- `replace=False` to append new items without overwriting existing ones
- Current language pair from `app.locale_from` and `app.locale_to`

### Validation
- Origin and Translation are required fields
- Language pair must be selected (locale_from, locale_to)
- Form clears after successful save

### Error Handling
- Prints error messages for validation failures
- Catches and logs exceptions during save operations
- Displays stack traces for debugging

## Testing
All 68 existing tests pass with the new feature.

## Example Workflow:
```
1. Start app → Select "RU-PL" language pair
2. Navigate to category level → Select "Verbs" dictionary  
3. Click "Add" button (appears next to "Select" button)
4. Form opens with:
   - Category: "Глаголы" (pre-filled, read-only)
   - Origin: <enter> "бегать"
   - Translation: <enter> "biegać"
5. Click "Save"
6. New verb added to RU-PL Verbs category
```

## Future Enhancements
- Add file picker for sound/image paths
- Add category dropdown populated from database
- Add batch import functionality
- Add edit functionality for existing items
- Add delete functionality

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
- Added "Add" button to main screen header
- Integrated with existing SQLite vocabulary repository

## Usage

1. Navigate to the main screen
2. Click the "Add" button in the header
3. Fill in the required fields (Origin and Translation)
4. Optionally fill in additional fields
5. Click "Save" to add the vocabulary item to the database
6. Click "Cancel" to return without saving

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

## Future Enhancements
- Add file picker for sound/image paths
- Add category dropdown populated from database
- Add batch import functionality
- Add edit functionality for existing items
- Add delete functionality

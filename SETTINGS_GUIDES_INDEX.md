# InkyPi settings.html Template - Complete Reference Index

## What You Need

This search found InkyPi plugin settings.html examples and created three comprehensive guides for creating a settings template for the Netatmo Weather plugin.

## Three Reference Guides Created

### 1. SETTINGS_QUICK_CHECKLIST.md (Start here if you're in a hurry)
**File**: `/home/garrinmf/TheHubMedia/netatmopi/SETTINGS_QUICK_CHECKLIST.md`

Quick reference checklist for implementation:
- Minimal template structure
- Every field requirements (checklist)
- Field example template to copy
- Common field types with examples
- Prepopulation script template
- Settings flow explanation
- Recommended fields for Netatmo
- Testing checklist
- File locations

**Best for**: Getting started quickly, reference while coding

---

### 2. SETTINGS_TEMPLATE_GUIDE.md (Comprehensive guide)
**File**: `/home/garrinmf/TheHubMedia/netatmopi/SETTINGS_TEMPLATE_GUIDE.md`

Complete guide with explanations:
- Best example: Simple Settings Form
- Full HTML template example (ready to use)
- Key structural elements required
- How settings flow through plugin
- API key configuration pattern
- Common CSS classes
- Input types supported
- Directory structure
- Example Netatmo implementation
- Settings integration in generate_image()
- References to other files

**Best for**: Understanding the complete picture, learning the patterns

---

### 3. SETTINGS_HTML_EXAMPLES.md (Real examples)
**File**: `/home/garrinmf/TheHubMedia/netatmopi/SETTINGS_HTML_EXAMPLES.md`

Real code examples from InkyPi plugins:
- Example 1: Weather Plugin (complex - 100+ lines)
  - Location selection with map modal
  - Conditional display based on provider
  - Multiple checkboxes and dropdowns
  - Advanced JavaScript patterns

- Example 2: AI Text Plugin (simple - 30 lines)
  - 3 simple form fields
  - Basic prepopulation
  - Minimal JavaScript
  - Perfect learning example

- Key takeaways from real examples
- Recommended structure for Netatmo

**Best for**: Seeing working examples, pattern matching

---

## The One File You Need to Create

**Path**: `/home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin/settings.html`

This file contains the user configuration form for the Netatmo Weather plugin.

---

## Reference Files (Already exist in your repo)

**Plugin code** with generate_settings_template():
- `/home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin/netatmo_weather.py`
  - Line 352-382: Shows API key declaration pattern
  - Shows how settings are passed to generate_image()

**Integration documentation**:
- `/home/garrinmf/TheHubMedia/netatmopi/INKYPI_INTEGRATION_GUIDE.md`
  - Section 3: Settings Template (Optional)
  - Complete InkyPi integration explanation

- `/home/garrinmf/TheHubMedia/netatmopi/QUICK_REFERENCE.md`
  - Line 102-125: Settings Template section
  - Quick code examples

---

## Real Examples from InkyPi GitHub

These plugins are referenced in SETTINGS_HTML_EXAMPLES.md:

**Simple Example (Recommended for learning)**:
https://github.com/fatihak/InkyPi/blob/main/src/plugins/ai_text/settings.html
- 3 form fields
- Basic prepopulation script
- Easy to understand

**Complex Example (For advanced patterns)**:
https://github.com/fatihak/InkyPi/blob/main/src/plugins/weather/settings.html
- Interactive map modal with Leaflet.js
- Conditional display based on dropdown
- Multiple checkboxes
- Advanced JavaScript

---

## Quick Navigation Guide

**I want to...**

- **Get started immediately**
  -> Read: SETTINGS_QUICK_CHECKLIST.md
  -> Copy field template, customize with Netatmo fields

- **Understand how everything works**
  -> Read: SETTINGS_TEMPLATE_GUIDE.md
  -> Then: SETTINGS_HTML_EXAMPLES.md
  -> Review: generate_settings_template() in netatmo_weather.py

- **See working code examples**
  -> Read: SETTINGS_HTML_EXAMPLES.md
  -> Look at: InkyPi plugins on GitHub

- **Create a specific field type**
  -> Check: SETTINGS_QUICK_CHECKLIST.md "Common Field Types"
  -> See real examples: SETTINGS_HTML_EXAMPLES.md

---

## Key Concepts (TL;DR)

### Form Structure
Every input needs:
1. `<div class="form-group">` wrapper
2. `<label class="form-label">` with `for` attribute
3. Input with `id`, `name`, `class="form-input"`
4. Prepopulation in JavaScript

### The Magic: The `name` Attribute
The `name` attribute on form inputs becomes the key in the settings dictionary:
```html
<input name="units" value="metric">  <!-- From form -->
<!-- Becomes in Python: -->
units = settings.get('units', 'metric')  <!-- In generate_image() -->
```

### API Keys
- Declared in `generate_settings_template()` in Python
- InkyPi's base template renders the form automatically
- Do NOT add API key inputs to settings.html
- Your plugin already has 4 keys declared

### CSS Classes
Use only:
- `.form-group` - Container
- `.form-label` - Label text
- `.form-input` - Input styling
- `.btn` - Buttons

### Prepopulation
Always include this JavaScript pattern:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    if (typeof loadPluginSettings !== 'undefined' && loadPluginSettings) {
        document.getElementById('fieldId').value = pluginSettings.fieldId || 'default';
    }
});
```

---

## Files You Created

These are all stored in `/home/garrinmf/TheHubMedia/netatmopi/`:

1. `SETTINGS_TEMPLATE_GUIDE.md` (11 KB)
   - Comprehensive template guide
   - Full HTML example ready to use

2. `SETTINGS_HTML_EXAMPLES.md` (13 KB)
   - Real examples from InkyPi plugins
   - Simple and complex patterns

3. `SETTINGS_QUICK_CHECKLIST.md` (5.8 KB)
   - Quick reference for implementation
   - Checklists and templates

4. `SETTINGS_GUIDES_INDEX.md` (this file)
   - Navigation guide
   - Quick reference

---

## Recommended Reading Order

1. **First**: SETTINGS_QUICK_CHECKLIST.md (5 min)
   - Get the basic structure
   - See what goes into each field

2. **Second**: SETTINGS_HTML_EXAMPLES.md (10 min)
   - See real working code
   - Understand patterns used in real plugins

3. **Third**: SETTINGS_TEMPLATE_GUIDE.md (15 min)
   - Deep understanding of how everything connects
   - See the full flow from HTML form to Python code

4. **Reference**: This file (SETTINGS_GUIDES_INDEX.md)
   - Navigate between guides
   - Look up specific concepts

---

## Next Steps

1. Choose your starting point from the guides above
2. Read through the recommended structure
3. Create `/home/garrinmf/TheHubMedia/netatmopi/inkypi-netatmo-plugin/settings.html`
4. Include form fields that match your generate_settings_template() API keys
5. Update generate_image() to use settings values
6. Test prepopulation by editing the plugin instance

---

## Support

All guides include code examples you can copy and customize.

Key example locations:
- Simple form: SETTINGS_QUICK_CHECKLIST.md "Minimal Template Structure"
- Full form: SETTINGS_TEMPLATE_GUIDE.md "Best Example: Simple Settings Form"
- Real plugin: SETTINGS_HTML_EXAMPLES.md "Example 2: AI Text Plugin (Simple)"

---

Created: January 2, 2026
For: Netatmo Weather Plugin InkyPi Integration

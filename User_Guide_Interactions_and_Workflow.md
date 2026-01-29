# Citation Linker - User Guide: Interactions and Workflow

## Table of Contents

1. [Overview](#overview)
2. [Application Workflow](#application-workflow)
3. [Mouse Interactions](#mouse-interactions)
4. [Keyboard Shortcuts](#keyboard-shortcuts)
5. [Button Controls](#button-controls)
6. [Configuration Panel](#configuration-panel)
7. [PDF Viewer Navigation](#pdf-viewer-navigation)
8. [Text Selection and Citation Marking](#text-selection-and-citation-marking)
9. [Multi-Article Documents](#multi-article-documents)
10. [Output Document Management](#output-document-management)
11. [Complete Usage Example](#complete-usage-example)

---

## Overview

Citation Linker is a Qt-based application for creating hyperlinks between in-text citations and bibliography entries in PDF documents. It provides an interactive interface for marking citations, configuring document settings, and generating linked output PDFs.

---

## Application Workflow

### Step-by-Step Process

```
┌─────────────────────────────────────────────────────────────┐
│ 1. START APPLICATION                                        │
│    → Application opens with upload dialog                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. UPLOAD PDF FILE                                          │
│    → Click "upload file/path" button                        │
│    → Select your PDF document                               │
│    → File loads into viewer                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. CONFIGURE DOCUMENT (Optional but Recommended)            │
│    → Click "config" button                                  │
│    → Load existing config OR create new configuration       │
│    → Set bibliography delimiters                            │
│    → Define special cases (ibid, op. cit., etc.)           │
│    → Choose annotation type and color                       │
│    → Set article breaks (for multi-article documents)       │
│    → Configure search options                               │
│    → Save configuration for future use                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. MARK CITATIONS (Interactive Mode)                        │
│    → Click "viewer" to return to PDF                        │
│    → Navigate to bibliography section                       │
│    → Select bibliography header text (right-click →         │
│       "bibliography")                                        │
│    → Select special case phrases (right-click →             │
│       "special_case")                                        │
│    → Application learns from your selections                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. PROCESS DOCUMENT                                         │
│    → Click "start linking"                                  │
│    → Confirm dialog (check configuration)                   │
│    → Application processes citations automatically          │
│    → Creates links between citations and bibliography       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. REVIEW OUTPUT                                            │
│    → Application switches to output view automatically      │
│    → View processed PDF with clickable citation links       │
│    → Click citations to jump to bibliography entries        │
│    → Use split view to compare original and output          │
│    → Manually add/edit links if needed (right-click)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. SAVE RESULT                                              │
│    → Click "save file"                                      │
│    → Choose destination location                            │
│    → Linked PDF saved for distribution                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Mouse Interactions

### PDF Viewer - Left Click

| Action | Location | Result |
|--------|----------|--------|
| **Click + Drag** | Anywhere on PDF | Select text region (yellow highlight appears) |
| **Click existing link** | Output document | Navigate to linked bibliography entry |
| **Click button** | Navigation/zoom controls | Execute button action |

### PDF Viewer - Right Click

| Context | Action | Result |
|---------|--------|--------|
| **On selected text** (Input mode) | Right-click → popup menu | Shows "bibliography" or "special_case" options |
| **On selected text** (Output mode) | Right-click → popup menu | Shows "add_link" or "add_destination" options |
| **On existing annotation** | Right-click on underline/highlight | Shows "delete" option to remove annotation |
| **On existing link** | Right-click on linked text | Shows "delete" option to remove link |

**Popup Menu Buttons:**

**Input Mode (Original Document):**
- **bibliography**: Mark selected text as bibliography section delimiter
- **special_case**: Mark selected text as special citation phrase (ibid, etc.)

**Output Mode (Processed Document):**
- **add_link**: Create a link source from selected region
- **add_destination**: Set destination for previously created link source
- **delete**: Remove selected annotation or link

### Mouse Wheel Events

| Modifier | Scroll Direction | Action |
|----------|-----------------|--------|
| **None** | Wheel Up | Previous page |
| **None** | Wheel Down | Next page |
| **None** | Wheel Left | History back (previous viewed page) |
| **None** | Wheel Right | History forward (next viewed page) |
| **Ctrl** | Wheel Up | Zoom in (increase zoom level) |
| **Ctrl** | Wheel Down | Zoom out (decrease zoom level) |
| **Shift** | Wheel Up/Down | Default Qt behavior (smooth scroll within page) |

---

## Keyboard Shortcuts

### Navigation Keys

| Key | Action | Description |
|-----|--------|-------------|
| **↑** (Up Arrow) | Previous Page | Go to previous page in document |
| **↓** (Down Arrow) | Next Page | Go to next page in document |
| **←** (Left Arrow) | History Back | Return to previously viewed page |
| **→** (Right Arrow) | History Forward | Go forward in navigation history |
| **Space** | Select Page | Toggle page selection for article boundaries |

### Page Selection (Space Key) - Multi-Article Mode

The Space key has special behavior for defining article boundaries:

**First Press**: Mark current page as article start
```
Page 5 selected → "First page selected: 5"
```

**Second Press (same page)**: Cancel selection
```
Page 5 selected again → "Clearing selection for page 5"
```

**Second Press (later page)**: Create article range
```
First: Page 5 → Second: Page 23 → "Article saved: pages 5 to 23"
```

**Press on existing boundary**: Remove article boundary
```
"you are on page 5 which is part of {first: 5, last: 23}" → removes boundary
```

### Navigation Control Keys

| Context | Key | Action |
|---------|-----|--------|
| Page input field | **Enter** | Jump to entered page number |
| Zoom selector | **Enter** | Apply custom zoom percentage |
| Any field | **Esc** | Cancel operation / close popup |

---

## Button Controls

### Main Window Buttons (Top Bar)

| Button | State | Action | When Visible |
|--------|-------|--------|--------------|
| **config** | Toggle button | Switch between viewer and configuration panel | After file upload |
| **start linking** | Action button | Begin citation linking process | After file upload |
| **output document** / **input document** | Toggle button | Switch between original and processed PDF views | After linking complete |
| **save file** | Action button | Save processed PDF to chosen location | After linking complete |
| **🗙** (Exit) | Action button | Close application | After file upload |

**Button Text Changes:**
- "config" ↔ "viewer" (when config panel shown)
- "output document" ↔ "input document" (when switching views)

### Configuration Panel Buttons

| Button | Context | Action |
|--------|---------|--------|
| **Load Config** | Bottom of config | Load configuration from file |
| **Save Config** | Bottom of config | Save current configuration to file |
| **New Config** | Bottom of config | Clear all fields, start fresh |
| **?** (Help) | Next to each field | Show help dialog for that field |
| **Add** | List fields | Add new item to list |
| **Remove** | List fields | Remove selected item from list |
| **Change** | List fields | Edit selected item in list |
| **▲** | List fields | Move item up in list |
| **▼** | List fields | Move item down in list |

### Navigation Controls (PDF Viewer)

| Control | Type | Action |
|---------|------|--------|
| **<** | Repeat button | Previous page (hold to auto-repeat) |
| **>** | Repeat button | Next page (hold to auto-repeat) |
| **<<** | Button | Navigate back in history |
| **>>** | Button | Navigate forward in history |
| **Page number** | Spin box | Display/input current page (shows as 1-based) |
| **Zoom selector** | Combo box | Change zoom level or mode |

**Zoom Options:**
- Fit Width
- Fit Page
- 12%, 25%, 33%, 50%, 66%, 75%, 100%, 125%, 150%, 200%, 400%
- Custom: Type any percentage (e.g., "152%")

---

## Configuration Panel

### Overview

The configuration panel allows you to define how the application processes your document. Each field has a **?** button that displays detailed help.

### Configuration Fields

#### Text/List Fields

**SPECIAL_CASE**
- List of phrases indicating repeated citations
- Examples: "Ibid.", "Op. cit.", "Prav tam", "Isto"
- Order matters: Less common variants first

**BIBLIOGRAPHY_DELIMITER**
- Text marking bibliography section start
- Examples: "Literature", "Bibliography", "References", "Viri in literatura"
- Multiple variants supported
- Order matters: Less common variants first, more common last

**ANNOT_TYPE**
- How citations are visually marked
- Options: `underline`, `highlight`

**COLOR**
- Color for citation annotations
- Options: `black`, `white`, `gray`, `blue`, `red`, `dark_blue`

**OFFSET**
- Page offset for multi-article documents
- Format: `+N` (forward) or `-N` (backward)
- Example: `+2` shifts article pages 2 forward

**ARTICLE_BREAKS**
- Page ranges for individual articles
- Format: `start:end` (end = where bibliography concludes)
- Example: `1:23`, `25:45`, `47:68`
- Only needed for multi-article documents with separate bibliographies

**SEARCH_EXCLUDE**
- Words to exclude from deep search
- Prevents false positives
- Example: "ur", "Ur." (editor abbreviations)

#### Boolean Options

**DEBUG**
- Enable verbose logging
- Useful for troubleshooting

**SOFT_YEAR**
- Relaxed year filtering
- Includes year ranges (1998-2004)
- Checks year ±1 for typos
- ⚠️ May create incorrect links

**DEEP_SEARCH**
- Permissive citation matching
- Finds citations not exactly matching bibliography format
- ⚠️ May create incorrect links

**ALTERNATIVE_BIB**
- Handle bibliography entries starting with year
- Format: `(Year). Work title...`
- ⚠️ May create incorrect links

### Configuration Workflow

1. **Load Existing Config** (if you have one):
   ```
   Click "Load Config" → Select .txt file → Fields populate automatically
   ```

2. **Create New Config**:
   ```
   Click "New Config" → Clears all fields → Configure manually
   ```

3. **Edit List Fields**:
   ```
   Click "Add" → Enter value → Click OK
   Click item → Click "Remove" to delete
   Click item → Click "Change" → Edit value
   Use ▲/▼ to reorder items
   ```

4. **Save Configuration**:
   ```
   Configure all fields → Click "Save Config" → Choose location
   ```

5. **Learn from Document** (Alternative):
   ```
   Click "viewer" → Select text in PDF → Right-click → Choose action
   Return to config → See updated special cases/delimiters
   ```

---

## PDF Viewer Navigation

### Page Navigation Methods

**1. Arrow Keys**: Up/Down for sequential pages

**2. Mouse Wheel**: Scroll up/down for pages (default behavior)

**3. Navigation Buttons**: Click < / > or hold for auto-repeat

**4. Page Input**: 
   - Click page number field
   - Type page number (1-based)
   - Press Enter

**5. History Navigation**:
   - Click << / >> buttons
   - Or use Left/Right arrow keys
   - Or horizontal mouse wheel

### History Tracking

The viewer maintains navigation history:
- Every page jump adds to history
- Back button returns to previous viewed page (not previous page number)
- Forward button moves forward in history
- Useful for jumping between citations and bibliography

**Example History:**
```
Page 1 → Page 15 → Page 3 → Page 15
         ↑         ↑         ↑
      History   History   History
         [1]      [2]       [3]

Back button: 15 → 3 → 15 → 1
Forward button: 1 → 15 → 3 → 15
```

### Zoom Controls

**Zoom Modes:**
- **Fit Width**: Page width fills viewer width
- **Fit Page**: Entire page visible in viewer
- **Custom %**: Specific zoom percentage

**Zoom Methods:**
1. Select from dropdown
2. Type custom percentage (e.g., "152%")
3. Ctrl + Mouse Wheel (up = zoom in, down = zoom out)

---

## Text Selection and Citation Marking

### Input Mode (Original Document)

**Purpose**: Mark bibliography sections and special cases for the application to learn from.

**Selection Process:**

1. **Select Bibliography Header**:
   ```
   Navigate to bibliography section
   → Click + drag over "Bibliography" or "Literature" text
   → Yellow highlight appears
   → Right-click → Select "bibliography"
   → Text added to bibliography delimiters
   ```

2. **Select Special Cases**:
   ```
   Find repeated citation phrase (e.g., "Ibid.")
   → Click + drag to select
   → Yellow highlight appears
   → Right-click → Select "special_case"
   → Phrase added to special cases list
   ```

3. **Verify in Config**:
   ```
   Click "config" button
   → Check SPECIAL_CASE and BIBLIOGRAPHY_DELIMITER lists
   → Your selections appear in the lists
   ```

**Tips:**
- Select exact text without extra spaces
- Include punctuation if relevant (e.g., "Ibid." not "Ibid")
- Can select multiple variants (e.g., "Ibid.", "ibid", "ib.")

### Output Mode (Processed Document)

**Purpose**: Manually add or edit links after automatic processing.

**Link Creation Process:**

1. **Create Link Source**:
   ```
   Select citation text (e.g., "Smith 2020")
   → Right-click → Select "add_link"
   → Link source created (waiting for destination)
   ```

2. **Set Link Destination**:
   ```
   Navigate to bibliography entry
   → Select bibliography entry text
   → Right-click → Select "add_destination"
   → Link completed (citation now clickable)
   ```

**Link Editing:**
- Right-click existing link → Select "delete" → Link removed
- Right-click existing annotation → Select "delete" → Annotation removed

---

## Multi-Article Documents

### What Are Multi-Article Documents?

Academic journals or conference proceedings where:
- One PDF contains multiple articles
- Each article has its own bibliography
- Citations in Article 1 should not link to Article 2's bibliography

### Setting Up Article Boundaries

**Method 1: Configuration Panel**

```
Click "config" → ARTICLE_BREAKS field
→ Click "Add"
→ Enter range: "1:23" (article pages 1-23, bibliography ends page 23)
→ Click "Add" again
→ Enter range: "25:45" (next article pages 25-45, bibliography ends page 45)
→ Continue for all articles
```

**Method 2: Interactive Selection (Space Key)**

```
Open PDF → Navigate to page 1 (Article 1 starts)
→ Press Space → "First page selected: 1"
→ Navigate to page 23 (Article 1 bibliography ends)
→ Press Space → "Article saved: pages 1 to 23"

→ Navigate to page 25 (Article 2 starts)
→ Press Space → "First page selected: 25"
→ Navigate to page 45 (Article 2 bibliography ends)
→ Press Space → "Article saved: pages 25 to 45"

Repeat for all articles
```

**Removing Article Boundary:**
```
Navigate to boundary page (first or last of an article)
→ Press Space → Boundary removed
```

### Output View - Article Navigation

When viewing processed multi-article documents:
- **Main viewer** (left): Shows full document
- **Alt viewer** (right): Shows only current article's bibliography page
- Navigate in main viewer → Alt viewer updates to show relevant bibliography

**Example:**
```
Main viewer on page 5 (Article 1, citation)
→ Alt viewer automatically shows page 23 (Article 1 bibliography)

Main viewer navigates to page 30 (Article 2, citation)
→ Alt viewer automatically jumps to page 45 (Article 2 bibliography)
```

---

## Output Document Management

### Viewing Processed Document

After clicking "start linking":
1. Application automatically switches to output view
2. Shows processed PDF with clickable links
3. Annotations visible (underlines or highlights)

**Output View Features:**
- Click citations → Jump to bibliography
- Split view: Main + Alt viewer (for multi-article)
- Manual link editing available

### Testing Links

**Manual Testing:**
1. Click on citation text (should jump to bibliography)
2. Check link accuracy
3. Use history back to return to citation

**Annotations:**
- Underlines/highlights show where links exist
- Right-click → Delete to remove if incorrect

### Saving Output

**Save Process:**
```
Click "save file" button
→ File dialog opens
→ Choose destination folder
→ Enter filename
→ Click "Save"
→ Success message appears
```

**File Locations:**
- Automatically saved to output directory (configured in Bridge)
- Copy saved to user-chosen location (via "save file" button)

### Switching Views

**Toggle Between Views:**
```
Click "output document" / "input document" button
→ Button text changes
→ Viewer switches

OR

Click "config" button to view/edit configuration
→ Hides current viewer
→ Shows configuration panel
```

**View States:**
- **Input View**: Original uploaded PDF
- **Output View**: Processed PDF with links (only after linking)
- **Config View**: Configuration panel

---

## Complete Usage Example

### Scenario: Processing a Journal Article

**Document**: Single academic article with bibliography at end

**Steps:**

1. **Launch and Upload**
   ```
   Start application
   → Upload dialog appears
   → Click "upload file/path"
   → Select "journal_article.pdf"
   → PDF loads in viewer
   ```

2. **Initial Configuration**
   ```
   Click "config" button
   → Click "Load Config" (if you have a previous config)
   → OR configure manually:
      - SPECIAL_CASE: Add "Ibid.", "Op. cit."
      - BIBLIOGRAPHY_DELIMITER: Add "References", "Bibliography"
      - ANNOT_TYPE: Select "underline"
      - COLOR: Select "blue"
   → Click "Save Config" (save for future use)
   ```

3. **Interactive Learning**
   ```
   Click "viewer" to return to PDF
   → Navigate to end of document (page 15)
   → See "References" header
   → Click + drag to select "References"
   → Right-click → Select "bibliography"
   
   → Scroll up to find citation (page 3)
   → See "Ibid." in text
   → Select "Ibid." text
   → Right-click → Select "special_case"
   ```

4. **Process Document**
   ```
   Click "start linking" button
   → Dialog: "Are you sure?"
   → Check configuration is correct
   → Click "Yes"
   → Application processes (may take 10-30 seconds)
   → Automatically switches to output view
   ```

5. **Review Output**
   ```
   Now in output view (split screen)
   → Left: Main document
   → Right: (empty - no multi-article)
   
   → Navigate to citation (page 3)
   → See blue underline under "Smith 2020"
   → Click underline → Jumps to page 15 (bibliography)
   → Click history back (<<) → Returns to page 3
   
   → Check several citations
   → All working correctly!
   ```

6. **Manual Adjustment** (if needed)
   ```
   → Find missed citation (page 8)
   → Select citation text "Jones 1998"
   → Right-click → "add_link"
   
   → Navigate to bibliography (page 15)
   → Find "Jones, A. (1998)..." entry
   → Select entry text
   → Right-click → "add_destination"
   → Link created!
   
   → Test: Click "Jones 1998" on page 8 → Jumps to page 15 ✓
   ```

7. **Save Result**
   ```
   Click "save file" button
   → Navigate to desired folder
   → Enter filename: "journal_article_linked.pdf"
   → Click "Save"
   → Message: "File saved successfully"
   ```

8. **Verify External File**
   ```
   Open "journal_article_linked.pdf" in any PDF reader
   → Citations are clickable
   → Links work in Adobe Reader, Foxit, browsers, etc.
   → Ready to distribute!
   ```

---

## Advanced Usage Tips

### Workflow Optimization

**1. Create Template Configs**
   - Save configs for different document types
   - Journal articles: one config
   - Books: different config
   - Conference proceedings: another config

**2. Use Keyboard Heavily**
   - Arrow keys for navigation (faster than mouse)
   - Ctrl+Wheel for quick zoom adjustments
   - Space for article boundaries (multi-article)

**3. Split-Screen Workflow**
   - Keep input view on one side for reference
   - Work in output view for manual edits
   - Toggle with button for comparison

### Troubleshooting Common Issues

**Missing Links After Processing:**
- Check bibliography delimiter is correct
- Verify special cases include all variants
- Try DEEP_SEARCH and SOFT_YEAR options (carefully!)
- Manually add missing links in output view

**Too Many False Links:**
- Disable DEEP_SEARCH and SOFT_YEAR
- Add problematic words to SEARCH_EXCLUDE
- Review and delete incorrect links manually

**Multi-Article Citations Linking to Wrong Bibliography:**
- Verify article boundaries are correct
- Check OFFSET setting if pages seem shifted
- Use Space key to interactively adjust boundaries

**Application Unresponsive:**
- Large PDFs may take time to process
- Check DEBUG mode for progress info
- Ensure sufficient RAM available

---

## Summary of All Interactions

### Quick Reference Card

| Input Method | Context | Action |
|-------------|---------|--------|
| **Mouse** | | |
| Left click + drag | PDF viewer | Select text region |
| Left click | Link (output) | Navigate to destination |
| Right click | Selected text | Show action menu |
| Right click | Annotation/link | Show delete menu |
| Wheel up/down | PDF viewer | Navigate pages |
| Ctrl + Wheel | PDF viewer | Zoom in/out |
| Shift + Wheel | PDF viewer | Smooth scroll |
| **Keyboard** | | |
| ↑ / ↓ | PDF viewer | Previous/Next page |
| ← / → | PDF viewer | History back/forward |
| Space | PDF viewer | Select page boundary |
| Enter | Page field | Jump to page |
| Enter | Zoom field | Apply zoom |
| **Buttons** | | |
| config / viewer | Main window | Toggle config panel |
| start linking | Main window | Process document |
| output/input document | Main window | Switch views |
| save file | Main window | Save processed PDF |
| 🗙 | Main window | Exit application |
| < / > | Navigator | Previous/Next page |
| << / >> | Navigator | History navigation |
| Load Config | Config panel | Load configuration |
| Save Config | Config panel | Save configuration |
| Add/Remove/Change | List fields | Manage list items |
| ? | Any config field | Show help |

---

## Best Practices

1. **Always save your configuration** after setting up a new document type
2. **Test the output** by clicking several citations before saving
3. **Use "Load Config"** for similar documents to save time
4. **Review automatically generated links** - they're not perfect
5. **Keep backup** of original PDF before processing
6. **Use DEBUG mode** if you encounter issues
7. **Start conservative** - enable DEEP_SEARCH only if needed
8. **Document your configs** - add comments in saved config files
9. **Verify in external reader** before distributing linked PDFs
10. **Process in batches** - reuse configs for similar documents

---

## Conclusion

Citation Linker provides both automated processing and fine-grained manual control for creating hyperlinked academic PDFs. Master the keyboard shortcuts and interactive selection features to dramatically speed up your workflow. The application learns from your inputs, making subsequent documents faster to process.

For technical issues or advanced usage, refer to the source code documentation or the detailed analysis documents in the project repository.

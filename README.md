# Citation Linker - Citation & Bibliography Structure Guide

## Usage
If you download the latest release executable for your platform it should work without any installation. (was not tested on mac)
Testing version also opens a console in Windows. there is a small delay between when console opens and the program starts and the console might overlap with the app so check in your system tray (menu bar)
if the program is running already if you don't see it.

## general app flow
- open the app - select a document you want to link
- in config window you can clear current config or load previous or manually adjust the parameters
- in document viewer you can:
    + use space to select the start and end of the articles you want to link (end is after bibliography)
    + mouse actions:
        * left click and drag - creates a selection that you can add to bibliography delimiters or special cases (check config for more info)
        * right click - delete links and annotations
- after you selected all the articles and edited config click start linking button
- next step it will open document viewer in split view:
    + left is used to check the text
    + right will snap to the bibliography of the article you are viewing on the left
- in split view you can add or remove links:
    + right click - delete link or annotation
    + left click and drag - create a selection and then:
        * in the left viewer click add link
        * in the right, make a new selection and click add destination
        * this will link the citation to bibliography
    
## Citation Style
The script works with **Chicago author-date style** (parenthetical citations) and expects citations primarily within parentheses in the format: `(Author Year)` or `(Author Year: pages)`.

## Citation Format Requirements

### Standard Citation Patterns
The following citation formats are recognized:

- `(Surname Year)` → `(Trocki 2008)`
- `(Surname Year: pages)` → `(Adorno 1966: 353–354)`
- `(Surname et al. Year: pages)` → `(Deckard et al. 2015: 17–22, 49–56)`
- Multiple citations: `(Surname1 Year1: pages; Surname2 Year2: pages)` → `(Trocki 2008: 7–8; Davidson 2019a: 24–28)`
- With prefixes: `(prim. Zima 2015: 2–4)` or `(Nav. po Davidson 2019b: 180)`
- Citations with author in text: `Peter V. Zima (2015: xi, 2–3, passim)`
- Repeated work reference: `(nav. d.: 17–22)` (customizable in `.config`)

### Special Cases and Exceptions
- **Quotes before citation**: `(»nach Auschwitz ein Gedicht zu schreiben, ist barbarisch«; Adorno 1969: 31)`
- **Nested parentheses**: `(Pascale Casanova [2004])` - parentheses within parentheses
- **Multiple years from same author**: `(Kermauner 1970: 93; 2013: 219)`
- **Multiple works cited together**: Must be separated by semicolons (`;`)
- **Citations without parentheses**: `see Frank 2002: 8–40 and 219–259` (may not be detected reliably)

### Important Citation Limitations
- **Author surname must be capitalized** - lowercase surnames will not be detected
- **No line breaks in surnames** - `Wol-fgang Iser (1988)` will fail
- **No declension of surnames** - inflected forms of surnames won't match
- **Author must precede year** - in parenthetical citations like `(text... Author [Year])`, the surname must be immediately before the year
- **Exact match required** - year and surname in citation must match bibliography exactly

## Bibliography Structure Requirements

### Standard Bibliography Format (Default)
Each bibliography entry must follow this structure:

```
Surname, Name, Year: Title. Publisher information.
```
or
```
Surname, Name, Year. Title. Publisher information.
```

**Key requirements:**
- Comma-separated format: `Surname, Name, Year`
- Year can be followed by colon (`:`), period (`.`), or other punctuation
- Examples: 
  - `Adorno, Theodor W., 1969: Prismen: Kulturkritik und Gesellschaft. Berlin: Suhrkamp Verlag.`
  - `Adorno, Theodor W., 1969. Prismen: Kulturkritik und Gesellschaft. Berlin: Suhrkamp Verlag.`

### Alternative Bibliography Format
If `ALTERNATIVE_BIB=True` in `.config`, the script also recognizes:

```
Year. Title and rest of entry
```

Example: `1964. Slovenska matica`

This format is useful for sources where the year appears first followed by a period.

## Configuration Options

### SOFT_YEAR (True/False)
**Default:** `True`

When enabled:
- Includes year ranges like `1998-2004` in matching
- Adds ±1 year tolerance to account for potential typos or OCR errors
- Example: Citation `(Smith 2010)` can match bibliography entry with year `2009`, `2010`, or `2011`
- **Warning:** May create false positive links

### DEEP_SEARCH (True/False)
**Default:** `True`

When enabled:
- More permissive matching between citations and bibliography
- Matches partial strings in author names (useful for compound surnames)
- Checks "others" field (co-authors, additional names)
- Example: Can match `Van der Waals` with `Waals` if conditions are met
- **Warning:** May create false positive links

### SEARCH_EXCLUDE
**Format:** List of strings to exclude when using DEEP_SEARCH

**Default:** `SEARCH_EXCLUDE="ur", "Ur", "Ur."`

Words that `DEEP_SEARCH` should NOT consider as valid matches for linking. Useful to exclude common abbreviations or editor markers that might otherwise create false matches.

Example: `"ur"` is often used for "editor" (Slovenian: "urednik") and should not be matched as an author name.
**Warning:** if not used with DEEP_SEARCH the script it's possible for script to find more false connections

### ALTERNATIVE_BIB (True/False)
**Default:** `False`

When enabled:
- Recognizes bibliography entries where year comes first: `Year. Title...`
- Traditional format `Surname, Name, Year:` is ALSO still checked
- Useful for certain citation styles or source materials
- **Warning:** May create false positive links

## General Limitations

1. **Single bibliography location**: The script currently works only with documents that have all references in one location (typically at the end)
2. **Chicago author-date style only**: Other citation styles (APA, MLA, etc.) are not supported
3. **PDF format required**: Only works with PDF documents
4. **One article at a time**: Designed for single articles or documents with one unified bibliography
5. **Language-agnostic surnames**: Works with any language that uses capital letters for surnames

## notice
the script was tested with the citation style used in the publications of *Studia Litteraria*: 
[link](https://omp.zrc-sazu.si/zalozba/catalog/series/A32)

## Best Practices

- Ensure bibliography entries follow the required format: `Surname, Name, Year` (comma-separated)
- Keep author names and years consistent between citations and bibliography
- Use `DEEP_SEARCH=False` and `SOFT_YEAR=False` for maximum precision if your document is clean
- Enable `DEEP_SEARCH` and `SOFT_YEAR` for documents with potential OCR errors or inconsistencies
- Add common abbreviations to `SEARCH_EXCLUDE` to reduce false positives

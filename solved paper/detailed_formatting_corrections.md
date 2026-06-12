# Detailed HTML-to-Markdown Conversion & Formatting Guidelines

This document details all the formatting correction types established during the conversion of HTML files (such as model answers) to Markdown (`.md`). In the future, any conversion script or manual correction phase must check for these issues step-by-step to prevent rendering errors on the website preview.

---

## Table of Contents
1. [HTML-to-Markdown Block Traps (Code Blocks & Red Lines)](#1-html-to-markdown-block-traps-code-blocks--red-lines)
2. [Bold Syntax & Spacing Rules](#2-bold-syntax--spacing-rules)
3. [Document Parity (Stray Asterisks & Mismatches)](#3-document-parity-stray-asterisks--mismatches)
4. [Document Hierarchies (Subheading Size Uniformity)](#4-document-hierarchies-subheading-size-uniformity)
5. [Bullet Points vs. Paragraph Integrity](#5-bullet-points-vs-paragraph-integrity)
6. [Nested Sub-bullet Indentation](#6-nested-sub-bullet-indentation)
7. [Metadata, Branding, & Page Number Extraction](#7-metadata-branding--page-number-extraction)
8. [Image Visibility & Filename Formatting](#8-image-visibility--filename-formatting)
9. [Step-by-Step Execution Checklist for Future Conversions](#9-step-by-step-execution-checklist-for-future-conversions)

---

## 1. HTML-to-Markdown Block Traps (Code Blocks & Red Lines)

### The Indentation Trap
*   **Root Cause**: In standard Markdown, any block of text indented by 4 or more spaces (or 1 tab) is interpreted as an **indented code block** (`<pre><code>`).
*   **Symptom on Website**: Text is rendered in monospace font inside a bordered code box. Furthermore, if the text starts with a hyphen `-`, code highlight libraries (such as Prism.js) auto-detect it as a `diff` block, coloring the entire text **red** (as a deletion).
*   **Fix**: All paragraphs, headers, tables, and standard bullet points must be restricted to **0 to 2 spaces of indentation** (e.g., `  - ` or `- `) unless they are actively nested under an open parent list item.

### The HTML Block Break
*   **Root Cause**: Many markdown parsers get stuck in HTML mode when they process raw HTML tags (like `<img>`). If markdown text immediately follows an HTML block on the next line without space, the parser treats the markdown as plain HTML text, skipping bolding and lists.
*   **Fix**: Always leave a **blank line** (`\n\n`) between any raw HTML tag and the following Markdown text.

#### Before vs. After Example:
```markdown
[BEFORE - Renders as red code block on website]
  <img src="images/photo.jpg">
    - **Vaishnavism and Shaivism** received royal patronage, while Buddhism and Jainism continued to flourish.

[AFTER - Renders as correct bold bullet point]
  <img src="images/photo.jpg">

  - **Vaishnavism and Shaivism** received royal patronage, while Buddhism and Jainism continued to flourish.
```

---

## 2. Bold Syntax & Spacing Rules

### Word Boundaries & Leading/Trailing Spaces
*   **Root Cause**: Markdown parser bold delimiters (`**`) only compile into HTML `<strong>` tags if they touch word boundaries correctly.
    *   **Rule 1**: Opening `**` must be preceded by a space (or punctuation) and followed immediately by a non-space character (e.g., ` **bold`).
    *   **Rule 2**: Closing `**` must be preceded by a non-space character and followed immediately by a space, punctuation, or end of line (e.g., `bold** `).
*   **Fix**: Correct spacing issues surrounding the asterisks.

#### Before vs. After Example:
```markdown
[BEFORE - Renders raw asterisks literal]
Peasant indebtedness and land alienation. Eg-**Revenue demand**

[AFTER - Renders bold text properly]
Peasant indebtedness and land alienation. Eg- **Revenue demand**
```

---

## 3. Document Parity (Stray Asterisks & Mismatches)

### The Bold Parity Flip
*   **Root Cause**: Because bold formatting is a toggle state in Markdown parsers, a single unmatched `**` or a stray `**` around punctuation (e.g., `**.**`) flips the bold state of the entire document. This turns subsequent bold text plain, and normal text bold.
*   **Fix**: Scan for and remove double asterisks wrapping isolated punctuation marks. Ensure the total count of double-asterisks in a line (or the file overall) alternates correctly.

#### Before vs. After Example:
```markdown
[BEFORE - Flips parity for the rest of the document]
State policy for equal treatment of all irrespective of faith**.** Eg- Appointment of **Rajputs**...

[AFTER - Restores correct document formatting parity]
State policy for equal treatment of all irrespective of faith. Eg- Appointment of **Rajputs**...
```

---

## 4. Document Hierarchies (Subheading Size Uniformity)

### Headings vs. Body Font Size
*   **Root Cause**: Converting HTML subheaders (`<h3>`, `<h4>`) to standard Markdown headers (`### Heading`) makes them visually larger than the body text, creating an uneven look if the user wants all text to match body font sizes.
*   **Fix**: 
    1. Do not use Markdown heading tags (`#`, `##`, `###`) inside answer blocks.
    2. Instead, format subheadings as plain bold lines (`**Subheading**`) and separate them with blank lines.
    3. Ensure headings are placed on their own separate lines to avoid them being "glued" to normal paragraph text.

#### Before vs. After Example:
```markdown
[BEFORE - Glued/Over-sized heading]
7. **Nai Talim** integrates ethics and skills. ### Way Forward 1. Replicating modern models...

[AFTER - Uniform heading size separated correctly]
7. **Nai Talim** integrates ethics and skills.

**Way Forward**

1. Replicating modern models...
```

---

## 5. Bullet Points vs. Paragraph Integrity

### Unintended Bullets
*   **Root Cause**: Naive HTML-to-Markdown converters change all text blocks inside list containers into bulleted lists (`- `), destroying plain paragraph blocks, introductory sentences, or concluding summaries.
*   **Fix**: Inspect tag types (`<p>` vs `<li>`) and style attributes to preserve plain paragraph formatting where text is intended to be read as a block of text, rather than a list item.

#### Before vs. After Example:
```markdown
[BEFORE - Concluding sentence bulleted]
- Mahatma Gandhi's thoughts represent a living philosophy. By prioritizing the planet over profit...

[AFTER - Correct paragraph format]
Mahatma Gandhi's thoughts represent a **living philosophy.** By prioritizing the planet over profit...
```

---

## 6. Nested Sub-bullet Indentation

### Visual List Hierarchies
*   **Root Cause**: Sub-bullets showing directly below a numbered parent item without indentation makes the list look flat and hard to read.
*   **Fix**: Indent the sub-bullets under a numbered item by exactly **2 spaces** (`  - ` or `  * `) or **4 spaces** depending on the parent list indentation. Do not mix indentation styles.

#### Before vs. After Example:
```markdown
[BEFORE - Flat hierarchy]
3. **Trusteeship principle**
- Encourages **corporate social responsibility (CSR)**.
- Reduces **wealth inequality**.

[AFTER - Properly nested hierarchy]
3. **Trusteeship principle**
    - Encourages **corporate social responsibility (CSR)**.
    - Reduces **wealth inequality**.
```

---

## 7. Metadata, Branding, & Page Number Extraction

### Formatting Clutter
*   **Root Cause**: Raw HTML converted from PDF/Web sources contains repeated footers, copyright notices, headers, and page numbers that break paragraph lines when translated to Markdown.
*   **Fix**: Identify and strip these patterns.
    *   Copyright texts: `Civilsdaily ©`, `All rights reserved`
    *   Address details: `New Delhi`, telephone numbers, etc.
    *   Stray numbers at line endings (representing PDF page counts).

---

## 8. Image Visibility & Filename Formatting

### Visibility Issues
*   **Root Cause**: Parentheses `()` inside image filenames (e.g., `image(2).jpg`) break Markdown image syntax `![](images/image(2).jpg)` because the parser thinks the first closing parenthesis `)` terminates the URL.
*   **Fix**: 
    1. Use standard HTML `<img>` tags: `<img src="images/image(2).jpg">`.
    2. Ensure the relative folder path is correct (typically `images/` folder inside the workspace).
    3. URL-encode path characters if necessary (`%20` for spaces, etc.).

---

## 9. Common Conversion Errors

### 9.6 Bullet Point vs. Paragraph Integrity
*   **Error**: Converted points incorrectly using bullet markers (`- `) when they were plain text paragraphs in the source HTML, or merging points into paragraphs.
*   **Fix**: Maintain the original HTML structure (e.g., distinguish between `<p>` and `<li>` tags) during conversion to ensure paragraphs remain paragraphs and only list items get bullet markers.

### 9.7 Image Visibility & Formatting
*   **Error**: Relative image paths not showing up in the browser, or parentheses in image filenames breaking markdown image formatting.
*   **Fix**: Use standard HTML `<img>` tags (`<img src="images/filename.jpg">`), make sure all referenced image files exist in the `images/` folder relative to the markdown file, and avoid using raw markdown image syntax `![]()` if parentheses in filenames cause parsing issues.

---

## 10. Step-by-Step Execution Checklist for Future Conversions

Use this checklist step-by-step whenever running a parser or converting a new HTML file to Markdown:

1.  **Parse Structural Elements**:
    *   Map `<h>` tags to appropriate markdown headers.
    *   Map `<p>` tags to block paragraphs (separated by `\n\n`).
    *   Map `<li>` tags to lists, retaining indentation.
2.  **Verify Bold Spacing**:
    *   Search for regex pattern `(\w+)\*\*(\w+)` and insert a space where appropriate (e.g., `Eg-**` to `Eg- **`).
3.  **Sanity Check Asterisk Count**:
    *   Count total `**` in the document. Ensure it is an even number.
    *   Detect and fix any instances of `**.**` or unmatched delimiters.
4.  **Insert Image Spacing**:
    *   Scan for `<img` tags. Insert `\n\n` before and after them.
    *   Ensure any bullet point directly following an image uses `  - ` (2 spaces) instead of `    - ` (4 spaces).
5.  **Remove Branding & Clutter**:
    *   Search for copyright, phone, address, and page number strings and remove them.
6.  **Verify Hierarchies**:
    *   Standardize subheading sizes in answers to match body font size using simple bold text.

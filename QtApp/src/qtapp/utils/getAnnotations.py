import pymupdf

def get_all_annotations(self, pdf_path, page_num):
    """Extract all annotations from a page using PyMuPDF"""
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    annotations = []

    for annot in page.annots():
        annot_data = {
            'type': annot.type[1],  # e.g., 'Underline', 'Highlight', 'Link'
            'rect': annot.rect,  # pymupdf.Rect in PDF coordinates
            'color': annot.colors.get('stroke', None),
            'opacity': annot.opacity,
            'border': annot.border,
        }

        # For link annotations, extract destination
        if annot.type[0] == pymupdf.PDF_ANNOT_LINK:
            link = annot.link
            if link:
                annot_data['link_type'] = link['kind']  # LINK_GOTO or LINK_URI
                annot_data['page_dest'] = link.get('page', None)
                annot_data['uri'] = link.get('uri', None)

        annotations.append(annot_data)

    doc.close()
    return annotations

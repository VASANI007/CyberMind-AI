import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding="utf-8")

input_pptx = r"reports/CyberMind AI – Project Review III.pptx"
output_pptx = r"reports/CyberMind AI – Project Review IV.pptx"

prs = Presentation(input_pptx)
print(f"Loaded base presentation with {len(prs.slides)} slides.")

# Theme Palette matching Review 3
C_DARK_NAVY  = RGBColor(0x24, 0x35, 0x41)
C_TITLE_TEXT = RGBColor(0x0F, 0x17, 0x2A)
C_MUTED_TEXT = RGBColor(0x64, 0x74, 0x8B)
C_BODY_TEXT  = RGBColor(0x1E, 0x29, 0x3B)
C_CARD_BG    = RGBColor(0xF8, 0xFA, 0xFC)
C_CARD_BORDER= RGBColor(0xCB, 0xD5, 0xE1)
C_BLUE       = RGBColor(0x29, 0x80, 0xB9)
C_GREEN      = RGBColor(0x33, 0xB6, 0x7D)
C_AMBER      = RGBColor(0xF5, 0x9E, 0x0B)
C_RED        = RGBColor(0xEF, 0x44, 0x44)
C_PURPLE     = RGBColor(0x8B, 0x5C, 0xF6)
C_CYAN       = RGBColor(0x06, 0xB6, 0xD4)
C_WHITE      = RGBColor(0xFF, 0xFF, 0xFF)

# Ensure exactly 14 slides by trimming excess slides if any
while len(prs.slides) > 14:
    rId = prs.slides._sldIdLst[-1].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[-1]

print(f"Slide count adjusted to: {len(prs.slides)}")

def clear_slide_content(slide, keep_decorations=True):
    """
    Clears content shapes from a slide while preserving title underline and footer.
    """
    to_delete = []
    for i, shape in enumerate(slide.shapes):
        # Keep title box (shape 0), underline (shape 1), footer bar, footer text, slide number
        name = shape.name
        top = shape.top
        # Shapes that are footer or header decorations
        if top >= 6180000: # footer elements
            continue
        if shape.name in ["TextBox 1", "Title 1"] and shape.top < 1000000:
            continue
        if shape.name in ["Rectangle 2"] and shape.top < 1100000:
            continue
        to_delete.append(shape)
    
    for shape in to_delete:
        sp = shape._element
        sp.getparent().remove(sp)

def set_slide_header(slide, title_text, slide_num):
    """
    Sets slide title and updates footer slide number.
    """
    # 1. Title
    for shape in slide.shapes:
        if shape.has_text_frame and shape.top < 1000000 and shape.left < 500000:
            tf = shape.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title_text
            p.font.name = "Arial"
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = C_TITLE_TEXT
            break
            
    # 2. Slide Number in Footer
    for shape in slide.shapes:
        if shape.has_text_frame and shape.top >= 6180000 and shape.left > 10000000:
            tf = shape.text_frame
            p = tf.paragraphs[0]
            p.text = str(slide_num)
            p.font.name = "Arial"
            p.font.size = Pt(32)
            p.font.bold = True
            p.font.color.rgb = C_WHITE
            break

print("Helper functions defined.")

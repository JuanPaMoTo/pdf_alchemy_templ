import pymupdf  # PyMuPDF
import os

class Cmdline:
    def __init__(self, args) -> None:
        self.args = args
        self.input_pdf = ""
        self.output_pdf = ""

    def get_num_pages(self):
        """Print the total number of pages in the input PDF."""
        doc = pymupdf.open(self.args.file_path) 
        print(f"Total pages: {doc.page_count}")
        doc.close()

    def split_pdf(self):
        """Split the input PDF into multiple PDFs based on page ranges.
        args.split is a list where each element is a list of zero‑based page indices.
        The output_path is treated as a directory; files are named part_1.pdf, part_2.pdf, …
        """
        if not self.args.split:
            print("No split ranges provided.")
            return
        os.makedirs(self.args.output_path, exist_ok=True)
        src = pymupdf.open(self.args.file_path)
        #From the split ranges check thatall of thm and append the ranges to a new pdf
        for idx, pages in enumerate(self.args.split, start=1):
            new_doc = pymupdf.open()
            for p in pages:
                new_doc.insert_pdf(src,from_page=p, to_page=p)
            out_file = os.path.join(self.args.output_path, f"part_{idx}.pdf")
            new_doc.save(out_file)
            new_doc.close()
        src.close()
        print(f"Created {len(self.args.split)} split PDFs in {self.args.output_path}")

    def del_range(self):
        """Delete the specified pages from the input PDF and write the result to output_path.
        args.delete is a list of lists of zero‑based page numbers. We flatten it.
        """
        if not self.args.delete:
            print("No pages specified for deletion")
            return

        parent_dir = os.path.dirname(self.args.output_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True) 

        pages_to_remove = sorted({p for sub in self.args.delete for p in sub})
        print("pages_to_remove")
        src = pymupdf.open(self.args.file_path)
        new_doc = pymupdf.Document()
        for i in range(src.page_count):
            if i not in (pages_to_remove):
                new_doc.insert_pdf(src, from_page=i, to_page=i)
        new_doc.save(self.args.output_path)
        new_doc.close()
        src.close()
        print(f"Saved PDF without specified pages to {self.args.output_path}")    
        
    def add_pdf(self):
        """Add pages from another PDF into the source PDF.
        The insert PDF is provided via the positional argument `insert`.
        Insertion point is defined by either `--after` or `--before` (1‑based).
        The result is written to output_path.
        """
        insert_path = self.args.insert
        src = pymupdf.open(self.args.file_path)
        insert_doc = pymupdf.open(insert_path)
        
        if getattr(self.args, "after", None) is not None:
            insert_at = self.args.after
        elif getattr(self.args, "before", None) is not None:
            insert_at = self.args.before - 1
        else:
            print("No insertion position specified")
            return
            
        new_doc = pymupdf.open()

        # 1. Insertamos la primera parte del documento original
        if insert_at > 0:
            new_doc.insert_pdf(src, from_page=0, to_page=insert_at-1)
            
        # 2. Insertamos el documento nuevo completo
        new_doc.insert_pdf(insert_doc, from_page=0, to_page=insert_doc.page_count-1)

        # 3. Insertamos el resto del documento original
        if insert_at < src.page_count:
            new_doc.insert_pdf(src, from_page=insert_at, to_page=src.page_count-1)

        # 4. Aseguramos que la carpeta exista antes de guardar
        parent_dir = os.path.dirname(self.args.output_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        # 5. Guardamos y cerramos todo al final
        new_doc.save(self.args.output_path)
        new_doc.close()
        src.close()
        insert_doc.close()
        print(f"Saved PDF with inserted pages to {self.args.output_path}")
        
    def crop_half(self):
        """Crop specified pages in half (left and right) and duplicate each as two pages.
        args.crop_half provides page ranges (zero‑based). For each page we create two pages:
        one with the left half of the original media box and one with the right half.
        The result is saved to output_path.
        """
        if not self.args.crop_half:
            print("No page specified for cropping")
            return
        pages =sorted({p for sub in self.args.crop_half for p in sub})
        src = pymupdf.open(self.args.file_path)

        output_dir = os.path.dirname(self.args.output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        new_doc=pymupdf.open()
        for i in range(src.page_count):
            page = src.load_page (i)
            if i in pages:
                rect = page.rect
                mid_x = (rect.x0 + rect.x1)/2
                left_rect = pymupdf.Rect(rect.x0,rect.y0,mid_x ,rect.y1)
                left_page =new_doc.new_page(width = left_rect.width, height =left_rect.height)
                left_page.show_pdf_page(pymupdf.Rect(0,0, left_rect.width, left_rect.height),src, i, clip=left_rect)

                right_rect = pymupdf.Rect(mid_x, rect.y0,rect.x1,rect.y1)
                right_page = new_doc.new_page(width=right_rect.width,height=right_rect.height)
                right_page.show_pdf_page(pymupdf.Rect  (0,0, right_rect.width, right_rect.height), src, i,clip=right_rect)
            else:
                new_doc.insert_pdf(src, from_page=i, to_page =i)
        new_doc.save(self.args.output_path)
        new_doc.close()
        src.close()
        print(f"Saved cropped PDF to {self.args.output_path}")

        #NUEVAS FUNCIONALIDADES
    def reorder_pages(self):
        """Reorder pages based on a specific sequence provided by the user."""
        if not self.args.reorder:
            print("No sequence provided for reordering.")
            return
            
        src = pymupdf.open(self.args.file_path)
        new_doc = pymupdf.open()
        
        for p in self.args.reorder:
            idx = p - 1  # Convertimos a índice base 0
            if 0 <= idx < src.page_count:
                new_doc.insert_pdf(src, from_page=idx, to_page=idx)
            else:
                print(f"Warning: Page {p} out of range, skipping.")
                
        parent_dir = os.path.dirname(self.args.output_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
            
        new_doc.save(self.args.output_path)
        new_doc.close()
        src.close()
        print(f"Saved reordered PDF to {self.args.output_path}")

    def to_image(self):
        """Convert specified pages to PNG images."""
        if not self.args.to_image:
            print("No pages specified for image conversion.")
            return
            
        # Aplanamos la lista de páginas usando la misma lógica que en del_range
        pages_to_convert = sorted({p for sub in self.args.to_image for p in sub})
        src = pymupdf.open(self.args.file_path)
        
        os.makedirs(self.args.output_path, exist_ok=True)
        
        for i in pages_to_convert:
            if 0 <= i < src.page_count:
                page = src.load_page(i)
                # dpi=150 asegura una buena calidad de imagen
                pix = page.get_pixmap(dpi=150)
                out_file = os.path.join(self.args.output_path, f"page_{i+1}.png")
                pix.save(out_file)
                
        src.close()
        print(f"Exported {len(pages_to_convert)} pages as PNG to {self.args.output_path}")




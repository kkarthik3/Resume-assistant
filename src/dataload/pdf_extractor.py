import requests
import io
import fitz  # PyMuPDF
from langchain.docstore.document import Document

class PDFWithLinksLoader:
    def __init__(self, url: str):
        self.url = url

    def load(self):
        # Download PDF data from URL
        response = requests.get(self.url)
        pdf_data = io.BytesIO(response.content)
        
        # Open the PDF from the byte stream
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        documents = []

        # Process each page of the PDF
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text")  # Extract visible text
            
            # Extract links from the page
            links = page.get_links()
            link_urls = {link['uri']: link['from'] for link in links if 'uri' in link}

            # Embed links alongside the nearby text
            for link_url, rect in link_urls.items():
                # Get the surrounding text near the link
                link_text = self.extract_text_near_link(page, rect)
                
                # Format the text with URL
                text = text.replace(link_text, f"{link_text} [Link: {link_url}]")

            # Create Document object
            document = Document(
                page_content=text,  # Text with embedded links
                metadata={"page": page_num}  # Page metadata
            )
            documents.append(document)

        return documents

    def extract_text_near_link(self, page, rect):
        """
        Extract the text near the link's bounding box.
        `rect` represents the coordinates of the link's bounding box.
        """
        # Get text within the bounding box of the link
        text_near_link = page.get_text("text", clip=rect)
        return text_near_link.strip()
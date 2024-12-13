from typing import List
from langchain_core.documents import Document
from concurrent.futures import ThreadPoolExecutor


class Scraper:
    def __init__(self, urls):
        self.urls = urls

    def run(self) -> List[Document]:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.scrape_url, url) for url in self.urls]
            return [future.result() for future in futures]

    def scrape_url(self, url: str) -> List[Document]:
        if url.endswith(".pdf"):
            return self.scrape_pdf(url)
        else:
            return self.scrape_html(url)

    def scrape_pdf(self, url: str) -> List[Document]:
        # from langchain_community.document_loaders import OnlinePDFLoader
        # loader = OnlinePDFLoader(url)
        # return loader.load()
        pass

    def scrape_html(self, url: str) -> List[Document]:
        from langchain_community.document_loaders import WebBaseLoader

        loader = WebBaseLoader(url)
        return loader.load()

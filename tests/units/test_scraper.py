import pytest
from botify.scraper.scraper import Scraper
from langchain_core.documents import Document


@pytest.fixture
def sample_urls():
    return [
        "https://python.langchain.com/docs/get_started/introduction",
        "https://pdfobject.com/pdf/sample.pdf",  # Actual PDF from arXiv
    ]


def test_scraper_initialization():
    """Test Scraper initialization with URLs."""
    urls = ["https://python.langchain.com"]
    scraper = Scraper(urls)
    assert scraper.urls == urls


def test_scrape_html():
    """Test HTML scraping functionality with real HTTP request."""
    url = "https://python.langchain.com/docs/get_started/introduction"
    scraper = Scraper([url])
    result = scraper.scrape_html(url)

    assert len(result) > 0
    assert isinstance(result[0], Document)
    assert "LangChain" in result[0].page_content


@pytest.mark.skip(reason="PDF scraping is not implemented yet")
def test_scrape_pdf():
    """Test PDF scraping functionality with real HTTP request."""
    url = "https://pdfobject.com/pdf/sample.pdf"  # "Large Language Models as General Pattern Machines" paper
    scraper = Scraper([url])
    result = scraper.scrape_pdf(url)

    assert len(result) > 0
    assert isinstance(result[0], Document)
    assert "language" in result[0].page_content.lower()


def test_run_with_multiple_urls():
    """Test running scraper with multiple URLs using real HTTP requests."""
    urls = [
        "https://python.langchain.com/docs/get_started/introduction",
        # "https://pdfobject.com/pdf/sample.pdf",
    ]
    scraper = Scraper(urls)
    results = scraper.run()

    assert len(results) == 1
    # print(results)
    assert all(isinstance(doc, Document) for doc in results)
    assert any("LangChain" in doc.page_content for doc in results)

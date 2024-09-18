"""Module for fetching and parsing articles from PubMed and PMC using Entrez efetch."""

from __future__ import annotations
import html
import requests
import unicodedata
from abc import ABC, abstractmethod
from io import StringIO
from pathlib import Path
from typing import IO, Any, Dict, Union 
from xml.etree.ElementTree import Element  # nosec
from zipfile import ZipFile
from typing import Generator
from defusedxml import ElementTree

_ENTREZ_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def _db_parser(article_id:str) -> str|None:
    """Parse the article ID to ensure it is in the correct format."""
    db = None
    if article_id.startswith('PMC') and article_id[3:].isdigit():
        db = "pmc"
    elif article_id.isdigit():
        db = "pubmed"
    return db

def _dl_article_xml(article_id:str, db:str|None) -> tuple[None|str,str] : 
    xml_string = None
    params = {"db": db, "id": article_id, "retmode": "xml"}
    response = requests.get(_ENTREZ_EFETCH_URL, params=params)
    if response.status_code == 200:
        xml_string = response.text
    return xml_string

def _parse_article(xml_string:str, db:str) -> Union[None,ArticleParser] : 
    parsed_article = None
    if db == "pmc":
        parsed_article = JATSXMLParser.from_string(xml_string)
    elif db == "pubmed":
        parsed_article = PubMedXMLParser(xml_string)
    # check if parsing was successful
    if not parsed_article.abstract and not parsed_article.paragraphs:
        parsed_article = None
    return parsed_article

def _reformat_article(parsed_article:ArticleParser) -> Dict[str,Any] :
    reformatted_article = {"Title":[parsed_article.title]}
    for sec_title,sentence in parsed_article.abstract :
        sec_title = "Abstract" if sec_title is None else "Abstract - " + sec_title
        reformatted_article[sec_title] = reformatted_article.get(sec_title,[]) + [sentence]
    for sec_title,sentence in parsed_article.paragraphs :
        reformatted_article[sec_title] = reformatted_article.get(sec_title,[]) + [sentence]
    return reformatted_article
    

def dl_and_parse(article_id:str) -> Dict[str,Union[None,Any]]:
    """Fetch article from PubMed or PMC using the ID using Entrez efetch 
    and parse it using the appropriate parser. Then returns dict containing keys : 
    article_xml(raw xml of downloaded article) and
    article_sections (parsed sections in the form of a dictionary with keys as section titles 
    and values as list of text content)"""
    parse_output = {
        "db" : None,
        "article_xml": None,
        "article_sections": None,
    }
    # parse id for correct db format
    parse_output["db"] = _db_parser(article_id)
    if parse_output["db"] is None:
        return parse_output
    parse_output["article_xml"] = _dl_article_xml(article_id, parse_output["db"])
    article_parser = _parse_article(parse_output["article_xml"], parse_output["db"])
    if article_parser is None :
        return parse_output
    parse_output["article_sections"] = _reformat_article(article_parser)
    return parse_output

class ArticleParser(ABC):
    """An abstract base class for article parsers."""

    @property
    @abstractmethod
    def title(self) -> str:
        """Get the article title.

        Returns
        -------
        str
            The article title.
        """

    @property
    @abstractmethod
    def abstract(self) -> list[str]:
        """Get a sequence of paragraphs in the article abstract.

        Returns
        -------
        list of str
            The paragraphs of the article abstract.
        """

    @property
    @abstractmethod
    def paragraphs(self) -> list[tuple[str, str]]:
        """Get all paragraphs and titles of sections they are part of.

        Returns
        -------
        list of (str, str)
            For each paragraph a tuple with two strings is returned. The first
            is the section title, the second the paragraph content.
        """


class JATSXMLParser(ArticleParser):
    def __init__(self, xml_stream: IO[Any]) -> None:
        super().__init__()
        self.content = ElementTree.parse(xml_stream)
        if self.content.getroot().tag == "pmc-articleset":
            self.content = self.content.find("article")

    @classmethod
    def from_string(cls, xml_string: str) -> JATSXMLParser:
        with StringIO(xml_string) as stream:
            obj = cls(stream)
        return obj

    @classmethod
    def from_zip(cls, path: str | Path) -> JATSXMLParser:
        with ZipFile(path) as myzip:
            xml_files = [
                x
                for x in myzip.namelist()
                if x.startswith("content/") and x.endswith(".xml")
            ]

            if len(xml_files) != 1:
                raise ValueError(
                    "There needs to be exactly one .xml file inside of content/"
                )

            xml_file = xml_files[0]

            # Parsing logic
            with myzip.open(xml_file, "r") as fh:
                obj = cls(fh)
        return obj

    @property
    def title(self) -> str:
        titles = self.content.find("./front/article-meta/title-group/article-title")
        return self._element_to_str(titles)

    @property
    def abstract(self) -> list[tuple[str, str]]:
        abstract = self.content.find("./front/article-meta/abstract")
        abstract_list: list[tuple[str, str]] = []
        if abstract:
            for sec_title, text in self.parse_section(abstract):
                abstract_list.append((sec_title,text))
        return abstract_list

    @property
    def paragraphs(self) -> list[tuple[str, str]]:
        paragraph_list: list[tuple[str, str]] = []

        # Paragraphs of text body
        body = self.content.find("./body")
        if body:
            paragraph_list.extend(self.parse_section(body,""))

        # Figure captions
        figs = self.content.findall("./body//fig")
        for fig in figs:
            fig_captions = fig.findall("caption")
            if fig_captions is None:
                continue
            caption = " ".join(self._element_to_str(c) for c in list(fig_captions))
            if caption:
                paragraph_list.append(("Figure Caption", caption))

        # Table captions
        tables = self.content.findall("./body//table-wrap")
        for table in tables:
            caption_elements = table.findall("./caption/p") or table.findall(
                "./caption/title"
            )
            if caption_elements is None:
                continue
            caption = " ".join(self._element_to_str(c) for c in caption_elements)
            if caption:
                paragraph_list.append(("Table Caption", caption))
        return paragraph_list
    
    def parse_section(self, section: Element, sec_title_path: str = "") -> Generator[tuple[str, str], None, None]:
        sec_title = self._element_to_str(section.find("title"))
        if sec_title == "Author contributions":
            return
        sec_title_path = sec_title_path + " - " + sec_title if sec_title_path else sec_title
        for element in section:
            if element.tag == "sec":
                yield from self.parse_section(element, sec_title_path)
            elif element.tag in {"title", "caption", "fig", "table-wrap", "label"}:
                continue
            else:
                text = self._element_to_str(element)
                if text:
                    yield sec_title_path, text

    def _inner_text(self, element: Element) -> str:
        text_parts = [html.unescape(element.text or "")]
        for sub_element in element:
            # recursively parse the sub-element
            text_parts.append(self._element_to_str(sub_element))
            # don't forget the text after the sub-element
            text_parts.append(html.unescape(sub_element.tail or ""))
        return unicodedata.normalize("NFKC", "".join(text_parts)).strip()

    def _element_to_str(self, element: Element | None) -> str:
        if element is None:
            return ""

        if element.tag in {
            "bold",
            "italic",
            "monospace",
            "p",
            "sc",
            "styled-content",
            "underline",
            "xref",
        }:
            # Mostly styling tags for which getting the inner text is enough.
            # Currently this is the same as the default handling. Writing it out
            # explicitly here to decouple from the default handling, which may
            # change in the future.
            return self._inner_text(element)
        elif element.tag == "sub":
            return f"_{self._inner_text(element)}"
        elif element.tag == "sup":
            return f"^{self._inner_text(element)}"
        elif element.tag in {
            "disp-formula",
            "email",
            "ext-link",
            "inline-formula",
            "uri",
        }:
            return ""
        else:
            # Default handling for all other element tags
            return self._inner_text(element)


class PubMedXMLParser(ArticleParser):
    """Parser for PubMed abstract."""

    def __init__(self, data: str | bytes) -> None:
        super().__init__()
        self.content = ElementTree.fromstring(data)

    @property
    def title(self) -> str:
        title = self.content.find("./PubmedArticle/MedlineCitation/Article/ArticleTitle")
        if title is None:
            return ""
        return "".join(title.itertext())

    @property
    def abstract(self) -> list[tuple[str,str]]:
        abstract = self.content.find("./PubmedArticle/MedlineCitation/Article/Abstract")

        if abstract is None:
            # No paragraphs to parse: stop and return an empty iterable.
            return []  # noqa
        
        paragraphs = abstract.iter("AbstractText")
        abstract_list: list[tuple[str,str]] = []
        if paragraphs is not None:
            for paragraph in paragraphs:
                sec_title = paragraph.get("Label") 
                abstract_list.append((sec_title,"".join(paragraph.itertext())))
        return abstract_list

    @property
    def paragraphs(self) -> list[tuple[str, str]]:
        # No paragraph to parse in PubMed article sets: return an empty iterable.
        return []



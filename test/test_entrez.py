import unittest
from outcome_switch.entrez import _dl_article_xml, _parse_article, _reformat_article

# Efetch tests
_VALID_PMCID = "PMC6206648"
_VALID_PMID_1 = "29283904"
_VALID_PMID_2 = "29214975"
_INVALID_1 = "10.1056/NEJMoa2110345"
_INVALID_2 = "0123456789"
_EMPTY = ""

# XML Parsing tests files
# TODO :  tests for parsing XML files 


class EntrezEfetchTest(unittest.TestCase):

    def test_valid_pmcid(self):
        self.assertIsNotNone(_dl_article_xml(_VALID_PMCID)[0])
        self.assertEqual(_dl_article_xml(_VALID_PMCID)[1], "pmc")
    
    def test_valid_pmid1(self):
        self.assertIsNotNone(_dl_article_xml(_VALID_PMID_1)[0])
        self.assertEqual(_dl_article_xml(_VALID_PMID_1)[1], "pubmed")
    
    def test_valid_pmid2(self):
        self.assertIsNotNone(_dl_article_xml(_VALID_PMID_2)[0])
        self.assertEqual(_dl_article_xml(_VALID_PMID_2)[1], "pubmed")
    
    def test_invalid1(self):
        self.assertIsNone(_dl_article_xml(_INVALID_1)[0])
    
    def test_invalid2(self):
        self.assertIsNone(_dl_article_xml(_INVALID_2)[0])
    
    def test_empty(self):
        self.assertIsNone(_dl_article_xml(_EMPTY)[0])
        self.assertIsNone(_dl_article_xml(_EMPTY)[1])
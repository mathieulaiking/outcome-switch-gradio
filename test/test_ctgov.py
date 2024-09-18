import unittest
from outcome_switch.ctgov import find_nctid, get_registry_outcomes, reformat_outcomes


_EMPTY_STRING = ""
# NCT REGEX extraction tests
_TEXT_WITH_ONE_NCT = """blablabla nct id is NCT04647656 blabla"""
_TEXT_WITH_TWO_NCT = """blablabla nct id is NCT04647656 blabla NCT06562582 bla"""
_TEXT_WITHOUT_NCT = "blablabla blablabla"

# NCT REGISTRY API tests
_CORRECT_NCT = "NCT04647656"
_INCORRECT_NCT = "PRN03216548"

# REGISTRY outcomes reformatting test
_CTGOV_OUTCOMES = {
    "primaryOutcomes": [
        {
            "measure": "Cognitive health assessment (NeuroTrax)",
            "description": "Memory, attention and information process will be evaluated using the NeuroTrax computerized cognitive evaluation battery.",
            "timeFrame": "Baseline, 2 months",
        }
    ],
    "secondaryOutcomes": [
        {
            "measure": "Brain perfusion",
            "description": "Cerebral blood volume and flow will be measured using perfusion MRI protocol Dynamic susceptibility contrast (DSC).",
            "timeFrame": "Baseline, 2 months",
        }
    ],
}

class NctidFinderTest(unittest.TestCase) :

    def test_text_with_one_nct(self):
        self.assertEqual(find_nctid(_TEXT_WITH_ONE_NCT), "NCT04647656")
    
    def test_text_with_two_nct(self):
        self.assertEqual(find_nctid(_TEXT_WITH_TWO_NCT), "NCT04647656")
    
    def test_text_without_nct(self):
        self.assertIsNone(find_nctid(_TEXT_WITHOUT_NCT))
    
    def test_empty_string(self):
        self.assertIsNone(find_nctid(_EMPTY_STRING))
    
    def test_none_input(self):
        self.assertIsNone(find_nctid(None))

class CtgovExtractionTest(unittest.TestCase) :
    
    def test_correct_nct(self):
        self.assertIsNotNone(get_registry_outcomes(_CORRECT_NCT))
    
    def test_incorrect_nct(self):
        self.assertIsNone(get_registry_outcomes(_INCORRECT_NCT))
    
    def test_empty_string(self):
        self.assertIsNone(get_registry_outcomes(_EMPTY_STRING))

class CtgovReformatTest(unittest.TestCase) :

    def test_correct_reformat_outcomes(self):
        self.assertIsInstance(reformat_outcomes(_CTGOV_OUTCOMES), list)
        self.assertEqual(len(reformat_outcomes(_CTGOV_OUTCOMES)), 2)
        self.assertIsInstance(reformat_outcomes(_CTGOV_OUTCOMES)[0], dict)
        self.assertIsInstance(reformat_outcomes(_CTGOV_OUTCOMES)[1], dict)
        self.assertEqual(reformat_outcomes(_CTGOV_OUTCOMES)[0]["type"], "primary")
        self.assertEqual(reformat_outcomes(_CTGOV_OUTCOMES)[1]["type"], "secondary")
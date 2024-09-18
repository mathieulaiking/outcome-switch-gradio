import unittest
from outcome_switch import filter_sections, filter_outcomes, get_sections_text

_VALID_DICT_WITH_2_SECTIONS = {
    "Methods - Outcomes - Primary outcome": [
        "The FIRST primary outcome is pain at 12months as measured by the VAS. The primary analysis is to assess whether surgical correction of the impingement morphology (arthroscopic osteochondroplasty) with/without labral repair, in adults aged 1850 years diagnosed with FAI, provides decreased pain at 12months compared to arthroscopic lavage of the hip joint with/without labral repair, as measured by the VAS. The VAS is a validated unidimensional scale that is easy to use, requires no verbal or reading skills, and is sufficiently versatile to be employed in a variety of settings [ \n         2 4]."
    ],
    "Methods - Outcomes - Secondary outcomes": [
        "Secondary outcomes include:",
        "Hip function as measured by the Hip Outcome Score (HOS).",
        "Generic physical and mental health as measured by the Short Form-12 (SF-12).",
        "Impact of hip-specific disease on function and lifestyle in the young, active patient as measured by the International Hip Outcome Tool (iHOT-12).",
        "Health utility as measured by the EuroQol (EQ-5D).",
        "Complications, including additional surgery and other serious and non-serious adverse events. Reasons for re-operations for the randomized hip typically include, but are not limited to re-injury of the labrum/cartilage, hip dislocation, hip instability, infection (deep or superficial), wound healing problem, soft tissue problem, and unresolved hip pain. Other hip-related adverse events to be reported include, but are not limited to, hip instability, tendinopathy, re-injury of the labrum/cartilage, hip osteoarthritis post-surgery, and infection (superficial or deep).",
        "The HOS is a self-administered hip score that was designed to capture hip function and outcomes following surgical therapies such as arthroscopy [ \n         5]. The HOS has been shown to have the greatest clinimetric evidence for use in patients with FAI or labral tears [ 6,  7]. The SF-12 may be self-completed or interview-administered and will help document general health status and the burden of illness that FAI presents [ 8]. The iHOT-12 is a shorter version of the iHOT-33 designed to be easier to complete in routine clinical practice to measure both health-related quality of life and changes after treatment in young, active patients with hip disorders [ 9]. This questionnaire has been shown to be valid, reliable, and responsive to change [ 9]. The EQ-5D is a standardized instrument for use as a measure of health outcome [ 10]. The EQ-5D comprises five dimensions of health (mobility, self-care, usual activities, pain/discomfort, and anxiety/depression). The EQ-5D has been used in previous studies involving patients with hip pain and has been extensively validated [ 11,  12].",
    ],
    "Discussion - Analysis plan - Blinded analyses": [
        "All statistical analyses will first be completed using blinded treatment groups (i.e. treatment X and Y). Interpretations for the effect of the surgical interventions will be documented based upon blinded X versus Y treatment [ \n         14]."
    ],
}

_FILTERED_SECTIONS = {
    "filtered_sections": {
        "Methods - Outcomes - Primary outcome": [
            "The FIRST primary outcome is pain at 12months as measured by the VAS. The primary analysis is to assess whether surgical correction of the impingement morphology (arthroscopic osteochondroplasty) with/without labral repair, in adults aged 1850 years diagnosed with FAI, provides decreased pain at 12months compared to arthroscopic lavage of the hip joint with/without labral repair, as measured by the VAS. The VAS is a validated unidimensional scale that is easy to use, requires no verbal or reading skills, and is sufficiently versatile to be employed in a variety of settings [ \n         2 4]."
        ],
        "Methods - Outcomes - Secondary outcomes": [
            "Secondary outcomes include:",
            "Hip function as measured by the Hip Outcome Score (HOS).",
            "Generic physical and mental health as measured by the Short Form-12 (SF-12).",
            "Impact of hip-specific disease on function and lifestyle in the young, active patient as measured by the International Hip Outcome Tool (iHOT-12).",
            "Health utility as measured by the EuroQol (EQ-5D).",
            "Complications, including additional surgery and other serious and non-serious adverse events. Reasons for re-operations for the randomized hip typically include, but are not limited to re-injury of the labrum/cartilage, hip dislocation, hip instability, infection (deep or superficial), wound healing problem, soft tissue problem, and unresolved hip pain. Other hip-related adverse events to be reported include, but are not limited to, hip instability, tendinopathy, re-injury of the labrum/cartilage, hip osteoarthritis post-surgery, and infection (superficial or deep).",
            "The HOS is a self-administered hip score that was designed to capture hip function and outcomes following surgical therapies such as arthroscopy [ \n         5]. The HOS has been shown to have the greatest clinimetric evidence for use in patients with FAI or labral tears [ 6,  7]. The SF-12 may be self-completed or interview-administered and will help document general health status and the burden of illness that FAI presents [ 8]. The iHOT-12 is a shorter version of the iHOT-33 designed to be easier to complete in routine clinical practice to measure both health-related quality of life and changes after treatment in young, active patients with hip disorders [ 9]. This questionnaire has been shown to be valid, reliable, and responsive to change [ 9]. The EQ-5D is a standardized instrument for use as a measure of health outcome [ 10]. The EQ-5D comprises five dimensions of health (mobility, self-care, usual activities, pain/discomfort, and anxiety/depression). The EQ-5D has been used in previous studies involving patients with hip pain and has been extensively validated [ 11,  12].",
        ],
    },
    "regex_priority_index": 0,
    "regex_priority_name": "strict_method_and_prim_sec",
    "check_type": "title",
}


_EMPTY_DICT = {}
from scripts.phase_m_apply_strict_title_linkage import strict_title_match


def test_strict_title_match_requires_four_significant_tokens():
    ok, _, total = strict_title_match("Ponte nuovo", "Ponte nuovo", None)
    assert ok is False
    assert total < 4


def test_strict_title_match_requires_seventy_five_percent_and_four_tokens():
    ok, matched, total = strict_title_match(
        "Ponte ciclopedonale Adda Cassano illuminazione",
        "Realizzazione ponte ciclopedonale Adda Cassano",
        "Opere di illuminazione pubblica",
    )
    assert ok is True
    assert matched >= 4
    assert matched * 4 >= total * 3


def test_generic_procurement_words_do_not_create_linkage():
    ok, _, _ = strict_title_match(
        "Riqualificazione stazione ferroviaria Bergamo pensiline ascensori",
        "Lavori di manutenzione e messa in sicurezza",
        "Servizi e forniture per il progetto",
    )
    assert ok is False

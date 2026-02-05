from reporting.law_enforcement import generate_law_enforcement_report

def test_law_enforcement_report_structure():
    report = generate_law_enforcement_report(
        case_id="case1",
        scam_type="UPI_REFUND_SCAM",
        confidence=0.85,
        entities=[],
        timeline=[]
    )

    assert report["audience"] == "LAW_ENFORCEMENT"
    assert "recommended_actions" in report
    assert report["confidence"] == 0.85

"""
Unit tests for intelligence reporting module.
"""

import pytest
from shreyas.app.reporting.intelligence_reporter import (
    IntelligenceReporter,
    IntelligenceReport,
)


@pytest.fixture
def reporter():
    """Create reporter instance."""
    return IntelligenceReporter()


@pytest.fixture
def mock_data():
    """Create mock data for reporting."""
    return {
        "conversation_id": "conv_123",
        "sender_info": {
            "sender_id": "scammer_001",
            "contact_method": "whatsapp",
            "platform": "whatsapp",
        },
        "extracted_entities": [
            {"type": "upi_id", "value": "scammer@upi", "confidence": 0.95},
            {"type": "phone", "value": "+91-9876543210", "confidence": 0.9},
            {"type": "url", "value": "https://malicious.com", "confidence": 0.85},
        ],
        "detection_results": {
            "final_score": 0.92,
            "tactics": ["phishing", "social_engineering"],
            "detector_results": {
                "linguistic": 0.85,
                "behavioral": 0.88,
                "link_intel": 0.95,
            },
        },
    }


def test_reporter_initialization(reporter):
    """Test reporter initialization."""
    assert reporter is not None


def test_generate_law_enforcement_report(reporter, mock_data):
    """Test generating law enforcement report."""
    report = reporter.generate_law_enforcement_report(
        conversation_id=mock_data["conversation_id"],
        sender_info=mock_data["sender_info"],
        extracted_entities=mock_data["extracted_entities"],
        detection_results=mock_data["detection_results"],
    )

    assert isinstance(report, IntelligenceReport)
    assert report.report_type == "law_enforcement"
    assert report.conversation_id == "conv_123"
    assert len(report.evidence) > 0
    assert len(report.recommendations) > 0


def test_generate_bank_report(reporter, mock_data):
    """Test generating bank report."""
    report = reporter.generate_bank_report(
        conversation_id=mock_data["conversation_id"],
        sender_info=mock_data["sender_info"],
        extracted_entities=mock_data["extracted_entities"],
    )

    assert report.report_type == "bank"
    assert len([e for e in report.extracted_intelligence["upi_accounts"]]) > 0


def test_generate_internal_report(reporter, mock_data):
    """Test generating internal report."""
    report = reporter.generate_internal_report(
        conversation_id=mock_data["conversation_id"],
        sender_info=mock_data["sender_info"],
        extracted_entities=mock_data["extracted_entities"],
        detection_results=mock_data["detection_results"],
    )

    assert report.report_type == "internal"
    assert len(report.recommendations) > 0


def test_generate_victim_support_report(reporter, mock_data):
    """Test generating victim support report."""
    recovery_guidance = [
        "Contact your bank immediately",
        "File FIR with police",
        "Monitor your accounts",
    ]

    report = reporter.generate_victim_support_report(
        conversation_id=mock_data["conversation_id"],
        sender_info=mock_data["sender_info"],
        extracted_entities=mock_data["extracted_entities"],
        recovery_guidance=recovery_guidance,
    )

    assert report.report_type == "victim_support"
    assert len(report.recommendations) == len(recovery_guidance)


def test_report_to_json(reporter, mock_data):
    """Test converting report to JSON."""
    report = reporter.generate_law_enforcement_report(
        conversation_id=mock_data["conversation_id"],
        sender_info=mock_data["sender_info"],
        extracted_entities=mock_data["extracted_entities"],
        detection_results=mock_data["detection_results"],
    )

    json_str = report.to_json()
    assert isinstance(json_str, str)
    assert "law_enforcement" in json_str
    assert mock_data["conversation_id"] in json_str


def test_export_report(reporter, mock_data):
    """Test exporting report in different formats."""
    report = reporter.generate_law_enforcement_report(
        conversation_id=mock_data["conversation_id"],
        sender_info=mock_data["sender_info"],
        extracted_entities=mock_data["extracted_entities"],
        detection_results=mock_data["detection_results"],
    )

    json_export = reporter.export_report(report, format="json")
    assert isinstance(json_export, str)
    assert len(json_export) > 0

    csv_export = reporter.export_report(report, format="csv")
    assert isinstance(csv_export, str)
    assert "LE-" in csv_export  # Law enforcement report ID prefix


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Unit tests for victim recovery module.
"""

import pytest
from shreyas.app.reporting.victim_recovery import (
    VictimRecoveryAssistant,
    ScamType,
    RiskLevel,
)


@pytest.fixture
def assistant():
    """Create recovery assistant."""
    return VictimRecoveryAssistant()


@pytest.fixture
def upi_fraud_entities():
    """Create mock UPI fraud entities."""
    return [
        {"type": "upi_id", "value": "scammer@upi", "confidence": 0.95},
        {"type": "amount", "value": "5000", "confidence": 0.9},
        {"type": "phone", "value": "+91-9876543210", "confidence": 0.85},
    ]


def test_assistant_initialization(assistant):
    """Test assistant initialization."""
    assert assistant is not None
    assert len(assistant.recovery_guides) > 0


def test_assess_upi_fraud(assistant, upi_fraud_entities):
    """Test assessing UPI fraud case."""
    detection_results = {"final_score": 0.95}

    assessment = assistant.assess_victim_situation(
        scam_type=ScamType.UPI_FRAUD,
        extracted_entities=upi_fraud_entities,
        detection_results=detection_results,
    )

    assert assessment.scam_type == ScamType.UPI_FRAUD
    assert assessment.risk_level == RiskLevel.CRITICAL
    assert assessment.financial_loss_estimate == 5000.0
    assert "Bank account" in assessment.data_exposed


def test_generate_recovery_plan(assistant, upi_fraud_entities):
    """Test generating recovery plan."""
    detection_results = {"final_score": 0.95}

    assessment = assistant.assess_victim_situation(
        scam_type=ScamType.UPI_FRAUD,
        extracted_entities=upi_fraud_entities,
        detection_results=detection_results,
    )

    plan = assistant.generate_recovery_plan(assessment)

    assert "immediate_actions" in plan
    assert "short_term_actions" in plan
    assert "long_term_actions" in plan
    assert "contact_numbers" in plan
    assert len(plan["immediate_actions"]) > 0


def test_immediate_actions_for_upi_fraud(assistant, upi_fraud_entities):
    """Test immediate actions for UPI fraud."""
    assessment = assistant.assess_victim_situation(
        scam_type=ScamType.UPI_FRAUD,
        extracted_entities=upi_fraud_entities,
        detection_results={"final_score": 0.9},
    )

    plan = assistant.generate_recovery_plan(assessment)
    immediate_actions = plan["immediate_actions"]

    # Should include bank contact
    bank_actions = [a for a in immediate_actions if "bank" in a["action"].lower()]
    assert len(bank_actions) > 0


def test_risk_level_determination(assistant):
    """Test risk level determination."""
    low_entities = []
    high_entities = [
        {"type": "upi_id", "value": "scammer@upi"},
        {"type": "aadhar", "value": "XXXX1234"},
        {"type": "password", "value": "hidden"},
    ]

    low_assessment = assistant.assess_victim_situation(
        scam_type=ScamType.UNKNOWN,
        extracted_entities=low_entities,
        detection_results={"final_score": 0.2},
    )

    high_assessment = assistant.assess_victim_situation(
        scam_type=ScamType.UNKNOWN,
        extracted_entities=high_entities,
        detection_results={"final_score": 0.95},
    )

    assert low_assessment.risk_level == RiskLevel.LOW
    assert high_assessment.risk_level == RiskLevel.CRITICAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

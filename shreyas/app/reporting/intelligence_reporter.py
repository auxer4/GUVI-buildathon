"""
Comprehensive intelligence reporting module.
Generates structured reports for law enforcement, banks, and internal analysis.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class IntelligenceReport:
    """Structured intelligence report."""
    report_id: str
    report_type: str  # "law_enforcement", "bank", "internal", "victim_support"
    timestamp: str
    conversation_id: str
    sender_profile: Dict[str, Any]
    extracted_intelligence: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float
    evidence: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


class IntelligenceReporter:
    """Generate intelligence reports for different stakeholders."""

    def __init__(self):
        """Initialize reporter."""
        logger.info("Intelligence reporter initialized")

    def generate_law_enforcement_report(
        self,
        conversation_id: str,
        sender_info: Dict[str, Any],
        extracted_entities: List[Dict[str, Any]],
        detection_results: Dict[str, Any],
    ) -> IntelligenceReport:
        """
        Generate report for law enforcement agencies.
        Includes: sender profile, tactics, evidence, recommendations.

        Args:
            conversation_id: Conversation ID
            sender_info: Sender/scammer info
            extracted_entities: Extracted entities (UPI, URLs, etc.)
            detection_results: Detection pipeline results

        Returns:
            IntelligenceReport
        """
        report_id = f"LE-{conversation_id[:16]}-{datetime.utcnow().timestamp():.0f}"

        # Categorize entities
        financial_entities = [e for e in extracted_entities if e.get("type") == "upi_id"]
        contact_entities = [e for e in extracted_entities if e.get("type") == "phone"]
        digital_entities = [e for e in extracted_entities if e.get("type") in ["url", "email"]]

        # Build evidence
        evidence = []
        if financial_entities:
            evidence.append({
                "type": "financial_instruments",
                "count": len(financial_entities),
                "entities": financial_entities,
                "severity": "high",
            })
        if contact_entities:
            evidence.append({
                "type": "contact_information",
                "count": len(contact_entities),
                "entities": contact_entities,
                "severity": "high",
            })
        if digital_entities:
            evidence.append({
                "type": "digital_infrastructure",
                "count": len(digital_entities),
                "entities": digital_entities,
                "severity": "medium",
            })

        # Generate recommendations
        recommendations = [
            "Block identified UPI IDs in banking sector",
            "Alert telecom providers about phone numbers",
            "Flag suspicious URLs with ISPs",
            "Cross-reference with other scam databases",
            "Monitor for related scam patterns",
        ]

        return IntelligenceReport(
            report_id=report_id,
            report_type="law_enforcement",
            timestamp=datetime.utcnow().isoformat(),
            conversation_id=conversation_id,
            sender_profile={
                "sender_id": sender_info.get("sender_id"),
                "contact_method": sender_info.get("contact_method"),
                "platform": sender_info.get("platform"),
                "tactics": detection_results.get("tactics", []),
            },
            extracted_intelligence={
                "upi_ids": [e.get("value") for e in financial_entities],
                "phone_numbers": [e.get("value") for e in contact_entities],
                "urls": [e.get("value") for e in digital_entities],
                "identified_relationships": [e for e in extracted_entities if e.get("type") == "relationship"],
            },
            risk_assessment={
                "final_score": detection_results.get("final_score", 0),
                "risk_level": "critical" if detection_results.get("final_score", 0) > 0.8 else "high",
                "detector_results": detection_results.get("detector_results", {}),
            },
            recommendations=recommendations,
            confidence_score=min(0.95, sum(e.get("confidence", 0.5) for e in extracted_entities) / max(len(extracted_entities), 1)),
            evidence=evidence,
        )

    def generate_bank_report(
        self,
        conversation_id: str,
        sender_info: Dict[str, Any],
        extracted_entities: List[Dict[str, Any]],
    ) -> IntelligenceReport:
        """
        Generate report for banking sector.
        Focus: UPI/account fraud patterns.

        Args:
            conversation_id: Conversation ID
            sender_info: Sender info
            extracted_entities: Extracted entities

        Returns:
            IntelligenceReport
        """
        report_id = f"BANK-{conversation_id[:16]}-{datetime.utcnow().timestamp():.0f}"

        financial_entities = [e for e in extracted_entities if e.get("type") == "upi_id"]

        recommendations = [
            "Immediate UPI ID freeze recommended",
            "Check transaction history on flagged IDs",
            "Implement velocity checks for these accounts",
            "Notify UPI authority for investigation",
            "Block if confirmed fraudulent",
        ]

        return IntelligenceReport(
            report_id=report_id,
            report_type="bank",
            timestamp=datetime.utcnow().isoformat(),
            conversation_id=conversation_id,
            sender_profile=sender_info,
            extracted_intelligence={
                "upi_accounts": financial_entities,
                "transaction_patterns": self._analyze_transaction_patterns(extracted_entities),
            },
            risk_assessment={
                "account_fraud_risk": "high" if financial_entities else "low",
                "urgency": "critical",
            },
            recommendations=recommendations,
            confidence_score=0.92,
            evidence=[{
                "type": "upi_accounts",
                "entities": financial_entities,
                "severity": "critical",
            }],
        )

    def generate_internal_report(
        self,
        conversation_id: str,
        sender_info: Dict[str, Any],
        extracted_entities: List[Dict[str, Any]],
        detection_results: Dict[str, Any],
        honeypot_engagement_data: Optional[Dict[str, Any]] = None,
    ) -> IntelligenceReport:
        """
        Generate internal analysis report for system learning.

        Args:
            conversation_id: Conversation ID
            sender_info: Sender info
            extracted_entities: Extracted entities
            detection_results: Detection pipeline results
            honeypot_engagement_data: Optional honeypot interaction data

        Returns:
            IntelligenceReport
        """
        report_id = f"INT-{conversation_id[:16]}-{datetime.utcnow().timestamp():.0f}"

        recommendations = [
            "Update detector patterns with this case",
            "Review detector false negatives",
            "Add sender to historical learning database",
            "Analyze honeypot engagement effectiveness",
            "Share indicators with partner networks",
        ]

        return IntelligenceReport(
            report_id=report_id,
            report_type="internal",
            timestamp=datetime.utcnow().isoformat(),
            conversation_id=conversation_id,
            sender_profile=sender_info,
            extracted_intelligence={
                "all_entities": extracted_entities,
                "entity_types": list(set(e.get("type") for e in extracted_entities)),
                "honeypot_data": honeypot_engagement_data or {},
            },
            risk_assessment=detection_results,
            recommendations=recommendations,
            confidence_score=0.88,
            evidence=[{
                "type": "full_analysis",
                "data": {
                    "extraction_count": len(extracted_entities),
                    "detector_count": len(detection_results.get("detector_results", {})),
                    "honeypot_engaged": honeypot_engagement_data is not None,
                }
            }],
        )

    def generate_victim_support_report(
        self,
        conversation_id: str,
        sender_info: Dict[str, Any],
        extracted_entities: List[Dict[str, Any]],
        recovery_guidance: Optional[List[str]] = None,
    ) -> IntelligenceReport:
        """
        Generate report for victim support and recovery.

        Args:
            conversation_id: Conversation ID
            sender_info: Sender info
            extracted_entities: Extracted entities
            recovery_guidance: Optional recovery steps

        Returns:
            IntelligenceReport
        """
        report_id = f"VICTIM-{conversation_id[:16]}-{datetime.utcnow().timestamp():.0f}"

        recommendations = recovery_guidance or [
            "Contact your bank immediately to block transactions",
            "File FIR with local police",
            "Report to Cyber Crime cell",
            "Document all communications",
            "Monitor your accounts for unauthorized activity",
            "Do NOT share OTP or banking credentials",
        ]

        return IntelligenceReport(
            report_id=report_id,
            report_type="victim_support",
            timestamp=datetime.utcnow().isoformat(),
            conversation_id=conversation_id,
            sender_profile=sender_info,
            extracted_intelligence={
                "scammer_contact_info": [e for e in extracted_entities if e.get("type") == "phone"],
                "suspicious_upi_ids": [e for e in extracted_entities if e.get("type") == "upi_id"],
                "malicious_urls": [e for e in extracted_entities if e.get("type") == "url"],
            },
            risk_assessment={
                "financial_risk": "high",
                "data_breach_risk": "medium",
                "identity_theft_risk": "low",
            },
            recommendations=recommendations,
            confidence_score=0.85,
            evidence=[{
                "type": "victim_support",
                "message": "Use this report to recover and protect yourself",
            }],
        )

    def _analyze_transaction_patterns(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze transaction patterns from extracted entities."""
        amounts = [e.get("value") for e in entities if e.get("type") == "amount"]

        return {
            "total_amount_requested": sum(float(a) for a in amounts if a) if amounts else 0,
            "transaction_count": len(amounts),
            "average_amount": sum(float(a) for a in amounts if a) / len(amounts) if amounts else 0,
        }

    def export_report(self, report: IntelligenceReport, format: str = "json") -> str:
        """
        Export report in specified format.

        Args:
            report: IntelligenceReport to export
            format: Export format ("json", "csv", "pdf")

        Returns:
            Exported report string
        """
        if format == "json":
            return report.to_json()
        elif format == "csv":
            # Simple CSV export
            data = report.to_dict()
            return f"{data['report_id']},{data['report_type']},{data['conversation_id']},{data['confidence_score']}"
        else:
            logger.warning(f"Unsupported export format: {format}")
            return report.to_json()

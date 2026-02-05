"""
Victim Recovery Assistance Module.
Provides personalized recovery guidance based on scam type and impact.
"""

import logging
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ScamType(Enum):
    """Types of scams."""
    UPI_FRAUD = "upi_fraud"
    PHISHING = "phishing"
    IMPERSONATION = "impersonation"
    EXTORTION = "extortion"
    FAKE_JOB = "fake_job"
    ROMANCE = "romance"
    INVESTMENT = "investment"
    TECHNICAL_SUPPORT = "technical_support"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Risk levels for victims."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class VictimAssessment:
    """Assessment of victim's situation."""
    scam_type: ScamType
    risk_level: RiskLevel
    financial_loss_estimate: float
    data_exposed: List[str]  # e.g., ["phone", "address", "bank_account"]
    urgency: str  # "immediate", "urgent", "moderate", "low"
    affected_platforms: List[str]  # e.g., ["whatsapp", "phone", "email"]


class VictimRecoveryAssistant:
    """Provides recovery guidance for scam victims."""

    def __init__(self):
        """Initialize recovery assistant."""
        self.recovery_guides = self._initialize_recovery_guides()
        logger.info("Victim recovery assistant initialized")

    def assess_victim_situation(
        self,
        scam_type: ScamType,
        extracted_entities: List[Dict[str, Any]],
        detection_results: Dict[str, Any],
    ) -> VictimAssessment:
        """
        Assess victim's situation based on scam details.

        Args:
            scam_type: Type of scam
            extracted_entities: Extracted entities (financial, contact, etc.)
            detection_results: Detection pipeline results

        Returns:
            VictimAssessment
        """
        # Determine risk level
        risk_level = self._determine_risk_level(extracted_entities, detection_results)

        # Estimate financial loss
        financial_loss = self._estimate_financial_loss(extracted_entities, scam_type)

        # Identify exposed data
        data_exposed = self._identify_exposed_data(extracted_entities)

        # Determine urgency
        urgency = "immediate" if risk_level == RiskLevel.CRITICAL else "urgent"

        # Identify affected platforms
        affected_platforms = self._identify_affected_platforms(extracted_entities)

        return VictimAssessment(
            scam_type=scam_type,
            risk_level=risk_level,
            financial_loss_estimate=financial_loss,
            data_exposed=data_exposed,
            urgency=urgency,
            affected_platforms=affected_platforms,
        )

    def generate_recovery_plan(
        self,
        assessment: VictimAssessment,
    ) -> Dict[str, Any]:
        """
        Generate personalized recovery plan for victim.

        Args:
            assessment: VictimAssessment from assess_victim_situation

        Returns:
            Recovery plan dict
        """
        plan = {
            "summary": f"You are a victim of {assessment.scam_type.value}. Urgency: {assessment.urgency.upper()}",
            "risk_assessment": {
                "level": assessment.risk_level.value,
                "financial_risk": f"₹{assessment.financial_loss_estimate:,.0f}",
                "data_exposed": assessment.data_exposed,
            },
            "immediate_actions": self._get_immediate_actions(assessment),
            "short_term_actions": self._get_short_term_actions(assessment),
            "long_term_actions": self._get_long_term_actions(assessment),
            "contact_numbers": self._get_emergency_contacts(assessment),
            "support_resources": self._get_support_resources(assessment),
        }

        logger.info(f"Generated recovery plan for {assessment.scam_type.value}")
        return plan

    def _determine_risk_level(
        self,
        extracted_entities: List[Dict[str, Any]],
        detection_results: Dict[str, Any],
    ) -> RiskLevel:
        """Determine risk level based on exposure."""
        risk_score = detection_results.get("final_score", 0)

        financial_entities = [e for e in extracted_entities if e.get("type") in ["upi_id", "amount"]]
        contact_entities = [e for e in extracted_entities if e.get("type") == "phone"]
        sensitive_entities = [e for e in extracted_entities if e.get("type") in ["aadhar", "email"]]

        # Score based on entity types and detection confidence
        exposure_score = (
            (len(financial_entities) * 0.4) +
            (len(contact_entities) * 0.3) +
            (len(sensitive_entities) * 0.3)
        )

        combined_score = (risk_score * 0.6) + (min(exposure_score, 1.0) * 0.4)

        if combined_score > 0.8:
            return RiskLevel.CRITICAL
        elif combined_score > 0.6:
            return RiskLevel.HIGH
        elif combined_score > 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _estimate_financial_loss(
        self,
        extracted_entities: List[Dict[str, Any]],
        scam_type: ScamType,
    ) -> float:
        """Estimate potential financial loss."""
        amounts = [float(e.get("value", 0)) for e in extracted_entities if e.get("type") == "amount"]

        if amounts:
            return sum(amounts)

        # Default estimates by scam type
        estimates = {
            ScamType.UPI_FRAUD: 5000,
            ScamType.PHISHING: 2000,
            ScamType.INVESTMENT: 50000,
            ScamType.ROMANCE: 100000,
            ScamType.EXTORTION: 10000,
            ScamType.TECHNICAL_SUPPORT: 1000,
        }

        return estimates.get(scam_type, 5000)

    def _identify_exposed_data(self, extracted_entities: List[Dict[str, Any]]) -> List[str]:
        """Identify what personal data has been exposed."""
        exposed = []

        entity_type_map = {
            "phone": "Phone number",
            "email": "Email address",
            "upi_id": "UPI/Bank account",
            "url": "Clicked malicious link",
            "aadhar": "Aadhar number",
            "otp": "OTP/2FA code",
            "password": "Password/Credentials",
            "location": "Location data",
        }

        for entity in extracted_entities:
            entity_type = entity.get("type")
            if entity_type in entity_type_map:
                exposed.append(entity_type_map[entity_type])

        return list(set(exposed)) if exposed else ["Account compromised"]

    def _identify_affected_platforms(self, extracted_entities: List[Dict[str, Any]]) -> List[str]:
        """Identify which communication platforms were used."""
        platforms = set()

        # Check for platform indicators in entities
        for entity in extracted_entities:
            context = entity.get("context", "").lower()
            if "whatsapp" in context:
                platforms.add("WhatsApp")
            elif "telegram" in context:
                platforms.add("Telegram")
            elif "facebook" in context or "fb" in context:
                platforms.add("Facebook")
            elif "email" in context or entity.get("type") == "email":
                platforms.add("Email")

        # Default to phone if no platform specified
        if not platforms:
            platforms.add("Phone/SMS")

        return sorted(list(platforms))

    def _get_immediate_actions(self, assessment: VictimAssessment) -> List[Dict[str, str]]:
        """Get immediate actions victim must take."""
        actions = []

        if "Bank account" in assessment.data_exposed or assessment.scam_type == ScamType.UPI_FRAUD:
            actions.extend([
                {
                    "action": "Contact your bank immediately",
                    "urgency": "CRITICAL",
                    "details": "Call your bank's fraud hotline and report the unauthorized transaction",
                },
                {
                    "action": "Block your bank cards/UPI",
                    "urgency": "CRITICAL",
                    "details": "Ask your bank to freeze your accounts and issue new cards",
                },
            ])

        if "OTP/2FA code" in assessment.data_exposed:
            actions.append({
                "action": "Change all passwords",
                "urgency": "CRITICAL",
                "details": "Use a secure device to change all online account passwords",
            })

        if assessment.scam_type in [ScamType.PHISHING, ScamType.EXTORTION]:
            actions.append({
                "action": "Do NOT click any links or download files",
                "urgency": "CRITICAL",
                "details": "Ignore further communications from the scammer",
            })

        actions.append({
            "action": "Document everything",
            "urgency": "HIGH",
            "details": "Save screenshots, messages, call logs, transaction records",
        })

        return actions

    def _get_short_term_actions(self, assessment: VictimAssessment) -> List[Dict[str, str]]:
        """Get short-term (next 24-48 hours) actions."""
        actions = [
            {
                "action": "File FIR (First Information Report)",
                "timeline": "Within 24 hours",
                "details": "Visit your nearest police station or file online at cybercrime.gov.in",
            },
            {
                "action": "Report to Cyber Crime Cell",
                "timeline": "Within 24 hours",
                "details": "File complaint at https://cybercrime.gov.in/",
            },
            {
                "action": "Monitor your bank/email accounts",
                "timeline": "Ongoing",
                "details": "Check for unauthorized transactions, login attempts, or account changes",
            },
            {
                "action": "Check credit reports",
                "timeline": "Within 48 hours",
                "details": "Request credit reports from CIBIL, Equifax, Experian to check for new loans",
            },
        ]

        if assessment.scam_type == ScamType.ROMANCE:
            actions.append({
                "action": "Block the scammer",
                "timeline": "Immediately",
                "details": "Block their phone number, social media accounts, email addresses",
            })

        return actions

    def _get_long_term_actions(self, assessment: VictimAssessment) -> List[Dict[str, str]]:
        """Get long-term (weeks to months) actions."""
        return [
            {
                "action": "Track complaint status",
                "timeline": "Weekly",
                "details": "Follow up with police/cyber cell using your FIR number",
            },
            {
                "action": "Enable two-factor authentication",
                "timeline": "This week",
                "details": "Enable 2FA on all important accounts (email, bank, social media)",
            },
            {
                "action": "Credit freeze",
                "timeline": "This week",
                "details": "Consider placing a credit freeze with credit bureaus",
            },
            {
                "action": "Monitor identity theft",
                "timeline": "Ongoing (6-12 months)",
                "details": "Subscribe to credit monitoring or check reports regularly",
            },
            {
                "action": "Recover funds (if applicable)",
                "timeline": "Ongoing",
                "details": "Work with bank and law enforcement to recover lost funds",
            },
        ]

    def _get_emergency_contacts(self, assessment: VictimAssessment) -> Dict[str, str]:
        """Get emergency contacts for victim."""
        return {
            "cyber_crime_helpline": "1930 or 155260",
            "national_cyber_crime_portal": "https://cybercrime.gov.in/",
            "local_police": "100",
            "ncrb_email": "complaints@icmrweb.org",
            "rbi_grievance": "https://www.rbi.org.in/",
            "banking_ombudsman": "https://www.moneywise.in/",
            "mental_health_support": "AASRA: 9820466726 (24/7)",
        }

    def _get_support_resources(self, assessment: VictimAssessment) -> Dict[str, str]:
        """Get support resources for victim."""
        return {
            "legal_aid": "https://nalsa.gov.in/ - National Legal Services Authority",
            "consumer_court": "https://consumer.gov.in/ - Consumer Grievance Redressal",
            "financial_counseling": "Seek help from bank financial counselor",
            "psychological_support": "Speak with a counselor or therapist about trauma",
            "community_support": "Connect with other scam survivors for support",
            "prevention_guide": "https://www.cybercrime.gov.in/prevention.html",
        }

    def _initialize_recovery_guides(self) -> Dict[ScamType, Dict[str, Any]]:
        """Initialize recovery guides for different scam types."""
        return {
            ScamType.UPI_FRAUD: {
                "description": "Unauthorized UPI/bank transfer fraud",
                "immediate_focus": "Bank account security",
            },
            ScamType.PHISHING: {
                "description": "Deceptive emails/links to steal credentials",
                "immediate_focus": "Password change and malware check",
            },
            ScamType.ROMANCE: {
                "description": "Emotional manipulation for money",
                "immediate_focus": "Block scammer and financial recovery",
            },
            ScamType.INVESTMENT: {
                "description": "Fake investment schemes",
                "immediate_focus": "Recover funds and prevent further losses",
            },
            ScamType.EXTORTION: {
                "description": "Blackmail and threats",
                "immediate_focus": "Police report and safe environment",
            },
        }

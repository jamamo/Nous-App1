import os
from openai import OpenAI

api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
client = OpenAI(api_key=api_key)


def triage_referral(referral_text):
    prompt = f"""
You are a senior NHS sonographer triaging referrals for the Non-Obstetric Ultrasound (NOUS) AQP service.

You must interpret referrals using sound clinical judgment, being pragmatic and not overly cautious.

### TRIAGE PRINCIPLES
- **Accept** referrals that are within AQP NOUS scope, even if minor details are missing, as long as the rationale is clinically appropriate.
- **Request Clarification** only if key details (e.g., side, organ, or clinical context) are truly unclear and could affect safe booking.
- **Reject** only if clearly outside AQP NOUS (e.g., obstetric, vascular, paediatric, or guided procedures).

If the referral indicates urinary, renal, or bladder symptoms, choose **KUB (Kidneys & Bladder)** instead of generic "Abdomen".  
If it relates to abdominal pain, liver, gallbladder, pancreas, or general upper abdominal symptoms, choose **Abdomen**.  
Be as specific as possible when selecting scan types.

### INSTRUCTIONS
Assess the referral under:
1️⃣ Urgency — Routine, Soon, or Urgent.  
2️⃣ Appropriateness — Does it fit AQP NOUS scope?  
3️⃣ Completeness — Are there enough details to book correctly?  
4️⃣ Next Action — Accept / Request Clarification / Reject.  
5️⃣ Recommended Scan Type — choose the *most specific* scan type from the list.  
6️⃣ Rationale — concise explanation for your decision.

### AVAILABLE SCAN TYPES
Abdomen, KUB (Kidneys & Bladder), Pelvis, Testes, Abdo wall/Hernia,
Left/Right foot, groin, hand, hip, knee, shoulder, thigh, wrist, elbow, ankle,
Soft tissue.

### OUTPUT FORMAT
Return your response in this exact format:

---
**Triage Summary**
**Urgency:** [Routine / Soon / Urgent]
**Appropriateness:** [short explanation]
**Completeness:** [brief comment]
**Next Action:** [Accept / Request Clarification / Reject]
**Recommended Scan Type:** [one from list]
**Rationale:** [brief, clinical reasoning — accept if fits AQP NOUS criteria]
---

Referral content:
{referral_text}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a pragmatic, NHS-compliant ultrasound triage assistant. "
                    "If the referral rationale is clinically sound and within AQP NOUS scope, "
                    "default to 'Accept' and recommend the correct scan type (e.g., KUB for UTI/renal symptoms)."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.25,
    )

    return completion.choices[0].message.content.strip()

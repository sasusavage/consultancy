"""
Seed script for Comfydoe.
Seeds both Lead data and all Homepage content into the database.
Run: python seed.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

from app import app, db
from models import Lead, SiteContent

def seed_leads():
    """Seed the database with initial lead data."""
    leads = [
        Lead(
            full_name='Al-Khalifa Logistics Group',
            email='ops@alkhalifa.ae',
            service='Logistics',
            status='New',
            message='Seeking a strategic partner for our West African freight corridor expansion. Volume: 200+ TEU monthly.'
        ),
        Lead(
            full_name='Ethereal Ventures Capital',
            email='deal@etherealvc.com',
            service='Consultancy',
            status='Qualified',
            message='Interested in a market-entry feasibility study for the ECOWAS region. Budget pre-approved.'
        ),
        Lead(
            full_name='Sino-Zheng Import/Export Ltd',
            email='trade@sinozheng.cn',
            service='Trade',
            status='Processing',
            message='Need compliance advisory for our new electronics import line into Ghana and Nigeria.'
        ),
        Lead(
            full_name='Nordic Retail Group AB',
            email='supply@nordicretail.se',
            service='Merchandise',
            status='Urgent',
            message='Urgent: require 5,000 units of general merchandise sourced from verified suppliers. Deadline: Q2.'
        ),
        Lead(
            full_name='Sahara Holdings Inc.',
            email='ceo@saharaholdings.com',
            service='Consultancy',
            status='New',
            message='Requesting a full operational audit of our supply chain across 3 subsidiaries.'
        ),
        Lead(
            full_name='Maersk Africa Division',
            email='partnerships@maersk.com',
            service='Logistics',
            status='Qualified',
            message='Exploring joint ventures for last-mile delivery solutions in Accra and Lagos.'
        ),
    ]

    existing = Lead.query.count()
    if existing == 0:
        for lead in leads:
            db.session.add(lead)
        db.session.commit()
        print(f"[OK] Seeded {len(leads)} leads.")
    else:
        print(f"[SKIP] {existing} leads already exist.")


def seed_content():
    """Seed all homepage content into the database so nothing is hardcoded."""
    defaults = {
        'hero_title': 'Turning Global Vision into <span class="text-gradient-gold">Operational Reality.</span>',
        'hero_subtitle': 'Comfort Doe provides elite consultancy, seamless logistics, and global trade solutions designed for the modern enterprise.',
        'hero_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDn3m5r3s6273e6JdLjmFNjR3hM0qkBmj32tvOSUs-eLldiAXgu4jal1mpDi1_fNagFLgMgb2j7_3huXSpI7kBCLVuUf2Bln_YXAptl2r5xIUJVt_paek1MDWi7X1vDaoOWq8ya2NEZKyMm8BtR17rTMo8b8NXuKBBUa8VB8nHU5324UDR-EBcWoyYKtlazmDoMRGH8H1gIukBdXezHrmo3FdSAE4PwX3g4H4cLRyv3Ur2jEA99hedKn3PkJF2GnSZbPWOiX3AkxIM',
        'about_text': "Comfort Doe is a distinguished leader in Africa's trade and consultancy landscape. As the founder of Comfydoe, she integrates strategic insight with hands-on operational expertise to help businesses bridge the gap between local potential and global markets.\n\nHer philosophy centers on \"Operational Sovereignty\" — the belief that a business's strength is defined by the resilience and autonomy of its core systems.",
        'about_quote': "Global trade isn't just about moving goods; it's about honoring the vision behind the product.",
        'about_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCGP9ArOTjl5PP1NlvIsb-SQoNkBV9NiGbeZ9WMgaHsyzAWdY_GYntW02AsnbUPtRl9_BURRqSpGu2b2YjBgZpnIMVaBA3fw06Lbp6neiE6n39AwdF5XROnAPeLldzqak1_TZzgXLIRavn3Ksih8VOdBFVkIc93bf2Wo1_Nlw78rd9m8snh-vX-1d_JKzJxGEpxo_Uyo2EcNDnexajRxZlg3KwnlRPeFujU18WX3M5-jPZWBzNrqRSAd4-5KdKb4R96_z4xBQd63_E',
        'strategy_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuBQyXQCAO8qxTmmkyGHwr0WNWMQaeuq1HlLcPVgRkfKXhpdmREs3lhtEN48q2iGRGnDE9ello940cubG2MY2x7jQhBcTCu-UYK9ecbQptEPOhvjTtpNFyQfhFZ-4tS_53h9jNL9jpAwH_tswEys4SLhvPBh9lIPFHFB6SMTB37Ydj-NwRs12RHo9Q9_Z1GwcINxy0FYZX6Y8vp9etR9S97kfaL3mwyxWq7x3CHl9qEMIHuxTjnGsRnqdrtAUTxrmcHWRrfjJXAP5wA',
        'logistics_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCkCFOwbrPeMRretclKPzV1kr32KDpOxGW4LcPuAK0HIbMtX5aJLXAfDwBsVaqltzd8jn09yyKHVcRjf8ko3YMHkc7kamucQAtjfKqpE3qSGif8d5-NpAsPObLeDfMDX8ndVI9yhcnw4NtNo190RfrUofmkRfs7VsYCfeayynEmj0ETFS4noF8-NRnCpE_64WybCOc6vcDB5IPDeurnWgvkIchHW944qjufWYF88YnOgfVsFt8dj5ndruxyX_QSPkwirIn5_gODO80',
        'contact_email': 'advisory@comfydoe.pro',
        'contact_phone': '+1 (555) COMFYDOE',
    }

    seeded = 0
    for key, value in defaults.items():
        existing = SiteContent.query.filter_by(key=key).first()
        if not existing:
            item = SiteContent(key=key, value=value)
            db.session.add(item)
            seeded += 1

    if seeded > 0:
        db.session.commit()
        print(f"[OK] Seeded {seeded} content entries.")
    else:
        print(f"[SKIP] All {len(defaults)} content entries already exist.")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("--- Seeding Leads ---")
        seed_leads()
        print("--- Seeding Homepage Content ---")
        seed_content()
        print("--- Done! ---")

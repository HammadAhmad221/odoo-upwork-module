{
    'name': 'Upwork Bid Tracker',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Track Upwork bids with Kanban and one-click CRM conversion',
    'description': """
Upwork Bid Tracker
==================
Manage high-volume Upwork bidding workflow:

* Kanban board with configurable stages
* Track multiple bidder profiles (Awais, Zain, Wahab, etc.)
* Separate fields for client budget vs. our proposed budget
* One-click conversion to CRM opportunity
* Per-bidder analytics and reporting
* Three-tab form: Job & Client / Proposal / Business Dev
    """,
    'author': 'Your Company',
    'website': '',
    'depends': ['base', 'mail', 'crm', 'hr', 'contacts'],
    'data': [
        # Security first
        'security/upwork_security.xml',
        'security/ir.model.access.csv',
        'security/upwork_record_rules.xml',
        # Sequences and seed data
        'data/upwork_sequence_data.xml',
        'data/upwork_bid_stage_data.xml',
        'data/upwork_profile_data.xml',
        # Views (config models first, then main)
        'views/upwork_bid_stage_views.xml',
        'views/upwork_profile_views.xml',
        'views/upwork_category_views.xml',
        'views/upwork_skill_tag_views.xml',
        'views/upwork_cover_template_views.xml',
        'views/upwork_bid_views.xml',
        'views/crm_lead_views.xml',
        'views/menus.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

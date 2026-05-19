from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class UpworkBid(models.Model):
    _name = 'upwork.bid'
    _description = 'Upwork Bid'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'submitted_date desc, id desc'
    _rec_name = 'name'

    # ============================================================
    #  HEADER / COMMON
    # ============================================================
    name = fields.Char(string='Job Title', required=True, tracking=True)
    reference = fields.Char(
        string='Reference', readonly=True, copy=False,
        default=lambda self: _('New'),
    )
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Good Fit'),
        ('2', 'Hot Lead'),
        ('3', 'Must Win'),
    ], default='0', tracking=True)
    company_id = fields.Many2one(
        'res.company', default=lambda s: s.env.company
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda s: s.env.ref('base.USD').id,
    )
    stage_id = fields.Many2one(
        'upwork.bid.stage', string='Stage',
        ondelete='restrict', tracking=True,
        group_expand='_read_group_stage_ids',
        default=lambda self: self._default_stage_id(),
    )
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked'),
    ], default='normal')

    # ============================================================
    #  SECTION 1 — JOB DETAILS + CLIENT DETAILS
    # ============================================================
    # --- Job ---
    job_url = fields.Char(string='Upwork Job URL')
    job_description = fields.Html(string='Job Description')
    job_type = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('hourly', 'Hourly'),
    ], string='Job Type', default='hourly')
    job_category_id = fields.Many2one('upwork.category', string='Category')
    skill_tag_ids = fields.Many2many(
        'upwork.skill.tag', string='Skills Required'
    )
    experience_level = fields.Selection([
        ('entry', 'Entry'),
        ('inter', 'Intermediate'),
        ('expert', 'Expert'),
    ], string='Experience Level')
    job_duration = fields.Selection([
        ('lt1m', 'Less than 1 month'),
        ('1to3', '1 to 3 months'),
        ('3to6', '3 to 6 months'),
        ('gt6', 'More than 6 months'),
    ], string='Job Duration')
    job_posted_date = fields.Datetime(string='Job Posted On')

    # CRITICAL: the CLIENT's budget — what they posted on Upwork
    client_budget = fields.Monetary(
        string='Client Budget',
        help='Budget the client posted on Upwork (minimum if a range).',
    )
    client_budget_max = fields.Monetary(
        string='Client Budget (Max)',
        help='Upper range — used for hourly jobs with min-max budgets.',
    )

    # --- Client ---
    client_name = fields.Char(string='Client Name')
    client_country_id = fields.Many2one(
        'res.country', string='Client Country'
    )
    client_total_spent = fields.Monetary(
        string='Client Total Spent on Upwork'
    )
    client_hire_rate = fields.Float(string='Client Hire Rate (%)')
    client_rating = fields.Float(string='Client Rating')
    client_reviews_count = fields.Integer(string='Client Reviews')
    client_jobs_posted = fields.Integer(string='Total Jobs Posted')
    client_payment_verified = fields.Boolean(string='Payment Verified')
    client_member_since = fields.Date(string='Client Member Since')

    # ============================================================
    #  SECTION 2 — PROPOSAL DETAILS
    # ============================================================
    proposal_description = fields.Html(
        string='Proposal / Cover Letter',
        help='The actual text submitted in the proposal.',
    )
    # CRITICAL: OUR proposed amount — separate from client_budget
    proposed_budget = fields.Monetary(
        string='Our Proposed Budget',
        help='The amount WE quoted in our proposal.',
        tracking=True,
    )
    proposed_rate_type = fields.Selection([
        ('hourly', 'Per Hour'),
        ('fixed', 'Fixed Total'),
        ('milestone', 'Per Milestone'),
    ], string='Rate Type', default='hourly')
    proposed_timeline = fields.Char(
        string='Proposed Timeline',
        help='e.g. "2 weeks", "1 month MVP + ongoing"',
    )
    connects_used = fields.Integer(string='Connects Used', tracking=True)
    boosted_bid = fields.Boolean(string='Boosted Proposal')
    boost_connects = fields.Integer(string='Boost Connects Spent')
    total_connects = fields.Integer(
        string='Total Connects',
        compute='_compute_total_connects', store=True,
    )
    cover_template_id = fields.Many2one(
        'upwork.cover.template', string='Template Used'
    )
    attachments_sent = fields.Integer(string='Attachments Sent')
    screening_answers = fields.Html(string='Screening Questions Answered')

    # Computed budget gap analysis
    budget_variance = fields.Monetary(
        string='Variance vs Client Budget',
        compute='_compute_budget_variance', store=True,
        help='Our proposed budget minus client budget. Positive = we bid above.',
    )

    # ============================================================
    #  SECTION 3 — BUSINESS DEVELOPMENT DETAILS
    # ============================================================
    # Which freelancer profile submitted this bid (Awais / Zain / Wahab)
    upwork_profile_id = fields.Many2one(
        'upwork.profile',
        string='Submitted From Profile',
        required=True, tracking=True,
        help='Which freelancer profile actually submitted this proposal.',
    )
    bidder_id = fields.Many2one(
        'hr.employee', string='Bidder',
        default=lambda s: s.env.user.employee_id,
        tracking=True,
    )
    bidder_user_id = fields.Many2one(
        'res.users', string='Assignee',
        default=lambda s: s.env.user,
        tracking=True,
    )
    team_id = fields.Many2one('crm.team', string='BD Team')

    # ============================================================
    #  TRACKING
    # ============================================================
    submitted_date = fields.Datetime(
        string='Submitted On',
        default=fields.Datetime.now, tracking=True,
    )
    viewed_date = fields.Datetime(string='Viewed by Client')
    replied_date = fields.Datetime(string='Client Replied On')
    interview_date = fields.Datetime(string='Interview Scheduled')
    closed_date = fields.Datetime(string='Closed On')
    total_proposals = fields.Integer(string='Competing Proposals')

    response_time_hours = fields.Float(
        string='Response Time (hrs)',
        compute='_compute_response_time', store=True,
    )
    days_since_submission = fields.Integer(
        string='Days Since Submission',
        compute='_compute_days_since_submission',
    )

    # ============================================================
    #  OUTCOME
    # ============================================================
    outcome = fields.Selection([
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('no_response', 'No Response'),
        ('withdrawn', 'Withdrawn'),
    ], default='pending', tracking=True)
    lost_reason_id = fields.Many2one('crm.lost.reason', string='Lost Reason')
    final_contract_value = fields.Monetary(string='Final Contract Value')
    notes = fields.Html(string='Internal Notes')

    # ============================================================
    #  CRM LINK
    # ============================================================
    crm_lead_id = fields.Many2one(
        'crm.lead', string='CRM Opportunity',
        readonly=True, copy=False,
    )
    partner_id = fields.Many2one('res.partner', string='Client Contact')
    converted_to_crm = fields.Boolean(
        compute='_compute_converted_to_crm', store=True,
    )
    conversion_date = fields.Datetime(
        string='Conversion Date', readonly=True
    )

    # ============================================================
    #  CONSTRAINTS
    # ============================================================
    _sql_constraints = [
        ('unique_bid_per_profile',
         'UNIQUE(job_url, upwork_profile_id)',
         'A bid for this job from this profile already exists.'),
    ]

    # ============================================================
    #  DEFAULTS & COMPUTES
    # ============================================================
    @api.model
    def _default_stage_id(self):
        return self.env['upwork.bid.stage'].search(
            [], limit=1, order='sequence'
        )

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env['upwork.bid.stage'].search([], order='sequence')

    @api.depends('connects_used', 'boost_connects')
    def _compute_total_connects(self):
        for rec in self:
            rec.total_connects = (
                (rec.connects_used or 0) + (rec.boost_connects or 0)
            )

    @api.depends('client_budget', 'proposed_budget')
    def _compute_budget_variance(self):
        for rec in self:
            rec.budget_variance = (
                (rec.proposed_budget or 0) - (rec.client_budget or 0)
            )

    @api.depends('submitted_date', 'replied_date')
    def _compute_response_time(self):
        for rec in self:
            if rec.submitted_date and rec.replied_date:
                delta = rec.replied_date - rec.submitted_date
                rec.response_time_hours = delta.total_seconds() / 3600.0
            else:
                rec.response_time_hours = 0.0

    def _compute_days_since_submission(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.submitted_date:
                rec.days_since_submission = (now - rec.submitted_date).days
            else:
                rec.days_since_submission = 0

    @api.depends('crm_lead_id')
    def _compute_converted_to_crm(self):
        for rec in self:
            rec.converted_to_crm = bool(rec.crm_lead_id)

    # ============================================================
    #  CRUD
    # ============================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'upwork.bid'
                ) or _('New')
        return super().create(vals_list)

    # ============================================================
    #  ACTIONS
    # ============================================================
    def action_convert_to_crm(self):
        """Create a crm.lead from this bid and link them."""
        self.ensure_one()
        if self.crm_lead_id:
            raise UserError(
                _('This bid is already linked to CRM opportunity: %s')
                % self.crm_lead_id.name
            )

        # Find or create partner
        partner = self.partner_id
        if not partner and self.client_name:
            partner = self.env['res.partner'].create({
                'name': self.client_name,
                'country_id': self.client_country_id.id,
                'comment': f'Created from Upwork bid: {self.reference}',
            })

        # Build description
        description_parts = [
            f'<p><b>Source:</b> Upwork Bid {self.reference}</p>',
        ]
        if self.job_url:
            description_parts.append(
                f'<p><b>Job URL:</b> <a href="{self.job_url}" '
                f'target="_blank">{self.job_url}</a></p>'
            )
        if self.upwork_profile_id:
            description_parts.append(
                f'<p><b>Submitted from profile:</b> '
                f'{self.upwork_profile_id.name}</p>'
            )
        description_parts.append(
            f'<p><b>Client Budget:</b> {self.client_budget or 0} '
            f'{self.currency_id.name}</p>'
        )
        description_parts.append(
            f'<p><b>Our Proposed Budget:</b> {self.proposed_budget or 0} '
            f'{self.currency_id.name}</p>'
        )
        if self.proposed_timeline:
            description_parts.append(
                f'<p><b>Proposed Timeline:</b> {self.proposed_timeline}</p>'
            )
        if self.proposal_description:
            description_parts.append('<p><b>Our Proposal:</b></p>')
            description_parts.append(self.proposal_description)
        if self.job_description:
            description_parts.append('<hr/><p><b>Original Job Description:</b></p>')
            description_parts.append(self.job_description)

        # Expected revenue: prefer proposed_budget, fall back to client_budget
        expected_revenue = self.proposed_budget or self.client_budget or 0
        # If hourly, rough estimate of monthly value
        if self.job_type == 'hourly' and expected_revenue:
            expected_revenue = expected_revenue * 40 * 4  # ~hours/week * weeks

        # CRM tags from skill tags
        crm_tag_ids = self.skill_tag_ids.mapped('crm_tag_id').ids

        lead_vals = {
            'name': self.name,
            'type': 'opportunity',
            'partner_id': partner.id if partner else False,
            'contact_name': self.client_name,
            'country_id': self.client_country_id.id,
            'expected_revenue': expected_revenue,
            'user_id': self.bidder_user_id.id,
            'team_id': self.team_id.id if self.team_id else False,
            'description': '\n'.join(description_parts),
            'upwork_bid_id': self.id,
        }
        if crm_tag_ids:
            lead_vals['tag_ids'] = [(6, 0, crm_tag_ids)]

        lead = self.env['crm.lead'].create(lead_vals)

        # Move to "Moved to CRM" stage if it exists
        moved_stage = self.env['upwork.bid.stage'].search(
            [('is_moved_to_crm', '=', True)], limit=1
        )
        update_vals = {
            'crm_lead_id': lead.id,
            'partner_id': partner.id if partner else False,
            'conversion_date': fields.Datetime.now(),
        }
        if moved_stage:
            update_vals['stage_id'] = moved_stage.id
        self.write(update_vals)

        self.message_post(
            body=_('Bid converted to CRM Opportunity: %s') % lead.name
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _('CRM Opportunity'),
            'res_model': 'crm.lead',
            'res_id': lead.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_crm_lead(self):
        self.ensure_one()
        if not self.crm_lead_id:
            raise UserError(_('No CRM opportunity linked.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'res_id': self.crm_lead_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_mark_won(self):
        won_stage = self.env['upwork.bid.stage'].search(
            [('is_won', '=', True)], limit=1
        )
        vals = {'outcome': 'won', 'closed_date': fields.Datetime.now()}
        if won_stage:
            vals['stage_id'] = won_stage.id
        self.write(vals)

    def action_mark_lost(self):
        lost_stage = self.env['upwork.bid.stage'].search(
            [('is_lost', '=', True)], limit=1
        )
        vals = {'outcome': 'lost', 'closed_date': fields.Datetime.now()}
        if lost_stage:
            vals['stage_id'] = lost_stage.id
        self.write(vals)

    # ============================================================
    #  SCHEDULED JOB
    # ============================================================
    @api.model
    def _cron_archive_stale_bids(self):
        """Move bids with no activity for 14+ days to 'No Response'."""
        cutoff = fields.Datetime.now() - timedelta(days=14)
        no_response_stage = self.env['upwork.bid.stage'].search(
            [('is_no_response', '=', True)], limit=1
        )
        if not no_response_stage:
            return
        stale = self.search([
            ('submitted_date', '<', cutoff),
            ('replied_date', '=', False),
            ('outcome', '=', 'pending'),
            ('converted_to_crm', '=', False),
            ('stage_id', '!=', no_response_stage.id),
        ])
        stale.write({
            'stage_id': no_response_stage.id,
            'outcome': 'no_response',
        })

from odoo import fields, models


class UpworkProfile(models.Model):
    _name = 'upwork.profile'
    _description = 'Upwork Freelancer Profile'
    _order = 'sequence, name'

    name = fields.Char(string='Profile Name', required=True)
    sequence = fields.Integer(default=10)
    username = fields.Char(string='Upwork Username')
    profile_url = fields.Char(string='Profile URL')
    profile_type = fields.Selection([
        ('freelancer', 'Freelancer'),
        ('agency', 'Agency'),
    ], default='freelancer', string='Profile Type')
    employee_id = fields.Many2one(
        'hr.employee', string='Default Bidder',
        help='Person who manages this profile by default'
    )
    connects_balance = fields.Integer(string='Connects Balance')
    monthly_refill = fields.Integer(string='Monthly Refill', default=10)
    hourly_rate_default = fields.Monetary(string='Default Hourly Rate')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.USD').id,
    )
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color')
    notes = fields.Text()
    bid_count = fields.Integer(
        string='Bids', compute='_compute_bid_count'
    )

    def _compute_bid_count(self):
        for rec in self:
            rec.bid_count = self.env['upwork.bid'].search_count(
                [('upwork_profile_id', '=', rec.id)]
            )

    def action_view_bids(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Bids from {self.name}',
            'res_model': 'upwork.bid',
            'view_mode': 'kanban,list,form',
            'domain': [('upwork_profile_id', '=', self.id)],
            'context': {'default_upwork_profile_id': self.id},
        }

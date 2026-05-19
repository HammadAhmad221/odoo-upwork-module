from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    upwork_bid_id = fields.Many2one(
        'upwork.bid', string='Source Upwork Bid',
        readonly=True, copy=False,
    )
    is_from_upwork = fields.Boolean(
        compute='_compute_is_from_upwork', store=True,
    )

    @api.depends('upwork_bid_id')
    def _compute_is_from_upwork(self):
        for lead in self:
            lead.is_from_upwork = bool(lead.upwork_bid_id)

    def action_view_upwork_bid(self):
        self.ensure_one()
        if not self.upwork_bid_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'upwork.bid',
            'res_id': self.upwork_bid_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

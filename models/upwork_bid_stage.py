from odoo import fields, models


class UpworkBidStage(models.Model):
    _name = 'upwork.bid.stage'
    _description = 'Upwork Bid Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded in Kanban')
    description = fields.Text(string='Description')
    # Behavioral flags used by automation
    is_replied = fields.Boolean(string='Client Replied Stage')
    is_moved_to_crm = fields.Boolean(string='Moved to CRM Stage')
    is_no_response = fields.Boolean(string='No Response Stage')
    is_won = fields.Boolean(string='Won Stage')
    is_lost = fields.Boolean(string='Lost Stage')

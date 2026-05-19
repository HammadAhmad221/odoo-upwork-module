from odoo import api, fields, models


class UpworkCoverTemplate(models.Model):
    _name = 'upwork.cover.template'
    _description = 'Upwork Cover Letter Template'
    _order = 'name'

    name = fields.Char(required=True)
    category_id = fields.Many2one('upwork.category', string='Best For')
    body = fields.Html(required=True)
    active = fields.Boolean(default=True)
    usage_count = fields.Integer(
        string='Times Used', compute='_compute_stats', store=False
    )
    win_count = fields.Integer(
        string='Times Won', compute='_compute_stats', store=False
    )
    win_rate = fields.Float(
        string='Win Rate (%)', compute='_compute_stats', store=False
    )

    def _compute_stats(self):
        Bid = self.env['upwork.bid']
        for tpl in self:
            bids = Bid.search([('cover_template_id', '=', tpl.id)])
            tpl.usage_count = len(bids)
            tpl.win_count = len(bids.filtered(lambda b: b.outcome == 'won'))
            tpl.win_rate = (
                (tpl.win_count / tpl.usage_count * 100)
                if tpl.usage_count else 0.0
            )

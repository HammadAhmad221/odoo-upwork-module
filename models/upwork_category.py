from odoo import fields, models


class UpworkCategory(models.Model):
    _name = 'upwork.category'
    _description = 'Upwork Job Category'
    _parent_store = True
    _order = 'name'

    name = fields.Char(required=True)
    parent_id = fields.Many2one(
        'upwork.category', string='Parent Category', ondelete='cascade'
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        'upwork.category', 'parent_id', string='Subcategories'
    )
    color = fields.Integer()
    active = fields.Boolean(default=True)

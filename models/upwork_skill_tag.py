from odoo import fields, models


class UpworkSkillTag(models.Model):
    _name = 'upwork.skill.tag'
    _description = 'Upwork Skill Tag'
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer()
    category_id = fields.Many2one('upwork.category', string='Category')
    crm_tag_id = fields.Many2one(
        'crm.tag', string='Linked CRM Tag',
        help='When a bid is converted to a CRM opportunity, this CRM tag is applied.'
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_skill_name', 'UNIQUE(name)', 'Skill name must be unique.')
    ]

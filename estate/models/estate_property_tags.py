from odoo import models, fields


class estate_property_tag(models.Model):
    _name = "tags"
    _description = "property character description"
    _order = "name desc"

    name = fields.Char('tag', required=True, default='Mec faut écrire un Tag')
    color = fields.Integer(string='Color Index', default=1)

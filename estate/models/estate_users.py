from odoo import fields, models

class Users(models.Model):
    _inherit = "res.users"


    property_ids = fields.One2many('propriete', 'vendeur', string='Properties', domain=['|',('status', '=', 'new'),('status', '=', 'offer_')] )





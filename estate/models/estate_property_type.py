from odoo import models, fields


class estate_property_type(models.Model):
    _name = "type"
    _description = "property type description"

    name = fields.Char('Type', required=True, default='Mec faut écrire un type')


    property_ids = fields.One2many('propriete', 'property_type_id', string='Properties')

    offers_ids = fields.One2many('offer', 'property_type_id', string='Offers')

    offer_count = fields.Integer('Offer count', compute='_compute_offer_count')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Le type de la propriété doit être unique')
    ]

    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offers_ids)

    def action_view_offers(self):
        return {
            'name': 'Offers',
            'type': 'ir.actions.act_window',
            'res_model': 'offer',
            'view_mode': 'tree,form',
            'context': {'create': False},
            'domain': [('property_type_id', '=', self.id)],
        }

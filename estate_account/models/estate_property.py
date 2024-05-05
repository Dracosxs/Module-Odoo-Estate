from odoo import models, fields, api


class estate_property(models.Model):
    _inherit = 'propriete'

    def action_sold(self):
        partener_id = self.acheteur_id.id
        move_type = 'out_invoice'

        # Create invoice
        invoice_vals = {

            'partner_id': partener_id,
            'move_type': move_type,

            'narration': 'Facture pour la vente de la propriété ' + self.name,
        }

        # Create invoice lines
        invoice = self.env['account.move'].create(invoice_vals)
        invoice_lines = [
            {
                'name': 'Prix de vente',
                'quantity': 1,
                'price_unit': self.expected_price,
            },
            {
                'name': 'Commission ',
                'quantity': 1,
                'price_unit': self.expected_price * 0.06,
            },
            {
                'name': 'Frais administratifs',
                'quantity': 1,
                'price_unit': 100.00,
            }
        ]

        # Add invoice lines to invoice
        invoice.write({'invoice_line_ids': [(0, 0, line) for line in invoice_lines]})

        res = super(estate_property, self).action_sold()

        return res

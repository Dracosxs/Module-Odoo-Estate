from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class estate_property_offer(models.Model):
    _name = "offer"
    _description = "Property Offer"
    _order = "price desc"

    price = fields.Float('Prix proposé')

    #Should have been set to required=True
    partner_id = fields.Many2one('res.partner', string="Acheteur", required=False)

    property_id = fields.Many2one('propriete', string='Proprieté de l\'offre', required=True, ondelete='cascade')

    validity = fields.Integer('Validité de l\'offre', default=7)

    property_type_id = fields.Many2one(related='property_id.property_type_id', string="Property Type", store=True)

    statusOffer = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ], string='Status de l\'offre', copy=False, readonly=True)

    property_status = fields.Selection(related='property_id.status', string="Property Status", readonly=True,
                                       store=True)

    total_offer = fields.Integer('Total Offer', compute='_compute_total_offer', store=True)

    date_deadline = fields.Date('Date limite de disponibilité', compute='_compute_date_deadline', store=True,
                                inverse='_inverse_validity')

    @api.model
    def unlink(self):
        property_ids = self.mapped('property_id')
        res = super(estate_property_offer, self).unlink()
        for property_id in property_ids:
            property_id._update_property_status()
        return res


    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.validity:
                record.date_deadline = fields.Date.today() + relativedelta(days=record.validity)

    @api.depends('date_deadline')
    def _inverse_validity(self):
        for record in self:
            if record.date_deadline:
                today = fields.Date.today()
                validity_days = (record.date_deadline - today).days
                record.validity = validity_days


    @api.constrains('price')
    def _check_price(self):
        for record in self:
            #if a price exists, then a offer exists
            record.property_id.status = 'offer_received'
            if not record.property_id:
                raise models.ValidationError('Vous devez spécifier une propriété pour cette offre')
            if fields.float_is_zero(record.property_id.expected_price, precision_digits=2):
                raise models.ValidationError(
                    'Il doit exister un prix de vente attendu pour cette propriété avant de pouvoir faire une offre')
            # Offer limited to 90% of base price
            if record.price < record.property_id.expected_price * 0.9:
                raise models.ValidationError(
                    'Le prix proposé ne peut pas être inférieur à 90% du prix de vente attendu')
            #The price of the new offer must be higher than the last offer
            other_offers = self.env['offer'].search([('property_id', '=', record.property_id.id)])
            if other_offers:
                if record.price < max(other_offers.mapped('price')):
                    raise models.ValidationError(
                        'Le prix proposé ne peut pas être inférieur à celui d\'une offre existante')



    def action_yes(self):
        for record in self:
            if record.property_id.status == 'cancel' or record.property_id.status == 'sold':
                raise models.ValidationError(
                    'Vous ne pouvez pas accepter une offre pour une propriété annulée ou vendue')
            else:
                record.statusOffer = 'accepted'
            #Mark all other offers for the same property as refused
            other_offers = self.env['offer'].search(
                [('property_id', '=', self.property_id.id), ('id', '!=', self.id)])
            other_offers.write({'statusOffer': 'refused'})
            for property in record.property_id:
                property.status = 'offer_accepted'
                property.prix_vente_final = record.price
                property.acheteur_id = record.partner_id


    def action_no(self):
        for record in self:
            if record.property_id.status == 'cancel' or record.property_id.status == 'sold':
                raise models.ValidationError(
                    'Vous ne pouvez pas accepter une offre pour une propriété annulée ou vendue')
            else:
                record.statusOffer = 'refused'
                for property in record.property_id:
                    property.prix_vente_final = "0"
                    property.acheteur_id = ""
                if record.property_id:
                    record.property_id.status = 'offer_received'


    @api.depends('property_id')
    def _compute_total_offer(self):
        for record in self:
            total_offers = self.env['offer'].search_count([('property_id', '=', record.property_id.id)])
            record.total_offer = total_offers
            if total_offers == 0:
                record.property_id.status = 'new'













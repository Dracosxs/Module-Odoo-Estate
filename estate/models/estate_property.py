from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError


class estate_property(models.Model):
    _name = "propriete"
    _description = "property description"
    _order = "id desc"

    name = fields.Char('Titre', required=True, default='Mec faut écrire un titre')

    description = fields.Text('Description du bien', default='Ceci est une description du bien')

    postal_code = fields.Char('Code postal', size=5, required=False)

    expected_price = fields.Float('Prix demandé', required=True)

    garden_area = fields.Float('Surface du jardin', required=True, default=0.0)

    living_area = fields.Float('Surface habitable', required=True, default=9.0)

    garden_orientation = fields.Selection([
        ('north', 'Nord'),
        ('south', 'Sud'),
        ('east', 'Est'),
        ('west', 'Ouest'),
    ], string='Orientation jardin')

    facades = fields.Integer('Façades', default=4)

    bedrooms = fields.Integer('Nombre de chambres', default=2)

    bathrooms = fields.Integer('Nombre de salles de bain', default=1)

    garage = fields.Boolean('Garage disponible', default=False)

    garden = fields.Boolean('Garden', default=False)

    active = fields.Boolean('Active', default=True,
                            help="The active field allows you to hide the property without removing it.")

    prix_vente_final = fields.Float('Prix de vente final', readonly=True)

    post_date = fields.Date('Date de mise en ligne', default=fields.Date.today, readonly=True)

    status = fields.Selection([
        ('new', 'Nouveau'),
        ('offer_received', 'Offre reçue'),
        ('offer_accepted', 'Offre acceptée'),
        ('sold', 'Vendu'),
        ('canceled', 'Annulé')
    ], string='Statut', default='new', help='oueeeeeeeeeeeeeeeeee.csv du help', required=True, copy=False)

    property_type_id = fields.Many2one('type', string='Type de bien', required=False, ondelete='cascade')

    vendeur = fields.Many2one('res.users', string='Responsable', required=True, default=lambda self: self.env.user)

    vendeur_id = fields.Char(related='vendeur.name', string='Vendeur', store=True, readonly=True)

    acheteur_id = fields.Many2one('res.partner', string="Acheteur", copy=False)

    tags_ids = fields.Many2many('tags', string='Tags habitat')

    offres_ids = fields.One2many("offer", "property_id", string="offre pour cette propriété")

    best_offer = fields.Float('Meilleure offre', compute='_get_best_offer')

    disponibility = fields.Date('Disponible jusqu\'a', compute='_compute_disponibility', store=True)

    total_area = fields.Float('Surface totale', compute='_totalArea_total', store=True)

    _sql_constraints = [('name_uniq', 'CHECK(facades)>= 3', 'Le nombre de façades doit être supérieur ou égal à 3'),
                        ('name_uniq', 'CHECK(expected_price>=0)', 'Le prix demandé doit être supérieur ou égal à 0'),
                        ('prix_vente_final_uniq', 'CHECK(prix_vente_final>=0)',
                         'Le prix de vente final doit être supérieur ou égal à 0'),
                        (
                        'bedrooms_uniq', 'CHECK(bedrooms>=0)', 'Le nombre de chambres doit être supérieur ou égal à 0'),
                        ('bathrooms_uniq', 'CHECK(bathrooms>=0)',
                         'Le nombre de salles de bain doit être supérieur ou égal à 0'),
                        ('garden_area_uniq', 'CHECK(garden_area>=0)',
                         'La surface du jardin doit être supérieur ou égal à 0'),
                        ('living_area_uniq', 'CHECK(living_area>=0)',
                         'La surface habitable doit être supérieur ou égal à 0'),
                        ('name_uniq', 'UNIQUE(name)', 'Le titre de la propriété doit être unique')
                        ]


    @api.ondelete(at_uninstall=False)
    def _unlink_if_property_new_or_canceled(self):
        for record in self:
            if record.status not in ('new', 'canceled'):
                raise UserError('Vous ne pouvez pas supprimer une propriété qui n\'est pas nouvelle ou annulée')
        return super(estate_property, self).unlink()


    @api.depends("living_area", "garden_area")
    def _totalArea_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offres_ids.price')
    def _get_best_offer(self):
        for record in self:
            best_offer = 0
            for offer in record.offres_ids:
                if offer.price > best_offer:
                    best_offer = offer.price
            record.best_offer = best_offer

    @api.depends('offres_ids.price')
    def _get_best_offer2(self):
        for record in self:
            record.best_offer = max(record.offres_ids.mapped('price'))

    @api.depends('post_date')
    def _compute_disponibility(self):
        for record in self:
            if record.post_date:
                record.disponibility = record.post_date + relativedelta(months=3)


    @api.depends('offres_ids', 'offres_ids.statusOffer')
    def _update_property_status(self):
        for record in self:
            # Vérifie si toutes les offres sont refusées ou s'il n'y a pas d'offres
            all_offers_no_offers = not record.offres_ids
            if all_offers_no_offers:
                record.status = 'new'

    @api.onchange('garden')
    def _onchange_garden_id(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for record in self:
            if record.status == 'canceled':
                raise UserError('Vous ne pouvez pas vendre une propriété annulée')
            record.status = 'sold'
            record.active = False

    def action_canceled(self):
        for record in self:
            if record.status == 'sold':
                raise UserError('Vous ne pouvez pas annuler une propriété vendue')
            record.status = 'canceled'
            record.active = False



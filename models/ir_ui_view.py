from odoo import models, fields


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('lem_calendar', 'LEM Calendar')])

    def _get_view_info(self):
        return {'lem_calendar': {'icon': 'fa fa-calendar'}} | super()._get_view_info()

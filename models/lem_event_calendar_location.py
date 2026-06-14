from odoo import models, fields, api

_COLOR_HEX = {
    0: '#FFFFFF', 1: '#F06050', 2: '#F4A460', 3: '#F7CD1F',
    4: '#6CC1ED', 5: '#814968', 6: '#EB7E7F', 7: '#2C8397',
    8: '#475577', 9: '#D6145F', 10: '#30C381', 11: '#9365B8',
}


class LemEventCalendarLocation(models.Model):
    _name = 'lem.event.calendar.location'
    _description = 'LEM Event Calendar Location'
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer(default=0)
    color_html = fields.Char()
    color_display = fields.Html(compute='_compute_color_display', store=False, sanitize=False, string='Color')
    address = fields.Char()
    google_maps_url = fields.Char(string='Google Maps URL')
    notes = fields.Text()
    active = fields.Boolean(default=True)

    entry_ids = fields.One2many('lem.event.calendar.entry', 'location_id', string='Calendar Entries')
    entry_count = fields.Integer(compute='_compute_entry_count', string='Entries')

    @api.depends('color')
    def _compute_color_display(self):
        for rec in self:
            hex_color = _COLOR_HEX.get(rec.color, '#FFFFFF')
            border = '1px solid rgba(0,0,0,0.15)' if rec.color == 0 else 'none'
            rec.color_display = (
                f'<span style="display:inline-block;width:16px;height:16px;border-radius:50%;'
                f'background:{hex_color};border:{border};vertical-align:middle;"></span>'
            )

    def _compute_entry_count(self):
        data = self.env['lem.event.calendar.entry'].read_group(
            [('location_id', 'in', self.ids)],
            ['location_id'],
            ['location_id'],
        )
        counts = {d['location_id'][0]: d['location_id_count'] for d in data}
        for rec in self:
            rec.entry_count = counts.get(rec.id, 0)

    def action_view_entries(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'lem.event.calendar.entry',
            'view_mode': 'lem_event_calendar,list,form',
            'domain': [('location_id', '=', self.id)],
            'context': {'default_location_id': self.id},
        }

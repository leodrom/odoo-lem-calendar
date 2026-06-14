from odoo import models, api

SYNC_FIELDS = {'name', 'date_begin', 'date_end'}
RES_MODEL = 'event.event'


class EventEvent(models.Model):
    _inherit = 'event.event'

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        for event in events:
            self.env['lem.calendar.entry'].create(self._lem_calendar_entry_vals(event))
        return events

    def write(self, vals):
        result = super().write(vals)
        if SYNC_FIELDS & set(vals.keys()):
            entries = self.env['lem.calendar.entry'].search([
                ('res_model', '=', RES_MODEL),
                ('res_id', 'in', self.ids),
            ])
            entry_by_res_id = {e.res_id: e for e in entries}
            for event in self:
                entry = entry_by_res_id.get(event.id)
                if entry:
                    entry.write(self._lem_calendar_entry_vals(event))
                else:
                    self.env['lem.calendar.entry'].create(self._lem_calendar_entry_vals(event))
        return result

    def unlink(self):
        self.env['lem.calendar.entry'].search([
            ('res_model', '=', RES_MODEL),
            ('res_id', 'in', self.ids),
        ]).unlink()
        return super().unlink()

    def _lem_calendar_entry_vals(self, event):
        return {
            'name': event.name,
            'date_start': event.date_begin,
            'date_end': event.date_end,
            'res_model': RES_MODEL,
            'res_id': event.id,
        }

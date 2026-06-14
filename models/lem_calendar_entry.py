from odoo import models, fields, api

_MODEL_TYPE = {
    'event.event': 'event',
    'crm.lead': 'lead',
}


class LemCalendarEntry(models.Model):
    _name = 'lem.calendar.entry'
    _description = 'LEM Calendar Entry'
    _order = 'date_start desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    date_start = fields.Datetime(required=True, string='Start', tracking=True)
    date_end = fields.Datetime(string='End', tracking=True)
    location_id = fields.Many2one('lem.location', string='Location', tracking=True, index=True)

    # Generic relation
    res_model = fields.Selection(
        selection='_get_reference_models',
        string='Object Type',
        index=True,
        tracking=True,
    )
    res_id = fields.Many2oneReference(
        model_field='res_model',
        string='Object',
        index=True,
    )

    linked_object_name = fields.Html(
        string='Object',
        compute='_compute_linked_object_name',
        store=False,
        sanitize=False,
    )

    color = fields.Integer(compute='_compute_color', store=True)

    entry_type = fields.Selection([
        ('event', 'Event'),
        ('lead', 'Opportunity'),
        ('manual', 'Manual'),
    ], compute='_compute_entry_type', store=True, string="Об'єкт")

    status_badge = fields.Html(compute='_compute_status_badge', store=False, sanitize=False, string=' ')

    status = fields.Selection([
        ('negotiation', 'В процесі погодження'),
        ('confirmed', 'Погоджено'),
        ('reserve', 'Резерв'),
        ('waiting', 'Очікуємо відповідь'),
        ('cancelled', 'Скасовано'),
    ], string='Статус', tracking=True, index=True)

    description = fields.Text()
    active = fields.Boolean(default=True)

    _STATUS_EMOJI = {
        'negotiation': '🟡',
        'confirmed':   '🟢',
        'reserve':     '🔵',
        'waiting':     '🟠',
        'cancelled':   '🔴',
    }

    def _compute_display_name(self):
        for rec in self:
            emoji = self._STATUS_EMOJI.get(rec.status, '')
            prefix = f'{emoji} ' if emoji else ''
            rec.display_name = f'{prefix}{rec.name}'

    _STATUS_STYLE = {
        'negotiation': ('#f0ad4e', 'В процесі'),
        'confirmed':   ('#28a745', 'Погоджено'),
        'reserve':     ('#17a2b8', 'Резерв'),
        'waiting':     ('#fd7e14', 'Очікуємо'),
        'cancelled':   ('#dc3545', 'Скасовано'),
    }

    @api.depends('status')
    def _compute_status_badge(self):
        for rec in self:
            if rec.status and rec.status in self._STATUS_STYLE:
                color, label = self._STATUS_STYLE[rec.status]
                rec.status_badge = (
                    f'<span style="display:inline-block;padding:1px 6px;border-radius:3px;'
                    f'font-size:11px;line-height:1.4;background:{color};color:#fff;'
                    f'font-weight:500;">{label}</span>'
                )
            else:
                rec.status_badge = False

    def _get_reference_models(self):
        return [
            ('event.event', 'Подія'),
            ('crm.lead', 'Угода'),
        ]

    @api.depends('res_model', 'res_id')
    def _compute_linked_object_name(self):
        for rec in self:
            if rec.res_model and rec.res_id:
                try:
                    obj = self.env[rec.res_model].browse(rec.res_id)
                    name = obj.display_name
                    url = f'/web#model={rec.res_model}&id={rec.res_id}&view_type=form'
                    rec.linked_object_name = f'<a href="{url}" style="white-space:normal;word-break:break-word;overflow-wrap:break-word;display:block;">{name}</a>'
                except Exception:
                    rec.linked_object_name = False
            else:
                rec.linked_object_name = False

    @api.depends('location_id.color')
    def _compute_color(self):
        for rec in self:
            rec.color = rec.location_id.color if rec.location_id else 0

    @api.depends('res_model')
    def _compute_entry_type(self):
        for rec in self:
            rec.entry_type = _MODEL_TYPE.get(rec.res_model, 'manual')

    def action_open_linked_object(self):
        self.ensure_one()
        if not self.res_model or not self.res_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }

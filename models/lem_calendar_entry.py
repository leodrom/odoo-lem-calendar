from markupsafe import Markup
from odoo import models, fields, api

_MODEL_TYPE = {
    'event.event': 'event',
    'crm.lead': 'lead',
}

_MODEL_LABEL = {
    'event.event': 'Подія',
    'crm.lead': 'Нагода',
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
        ('event', 'Подія'),
        ('lead', 'Нагода'),
        ('manual', 'Невизначений'),
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
            ('crm.lead', 'Нагода'),
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

    @api.onchange('res_id')
    def _onchange_res_id(self):
        if self.res_model and self.res_id:
            obj = self.env[self.res_model].browse(self.res_id)
            if obj.exists():
                self.name = obj.display_name

    def _get_linked_obj(self, res_model, res_id):
        if not res_model or not res_id:
            return None
        obj = self.env[res_model].browse(res_id)
        return obj if obj.exists() else None

    def _post_link_log(self, rec, obj, old_name):
        obj_label = _MODEL_LABEL.get(rec.res_model, rec.res_model)
        obj_url = f'/web#model={rec.res_model}&id={rec.res_id}&view_type=form'
        obj_link = f'<a href="{obj_url}">{obj.display_name}</a>'
        cal_url = f'/web#model=lem.calendar.entry&id={rec.id}&view_type=form'
        cal_link = f'<a href="{cal_url}">{rec.display_name}</a>'

        # Log on calendar entry
        note = Markup('Прив\'язано {}: {}.').format(obj_label, Markup(obj_link))
        if old_name and old_name != obj.display_name:
            note += Markup(' Назву змінено з «{}» на «{}».').format(old_name, obj.display_name)
        rec.message_post(body=note, message_type='comment', subtype_xmlid='mail.mt_note')

        # Log on linked object (only if it has chatter)
        if hasattr(obj, 'message_post'):
            obj.message_post(
                body=Markup('Прив\'язано до запису Календаря подій: {}.').format(Markup(cal_link)),
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.res_model and rec.res_id:
                obj = self._get_linked_obj(rec.res_model, rec.res_id)
                if obj:
                    old_name = rec.name
                    if rec.name != obj.display_name:
                        super(LemCalendarEntry, rec).write({'name': obj.display_name})
                    self._post_link_log(rec, obj, old_name)
        return records

    def write(self, vals):
        old_state = {}
        if 'res_id' in vals or 'res_model' in vals:
            for rec in self:
                old_state[rec.id] = {
                    'res_model': rec.res_model,
                    'res_id': rec.res_id,
                    'name': rec.name,
                }

        result = super().write(vals)

        for rec in self:
            old = old_state.get(rec.id)
            if not old:
                continue
            if not rec.res_model or not rec.res_id:
                continue
            if rec.res_model == old['res_model'] and rec.res_id == old['res_id']:
                continue
            obj = self._get_linked_obj(rec.res_model, rec.res_id)
            if not obj:
                continue
            old_name = old['name']
            if rec.name != obj.display_name:
                super(LemCalendarEntry, rec).write({'name': obj.display_name})
            self._post_link_log(rec, obj, old_name)

        return result

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

import logging
from markupsafe import Markup, escape
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

_MODEL_TYPE = {
    'event.event': 'event',
    'crm.lead': 'lead',
}

_MODEL_PATH = {
    'event.event': 'events',
    'crm.lead': 'crm',
}



class LemCalendarEntry(models.Model):
    _name = 'lem.event.calendar.entry'
    _description = 'LEM Calendar Entry'
    _order = 'date_start desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    date_start = fields.Datetime(required=True, string='Start', tracking=True)
    date_end = fields.Datetime(string='End', tracking=True)
    location_id = fields.Many2one('lem.event.calendar.location', string='Location', tracking=True, index=True)

    # Generic relation
    res_model = fields.Selection(
        selection='_get_reference_models',
        string='Тип об\'єкту',
        index=True,
        tracking=True,
    )
    res_id = fields.Many2oneReference(
        model_field='res_model',
        string='Об\'єкт',
        index=True,
        # Many2oneReference has no DB FK, so ondelete is not applicable;
        # stale references are handled gracefully in _compute_linked_object_name.
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string='Нагода',
        domain=[('type', '=', 'opportunity')],
        compute='_compute_lead_id',
        inverse='_inverse_lead_id',
        store=False,
    )

    linked_object_name = fields.Html(
        string='Об\'єкт',
        compute='_compute_linked_object_name',
        store=False,
        sanitize=False,
    )

    color = fields.Integer(compute='_compute_color', store=True)

    entry_type = fields.Selection([
        ('event', 'Подія'),
        ('lead', 'Нагода'),
        ('manual', 'Невизначений'),
    ], compute='_compute_entry_type', store=True, string='Об\'єкт')

    status_badge = fields.Html(compute='_compute_status_badge', store=False, sanitize=False, string=' ')

    status = fields.Selection([
        ('negotiation', 'В процесі погодження'),
        ('confirmed', 'Погоджено'),
        ('reserve', 'Резерв'),
        ('waiting', 'Очікуємо відповідь'),
        ('cancelled', 'Скасовано'),
    ], string='Статус', tracking=True, index=True)

    user_id = fields.Many2one('res.users', string='Відповідальний', index=True)
    description = fields.Html(sanitize=True, sanitize_style=True)
    active = fields.Boolean(default=True)

    entry_role = fields.Selection([
        ('main', 'Основна'),
        ('prep', 'Підготовча'),
    ], string='Роль', default='main', required=True, tracking=True, index=True)

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
            role_prefix = '⚙ ' if rec.entry_role == 'prep' else ''
            status_prefix = f'{emoji} ' if emoji else ''
            rec.display_name = f'{role_prefix}{status_prefix}{rec.name}'

    _STATUS_COLOR = {
        'negotiation': '#f0ad4e',
        'confirmed':   '#28a745',
        'reserve':     '#17a2b8',
        'waiting':     '#fd7e14',
        'cancelled':   '#dc3545',
    }

    _STATUS_BADGE_LABEL = {
        'negotiation': 'В процесі',
        'confirmed':   'Погоджено',
        'reserve':     'Резерв',
        'waiting':     'Очікуємо',
        'cancelled':   'Скасовано',
    }

    @api.depends('status')
    def _compute_status_badge(self):
        for rec in self:
            color = self._STATUS_COLOR.get(rec.status)
            label = self._STATUS_BADGE_LABEL.get(rec.status)
            if color and label:
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
                    if not obj.exists():
                        rec.linked_object_name = False
                        continue
                    path = _MODEL_PATH.get(rec.res_model)
                    url = f'/odoo/{path}/{rec.res_id}' if path else f'/web#model={rec.res_model}&id={rec.res_id}&view_type=form'
                    rec.linked_object_name = Markup(
                        '<a class="o_lem_object_link" href="{}" data-model="{}" data-id="{}"'
                        ' style="white-space:normal;word-break:break-word;'
                        'overflow-wrap:break-word;display:block;">{}</a>'
                    ).format(url, rec.res_model, rec.res_id, obj.display_name)
                except Exception:
                    _logger.exception("Error computing linked_object_name for %s id=%s", rec.res_model, rec.res_id)
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

    @api.depends('res_model', 'res_id')
    def _compute_lead_id(self):
        for rec in self:
            rec.lead_id = rec.res_id if (rec.res_model == 'crm.lead' and rec.res_id) else False

    def _inverse_lead_id(self):
        for rec in self:
            if rec.lead_id:
                rec.res_model = 'crm.lead'
                rec.res_id = rec.lead_id.id
            elif rec.res_model == 'crm.lead':
                rec.res_id = False

    @api.onchange('res_model')
    def _onchange_res_model(self):
        self.res_id = False
        self.lead_id = False

    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        if self.lead_id:
            self.name = self.lead_id.display_name
            if self.lead_id.user_id:
                self.user_id = self.lead_id.user_id

    @api.onchange('res_id')
    def _onchange_res_id(self):
        if self.res_model and self.res_id:
            obj = self.env[self.res_model].browse(self.res_id)
            if obj.exists():
                self.name = obj.display_name
                if hasattr(obj, 'user_id') and obj.user_id:
                    self.user_id = obj.user_id

    def _get_linked_obj(self, res_model, res_id):
        if not res_model or not res_id:
            return None
        obj = self.env[res_model].browse(res_id)
        return obj if obj.exists() else None

    def _sync_from_linked_obj(self, rec, obj):
        vals = {}
        if rec.name != obj.display_name:
            vals['name'] = obj.display_name
        if hasattr(obj, 'user_id') and obj.user_id and rec.user_id != obj.user_id:
            vals['user_id'] = obj.user_id.id
        if vals:
            super(LemCalendarEntry, rec).write(vals)

    def _post_link_log(self, rec, obj, old_name):
        obj_labels = {'event.event': _('Event'), 'crm.lead': _('Opportunity')}
        obj_label = obj_labels.get(rec.res_model, rec.res_model)
        obj_url = f'/web#model={rec.res_model}&id={rec.res_id}&view_type=form'
        obj_link = Markup('<a href="{}">{}</a>').format(obj_url, obj.display_name)
        cal_url = f'/web#model=lem.event.calendar.entry&id={rec.id}&view_type=form'
        cal_link = Markup('<a href="{}">{}</a>').format(cal_url, rec.display_name)

        # Log on calendar entry
        note = Markup(_('Linked {}: {}.')).format(obj_label, obj_link)
        if old_name and old_name != obj.display_name:
            note += Markup(_(' Name changed from «{}» to «{}».')).format(old_name, obj_link)
        rec.message_post(body=note, message_type='comment', subtype_xmlid='mail.mt_note')

        # Log on linked object (only if it has chatter)
        if hasattr(obj, 'message_post'):
            obj.message_post(
                body=Markup(_('Linked to Calendar Event record: {}.')).format(cal_link),
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

    def _normalize_vals(self, vals):
        if vals.get('res_id') == 0:
            vals['res_id'] = False
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._normalize_vals(v) for v in vals_list]
        records = super().create(vals_list)
        for rec in records:
            if rec.res_model and rec.res_id:
                obj = self._get_linked_obj(rec.res_model, rec.res_id)
                if obj:
                    old_name = rec.name
                    self._sync_from_linked_obj(rec, obj)
                    self._post_link_log(rec, obj, old_name)
        return records

    def write(self, vals):
        self._normalize_vals(vals)
        old_state = {}
        track_fields = 'res_id' in vals or 'res_model' in vals or 'user_id' in vals
        if track_fields:
            for rec in self:
                old_state[rec.id] = {
                    'res_model': rec.res_model,
                    'res_id': rec.res_id,
                    'name': rec.name,
                    'user_id': rec.user_id,
                }

        result = super().write(vals)

        for rec in self:
            old = old_state.get(rec.id)
            if not old:
                continue

            # Log user_id change
            old_user = old['user_id']
            if rec.user_id != old_user:
                old_label = old_user.name if old_user else '—'
                new_label = rec.user_id.name if rec.user_id else '—'
                rec.message_post(
                    body=Markup(_('Responsible changed: {} → <b>{}</b>.')).format(old_label, new_label),
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )

            # Log object link change
            if not rec.res_model or not rec.res_id:
                continue
            if rec.res_model == old['res_model'] and rec.res_id == old['res_id']:
                continue
            obj = self._get_linked_obj(rec.res_model, rec.res_id)
            if not obj:
                continue
            old_name = old['name']
            self._sync_from_linked_obj(rec, obj)
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

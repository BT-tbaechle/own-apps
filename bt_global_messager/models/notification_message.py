# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from datetime import datetime, timedelta
from openerp import models, fields, api
from openerp.tools import image_resize_image

OFFSET_INTERVALS = [('minutes', "Minutes"),
                    ('hours', "Hours"),
                    ('days', "Days"),
                    ('weeks', "Weeks")]

OFFSET_MULTIPLIER = {'minutes': 1,
                     'hours': 60,
                     'days': 1440,
                     'weeks': 10080}

NOTIFY_TIME_TYPES = [('time_type_rel', 'relative'),
                     ('time_type_abs', 'absolute')]


class NotificationMessage(models.Model):
    _name = 'notification.message'

    _order = 'effective_notification_datetime'

    def _get_default_icon(self):
        icon = False
        if self.env.context.get('default_notification_id'):
            notification_id = self.env['notification.notification'].browse(self.env.context.get('default_notification_id'))
            icon = notification_id.icon
        return icon

    notification_id = fields.Many2one('notification.notification', string="Notification", required=True,
                                      on_delete='cascade')

    custom_message = fields.Boolean(string="Customise Message")
    name = fields.Char(string="Title", translate=True)
    message = fields.Text(string="Text", translate=True)
    icon = fields.Binary(string="Icon", attachment=True, default=_get_default_icon)
    timeout = fields.Integer(string="Timeout (sec)")
    event_datetime = fields.Datetime(string="Event Date", related='notification_id.event_datetime', readonly=True, store=True)

    notify_time_type = fields.Selection(NOTIFY_TIME_TYPES, string="Type", required=True)
    notify_type_ids = fields.Many2many('notification.type', string="Notification Type", required=True)

    notification_offset = fields.Integer(string="Offset (min)", compute='_compute_minute_offset', store=True)
    notification_offset_as_unit = fields.Integer(string="Offset")
    notification_offset_unit = fields.Selection(OFFSET_INTERVALS, string="Offset Unit", default=OFFSET_INTERVALS[0][0])
    notification_datetime = fields.Datetime(string="Send Date")
    effective_notification_datetime = fields.Datetime(string="Send Date", compute='_compute_effective_date_time', store=True)

    is_sent = fields.Boolean(string="Sent", readonly=True)

    @api.onchange('custom_message')
    def _reset_to_default_msg(self):
        if not self.custom_message:
            self.name = self.notification_id.name
            self.message = self.notification_id.message
            self.icon = self._get_default_icon()
            self.timeout = self.notification_id.timeout

    @api.model
    def create(self, vals):
        if 'project_img' in vals:
            vals['project_img'] = image_resize_image(vals['project_img'], size=(100, None))
        return super(NotificationMessage, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'project_img' in vals:
            vals['project_img'] = image_resize_image(vals['project_img'], size=(100, None))
        return super(NotificationMessage, self).write(vals)

    @api.model
    def _send_due_messages(self, ids=[]):
        datetime_now = datetime.now()
        due_message_ids = self.env['notification.message'].search(['&',
                                                                    ('is_sent', '=', False),
                                                                    ('effective_notification_datetime', '<=', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))])
        for due_message in due_message_ids:
            users = self.env['res.users'].search([])
            for user in users:
                message = self.env['ir.translation']._get_source(None, 'model', user.lang, due_message.message)
                title = self.env['ir.translation']._get_source(None, 'model', user.lang, due_message.name)
                if self.env.ref('bt_global_messager.notification_type_odoo').id in due_message.notify_type_ids.ids:
                    user.notify_warning(message, title=title, sticky=True)

                if self.env.ref('bt_global_messager.notification_type_desktop').id in due_message.notify_type_ids.ids:
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    attachment = self.env['ir.attachment'].search([
                        ('res_model', '=', due_message._name),
                        ('res_id', '=', due_message.id),
                        ('res_field', '=', 'icon')
                    ], order="create_date", limit=1)
                    image_url = ""
                    if attachment:
                        image_url = "{}/web/content/{}".format(base_url, attachment[0].id)
                    user.notify_push(message, title=title, icon=image_url, timeout=self.timeout)
            due_message.write({'is_sent':True})

    @api.depends('notification_offset_as_unit', 'notification_offset_unit')
    def _compute_minute_offset(self):
        for record in self:
            if record.notification_offset_as_unit and record.notification_offset_unit:
                multiplier = OFFSET_MULTIPLIER[record.notification_offset_unit]
                record.notification_offset = record.notification_offset_as_unit * multiplier

    @api.depends('notification_datetime', 'event_datetime',  'notification_offset')
    def _compute_effective_date_time(self):
        for record in self:
            if record.notify_time_type == 'time_type_rel':
                if record.notification_offset and record.event_datetime:
                    event_datetime_object = datetime.strptime(record.event_datetime, '%Y-%m-%d %H:%M:%S')
                    record.effective_notification_datetime = event_datetime_object + timedelta(minutes=record.notification_offset)
            else:
                record.effective_notification_datetime = record.notification_datetime

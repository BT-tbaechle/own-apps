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


class NotificationMessage(models.Model):
    _name = 'notification.message'

    def _get_default_icon(self):
        icon = False
        if self.env.context.get('default_notification_id'):
            notification_id = self.env['notification.notification'].browse(self.env.context.get('default_notification_id'))
            icon = notification_id.icon
        return icon

    notification_id = fields.Many2one('notification.notification', string="Notification", required=True)

    custom_message = fields.Boolean(string="Customise Message")
    name = fields.Char(string="Title")
    message = fields.Text(string="Text")
    icon = fields.Binary(string="Icon", attachment=True, default=_get_default_icon)
    timeout = fields.Integer(string="Timeout (sec)")
    event_date = fields.Date(string="Event Date", related='notification_id.event_date', readonly=True, store=True)
    event_time = fields.Float(string="Event Time", related='notification_id.event_time', readonly=True, store=True)

    notify_time_type_id = fields.Many2one('notification.time.type', string="Type", required=True)
    notify_type_ids = fields.Many2many('notification.type', string="Notification Type", required=True)

    notification_offset = fields.Integer(string="Offset (min)", compute='_compute_minute_offset', store=True)
    notification_offset_as_unit = fields.Integer(string="Offset")
    notification_offset_unit = fields.Selection(OFFSET_INTERVALS, string="Offset Unit", default=OFFSET_INTERVALS[0][0])
    notification_date = fields.Date(string="Send Date")
    notification_time = fields.Float(string="Send Time")
    effective_notification_date = fields.Date(string="Send Date", compute='_compute_effective_date_time', store=True)
    effective_notification_time = fields.Float(string="Send Time", compute='_compute_effective_date_time', store=True)

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
        time_now = datetime.now().time()
        due_message_ids = self.env['notification.message'].search(['&',
                                                                    ('is_sent', '=', False),
                                                                    '|',
                                                                    ('effective_notification_date', '<', fields.Date.today()),
                                                                    '&',
                                                                    ('effective_notification_date', '=', fields.Date.today()),
                                                                    ('effective_notification_time', '<=', time_now.hour + time_now.minute / 60.0),
                                                                    ])
        for message in due_message_ids:
            users = self.env['res.users'].search([])
            users.notify_warning(message.message, title=message.name, sticky=True)
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            attachment = self.env['ir.attachment'].search([
                                                               ('res_model', '=', message._name),
                                                               ('res_id', '=', message.id),
                                                               ('res_field', '=', 'icon')
                                                           ], order="create_date", limit=1)
            image_url = ""
            if attachment:
                image_url = "{}/web/content/{}".format(base_url, attachment[0].id)
            users.notify_push(message.message, title=message.name, icon=image_url, timeout=self.timeout)
            message.write({'is_sent':True})

    @api.depends('notification_offset_as_unit', 'notification_offset_unit')
    def _compute_minute_offset(self):
        for record in self:
            if record.notification_offset_as_unit and record.notification_offset_unit:
                multiplier = OFFSET_MULTIPLIER[record.notification_offset_unit]
                record.notification_offset = record.notification_offset_as_unit * multiplier

    @api.depends('notification_date', 'notification_time', 'event_date', 'event_time', 'notification_offset')
    def _compute_effective_date_time(self):
        for record in self:
            if record.notify_time_type_id.id == self.env.ref('bt_global_messager.notification_time_type_rel').id:
                if record.notification_offset and record.event_time and record.event_date:
                    minutes = (record.event_time - int(record.event_time)) * 60
                    event_date_str = "{} {}:{}".format(record.event_date, int(record.event_time), int(minutes))
                    event_datetime_object = datetime.strptime(event_date_str, '%Y-%m-%d %H:%M')
                    notify_datetime_object = event_datetime_object + timedelta(minutes=record.notification_offset)
                    record.effective_notification_date = notify_datetime_object.date().strftime('%Y-%m-%d')
                    hours_float = notify_datetime_object.hour + notify_datetime_object.minute/60.0
                    record.effective_notification_time = hours_float
            else:
                record.effective_notification_date = record.notification_date
                record.effective_notification_time = record.notification_time


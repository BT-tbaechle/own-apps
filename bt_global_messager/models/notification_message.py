# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from datetime import datetime
from openerp import models, fields, api


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
    icon = fields.Binary(string="Icon", default=_get_default_icon)
    timeout = fields.Integer(string="Timeout (sec)")
    event_date = fields.Date(string="Event Date", related='notification_id.event_date', readonly=True)
    event_time = fields.Float(string="Event Time", related='notification_id.event_time', readonly=True)

    notify_time_type = fields.Many2one('notification.time.type', string="Type", required=True)

    notification_offset = fields.Integer(string="Offset (min)")
    notification_date = fields.Date(string="Send Date")
    notification_time = fields.Float(string="Send Time")

    is_sent = fields.Boolean(string="Sent", readonly=True)


    # @api.onchange('notification_date', 'notification_time', 'event_date', 'event_time')
    # def _get_event_offset(self):
    #     notification_offset = 0
    #     if (self.notification_date and self.notification_time and
    #             self.event_date and self.event_time and
    #             self.notify_time_type.id == self.env.ref('bt_global_messager.notification_time_type_abs').id):
    #         time = '{0:02.0f}:{1:02.0f}'.format(*divmod(self.notification_time * 60, 60))
    #         message_date_str = "{} {}".format(self.notification_date, time)
    #         message_datetime_object = datetime.strptime(message_date_str, '%Y-%m-%d %H:%M')
    #         time = '{0:02.0f}:{1:02.0f}'.format(*divmod(self.event_time * 60, 60))
    #         event_date_str = "{} {}".format(self.event_date, time)
    #         event_datetime_object = datetime.strptime(event_date_str, '%Y-%m-%d %H:%M')
    #         offset = event_datetime_object - message_datetime_object
    #         notification_offset = int(offset.total_seconds() / 60)
    #     return {'value': {'notification_offset': notification_offset}}
    #
    #
    # @api.onchange('notification_offset', 'event_date', 'event_time')
    # def _get_event_date_time(self):
    #     if self.notify_time_type.id == self.env.ref('bt_global_messager.notification_time_type_rel').id:
    #         notification_time = 6.0
    #         return {'value': {'notification_time': notification_time}}

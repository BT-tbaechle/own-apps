# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from openerp import models, fields, api


class NotificationMessage(models.Model):
    _name = 'notification.message'

    notification_id = fields.Many2one('notification.notification', string="Notification")

    custom_message = fields.Boolean(string="Customise Message")
    name = fields.Char(string="Title")
    message = fields.Text(string="Text")
    icon = fields.Binary(string="Icon")
    timeout = fields.Integer(string="Timeout (sec)")
    event_date = fields.Date(string="Event Date")
    event_time = fields.Float(string="Event Time")

    notify_time_type = fields.Many2one('notification.time.type', string="Type")

    notification_offset = fields.Integer(string="Offset (min)")
    notification_date = fields.Date(string="Send Date")
    notification_time = fields.Float(string="Send Time")

    is_sent = fields.Boolean(string="Sent", readonly=True)


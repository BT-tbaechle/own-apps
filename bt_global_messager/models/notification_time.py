# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from openerp import models, fields, api


class NotificationTime(models.Model):
    _name = 'notification.time'

    notification_id = fields.Many2one('notification.notification', string="Notification")
    notify_time_type = fields.Many2one('notification.time.type', string="Type")

    notification_offset = fields.Float(string="Offset")
    notification_date = fields.Date(string="Send Date")
    notification_time = fields.Float(string="Send Time")

    is_sent = fields.Boolean(string="Sent", readonly=True)

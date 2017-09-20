# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from openerp import models, fields, api


class Notification(models.Model):
    _name = 'notification.notification'

    name = fields.Char(string="Title")
    message = fields.Text(string="Text")
    icon = fields.Binary(string="Icon")
    timeout = fields.Integer(string="Timeout (sec)")

    instant_send = fields.Boolean(string="Send instantly")
    event_date = fields.Date(string="Event Date")
    event_time = fields.Float(string="Event Time")
    notification_time_ids = fields.One2many('notification.time', inverse_name='notification_id',
                                            string="Notification Times")
    notification_time_names = fields.Char(string="Notification Times",
                                          compute='_generate_notify_time_names')

    @api.depends('notification_time_ids')
    def _generate_notify_time_names(self):
        pass
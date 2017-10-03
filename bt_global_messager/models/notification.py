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


class Notification(models.Model):
    _name = 'notification.notification'

    name = fields.Char(string="Title")
    message = fields.Text(string="Text")
    icon = fields.Binary(string="Icon")
    timeout = fields.Integer(string="Timeout (sec)")

    send_manually = fields.Boolean(string="Send manually")
    event_date = fields.Date(string="Event Date")
    event_time = fields.Float(string="Event Time")
    notification_time_ids = fields.One2many('notification.message', inverse_name='notification_id',
                                            string="Notification Times")
    notification_time_names = fields.Char(string="Notification Times",
                                          compute='_generate_notify_time_names')

    @api.depends('notification_time_ids')
    def _generate_notify_time_names(self):
        pass

    @api.onchange('send_manually')
    def _reset_time_date(self):
        if self.send_manually:
            self.event_date = False
            self.event_time = False

    @api.multi
    def write(self, vals):
        if vals.get('send_manually'):
            vals['event_date'] = False
            vals['event_time'] = False
        return super(Notification, self).write(vals)

    @api.multi
    def send_notification(self):
        self.env.user.notify_warning(self.message, title=self.name, sticky=True)

        values = {'name': self.name,
                  'message': self.message,
                  'notification_id': self.id,
                  'icon': self.icon,
                  'timeout': self.timeout,
                  'notify_time_type': self.env.ref('bt_global_messager.notification_time_type_abs').id,
                  'notification_date': fields.Date.today(),
                  'is_sent': True}
        time_now = datetime.now().time()
        values['notification_time'] = time_now.hour + time_now.minute/60.0
        self.env['notification.message'].create(values)

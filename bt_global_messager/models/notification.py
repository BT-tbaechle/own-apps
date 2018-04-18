# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from datetime import datetime

import openerp
from openerp import models, fields, api
from openerp.tools import image_resize_image


class Notification(models.Model):
    _name = 'notification.notification'

    @api.model
    def _get_default_image(self,):
        image = open(openerp.modules.get_module_resource('bt_global_messager', 'static/src/img', 'odoo_logo.png')).read()
        return image.encode('base64')

    name = fields.Char(string="Title", required=True)
    message = fields.Text(string="Text", required=True)
    icon = fields.Binary(string="Icon", attachment=True, default=_get_default_image)
    timeout = fields.Integer(string="Timeout (sec)")

    send_manually = fields.Boolean(string="Send manually")
    event_date = fields.Date(string="Event Date")
    event_time = fields.Float(string="Event Time")
    notification_time_ids = fields.One2many('notification.message', inverse_name='notification_id',
                                            string="Notification Times")
    notification_time_names = fields.Char(string="Notification Times",
                                          compute='_generate_notify_time_names')
    notify_type_ids = fields.Many2many('notification.type', string="Notification Type")

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
        self.env.user.notify_warning(self.message, title=self.name)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('res_field', '=', 'icon')
        ], order="create_date", limit=1)
        image_url = ""
        if attachment:
            image_url = "{}/web/content/{}".format(base_url, attachment[0].id)
        self.env.user.notify_push(self.message, title=self.name, icon=image_url, timeout=self.timeout)

        values = {'name': self.name,
                  'message': self.message,
                  'notification_id': self.id,
                  'icon': self.icon,
                  'timeout': self.timeout,
                  'notify_time_type_id': self.env.ref('bt_global_messager.notification_time_type_abs').id,
                  'notification_date': fields.Date.today(),
                  'is_sent': True}
        time_now = datetime.now().time()
        values['notification_time'] = time_now.hour + time_now.minute/60.0
        self.env['notification.message'].create(values)

    @api.model
    def create(self, vals):
        if 'icon' in vals:
            vals['icon'] = image_resize_image(vals['icon'], size=(100, None))
        return super(Notification, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'icon' in vals:
            vals['icon'] = image_resize_image(vals['icon'], size=(100, None))
        return super(Notification, self).write(vals)

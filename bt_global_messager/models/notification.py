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

    def _get_default_notify_types(self):
        return [self.env.ref('bt_global_messager.notification_type_odoo').id,
                self.env.ref('bt_global_messager.notification_type_desktop').id]

    name = fields.Char(string="Title", required=True, translate=True)
    message = fields.Text(string="Text", translate=True)
    icon = fields.Binary(string="Icon", attachment=True, default=_get_default_image)
    timeout = fields.Integer(string="Timeout (sec)")  # TODO: implement timeout for pop-up

    send_manually = fields.Boolean(string="Send manually")
    event_datetime = fields.Datetime(string="Event Time")
    notification_time_ids = fields.One2many('notification.message', inverse_name='notification_id',
                                            string="Notification Times")
    notify_type_ids = fields.Many2many('notification.type', string="Notification Type",
                                       default=_get_default_notify_types)

    @api.one
    def copy(self, default={}):
        default['event_datetime'] = False

        result = super(Notification, self).copy(default)

        messages_to_copy = self.notification_time_ids.search([('notification_id', '=', self.id),
                                                              ('notify_time_type', '=', 'time_type_rel')])
        message_list = []
        for message in messages_to_copy:
            message_dict = dict()
            message_dict['custom_message'] = message.custom_message
            message_dict['event_datetime'] = message.event_datetime
            message_dict['icon'] = message.icon
            message_dict['is_sent'] = False
            message_dict['message'] = message.message
            message_dict['name'] = message.name
            message_dict['notification_id'] = result.id
            message_dict['notification_offset_as_unit'] = message.notification_offset_as_unit
            message_dict['notification_offset_unit'] = message.notification_offset_unit
            message_dict['notify_time_type'] = message.notify_time_type
            message_dict['notify_type_ids'] = message.notify_type_ids.ids
            message_dict['timeout'] = message.timeout
            message_list.append(self.env['notification.message'].create(message_dict).id)

        result.notification_time_ids = [(6, 0, message_list)]
        return result

    @api.multi
    def send_notification(self):
        users = self.env['res.users'].search([])
        for user in users:
            message = self.env['ir.translation']._get_source(None, 'model', user.lang, self.message)
            title = self.env['ir.translation']._get_source(None, 'model', user.lang, self.name)
            if self.env.ref('bt_global_messager.notification_type_odoo').id in self.notify_type_ids.ids:
                user.notify_warning(message, title=title, sticky=True)

            if self.env.ref('bt_global_messager.notification_type_desktop').id in self.notify_type_ids.ids:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', self._name),
                    ('res_id', '=', self.id),
                    ('res_field', '=', 'icon')
                ], order="create_date", limit=1)
                image_url = ""
                if attachment:
                    image_url = "{}/web/content/{}".format(base_url, attachment[0].id)
                user.notify_push(message, title=title, icon=image_url, timeout=self.timeout)

            values = {'name': self.name,
                      'message': self.message,
                      'notification_id': self.id,
                      'icon': self.icon,
                      'timeout': self.timeout,
                      'notify_time_type': 'time_type_abs',
                      'notification_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                      'is_sent': True}

        message = self.env['notification.message'].create(values)
        message.notify_type_ids = self.notify_type_ids.ids

    @api.model
    def create(self, vals):
        if vals.get('icon'):
            vals['icon'] = image_resize_image(vals['icon'], size=(100, None))
        return super(Notification, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('icon'):
            vals['icon'] = image_resize_image(vals['icon'], size=(100, None))

        result = super(Notification, self).write(vals)

        if vals.get('event_datetime'):
            for message in self.notification_time_ids:
                if message.notify_time_type == 'time_type_rel' and \
                        self.event_datetime > message.effective_notification_datetime:
                    message.is_sent = False

        return result

    @api.multi
    def unlink(self):
        self.notification_time_ids.unlink()
        return super(Notification, self).unlink()

# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2018 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from openerp import api, fields, models, _


class ResUsersExt(models.Model):

    _inherit = 'res.users'

    notify_channel_push_ref = fields.Char(compute='_compute_notify_channel_refs')
    notify_channel_odoo_info_ref = fields.Char(compute='_compute_notify_channel_refs')
    notify_channel_odoo_warn_ref = fields.Char(compute='_compute_notify_channel_refs')

    @api.multi
    @api.depends('create_date')
    def _compute_notify_channel_refs(self):
        for record in self:
            rec_id = record.id
            record.notify_channel_push_ref = 'notification_push_{}'.format(rec_id)
            record.notify_channel_odoo_info_ref = 'notification_odoo_info_{}'.format(rec_id)
            record.notify_channel_odoo_warn_ref = 'notification_odoo_warn_{}'.format(rec_id)

    @api.multi
    def send_push_notification(self, message, title=None, icon=None, timeout=None):
        title = title or _('Notification')
        self._notification_channel('notify_channel_push_ref', message, title, icon, timeout)

    @api.multi
    def send_odoo_info_notification(self, message, title=None, sticky=False):
        title = title or _('Information')
        self._notification_channel('notify_channel_odoo_info_ref', message, title, sticky)

    @api.multi
    def send_odoo_warn_notification(self, message, title=None, sticky=False):
        title = title or _('Warning')
        self._notification_channel('notify_channel_odoo_warn_ref', message, title, sticky)

    @api.multi
    def _notification_channel(self, channel_ref_field, message, title, sticky=None, icon=None, timeout=None):
        bus_dict = {
            'title': title,
            'message': message,
            'sticky': sticky,
            'icon': icon,
            'timeout': timeout,
        }
        notification_list = [(getattr(record, channel_ref_field), bus_dict) for record in self]
        self.env['bus.bus'].sendmany(notification_list)

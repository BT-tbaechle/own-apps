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

    @api.multi
    @api.depends('create_date')
    def _compute_channel_names(self):
        for record in self:
            res_id = record.id
            record.notify_info_channel_name = 'notify_info_%s' % res_id
            record.notify_warning_channel_name = 'notify_warning_%s' % res_id
            record.notify_push_channel_name = 'notify_push_%s' % res_id

    notify_push_channel_name = fields.Char(compute='_compute_channel_names')

    @api.multi
    def notify_push(self, message, title=None, sticky=False, icon=None, timeout=None):
        title = title or _('Warning')
        self._notify_channel(
            'notify_push_channel_name', message, title, sticky, icon, timeout)

    @api.multi
    def _notify_channel(self, channel_name_field, message, title, sticky, icon=None, timeout=None):
        # New channel for push.js desktop notification
        bus_message = {
            'message': message,
            'title': title,
            'sticky': sticky,
            'icon': icon,
            'timeout': timeout,
        }
        notifications = [(getattr(record, channel_name_field), bus_message)
                         for record in self]
        self.env['bus.bus'].sendmany(notifications)

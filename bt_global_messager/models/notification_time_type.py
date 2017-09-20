# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from openerp import models, fields, api


class NotificationTimeType(models.Model):
    _name = 'notification.time.type'

    name = fields.Char(string="Name")

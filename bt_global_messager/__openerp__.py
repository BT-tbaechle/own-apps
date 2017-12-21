# -*- coding: utf-8 -*- # pylint: disable=C0111
##############################################################################
#
#    Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################
{
    'name': "BT Global Messager",
    'summary': "Module that allows instant or time-based messaging with users.",
    'author': "braintec AG",
    'license': 'LGPL-3',
    'version': '9.0.0',
    'category': 'Extra Tools',
    'website': 'http://www.braintec-group.com',
    'images': [
    ],
    'depends': [
        'base',
        'web_notify',
    ],
    'data': [
        'data/notification_time_type_data.xml',
        'data/notification_type_data.xml',
        'data/ir_cron_data.xml',
        'static/src/xml/bt_global_messager_css_data.xml',
        'views/notification_message_views.xml',
        'views/notification_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

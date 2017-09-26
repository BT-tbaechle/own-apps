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
        'data/notification.time.type.csv',
        'views/notification_message_views.xml',
        'views/notification_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

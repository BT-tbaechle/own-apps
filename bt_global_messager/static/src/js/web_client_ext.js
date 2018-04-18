odoo.define('bt_global_messager.WebClient', function (require) {
    "use strict";

    var WebClient = require('web_notify.WebClient');
    var base_bus = require('bus.bus');
    var _ = require('_');

    WebClient.include({
        start_polling: function() {
            this.channel_warning = 'notify_warning_' + this.session.uid;
            this.channel_info = 'notify_info_' + this.session.uid;
            this.channel_push = 'notify_push_' + this.session.uid;
            base_bus.bus.add_channel(this.channel_warning);
            base_bus.bus.add_channel(this.channel_info);
            base_bus.bus.add_channel(this.channel_push);
            base_bus.bus.on('notification', this, this.bus_notification);
            base_bus.bus.start_polling();
        },
        bus_notification: function(notifications) {
            var self = this;
            _.each(notifications, function (notification) {
                var channel = notification[0];
                var message = notification[1];
                if (channel === self.channel_warning) {
                    self.on_message_warning(message);
                } else if (channel == self.channel_info) {
                    self.on_message_info(message);
                } else if (channel == self.channel_push) {
                    self.on_message_push(message);
                }
            });
        },
        on_message_push: function (message) {
            if (this.notification_manager) {
                Push.create(message.title, {
                    body: message.message,
                    icon: message.icon,
                    timeout: message.timeout,
                    onClick: function () {
                        window.focus();
                        this.close();
                    }
                });
            }
        },
    });

});
odoo.define('bt_global_messager.WebClient', function (require) {
    "use strict";

    var WebClient = require('web.WebClient');
    var base_bus = require('bus.bus');
    var _ = require('_');

    WebClient.include({
        init: function(parent, client_options){
            this._super(parent, client_options);
        },
        show_application: function() {
            this._super();
            this.start_polling();
        },
        on_logout: function() {
            var self = this;
            base_bus.bus.off('notification', this, this.handle_notifications);
            this._super();
        },
        start_polling: function() {
            this.channel_push = 'notification_push_' + this.session.uid;
            this.channel_odoo_warn = 'notification_odoo_warn_' + this.session.uid;
            this.channel_odoo_info = 'notification_odoo_info_' + this.session.uid;
            base_bus.bus.add_channel(this.channel_push);
            base_bus.bus.add_channel(this.channel_odoo_warn);
            base_bus.bus.add_channel(this.channel_odoo_info);
            base_bus.bus.on('notification', this, this.handle_notifications);
            base_bus.bus.start_polling();
        },
        handle_notifications: function(notifications) {
            var self = this;
            _.each(notifications, function (notification) {
                var channel = notification[0];
                var message = notification[1];
                if (channel === self.channel_push) {
                    self.trigger_desktop_popup(message);
                } else if (channel == self.channel_odoo_warn) {
                    self.trigger_odoo_warn(message);
                } else if (channel == self.channel_odoo_info) {
                    self.trigger_odoo_info(message);
                }
            });
        },
        trigger_desktop_popup: function (message) {
            if (this.notification_manager) {
                Push.create(message.title, {
                    body: message.message,
                    icon: message.icon,
                    timeout: message.timeout,
                    requireInteraction: true,
                    onClick: function () {
                        window.focus();
                        this.close();
                    }
                });
            }
        },
        trigger_odoo_warn: function(message){
            if(this.notification_manager) {
                this.notification_manager.do_warn(message.title, message.message, message.sticky);
            }
        },
        trigger_odoo_info: function(message){
            if(this.notification_manager) {
                this.notification_manager.do_notify(message.title, message.message, message.sticky);
            }
        }
    });
    
    return WebClient;
    
});
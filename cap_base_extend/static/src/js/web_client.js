odoo.define('cap_base_extend.web_client', function (require) {
"use strict";


var AbstractWebClient = require('web.AbstractWebClient');
var utils = require('web.utils');
var session = require('web.session');
var config = require('web.config');
var core = require('web.core');
var _t = core._t;


return AbstractWebClient.include({
    start: function () {
        var self = this;
        // we add the o_touch_device css class to allow CSS to target touch
        // devices.  This is only for styling purpose, if you need javascript
        // specific behaviour for touch device, just use the config object
        // exported by web.config
        this.$el.toggleClass('o_touch_device', config.device.touch);
        this.on("change:title_part", this, this._title_changed);
        this._title_changed();
        var state = $.bbq.getState();
        // If not set on the url, retrieve cids from the local storage
        // of from the default company on the user
        var current_company_id = session.user_companies.current_company[0]
        var allowed_companies = _.map(session.user_companies.allowed_companies, function(company) {return company[0]});
        if (!state.cids) {
            if (utils.get_cookie('cids') !== null){
               state.cids = allowed_companies.toString();
            }
        }
        var stateCompanyIDS = _.map(state.cids.split(','), function (cid) { return parseInt(cid) });
        var userCompanyIDS = _.map(session.user_companies.allowed_companies, function(company) {return company[0]});
        // Check that the user has access to all the companies
        if (!_.isEmpty(_.difference(stateCompanyIDS, userCompanyIDS))) {
            state.cids = String(stateCompanyIDS);
            stateCompanyIDS = [current_company_id]
        }
        // Update the user context with this configuration
        session.user_context.allowed_company_ids = stateCompanyIDS;
        $.bbq.pushState(state);
        // Update favicon
        $("link[type='image/x-icon']").attr('href', '/web/image/res.company/' + String(stateCompanyIDS[0]) + '/favicon/')

        return session.is_bound
            .then(function () {
                self.$el.toggleClass('o_rtl', _t.database.parameters.direction === "rtl");
                self.bind_events();
                return Promise.all([
                    self.set_action_manager(),
                    self.set_loading()
                ]);
            }).then(function () {
                if (session.session_is_valid()) {
                    return self.show_application();
                } else {
                    // database manager needs the webclient to keep going even
                    // though it has no valid session
                    return Promise.resolve();
                }
            }).then(function () {
                // Listen to 'scroll' event and propagate it on main bus
                self.action_manager.$el.on('scroll', core.bus.trigger.bind(core.bus, 'scroll'));
                core.bus.trigger('web_client_ready');
                odoo.isReady = true;
                if (session.uid === 1) {
                    self.$el.addClass('o_is_superuser');
                }
            });
    },
})
});
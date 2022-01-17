odoo.define('cap_hide_save_and_new_button.view_dialogs', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var ViewDialogs = require('web.view_dialogs');
var dom = require('web.dom');
var view_registry = require('web.view_registry');
var select_create_controllers_registry = require('web.select_create_controllers_registry');

var _t = core._t;

/**
 * Create and edit dialog (displays a form view record and leave once saved)
 */
ViewDialogs.FormViewDialog.include({
    /**
     * @param {Widget} parent
     * @param {Object} [options]
     * @param {string} [options.parentID] the id of the parent record. It is
     *   useful for situations such as a one2many opened in a form view dialog.
     *   In that case, we want to be able to properly evaluate domains with the
     *   'parent' key.
     * @param {integer} [options.res_id] the id of the record to open
     * @param {Object} [options.form_view_options] dict of options to pass to
     *   the Form View @todo: make it work
     * @param {Object} [options.fields_view] optional form fields_view
     * @param {boolean} [options.readonly=false] only applicable when not in
     *   creation mode
     * @param {boolean} [options.deletable=false] whether or not the record can
     *   be deleted
     * @param {boolean} [options.disable_multiple_selection=false] set to true
     *   to remove the possibility to create several records in a row
     * @param {function} [options.on_saved] callback executed after saving a
     *   record.  It will be called with the record data, and a boolean which
     *   indicates if something was changed
     * @param {function} [options.on_remove] callback executed when the user
     *   clicks on the 'Remove' button
     * @param {BasicModel} [options.model] if given, it will be used instead of
     *  a new form view model
     * @param {string} [options.recordID] if given, the model has to be given as
     *   well, and in that case, it will be used without loading anything.
     * @param {boolean} [options.shouldSaveLocally] if true, the view dialog
     *   will save locally instead of actually saving (useful for one2manys)
     */
    init: function (parent, options) {
        var self = this;
        options = options || {};

        this.res_id = options.res_id || null;
        this.on_saved = options.on_saved || (function () {});
        this.on_remove = options.on_remove || (function () {});
        this.context = options.context;
        this.model = options.model;
        this.parentID = options.parentID;
        this.recordID = options.recordID;
        this.shouldSaveLocally = options.shouldSaveLocally;
        this.readonly = options.readonly;
        this.deletable = options.deletable;
        this.disable_multiple_selection = options.disable_multiple_selection;
        var oBtnRemove = 'o_btn_remove';

        var multi_select = !_.isNumber(options.res_id) && !options.disable_multiple_selection;
        // force multi_select = false
        multi_select = false;
        var readonly = _.isNumber(options.res_id) && options.readonly;

        if (!options.buttons) {
            options.buttons = [{
                text: (readonly ? _t("Close") : _t("Discard")),
                classes: "btn-secondary o_form_button_cancel",
                close: true,
                click: function () {
                    if (!readonly) {
                        self.form_view.model.discardChanges(self.form_view.handle, {
                            rollback: self.shouldSaveLocally,
                        });
                    }
                },
            }];

            if (multi_select) {
                options.buttons.splice(1, 0, {
                    text: _t("Save & New"),
                    classes: "btn-primary",
                    click: function () {
                        self._save()
                            .then(self.form_view.createRecord.bind(self.form_view, self.parentID))
                            .then(function () {
                                if (!self.deletable) {
                                    return;
                                }
                                self.deletable = false;
                                self.buttons = self.buttons.filter(function (button) {
                                    return button.classes.split(' ').indexOf(oBtnRemove) < 0;
                                });
                                self.set_buttons(self.buttons);
                                self.set_title(_t("Create ") + _.str.strRight(self.title, _t("Open: ")));
                            });
                    },
                });
            }

            if (!readonly) {
                options.buttons.unshift({
                    text: (multi_select ? _t("Save & Close") : _t("Save")),
                    classes: "btn-primary",
                    click: function () {
                        self._save().then(self.close.bind(self));
                    }
                });

                var multi = options.disable_multiple_selection;
                if (!multi && this.deletable) {
                    this._setRemoveButtonOption(options, oBtnRemove);
                }
            }
        }
        this._super(parent, options);
    },


});

return {
    FormViewDialog: FormViewDialog,
};

});

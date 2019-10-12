odoo.define('e2yun_website_helpdesk_form.animation', function (require) {
    'use strict';

    var core = require('web.core');
    var time = require('web.time');
    var ajax = require('web.ajax');
    var sAnimation = require('website.content.snippets.animation');

    var _t = core._t;
    var qweb = core.qweb;

    sAnimation.registry.form_builder_send = sAnimation.Class.extend({
        selector: '.s_website_form_e2yun',

        willStart: function () {
            var def;
            if (!$.fn.datetimepicker) {
                def = ajax.loadJS("/web/static/lib/tempusdominus/tempusdominus.js");
            }
            return $.when(this._super.apply(this, arguments), def);
        },

        start: function (editable_mode) {
            if (editable_mode) {
                this.stop();
                return;
            }
            var self = this;
            this.templates_loaded = ajax.loadXML('/website_form/static/src/xml/website_form.xml', qweb);
            this.$target.find('.aui-website-form-send').on('click', function (e) {
                self.send(e);
            });
            this.$target.find('#team_list').on('change', function (e) {
                 window.location.href = window.location.origin + '/helpdesk/'+this.value+'/submit';
            });

            // Initialize datetimepickers
            var l10n = _t.database.parameters;
            var datepickers_options = {
                minDate: moment({y: 1900}),
                maxDate: moment().add(200, "y"),
                calendarWeeks: true,
                icons: {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    next: 'fa fa-chevron-right',
                    previous: 'fa fa-chevron-left',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down',
                },
                locale: moment.locale(),
                format: time.getLangDatetimeFormat(),
            };
            this.$target.find('.o_website_form_datetime').datetimepicker(datepickers_options);

            // Adapt options to date-only pickers
            datepickers_options.format = time.getLangDateFormat();
            this.$target.find('.o_website_form_date').datetimepicker(datepickers_options);

            wx.getLocation({
                type: 'wgs84', // 默认为wgs84的gps坐标，如果要返回直接给openLocation用的火星坐标，可传入'gcj02'
                success: function (res) {
                    var latitude = res.latitude; // 纬度，浮点数，范围为90 ~ -90
                    var longitude = res.longitude; // 经度，浮点数，范围为180 ~ -180。
                    var speed = res.speed; // 速度，以米/每秒计
                    var accuracy = res.accuracy; // 位置精度
                    var locations = res.longitude + "," + res.latitude; //微信位置
                    var locations = res.longitude + "," + res.latitude; //微信位置
                    $.getJSON("/amap/convert?location=" + locations,   //将微信地址转为正确的地址，由于GV地址位置有偏差
                        function (result) {
                            var tolocations = result.locations;//实际地址
                            var useraddress = $('input[name=address]').val();
                            if(useraddress.trim() == "") {
                                $('input[name=address]').val(result.formatted_address)
                            }
                        });
                }, fail: function () {

                }
            }); // end getLocation

            return this._super.apply(this, arguments);
        },

        destroy: function () {
            this._super.apply(this, arguments);
            this.$target.find('button').off('click');
        },

        send: function (e) {
            e.preventDefault();  // Prevent the default submit behavior
            this.$target.find('.aui-website-form-send').off('click').addClass('aui-website-form-send-disabled');  // Prevent users from crazy clicking

            var self = this;

            self.$target.find('#o_website_form_result').empty();
            if (!self.check_error_fields({})) {
                self.update_status('invalid');
                return false;
            }

            // Prepare form inputs
            this.form_fields = this.$target.serializeArray();
            _.each(this.$target.find('input[type=file]'), function (input) {
                $.each($(input).prop('files'), function (index, file) {
                    // Index field name as ajax won't accept arrays of files
                    // when aggregating multiple files into a single field value
                    self.form_fields.push({
                        name: input.name + '[' + index + ']',
                        value: file
                    });
                });
            });

            // Serialize form inputs into a single object
            // Aggregate multiple values into arrays
            var form_values = {};
            _.each(this.form_fields, function (input) {
                if (input.name in form_values) {
                    // If a value already exists for this field,
                    // we are facing a x2many field, so we store
                    // the values in an array.
                    if (Array.isArray(form_values[input.name])) {
                        form_values[input.name].push(input.value);
                    } else {
                        form_values[input.name] = [form_values[input.name], input.value];
                    }
                } else {
                    if (input.value !== '') {
                        form_values[input.name] = input.value;
                    }
                }
            });

            // Overwrite form_values array with values from the form tag
            // Necessary to handle field values generated server-side, since
            // using t-att- inside a snippet makes it non-editable !
            for (var key in this.$target.data()) {
                if (_.str.startsWith(key, 'form_field_')) {
                    form_values[key.replace('form_field_', '')] = this.$target.data(key);
                }
            }
            self.send_form('send');
            // Post form and handle result
            ajax.post(this.$target.attr('action') + (this.$target.data('force_action') || this.$target.data('model_name')), form_values)
                .then(function (result_data) {
                    result_data = $.parseJSON(result_data);
                    if (!result_data.id) {
                        // Failure, the server didn't return the created record ID
                        self.update_status('error');
                        if (result_data.error_fields) {
                            // If the server return a list of bad fields, show these fields for users
                            self.check_error_fields(result_data.error_fields);
                        }
                    } else {
                        // Success, redirect or update status
                        var success_page = self.$target.attr('data-success_page');
                        if (success_page) {
                            $(window.location).attr('href', success_page);
                        } else {
                            self.update_status('success');
                        }

                        // Reset the form
                        self.$target[0].reset();
                    }
                })
                .fail(function (result_data) {
                    self.update_status('error');
                });
        },

        check_error_fields: function (error_fields) {
            var self = this;
            var form_valid = true;
            // Loop on all fields

            this.$target.find('input,textarea').each(function (k, field) {
                var $field = $(field);
                var field_name = $field.attr("name");
                if (($field.attr("type") === 'text'
                        || $field.attr("type") === 'datetime-local'
                        || $field.is('textarea')
                    )
                    && $field.attr("required") === "required") {
                    if ($field.val().length == 0) {
                        $field.addClass('o_has_error').find('.form-control').addClass('is-invalid');
                        $field.popover('show');
                        $field.focus();
                        form_valid = false;
                        return form_valid;
                    }
                }
            });


            return form_valid;
        },

        is_datetime_valid: function (value, type_of_date) {
            if (value === "") {
                return true;
            } else {
                try {
                    this.parse_date(value, type_of_date);
                    return true;
                } catch (e) {
                    return false;
                }
            }
        },

        // This is a stripped down version of format.js parse_value function
        parse_date: function (value, type_of_date, value_if_empty) {
            var date_pattern = time.getLangDateFormat(),
                time_pattern = time.getLangTimeFormat();
            var date_pattern_wo_zero = date_pattern.replace('MM', 'M').replace('DD', 'D'),
                time_pattern_wo_zero = time_pattern.replace('HH', 'H').replace('mm', 'm').replace('ss', 's');
            switch (type_of_date) {
                case 'datetime':
                    var datetime = moment(value, [date_pattern + ' ' + time_pattern, date_pattern_wo_zero + ' ' + time_pattern_wo_zero], true);
                    if (datetime.isValid())
                        return time.datetime_to_str(datetime.toDate());
                    throw new Error(_.str.sprintf(_t("'%s' is not a correct datetime"), value));
                case 'date':
                    var date = moment(value, [date_pattern, date_pattern_wo_zero], true);
                    if (date.isValid())
                        return time.date_to_str(date.toDate());
                    throw new Error(_.str.sprintf(_t("'%s' is not a correct date"), value));
            }
            return value;
        },
        send_form: function (status) {
            if (status == 'send') {
                this.$target.find('.aui-website-form-send').off('click').addClass('aui-website-form-send-disabled');
                this.$target.find('.aui-website-form-send').attr("disabled", true);
                this.$target.find('.aui-website-form-send-text').text("正在提交")
            }

        },
        update_status: function (status) {
            var self = this;
            if (status !== 'success') {  // Restore send button behavior if result is an error
                this.$target.find('.aui-website-form-send').on('click', function (e) {
                    self.send(e);
                }).removeClass('aui-website-form-send-disabled');
                this.$target.find('.aui-website-form-send').attr("disabled", false);
            }
            var $result = this.$('#o_website_form_result');
            this.$target.find('. aui-website-form-send-text').text("提交")
            this.templates_loaded.done(function () {
                $result.replaceWith(qweb.render("website_form.status_" + status));
            });
        },
    });
});

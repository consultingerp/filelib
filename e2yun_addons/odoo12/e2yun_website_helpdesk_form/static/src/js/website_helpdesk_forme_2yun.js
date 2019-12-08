odoo.define('e2yun_website_helpdesk_form.animation', function (require) {
    'use strict';

    var core = require('web.core');
    var time = require('web.time');
    var ajax = require('web.ajax');
    var sAnimation = require('website.content.snippets.animation');

    var _t = core._t;
    var qweb = core.qweb;
    ajax.loadXML('/e2yun_website_helpdesk_form/static/src/xml/helpdeskdesk_matnr.xml', qweb);

    sAnimation.registry.form_builder_send = sAnimation.Class.extend({
        selector: '.s_website_form_e2yun',
        events: {
            //'change input[name=user_phone]': '_searchusermatnr',
            'click a[id=wximages]': '_userimag',
            'click a[id=online_customer]':'_clickteamcustomer'
        },
        willStart: function () {
            var def;
            if (!$.fn.datetimepicker) {
                def = ajax.loadJS("/web/static/lib/tempusdominus/tempusdominus.js");
            }
            return $.when(this._super.apply(this, arguments), def);
        }, wxGetLocation: function () {
            setTimeout(function () {
                var isuserlocation = false;
                var user_addres_Setting = function (addressComponent, formatted_address) {
                    var $target = $('#u_address');
                    var team_list_text = $("#team_list option:selected").text();
                    if (addressComponent == "") {
                        $('input[name=j_address]').val(formatted_address)
                        $target.citySelect(); //默认
                        $target.on('click', function (event) {
                            event.stopPropagation();
                            $target.citySelect('open');
                        });
                        $target.on('done.ydui.cityselect', function (ret) {
                            $(this).val(ret.provance + ' ' + ret.city + ' ' + ret.area);
                            $('input[name=j_address]').val('');
                        });
                        return;
                    }
                    var provance = addressComponent.province;
                    var city = addressComponent.district;
                    var area = ""
                    $('input[name=u_address]').val(provance + " " + city + " ")
                    let area_user = {}
                    area_user.provance = "";
                    area_user.city = "";
                    area_user.area = "";
                    $.each(YDUI_CITYS, function (k, v) { //第一层
                        if (v.n == provance || provance.indexOf(v.n) > -1) {
                            //console.log("1" + v.n);
                            area_user.provance = v.n
                            formatted_address = formatted_address.replace(provance, '');
                            $.each(v.c, function (k, v) {   //第二层
                                if (v.n.indexOf(city) > -1) {
                                    //console.log("2:" + v.n + "::" + v.a);
                                    area_user.city = v.n
                                    formatted_address = formatted_address.replace(city, '');
                                    $.each(v.a, function (k, v) { // 第三层
                                        if (k == 0) area_user.area = v;
                                        if (v.indexOf(area) > -1) {
                                            console.log(k + ":" + v);
                                            area_user.area = v;
                                            return false;
                                        }
                                    });
                                }
                            });
                        }

                    });
                    $target.citySelect({  //带地址
                        provance: area_user.provance,
                        city: area_user.city,
                        area: area_user.area
                    });
                    $('input[name=j_address]').val(formatted_address)
                    // $target.citySelect(); //默认
                    $target.on('click', function (event) {
                        event.stopPropagation();
                        $target.citySelect('open');
                    });
                    $target.on('done.ydui.cityselect', function (ret) {
                        $(this).val(ret.provance + ' ' + ret.city + ' ' + ret.area);
                        $('input[name=j_address]').val('');

                    });
                };
                var useraddress = $('input[name=j_address]').val();
                var is_wx_client = $('input[name=is_wx_client]').val();
                if (is_wx_client == "1" || useraddress.trim() == "") { // 如果地址为空，没有默认地址，去取定位地
                    wx.getLocation({
                        type: 'wgs84', // 默认为wgs84的gps坐标，如果要返回直接给openLocation用的火星坐标，可传入'gcj02'
                        success: function (res) {
                            var latitude = res.latitude; // 纬度，浮点数，范围为90 ~ -90
                            var longitude = res.longitude; // 经度，浮点数，范围为180 ~ -180。
                            var speed = res.speed; // 速度，以米/每秒计
                            var accuracy = res.accuracy; // 位置精度
                            var locations = res.longitude + "," + res.latitude; //微信位置
                            var locations = res.longitude + "," + res.latitude; //微信位置
                            isuserlocation = true;
                            $.getJSON("/amap/convert?location=" + locations,   //将微信地址转为正确的地址，由于GV地址位置有偏差
                                function (result) {
                                    var tolocations = result.locations;//实际地址
                                    var formatted_address = result.addressComponent; //坐标定位
                                    console.log(formatted_address);
                                    if (useraddress.trim() == "") {
                                        $('input[name=j_address]').val(result.formatted_address)
                                        user_addres_Setting(formatted_address, result.formatted_address);
                                    }
                                });
                        }, fail: function (res) {
                            user_addres_Setting('', '');
                            console.log("失败调用");

                        }, cancel: function (res) {
                            user_addres_Setting('', '');
                            alert('用户拒绝授权获取地理位置');
                        }
                    }); // end getLocation

                }
            }, 1500);

        }, start: function (editable_mode) {
            if (editable_mode) {
                this.stop();
                return;
            }

            var state_id = $('input[name=state_id]').val();
            var city_id = $('input[name=city_id]').val();
            var area_id = $('input[name=area_id]').val();
            if (state_id != "") {
                $('input[name=u_address]').val(state_id + " " + city_id + " " + area_id)
                this.start_addres(state_id, city_id, area_id)
            }
            var is_wx_client = $('input[name=is_wx_client]').val();
            if (is_wx_client == '0') {   //判断是微信浏览器 不是就加载空地址让用户选择
                this.start_addres('', '', '');
                $('.mod_hang_appeal_show').css("display", "block");
            }else{
                 this.start_addres('', '', '');
                // this.$target.find('.mod_hang_appeal_show').css("display", "none");
            }

            this.start_date_controls();
            this.after_sales_tel_show();
            //this.address_resolution();
            //console.log(this.getArea('重庆市九龙坡区石桥铺街道兰美路988-26号隆鑫·花漾湖'));

            var self = this;
            this.templates_loaded = ajax.loadXML('/website_form/static/src/xml/website_form.xml', qweb);
            this.$target.find('.aui-website-form-send').on('click', function (e) {
                self.send(e);
            });
            this.$target.find('#user_helpdesk').on('click', function (e) {
                var team_id = $('input[name=team_id]').val();
                window.location.href = window.location.origin + '/helpdesk/user_helpdesk/' + team_id;
            });
            this.$target.find('#team_list').on('change', function (e) {
                window.location.href = window.location.origin + '/helpdesk/' + this.value + '/submit';
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
            this.wxGetLocation();
            this.$target.find('.openerp o_livechat_button d-print-none').hide();
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
                    if ($field.val().trim().length == 0) {
                        $field.addClass('o_has_error').find('.form-control').addClass('is-invalid');
                        $field.popover('show');
                        $field.focus();
                        form_valid = false;
                        return form_valid;
                    }
                }
                if (field_name == "phone") {
                    var phone = $field.val();
                    if (!(/^1[3456789]\d{9}$/.test(phone))) {
                        alert("联系电话有误，请新重填");
                        form_valid = false;
                        return form_valid;
                    }
                }
                if (field_name == "user_phone") {
                    var phone = $field.val();
                    if (phone != "" && !(/^1[3456789]\d{9}$/.test(phone))) {
                        alert("购买电话有误，请新重填");
                        form_valid = false;
                        return form_valid;
                    }
                }
            });


            return form_valid;
        }, _clickteamcustomer: function (e) {
            var team_id = $('input[name=team_id]').val();
            window.location.href = window.location.origin + '/helpdesk/user_helpdesk/' + team_id+"";
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
            this.$target.find('.aui-website-form-send-text').text("提交")
            this.templates_loaded.done(function () {
                $result.replaceWith(qweb.render("website_form.status_" + status));
            });
        }, start_addres: function (provance, city, area) {
            var $target = $('#u_address');
            var team_list_text = $("#team_list option:selected").text();
            var user_addres = this.address_resolution(provance, city, area);
            $target.citySelect({  //带地址
                provance: user_addres.provance,
                city: user_addres.city,
                area: user_addres.area
            });
            // $target.citySelect(); //默认
            $target.on('click', function (event) {
                event.stopPropagation();
                $target.citySelect('open');
            });
            $target.on('done.ydui.cityselect', function (ret) {
                $(this).val(ret.provance + ' ' + ret.city + ' ' + ret.area);
                $('input[name=j_address]').val('');
            });

        }, _searchusermatnr: function (e) {
            var self = this;
            var $input = $(e.target);
            var user_phone = $input.val()
            if (user_phone != "" && !(/^1[3456789]\d{9}$/.test(user_phone))) {
                alert("购买电话有误，请新重填");
                return false;
            }
            self._rpc({
                route: '/helpdesk/searchusermatnr',
                params: {
                    telephone: $input.val()
                },
            }).then(function (result) {
                var html = qweb.render('matnrs_list', {
                    matnrs: result.matnrs
                });
                self.$('#matnrs').empty();
                self.$('#matnrs').append(html)
                var matnrs_option = new Array();
                for (let index in result.matnrs) {
                    var matnr = result.matnrs[index];
                    if (result.matnrs.length > 0 && typeof matnr.arktx != "undefined") {
                        matnrs_option.push({label: matnr.arktx, value: matnr.matnr})
                    }

                }
                $("#mySelect").empty();
                if (matnrs_option.length > 0) {
                    self.$('#matnrs').show();
                    var mySelect = $("#mySelect").mySelect({
                        mult: true,//true为多选,false为单选
                        option: matnrs_option,
                        onChange: function (res, res2) {//选择框值变化返回结果
                            $('input[name=matnrs]').val(res);
                            $('input[name=arktxs]').val(res2);
                        }
                    });
                    mySelect.setResult([]);
                } else {
                    self.$('#matnrs').hide();
                }

            });


        }, start_date_controls: function () {
            var theme = "ios";
            var mode = "scroller";
            var display = "bottom";
            var lang = "zh";
            var date = new Date;
            var dateend = new Date;
            dateend.setMonth(dateend.getMonth() + 2);
            $('#order_datetime').mobiscroll().date({
                theme: theme,
                mode: mode,
                minDate: new Date(date.getFullYear(), date.getMonth(), date.getDate() + 2),
                maxDate: new Date(dateend.getFullYear(), dateend.getMonth(), dateend.getDate()),
                dateFormat: "yyyy-mm-dd",
                display: display,
                lang: lang
            });
        },
        address_resolution: function (provance, city, area) {
            let area_user = {}
            area_user.provance = "";
            area_user.city = "";
            area_user.area = "";
            $.each(YDUI_CITYS, function (k, v) { //第一层
                if (v.n == provance) {
                    //console.log("1" + v.n);
                    area_user.provance = provance
                    $.each(v.c, function (k, v) {   //第二层
                        if (v.n.indexOf(city) > -1) {
                            //console.log("2:" + v.n + "::" + v.a);
                            area_user.city = v.n
                            $.each(v.a, function (k, v) { //
                                if (k == 0) area_user.area = v;
                                if (v.indexOf(area) > -1) {
                                    console.log(k + ":" + v);
                                    area_user.area = v;
                                    return false;
                                }
                            });
                        }
                    });
                }

            });
            return area_user;
        }, after_sales_tel_show: function () {
            var html_after_sales = ' <li>尊敬的客户，您好！欢迎进行售后服务咨询，如需电话咨询请按下方提示进行操作：</li>\n' +
                '                                    <li><i class="fa fa-phone"/> <span>北京：售后服务时间8:30-17:30，联系电话:<a  href="tel:010-81501568">010-81501568</a></span></li>\n' +
                '                                    <li><i class="fa fa-phone"/> <span>深圳：售后服务时间8:00-17:30，联系电话:<a  href="tel:0755-26913085">0755-26913085</a></span></li>'
            $('#connect').find('.list-unstyled').replaceWith(html_after_sales)
        }, getArea: function (str) {
            let area = {}
            let index11 = 0
            let index1 = str.indexOf("省")
            if (index1 == -1) {
                index11 = str.indexOf("自治区")
                if (index11 != -1) {
                    area.Province = str.substring(0, index11 + 3)
                } else {
                    area.Province = str.substring(0, 0)
                }
            } else {
                area.Province = str.substring(0, index1 + 1)
            }

            let index2 = str.indexOf("市")
            if (index11 == -1) {
                area.City = str.substring(index11 + 1, index2 + 1)
            } else {
                if (index11 == 0) {
                    area.City = str.substring(index1 + 1, index2 + 1)
                } else {
                    area.City = str.substring(index11 + 3, index2 + 1)
                }
            }

            let index3 = str.lastIndexOf("区")
            if (index3 == -1) {
                index3 = str.indexOf("县")
                area.Country = str.substring(index2 + 1, index3 + 1)
            } else {
                area.Country = str.substring(index2 + 1, index3 + 1)
            }
            return area;
        }, _userimag(serviceorderid) {
            var images = {
                localId: [],
                serverId: [],
                localwebid: []
            };
            wx.chooseImage({
                count: 9, // 默认9
                sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有
                sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
                success: function (res) {
                    var localIds = res.localIds; // 返回选定照片的本地ID列表，localId可以作为img标签的src属性显示图片
                    //alert("localIds:"+localIds);
                    images.localId = res.localIds;

                    alert('已选择 ' + res.localIds.length + ' 张图片');
                    if (images.localId.length == 0) {
                        alert('请先使用 chooseImage 接口选择图片');
                        return;
                    }
                    var i = 0, length = images.localId.length;
                    images.serverId = [];

                    function upload() {
                        wx.uploadImage({
                            localId: images.localId[i],
                            success: function (res) {
                                var image_index = i;
                                i++;
                                var serverId = res.serverId; // 返回图片的服务器端ID
                                //alert("serverId:"+serverId);
                                images.serverId.push(res.serverId);
                                alert(images.localId[image_index]);
                                images.localwebid.push(images.localId[image_index]);
                                // var image = "<a id='image" + image_index + "' href='#popupPhotoLandscape" + image_index + "' data-rel='popup' data-position-to='window' class='ui-btn ui-corner-all ui-shadow ui-btn-inline'>";
                                // image = image + "<image idth='60px' height='60px' src='" + images.localId[image_index] + "'/>";
                                // image = image + "</a>";
                                // image = image + "<div data-role='popup' id='popupPhotoLandscape' class='photopopup' data-overlay-theme='b' data-corners='true' data-tolerance='50,30'>";
                                // image = image + "<div data-role='controlgroup' data-type='horizontal'>";
                                // image = image + " <a href=\"javascript:deleteimage('"+image_index+"')\"    data-ajax='false'>删除</a>";
                                // image = image + " <a href='#' data-rel='back'>back</a>";
                                // image = image + "</div>";
                                // image = image + "<img src='" + images.localId[image_index] + "'' alt='Photo landscape'>";
                                // image = image + "</div>";
                                var image = "";
                                image = image + "<img src='" + images.localId[image_index] + "'' alt='Photo landscape'>";
                                image = image + " <a href=\"javascript:\"    data-ajax='false'>删除</a>";

                                alert(image);
                                // var image=$("<image idth='60px' height='60px' src='${pageContext.request.contextPath}/weixinfile/"+data.media_id+"'/>");
                                $("#imagecount").append(image).trigger("create");


                                alert(i + "：" + length);
                                if (i < length) {
                                    upload();
                                }
                            },
                            fail: function (res) {
                                alert(JSON.stringify(res));
                            }
                        });

                    } // end
                    upload();
                }
            });

        }

    });
});

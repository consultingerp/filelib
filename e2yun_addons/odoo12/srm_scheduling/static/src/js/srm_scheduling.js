odoo.define('srm_scheduling', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var mixins = require('web.mixins');
    var page=0; //初始页
    var size=4; //每页显示多少条
    var table_data_map={};
    var current_select_bmeng="";
    var is_supplier=true;
    var supplier_bmeng_temp=0;
    var s_c_schedul_map;  //供应商确认数据列表
    var initial_requirement_map; //期初需求
    var revisions_edit_flag=""; //验证是否历史版本，历史版本：0，不能编辑
var srm_scheduling = Widget.extend({
    template: 'srm_scheduling_qweb',
    init:function(){
         this._super.apply(this, arguments);
     },
    start: function() {
    var q=this.$el;
    var self = this;
    var supplier=q.find("#query_supplier_code").val();
    var version=q.find("#query_version").val();
    var werks=q.find("#query_werks_code").val();
    var query_xqrq_e=q.find("#query_xqrq_e").val();
    var query_matnr=q.find("#query_matnr").val();
    var totalData=0; //总页数
    page=0;
    this._rpc({ model:'srm.scheduling',method:'intitle_data',args: [size, page,supplier,werks,query_xqrq_e,query_matnr],
         }).then(function (result) {
            if(result['is_supplier']==0){
                is_supplier=false
            }else{
                $("#query_supplier_code_text").hide();//隐藏
                $("#query_supplier_code").hide();//隐藏
            }
            var tb = q.find('#table0');
            totalData = result['count'];
            s_c_schedul_map=result['s_c_schedule'];
            revisions_edit_flag=result['revisions_edit_flag'];
            initial_requirement_map=result['initial_requirement'];
            if(totalData>0) {
                self.bindclick(self, totalData);
                self.inser_data(tb, result);
                $('#query_version').val(result["version"]);
            }else {
                self.show_msg_alert("没有数据"+result["msg"])
            }
       });


      this.$el.find('#query_button').on('click', function (e) {
             page=0;
              var supplier =q.find("#query_supplier_code").val();
              var werks=q.find("#query_werks_code").val();
              var query_xqrq_e=q.find("#query_xqrq_e").val();
              var query_matnr=q.find("#query_matnr").val();
              self.test_read(self,size, page,supplier,werks,query_xqrq_e,query_matnr)

          });


    },
    test_read: function (self,size, page,supplier,werks,query_xqrq_e,query_matnr) {
        var q=this.$el;
        var totalData=0
         this._rpc({ model:'srm.scheduling',method:'intitle_data',args: [size, page,supplier,werks,query_xqrq_e,query_matnr],
             }).then(function (result) {
                var tb=q.find('#table0');
                totalData = result['count'];
                s_c_schedul_map=result['s_c_schedule'];
                revisions_edit_flag=result['revisions_edit_flag'];
                initial_requirement_map=result['initial_requirement'];
                if(totalData>0) {
                    if (result["msg"]!=""){
                        self.show_msg_alert(result["msg"])
                    }
                    self.bindclick(self, totalData);
                    self.inser_data(tb, result);
                }else{
                     tb.empty("");
                     self.show_msg_alert("没有数据,"+result["msg"])
                }
              });
    },
    gelegate:function (action,selector,callback){
        document.addEventListener(action,function(e){
            if(selector==e.target.tagName.toLowerCase()||selector==e.target.className){
                callback(e);
            }
        })
    },



    bindclick:function(self,totalData){
           var q=this.$el;
             $('#s_count').text(totalData);
             $('#l_count').text(size);
             $('#p_count').text((totalData/size).toFixed(0));
           //分页
            $('.M-box11').pagination({
                mode: 'fixed',
                pageCount:totalData,
				totalData: totalData,
				showData: size,
				//jump: true,
				callback: function (api) {
                       var supplier = q.find("#query_supplier_code").val();
                       var werks=q.find("#query_werks_code").val();
                        var query_xqrq_e=q.find("#query_xqrq_e").val();
                         var query_matnr=q.find("#query_matnr").val();
                    page=api.getCurrent()-1;
                self._rpc({ model:'srm.scheduling',method:'intitle_data',args: [size, page,supplier,werks,query_xqrq_e,query_matnr],
                  }).then(function (result) {
                    s_c_schedul_map=result['s_c_schedule'];
                    revisions_edit_flag=result['revisions_edit_flag'];
                    initial_requirement_map=result['initial_requirement'];
                    var tb=q.find('#table0');
                        self.inser_data(tb,result);
                   });
				}
         });

        this.$el.find("label").unbind('click');
        self.gelegate('click','label',function(e){
             //判断是否查看数据历史记录
                var val =""
                if (navigator.userAgent.indexOf('Firefox') >= 0) {
                        val = e.target.id  //定义val值为点击的此td的id值；
                }else {
                        val = e.srcElement.id  //定义val值为点击的此td的id值；
                }

            if(val!=""){
                var vallogflag=val.substring(0,2)
                if(vallogflag=="bz") {
                    //点击备注加载日志页面
                    self.show_model_data_log();
                    return;
                }
             }else {
                    return;
             }

              q.find("#model_bmeng").val("");
              self.refresh_config_form();
              self.show_confirm_the_schedule(val)

         });
        this.$el.find("label").unbind('img');
        //this.$target.find('.o_website_form_send').on('click',function (e) {self.send(e);}).removeClass('disabled');
        self.gelegate('click','img',function(e){
              q.find("#model_bmeng").val("");
              var val =""
                if (navigator.userAgent.indexOf('Firefox') >= 0) {
                        val = e.target.id  //定义val值为点击的此td的id值；
                }else {
                        val = e.srcElement.id  //定义val值为点击的此td的id值；
                }

                // if(table_data_map[val]) {
                //     if (table_data_map[val]['jhtsl'] && table_data_map[val]['jhtsl'] > 0) {
                //         return;
                //     }
                // }

                self.refresh_config_form();
                self.show_confirm_the_schedule(val)

         });
           this.$el.find("#alert_message_close").unbind('click');

           this.$el.delegate("#alert_message_close","click",function(){
                    $('#div_alert_message').hide();
           })


           this.$el.find("#btnupdate_bmeng").unbind('click');

           this.$el.delegate("#btnupdate_bmeng","click",function(){
                var bmeng =q.find("#model_bmeng").val();
                var zdpcs =q.find("#model_zdpcs").text();
                var msg="";
                var is_h_hu_l=1;  //红0：黄1，绿2


               if(!is_supplier){
                  if(!bmeng&&bmeng<99999){
                         msg="请输入排程数"
                  }else if(bmeng<0){
                         msg="请输入大于0的确认数"
                  }else if(Number(bmeng)>Number(zdpcs)){
                         msg="排程数量不能大于当前最大排程数"
                  }else if(Number(bmeng)>Number(supplier_bmeng_temp)){
                         msg="采购员确认数不能大于供应商确认数"
                  }
               }else {
                  var menge=table_data_map[current_select_bmeng]['menge']
                  if(!bmeng){
                         msg="请输入排程数"
                  }else if(bmeng<0){
                         msg="请输入大于0的确认数"
                  }else if(Number(bmeng)>Number(zdpcs)){
                         msg="排程数量不能大于当前最大排程数"
                  }else{
                      //验证是否满足排程需求
                      var current_select_ddatekey = current_select_bmeng.substring(current_select_bmeng.length - 10, current_select_bmeng.length)
                      var initial_requirement_mapkey = table_data_map[current_select_bmeng]['versi']  + table_data_map[current_select_bmeng]['lifnr'] + table_data_map[current_select_bmeng]['matnr']
                      s_c_schedul_map[initial_requirement_mapkey][current_select_ddatekey]['bmeng'] = bmeng;
                      var sum_bmeng = 0;
                      var temp_sum_bmeng=0;  //验证确认数是否用于满足期初数
                      for (var key in s_c_schedul_map[initial_requirement_mapkey]) {
                          if(!s_c_schedul_map[initial_requirement_mapkey][key]['bmeng']){
                              continue
                          }
                          sum_bmeng += Number(s_c_schedul_map[initial_requirement_mapkey][key]['bmeng'])  //汇总确认数不能大于当前总需求数
                          if(Number(s_c_schedul_map[initial_requirement_mapkey][key]['bmeng'])>Number(s_c_schedul_map[initial_requirement_mapkey][key]['menge']) ){
                                     temp_sum_bmeng+=Number(s_c_schedul_map[initial_requirement_mapkey][key]['bmeng'])-Number(s_c_schedul_map[initial_requirement_mapkey][key]['menge'])
                          }
                      }
                      if(Number(sum_bmeng)>Number(table_data_map[current_select_bmeng]['total_requirement_sum'])){
                           msg="排程数量不能大于总需求数"
                      }
                     var qcxqsl=Number(initial_requirement_map[initial_requirement_mapkey]['ysqcxqsl'])
                     //日期内汇总大于期初需求
                     // if((temp_sum_bmeng>=qcxqsl)&&(bmeng==menge)){
                     if(bmeng==menge){
                             is_h_hu_l=2
                      }
                  }
              }
               if(msg!=""){
                    self.show_msg_alert(msg)
                    return;
               }

               var is_pomsg=false
              if(Number(table_data_map[current_select_bmeng]['unclean_po'])<sum_bmeng){
                   // var isconfirm=confirm("PO不满足,确认是否继续")
                   // alert(isconfirm)
                     //setTimeout(function(){},5000);
                      self.show_msg_alert("PO不满足")
                       is_pomsg=true
                     // setTimeout(function(){ },1000);
                     // self.sleep(5000);  //睡眠5秒;

               }

               var state=""
               var beizhu_temp=""
               if(is_supplier){
                    if(table_data_map[current_select_bmeng]['line_state']=="采购员确认"){
                        state="supplier_edit";
                    }else{
                         state="supplier_confirm";
                    }

               }else{
                    state="purchase_confirm"
                    is_h_hu_l=2
               }

               if(table_data_map[current_select_bmeng]['schedule_confirm']==false){
                    is_h_hu_l=2
                    state="not_confirm"
               }
               var current_bmeng=bmeng;
               var versi=table_data_map[current_select_bmeng]['versi']
               var lifnr=table_data_map[current_select_bmeng]['lifnr']
               var ddate=table_data_map[current_select_bmeng]['ddate']
               var matnr=table_data_map[current_select_bmeng]['matnr']

              if(table_data_map[current_select_bmeng]['wxq']){
                 self._rpc({ model:'srm.scheduling',method:'add_demand',args:  [versi,lifnr,ddate,matnr,current_bmeng,state,is_h_hu_l],
                 }).then(function (result) {
                            if(result==1){
                                if(is_pomsg) {
                                    setTimeout(function () {
                                        $('#modelupdate_bmeng').modal('hide');
                                        self.refresh_data(self);
                                    }, 1500);
                                }else{
                                    $('#modelupdate_bmeng').modal('hide');
                                     self.refresh_data(self);
                                }

                            }else{
                                self.show_msg_alert("错误")
                            }
                  })
              }else{
                   self._rpc({ model:'srm.scheduling',method:'update_bmeng',args:[versi,lifnr,ddate,matnr,current_bmeng,state,is_h_hu_l],
                   }).then(function (result) {
                            if(result==1){
                                 if(is_pomsg) {
                                    setTimeout(function () {
                                        $('#modelupdate_bmeng').modal('hide');
                                        self.refresh_data(self);
                                    }, 1500);
                                }else{
                                    $('#modelupdate_bmeng').modal('hide');
                                     self.refresh_data(self);
                                }
                            }else{
                                self.show_msg_alert("错误")
                            }
                })
              }




            });
   },
    inser_data:function(tb,result){
               tb.empty("");
               var initial_requirement=0;
                    //表格抬头
                    var table_title="<tr>";

                    for(var i=0; i<result['title'].length; i++){
                        if(i<2){
                             table_title+="<th style='width:200px' >"+result['title'][i]+"</th>";
                        }else if(i>5) {
                             var title_map=result['title_map'][result['title'][i]]
                               table_title+="<td>"+title_map['week']+"<br>"+title_map['date']+"</td>";
                              //table_title+="<th>"+result['title'][i]+"</th>";
                        }else{
                             table_title+="<th>"+result['title'][i]+"</th>";
                        }
                    }
                    table_title+="</tr>";
                    tb.append(table_title)
                    var table_content="";
                    //表格内容
                    for (var i=0; i<result['data'].length;i++){
                         var v=result['data'][i]
                         var initial_requirement_mapkey=v['versi']+v['lifnr']+v['matnr']
                         table_content+="<tr>";
                         var supplier="";
                         if(v['supplier']){
                                supplier=v['supplier'];
                         }
                         table_content+="<td  rowspan=5  >"+supplier+"<br>"+v['supplier_name']+"</td>";
                         table_content+="<td  rowspan=5  >"+v['matnr_a']+"<br>"+v['matnrdesc']+"</td>";
                         if(v['initial_requirement']){
                             initial_requirement=v['initial_requirement']
                             table_content+="<td>"+initial_requirement+"</td>";  //期初需求
                             // table_content+="<td><li id=qc"+ initial_requirement_mapkey +">"+initial_requirement_map[initial_requirement_mapkey]['ysqcxqsl']+"</li></td>";  //期初需求
                         }else{
                             initial_requirement=0
                             table_content+="<td></td>";  //期初需求
                         }
                         table_content+="<td>计划</td>";
                         table_content+="<td>"+v['unclean_po']+"</td>"; //未清PO
                         table_content+="<td>"+v['total_requirement']+"</td>"; //总需求

                        for(var j=6; j<result['title'].length; j++){
                            var qr=v['requirement_line'][result['title'][j]];
                             if(Object.keys(qr).length> 0) {
                                table_content += "<td>" + qr['menge'] + "</td>";
                             }else{
                                 table_content += "<td></td>";
                             }
                         }
                         table_content+="</tr>"
                         table_content+="<tr>";
                         table_content+="<td></td>";  //期初需求
                         table_content+="<td>确认</td>";
                         table_content+="<td></td>"; //未清PO
                         table_content+="<td>"+v['qrs_sum']+"</td>"; //总需求
                      var table_data_key="";
                      var qrr="";
                      var qrrr={}


                      var temp_num=initial_requirement  //截止到今天的期初数
                       for(var j=6; j<result['title'].length; j++){
                           qr=v['requirement_line'][result['title'][j]];
                           if(Object.keys(qr).length> 0) {
                               qrr={};
                               table_data_key= qr['versi']  + qr['lifnr'] + v['matnr']+qr['ddate'] ;
                                if(table_data_key){
                                   table_data_key=table_data_key.replace(/[ ]/g,"")
                                }


                               qr['matnr']= v['matnr'];
                               qr['matnr_a']= v['matnr_a'];
                               qr['supplier_code']= v['supplier'];
                               qr['supplier_name']= v['supplier_name'];
                               qr['matnrdesc']= v['matnrdesc'];
                               qr['min_qty_jsh']=v['min_qty_jsh'];
                               qr['unclean_po']=v['unclean_po'];
                               qr['time_tolerance']=v['time_tolerance'];
                               qr['schedule_confirm']=v['schedule_confirm'];
                               qr['total_requirement_sum']=v['total_requirement_sum'];


                               qrr=qr
                               /**计算最大排程数
                                * 1
                                * 期初数=原始期初数量+（截止到今天的期初数-确认排程数）
                                * 2
                                *当前最大可排程数
                                * 最大可排程数=(1.期初数+当天需求数+容差天数可排数量)
                                * 3
                                * 最小包装数
                                * 2.最大排程数>0，计算最小包装（目前没考虑数量容差）
                                *
                                *
                                * **/
                               var bmeng=0;
                               var menge=0;
                               if(qr['bmeng']){
                                   bmeng=qr['bmeng'];
                               }
                               if(qr['menge']){
                                   menge=qr['menge'];
                               }

                             var zdpcs_temp=menge;
                             if(v['time_tolerance']){

                               var day_i=0;
                               while (day_i<Number(v['time_tolerance'])){
                                   day_i++
                                   var d=new Date(qr['ddate']);
                                   d.setDate(d.getDate()+day_i);
                                   var d_format =d.Format("yyyy-MM-dd");

                                   if(v['requirement_line'][[d_format]]&&v['requirement_line'][[d_format]]['menge']>0){
                                        zdpcs_temp+=(Number(v['requirement_line'][[d_format]]['menge'])-Number(v['requirement_line'][[d_format]]['bmeng']));
                                   }
                                }
                             }

                              zdpcs_temp=zdpcs_temp+temp_num;
                              temp_num=temp_num+(menge-bmeng); //计算截止到今天的期初数
                               if(zdpcs_temp>0){
                                   //计算最小包装
                                    if (qr['min_qty']&&qr['min_qty']>0){
                                          var min_qty=qr['min_qty'];
                                          //zdpcs_temp=zdpcs_temp+qr['the_quota']
                                          var minqty_i=1
                                          while ((min_qty*minqty_i)< zdpcs_temp)
                                          {
                                              minqty_i++
                                          }
                                          min_qty=min_qty*minqty_i
                                          zdpcs_temp+=(min_qty-zdpcs_temp)
                                    }
                                         qr['zdpcs']=zdpcs_temp;
                               }else {
                                      qr['zdpcs']=0;

                               }
                               table_data_map[table_data_key]=qr;
                              //var temp_nunber=Number(initial_requirement_map[qr['versi']+ qr['lifnr'] + v['matnr']]['qcxqsl'])
                              //temp_num<0&&
                              if((menge==bmeng)||qr["line_state"]=="采购员确认"||qr["line_state"]=="无需确认"){
                                       table_content += "<td     id=td"+table_data_key+"  class='td_lvse' style='background-color: #00ff00' ><label id="+table_data_key+">" + bmeng + "</label></td>";
                               }else if(qr["line_state"]=="供应商确认"||qr["line_state"]=="供应商修改"){
                                    if(is_supplier){
                                        table_content += "<td    id=td"+table_data_key+"  class='td_huangse' style='background-color: #ffff00'   ><label id="+ table_data_key +">" + bmeng + "</label></td>";
                                    }else{
                                        table_content += "<td    id=td"+table_data_key+"  class='td_hongse' style='background-color: #ff0000'  ><label id="+ table_data_key + ">" + bmeng + "</label></td>";
                                    }

                                }else if(qr["line_state"]=="业务新建"){
                                  if(is_supplier){
                                        table_content += "<td id=td"+table_data_key+"  class='td_hongse' style=background-color: #ff0000 ><label id="+ table_data_key + ">" + bmeng + "</label></td>";
                                    }else{
                                        table_content += "<td id=td"+table_data_key+"  class='td_huangse' style=background-color: #ffff00 ><label id=" + table_data_key +">" + bmeng + "</label></td>";
                                    }
                                }
                            }else {
                                qrrr={}
                                qrrr['menge']=0;
                                var zdpcs_temp=0;
                                qrrr['ddate']=result['title'][j];
                                qrrr['wxq']=true
                                qrrr['matnr']= v['matnr'];
                                qrrr['lifnr']=v['lifnr'];
                                qrrr['versi']=v['versi'];
                                qrrr['line_state']="供应商确认";
                                qrrr['total_requirement']=v['total_requirement'];
                                qrrr['matnr']= v['matnr'];
                                qrrr['matnr_a']= v['matnr_a'];
                                qrrr['supplier_code']= v['supplier'];
                                qrrr['supplier_name']= v['supplier_name'];
                                qrrr['matnrdesc']= v['matnrdesc'];
                                qrrr['min_qty_jsh']=v['min_qty_jsh'];
                                qrrr['unclean_po']=v['unclean_po'];
                                qrrr['the_quota']=v['the_quota'];
                                qrrr['min_qty']=v['min_qty'];
                                qrrr['time_tolerance']=v['time_tolerance'];
                                qrrr['schedule_confirm']=v['schedule_confirm'];
                                qrrr['jhtsl']=0;
                                qrrr['total_requirement_sum']=v['total_requirement_sum'];

                                table_data_key= qrrr['versi']  + qrrr['lifnr'] + qrrr['matnr']+qrrr['ddate'] ;
                                if(table_data_key){
                                   table_data_key=table_data_key.replace(/[ ]/g,"")
                                }

                              if(v['time_tolerance']){
                               var day_i=0;
                               while (day_i<Number(v['time_tolerance'])){
                                   day_i++
                                   var d = new Date(qrrr['ddate'])
                                   d.setDate(d.getDate()+day_i);
                                   var d_format =d.Format("yyyy-MM-dd");
                                       if(v['requirement_line'][[d_format]]&&v['requirement_line'][[d_format]]['menge']>0){
                                       zdpcs_temp+=Number(v['requirement_line'][[d_format]]['menge']);
                                   }
                               }
                             }

                              zdpcs_temp=zdpcs_temp+temp_num;

                              //temp_num=temp_num+(menge-bmeng);

                               if(zdpcs_temp>0){
                                    if (qrrr['min_qty']&&qrrr['min_qty']>0){
                                          var min_qty=qrrr['min_qty'];
                                          //zdpcs_temp=zdpcs_temp+qrrr['the_quota']
                                          var minqty_i=1
                                          while ((min_qty*minqty_i)< zdpcs_temp)
                                          {
                                              minqty_i++
                                          }
                                          min_qty=min_qty*minqty_i
                                          zdpcs_temp+=(min_qty-zdpcs_temp)
                                    }
                                      qrrr['zdpcs']=zdpcs_temp;
                               }else {
                                      qrrr['zdpcs']=0;
                               }
                                table_data_map[table_data_key]=qrrr;
                                table_content += "<td><img id="+table_data_key+"  src='/srm_scheduling/static/src/img/bi001.png'  alt='add'  height=20px width=20px /></td>";
                                //table_content += "<td></td>";
                               }
                         }
                         table_content+="</tr>";
                         table_content+="<tr>";
                         table_content+="<td></td>";  //期初需求
                         table_content+="<td>交货单</td>";
                         table_content+="<td></td>";
                         table_content+="<td>"+v['jhd_sum']+"</td>"; //总需求
                        for(var j=6; j<result['title'].length; j++){
                            qr=v['requirement_line'][result['title'][j]];
                              if(Object.keys(qr).length> 0) {
                                  table_content += "<td>" + qr['jhtsl'] + "</td>";
                              }else {
                                  table_content += "<td></td>";
                              }
                         }
                         table_content+="</tr>";

                         table_content+="<tr>";
                         table_content+="<td></td>";  //期初需求
                         table_content+="<td>已收货</td>";
                         table_content+="<td></td>";

                         if(v['yjhsl']){
                               table_content += "<td>" + v['yjhsl'] + "</td>"; //总需求
                         }else {
                                table_content += "<td></td>";
                         }


                        for(var j=6; j<result['title'].length; j++){
                            var qr=v['requirement_line'][result['title'][j]];
                              if(Object.keys(qr).length> 0) {
                                  table_content += "<td>" + qr['yjhsl'] + "</td>";
                              }else {
                                   table_content += "<td></td>";
                              }
                         }

                         table_content+="</tr>";

                         table_content+="<tr>";
                         table_content+="<td></td>";  //期初需求
                         table_content+="<td>备注</td>";
                         table_content+="<td></td>"; //未清PO
                         table_content+="<td></td>"; //总需求
                        for(var j=6; j<result['title'].length; j++){
                             qr=v['requirement_line'][result['title'][j]];
                            var table_data_key= qr['versi']  + qr['lifnr'] + v['matnr']+qr['ddate'] ;
                               if(table_data_key){
                                   table_data_key=table_data_key.replace(/[ ]/g,"")
                                }
                               if(Object.keys(qr).length > 0) {
                                   var memo=""
                                   if(qr["line_state"]){
                                       memo=qr["line_state"]
                                   }

                                   table_content += "<td><label id=bz" + table_data_key +  ">" + memo + "</label></td>";
                               }else {
                                   table_content += "<td></td>";
                               }
                         }
                         table_content+="</tr>";
                    }
                   tb.append(table_content)
   },refresh_data:function(self){
         //刷新页面数据
                      var supplier = $("#query_supplier_code").val();
                       var werks=$("#query_werks_code").val();
                       var query_xqrq_e=$("#query_xqrq_e").val();
                       var query_matnr=$("#query_matnr").val();


                 this._rpc({ model:'srm.scheduling',method:'intitle_data',args: [size, page,supplier,werks,query_xqrq_e,query_matnr], }).then(function (result) {
                    s_c_schedul_map=result['s_c_schedule'];
                    initial_requirement_map=result['initial_requirement'];
                    var totalData = result['count'];
                    var tb=$("#table0")
                        //self.bindclick(self, totalData);
                        self.inser_data(tb,result);
                   });
    },sleep: function(numberMillis) {
        var now = new Date();
        var exitTime = now.getTime() + numberMillis;
        while (true) {
            now = new Date();
            if (now.getTime() > exitTime)
                return;
        }
    },show_confirm_the_schedule:function(val){
             if(val==""){
                 return;
             }
             current_select_bmeng=val;
             $('#model_supplier').html(table_data_map[val]['supplier_code']);

             $('#model_supplier_name').html(table_data_map[val]['supplier_name']);

             $('#model_matnr').html(table_data_map[val]['matnr_a']);   //物料

             $('#model_ddate').html(table_data_map[val]['ddate']);   //日期

             $('#model_matnr_name').html(table_data_map[val]['matnrdesc']);  //物料名称

             $('#model_d_o_days').html(table_data_map[val]['time_tolerance']);   //时间容差

             $('#model_the_quota').html(table_data_map[val]['the_quota']);  //数量容差

             $('#model_zxbzs').html(table_data_map[val]['min_qty']);      //最小包装量

             $('#model_unclean_po').html(table_data_map[val]['unclean_po']);  //未清PO

             $('#model_dqpcs').html(table_data_map[val]['menge']);  //当前排程数
             //最大排程取剩余可排程数
             $('#model_zdpcs').html(table_data_map[val]['zdpcs']); //最大排程数+期初需求
             if(Number(table_data_map[val]['bmeng'])>0){
                 supplier_bmeng_temp=Number(table_data_map[val]['bmeng']);
                  if(!is_supplier) {
                     $("#model_bmeng").val(Number(table_data_map[val]['bmeng']));
                  }
             }
             $('#modelupdate_bmeng').modal('show');
     },refresh_config_form:function () {
             $('#model_supplier').html("");
             $('#model_supplier_name').html("");
             $('#model_matnr').html("");   //物料
             $('#model_ddate').html("");   //日期
             $('#model_matnr_name').html("");  //物料名称
             $('#model_d_o_days').html("");   //时间容差
             $('#model_the_quota').html("");  //数量容差
             $('#model_zxbzs').html("");      //最小包装量
             $('#model_unclean_po').html("");  //未清PO
             $('#model_dqpcs').html("");  //当前排程数
     },update_calculate_initial_flag:function (u_calcu_init_flag_listMap) {

          this._rpc({ model:'srm.scheduling',method:'update_calculate_initial_flag',args:[u_calcu_init_flag_listMap],
                   }).then(function (result) {
                    if(result==0){
                          $('#alert_message').html("后台更新标识异常")
                    }
            });
    },show_msg_alert:function (msg) {
             this.do_warn(msg);
    },show_model_data_log:function () {
    return;
    var tb=$('#tab_datalog');
    tb.empty("");
     var table_content="<tr><td>操作时间</td><td>操作人</td><td>原始数据</td><td>变更后数据</td></tr>"
       for(var i=0; i<3;i++){
            table_content+="<tr><td>2018年7月3日14:41:51</td><td>adddmn</td><td></td><td>100</td></tr>"
       }

       tb.append(table_content);
        $('#model_datalog').modal('show');
    },
    on_attach_callback: function () {

    },
    canBeRemoved: function () {
        return $.when();
    },
    on_detach_callback: function () {}

});

core.action_registry.add('srm_scheduling', srm_scheduling);

return srm_scheduling;
});

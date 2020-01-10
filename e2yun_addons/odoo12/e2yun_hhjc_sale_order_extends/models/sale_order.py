# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api, exceptions, _
import datetime
import suds.client
import json
from . import myjsondateencode
import logging

_logger = logging.getLogger(__name__)


class SaleOrderCrmStatusFlow(models.Model):
    _name = 'sale.order.crmstate.flow'

    order_id = fields.Many2one('sale.order', '销售订单')
    crmstate = fields.Char("CRM订单状态", default="新建",
                           help="A.1已接单2加工中3加工完成4部分送货 / 送货完成5（改派状态）\nB.1已接单2生产中3全部入库/部分入库4部分送货/送货完成5（改派状态）\nC.1已接单2部分送货/送货完成3（改派状态）")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    salesorderid = fields.Char('订单编号', copy=False)
    vip = fields.Char('客户编号')
    vipname = fields.Char('客户名称')
    kunnr = fields.Char('门店名称')
    telephone = fields.Char('联系电话')
    address = fields.Char('客户地址')
    ywy = fields.Char('导购员')
    gongsishejishitext = fields.Char('公司设计师')
    yujijiaohuoriqi = fields.Date('预计交货日期')
    po = fields.Char('客户PO号')
    contractno = fields.Char('合同编号')
    orderreason = fields.Char('订单原因')
    elevator = fields.Boolean('电梯')
    upstairs = fields.Boolean('送货上楼')
    gongzhang = fields.Char('工长')
    shejishi = fields.Char('设计师')
    jiesuanjine = fields.Float('结算金额')
    jiangjiafei1 = fields.Float('降价费1')
    jiangjiafei2 = fields.Float('降价费2')
    vkorg = fields.Char('销售组织')
    branch = fields.Char('分部')
    werks = fields.Char('工厂')
    feiyongshishou = fields.Float('费用实收')
    remarks = fields.Float('备注')
    orderstatustext = fields.Char('订单状态')
    viptypetext = fields.Char('门店类别')
    orderdate = fields.Date('下单日期')
    pricedate = fields.Date('定价日期')
    ordertypetext = fields.Char('订单类型')
    createuserid = fields.Char('创建人')
    insertdatetime = fields.Date('创建时间')
    updater = fields.Char('更新人')
    totalmoney = fields.Float('总金额')
    operatedatetime = fields.Datetime('pos最后更新时间')

    vkorgtext = fields.Char('事业部')
    vtweg = fields.Char('分销渠道')

    # 订单状态的粒度定义，或产品或产品分类定义订单状态，或是定义统一的订单状态，通过业务运行触发订单状态更新。推送消息给客户，或客户可在自己个人中心查看。
    # 订单信息：显示已支付的总金额
    # A
    # .1
    # 已接单2加工中3加工完成4部分送货 / 送货完成5（改派状态）
    # 送货状态推送送货人信息（已推送）。
    # 二维码不一定是具体产品，可能是系列或者类别的。
    # 瓷砖Z101\Z106、销售订单行项目采购交货页签（加工字段有一个项目为是）
    # 1.
    # 确认销售单（除已关闭状态）， 2.
    # 加工单状态是已传输
    # .3.加工单状态是已转储。4.
    # 部分送货有送货，销售订单所有行项目已交完货为送货完成。5.
    # 取相应退货订单的退货原因。（有退货就显示）
    # 备注：装运条件是空退空出的不是显示在客户的“我的订单”里
    # 整张订单关闭不显示。
    # 送货剩下行项目关闭，状态更新为送货完成。
    # B
    # .1
    # 已接单2生产中3全部入库 / 部分入库4部分送货 / 送货完成5（改派状态）
    # Z102\Z103\Z105, 行项目物料的是否是否定制为001，只要有一个是就是定制品
    # 1.
    # 确认报价单（订单状态不等于已传输与已关闭），2.
    # 订单状态为已传输（当有关闭定制品行项目时检查是否有效的产品项目），3.
    # 所有行项目入库就是已入库是全部入库，部分行项目入库显示部分入库。检查销售订单库存（对应物料，对应批次），允许手工修改。4.
    # 部分送货有送货，销售订单所有行项目已交完货为送货完成。5.
    # 取相应退货订单的退货原因。
    # 整张订单关闭不显示。
    # 送货剩下行项目关闭，状态更新为送货完成。
    # C
    # .1
    # 已接单2部分送货 / 送货完成3（改派状态）
    # 除A\B之外的。
    # 1.
    # 确认报价单（订单状态不等于已关闭），2.
    # 部分送货有送货，销售订单所有行项目已交完货为送货完成。3.
    # 取相应退货订单的退货原因。
    # 任务：销售订单相关字段
    # A.1已接单2加工中3加工完成4部分送货 / 送货完成5（改派状态）
    # B.1已接单2生产中3全部入库/部分入库4部分送货/送货完成5（改派状态）
    # C.1已接单2部分送货/送货完成3（改派状态）
    crmstate = fields.Char("CRM订单状态", default="新建",
                           help="A.1已接单2加工中3加工完成4部分送货 / 送货完成5（改派状态）\nB.1已接单2生产中3全部入库/部分入库4部分送货/送货完成5（改派状态）\nC.1已接单2部分送货/送货完成3（改派状态）")

    crmstate_flow = fields.One2many('sale.order.crmstate.flow', 'order_id', string='CRM状态流')

    # @api.model
    # def create(self, vals):
    #     res = super(SaleOrder, self).create(vals)
    #     if 'is_sync' not in vals or not vals['is_sync']:
    #         try:
    #             res.action_sync_sale_to_pos()
    #         except Exception as e:
    #             _logger.error("同步订单到POS出现错误，对象: %s，错误信息：%s", self, e)
    #     return res

    @api.model
    def create(self, vals):
        if 'pricelist_id' not in vals:
            pricelist_id = self.env['res.company']._company_default_get(
                'sale.order').partner_id.property_product_pricelist
            if pricelist_id:
                vals['pricelist_id'] = pricelist_id.id

        res = super(SaleOrder, self).create(vals)
        try:
            if 'is_sync' in vals and vals['is_sync']:
                res.state = 'sent'
            if res.salesorderid:
                if res.ywy:
                    _logger.info('创建开始设置销售员信息=============================')
                    users = self.sudo().env['res.users'].search([('name', '=', res.ywy)])
                    if users:
                        myuser = users[0]
                        for user in users:
                            if not user.customer:
                                myuser = user
                        if myuser:
                            res.user_id = myuser
                if res.kunnr:
                    _logger.info('创建开始设置门店和公司信息=============================')
                    kunnrs = self.sudo().env['crm.team'].search([('shop_code', '=', res.kunnr)])
                    if kunnrs:
                        res.team_id = kunnrs[0]
                        res.company_id = res.team_id.company_id
        except Exception as e:
            _logger.error(e)
        return res

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        try:
            for item in self:
                if 'is_sync' in vals and vals['is_sync']:
                    if item.state == 'draft':
                        item.state = 'sent'
                if item.sudo().pricelist_id.company_id != item.sudo().team_id.company_id:
                    _logger.info('==========================开始修改价格表=============================================')
                    pricelist = self.sudo().env['product.pricelist'].search(
                        [('company_id', '=', item.sudo().team_id.company_id.id)], limit=1)
                    if pricelist:
                        item.pricelist_id = pricelist
                    for order_line in item.order_line:
                        order_line.product_uom_change()
        except Exception as e:
            _logger.error(e)
        if 'crmstate' in vals and vals['crmstate']:
            for item in self:
                flow = self.env['sale.order.crmstate.flow'].search(
                    [('order_id', '=', self.id), ('crmstate', '=', vals['crmstate'])])
                if not flow:
                    self.env['sale.order.crmstate.flow'].create({
                        'order_id': self.id,
                        'crmstate': vals['crmstate'],
                    })

        try:
            for item in self:
                if item.salesorderid:
                    if 'ywy' in vals and vals['ywy']:
                        _logger.info('更新开始设置销售员信息=============================')
                        users = item.sudo().env['res.users'].search([('name', '=', vals['ywy'])])
                        if users:
                            item.user_id = users[0]
                    if 'kunnr' in vals and vals['kunnr']:
                        _logger.info('更新开始设置门店和公司信息=============================')
                        kunnrs = item.sudo().env['crm.team'].search([('shop_code', '=', vals['kunnr'])])
                        if kunnrs:
                            item.team_id = kunnrs[0]
                            item.company_id = item.team_id.company_id
        except Exception as e:
            _logger.error(e)
        return res

    # @api.multi
    # @api.depends('crmstate')
    # def _compute_crmstate(self):
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #     url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncSaleOrder?wsdl'  # webservice调用地址
    #     client = suds.client.Client(url)
    #     datajsonstring = {}
    #     datajsonstring['salesorderid']
    #     result = client.service.getSaleOrderCrmState(json.dumps(datajsonstring, cls=myjsondateencode.MyJsonEncode))
    #     resultjson = json.loads(result)
    #     sucess = resultjson['sucess']
    #     if sucess == 'no':
    #         raise exceptions.Warning("同步失败,返回信息：%s" % resultjson['message'])
    #     self.crmstate = resultjson['crmstate']

    def action_sync_sale_state_from_pos(self):
        if self and self.salesorderid:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncSaleOrder?wsdl'  # webservice调用地址
            client = suds.client.Client(url)
            datajsonstring = {}
            datajsonstring['salesorderid'] = self.salesorderid
            result = client.service.getSaleOrderCrmState(json.dumps(datajsonstring, cls=myjsondateencode.MyJsonEncode))
            resultjson = json.loads(result)
            sucess = resultjson['sucess']
            if sucess == 'no':
                raise exceptions.Warning("同步失败,返回信息：%s" % resultjson['message'])
            self.crmstate = resultjson['crmstate']
        else:
            raise exceptions.Warning("POS销售订单为空，不能同步pos状态！")

    def action_sync_sale_to_pos(self):
        res = self
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncSaleOrder?wsdl'  # webservice调用地址
        client = suds.client.Client(url)
        datajsonstring = {}
        for key in res._fields.keys():
            if res._fields[key].type not in ('many2one', 'many2many', 'one2many', 'binary'):
                datajsonstring[key] = res[key] or ''
        # datajsonstring = dict(res)
        # for key in datajsonstring.keys():
        #     if not datajsonstring[key]:
        #         datajsonstring[key] = ''
        datajsonstring['posid'] = res.partner_id.app_code
        datajsonstring['kunnr'] = res.team_id.shop_code or ''
        datajsonstring['VTEXT'] = res.team_id.shop_type or '电商终端'
        datajsonstring['orderdate'] = res.create_date.today()
        datajsonstring['operator'] = self.env.user.name
        datajsonstring['dianyuan'] = res.user_id.name
        datajsonstring['totalmoney'] = res.amount_total
        datajsonstring['jiesuanjine'] = res.amount_total
        datajsonstring['bukrs'] = res.company_id.company_code
        datajsonstring['bukrstext'] = res.company_id.name
        datajsonstring['degree'] = 'A'
        datajsonstring['pricedate'] = res.create_date.strftime("%Y-%m-%d")
        datajsonstring['yujijiaohuoriqi'] = res.create_date.strftime("%Y-%m-%d")
        # datajsonstring['dianyuan'] = res.user_id.login
        orderitem = []
        num = 10

        # chuxiao_total = 0

        for line in res.order_line:
            item = {}
            line.product_id
            # if line.price_unit < 0:
            #     chuxiao_total += line.price_unit * line.product_uom_qty
            #     pass
            # else:
            item['matnr'] = line.product_id.default_code
            item['maktx'] = line.product_id.name
            item['spart'] = line.product_id.product_group
            item['sparttext'] = line.product_id.product_group
            item['prdha'] = line.product_id.layer
            item['prdhatext'] = line.product_id.layer_name
            item['maktx'] = line.product_id.name
            item['itemtype'] = 'ZTA1'
            item['itemtypetext'] = '标准项目'
            item['jiaohuozhuangtaitext'] = '未创建交货单'
            item['rownum'] = num
            item['kwmen'] = line.product_uom_qty
            item['vrkme'] = line.product_uom.name
            item['meins'] = line.product_uom.name
            item['kbetr'] = line.price_unit
            item['xiaoshoujine'] = line.price_unit
            item['jiesuanjine'] = line.price_unit
            item['itemtotal'] = item['xiaoshoujine'] * item['kwmen']
            item['itemjiesuantotal'] = item['jiesuanjine'] * item['kwmen']
            item['kpein'] = 1
            num += 10
            orderitem.append(item)

        item = {}
        item['matnr'] = '100'
        item['maktx'] = 'AZF安装费'
        item['ismanualinsert'] = 1
        # item['spart'] = line.product_id.product_group
        # item['sparttext'] = line.product_id.product_group
        # item['prdha'] = line.product_id.layer
        # item['prdhatext'] = line.product_id.layer_name
        item['itemtype'] = 'ZWOD'
        item['itemtypetext'] = '费用项目'
        item['jiaohuozhuangtaitext'] = '无需交货'
        item['rownum'] = num
        item['kwmen'] = 1
        item['vrkme'] = 'SET'
        item['meins'] = 'SET'
        item['kbetr'] = 0
        item['xiaoshoujine'] = 0
        item['jiesuanjine'] = 0
        item['itemtotal'] = 0
        item['itemjiesuantotal'] = 0
        item['kpein'] = 1
        orderitem.append(item)

        # try:
        #     newtotalmoney = 0
        #     if chuxiao_total < 0:
        #         for item in orderitem:
        #             price_unit = round(item['itemtotal'] / (datajsonstring['totalmoney'] - chuxiao_total) * datajsonstring['totalmoney'] / item['kwmen'], 2)
        #             totalmoney = price_unit * item['kwmen']
        #             item['xiaoshoujine'] = price_unit
        #             item['jiesuanjine'] = price_unit
        #             item['itemtotal'] = totalmoney
        #             item['itemjiesuantotal'] = totalmoney
        #             newtotalmoney += totalmoney
        #         if newtotalmoney != datajsonstring['totalmoney']:
        #             leave_money = newtotalmoney - datajsonstring['totalmoney']
        #             orderitem[0]['itemtotal'] = orderitem[0]['itemtotal'] + leave_money
        #             orderitem[0]['itemjiesuantotal'] = orderitem[0]['itemtotal']
        #             orderitem[0]['xiaoshoujine'] = orderitem[0]['xiaoshoujine'] + leave_money / orderitem[0]['kwmen']
        #             orderitem[0]['jiesuanjine'] = orderitem[0]['xiaoshoujine']
        #         # datajsonstring['totalmoney'] = newtotalmoney
        # except Exception as e:
        #     _logger.log(str(e))
        datajsonstring['orderitem'] = orderitem
        result = client.service.synSaleOrderFromCrm(json.dumps(datajsonstring, cls=myjsondateencode.MyJsonEncode))
        resultjson = json.loads(result)
        sucess = resultjson['sucess']
        if sucess == 'no':
            raise exceptions.Warning("同步失败,返回信息：%s" % resultjson['message'])
        res.salesorderid = resultjson['salesorderid']
        if 'orderstatustext' in resultjson and resultjson['orderstatustext']:
            res.orderstatustext = resultjson['orderstatustext']
        res.crmstate = '已接单'

    def action_unfreeze_order(self):
        # self.env['sale.order']._fields.keys()
        if self.orderstatustext == '冻结':
            ICPSudo = self.env['ir.config_parameter'].sudo()
            url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncSaleOrder?wsdl'  # webservice调用地址
            client = suds.client.Client(url)
            datajsonstring = {'salesorderid': self.salesorderid}
            result = client.service.unfreezeSaleOrder(json.dumps(datajsonstring, cls=myjsondateencode.MyJsonEncode))
            resultjson = json.loads(result)
            if 'orderstatus' in resultjson and resultjson['orderstatus']:
                self.orderstatus = resultjson['orderstatus']
                self.orderstatustext = resultjson['orderstatustext']
            return result
        else:
            raise exceptions.Warning(_("订单状态为：%s，订单无需审批！" % self.orderstatustext))

    @api.model
    def action_sync_pos_sale_order_pos_invoke(self, data):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncSaleOrder?wsdl'  # webservice调用地址
        pageSize = ICPSudo.get_param('e2yun.pos_sync_pageSize') or 20
        client = suds.client.Client(url)
        sale_order = self.env['sale.order']
        sale_order_line = self.env['sale.order.line']

        if data['salesorderid']:
            result = client.service.getSaleOrderInfo(data['salesorderid'])
            json2python = json.loads(result)
            line = json2python['orderHead']
            if 'vkorg' not in line or line['vkorg'] not in ['1000', '2000']:
                return True
            order = sale_order.search([('salesorderid', '=', line['salesorderid'])])
            order.order_line.unlink()
            data = {}
            date_line = {}
            for key in line.keys():
                if key in sale_order._fields:
                    data[key] = line[key]
            data['createuserid'] = line['createusername']
            data['kunnr'] = line['kunnrname']
            partner = self.env['res.partner'].search([('app_code', '=', line['memberposid'])])
            if partner:
                data['partner_id'] = partner.id
            else:
                raise exceptions.Warning("客户：%s不存在，请检查客户是否同步了。" % (line['memberposid']))
            data['is_sync'] = True
            if order:
                order.write(data)
                order_id = order
            else:
                order_id = sale_order.create(data)
            orderitem = json2python['orderItem']
            not_sync_matnr = ''
            for line in orderitem:
                for key in line:
                    if key in sale_order_line._fields:
                        date_line[key] = line[key]
                date_line['itemtype'] = line['itemtypetext']
                date_line['order_id'] = order_id.id
                date_line['name'] = line['maktx']
                date_line['price_unit'] = line['xiaoshoujine']
                date_line['product_uom_qty'] = line['kwmen']
                product = self.env['product.product'].search([('default_code', '=', line['matnr'])])
                if not product:
                    self.env['product.template'].sync_pos_matnr_to_crm(line['matnr'], '')
                    product = self.env['product.product'].search([('default_code', '=', line['matnr'])])
                if product:
                    date_line['product_id'] = product.id
                    date_line['is_sync'] = True
                    sale_order_line.create(date_line)
                else:
                    not_sync_matnr += line['matnr'] + ','
                if not_sync_matnr:
                    raise exceptions.Warning("物料号：%s不存在，请检查物料是否同步了。" % not_sync_matnr)
            order_id.crmstate = '已接单'
        return True

    def action_sync_pos_sale_order(self):
        # self.env['sale.order']._fields.keys()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncSaleOrder?wsdl'  # webservice调用地址
        pageSize = ICPSudo.get_param('e2yun.pos_sync_pageSize') or 20
        client = suds.client.Client(url)
        sale_order = self.env['sale.order']
        sale_order_line = self.env['sale.order.line']

        if self.salesorderid:
            result = client.service.getSaleOrderInfo(self.salesorderid)
            json2python = json.loads(result)
            line = json2python['orderHead']
            order = sale_order.search([('salesorderid', '=', line['salesorderid'])])
            order.order_line.unlink()
            data = {}
            date_line = {}
            for key in line.keys():
                if key in sale_order._fields:
                    data[key] = line[key]
            data['createuserid'] = line['createusername']
            data['kunnr'] = line['kunnrname']
            partner = self.env['res.partner'].search([('app_code', '=', line['memberposid'])])
            if partner:
                data['partner_id'] = partner.id
            else:
                data['partner_id'] = 3
            data['is_sync'] = True
            data['crmstate'] = '已接单'
            order.write(data)
            order_id = order
            orderitem = json2python['orderItem']
            for line in orderitem:
                for key in line:
                    if key in sale_order_line._fields:
                        date_line[key] = line[key]

                date_line['itemtype'] = line['itemtypetext']
                date_line['order_id'] = order_id.id
                date_line['name'] = line['maktx']
                product = self.env['product.product'].search([('default_code', '=', line['matnr'])])
                if not product:
                    self.env['product.template'].sync_pos_matnr_to_crm(line['matnr'], '2000-01-01')
                    product = self.env['product.product'].search([('default_code', '=', line['matnr'])])
                if product:
                    date_line['product_id'] = product.id
                else:
                    raise exceptions.Warning("物料号：%s不存在，请检查物料是否同步了。" % (line['matnr']))
                date_line['is_sync'] = True
                sale_order_line.create(date_line)
        else:
            info = self.env['sale.order'].search([('operatedatetime', '!=', False)], order='operatedatetime desc',
                                                 limit=1)
            if info.operatedatetime:
                lastDate = info.operatedatetime.strftime('%Y-%m-%d %H:%M:%S')
            else:
                startDate = "2010-10-01"
                lastDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').time()
                lastDate = lastDate.strftime('%Y-%m-%d %H:%M:%S')

            result = client.service.getSaleOrderInfos(lastDate, pageSize)
            json2python = json.loads(result)
            for line in json2python['ROOT']:
                data = {}
                date_line = {}
                for key in line.keys():
                    if key in sale_order._fields:
                        data[key] = line[key]
                partner = self.env['res.partner'].search([('app_code', '=', line['memberposid'])])
                data['partner_id'] = partner.id
                data['is_sync'] = True
                order_id = sale_order.create(data)

                orderitem = line.pop('orderitem')
                for line in orderitem:
                    for key in line:
                        if key in sale_order_line._fields:
                            date_line[key] = line[key]
                    date_line['order_id'] = order_id.id
                    date_line['name'] = line['maktx']
                    product = self.env['product.product'].search([('default_code', '=', line['matnr'])])
                    if not product:
                        self.env['product.product'].sync_pos_matnr_to_crm(line['matnr'], '2000-01-01')
                        product = self.env['product.product'].search([('default_code', '=', line['matnr'])])
                    date_line['product_id'] = product.id
                    sale_order_line['is_sync'] = True
                    sale_order_line.create(date_line)

            # raise Exception('pos销售订单为空，不能同步！')

        return True

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        # if 'is_sync' not in vals or not vals['is_sync']:
        # try:
        for item in self:
            item.action_sync_sale_to_pos()
        # except Exception as e:
        #     _logger.error("同步订单到POS出现错误，对象: %s，错误信息：%s", self, e)
        return res

    @api.multi
    def action_sync_to_pos(self):
        # res = super(SaleOrder, self).action_confirm()
        # if 'is_sync' not in vals or not vals['is_sync']:
        # try:
        for item in self:
            item.action_sync_sale_to_pos()
        # except Exception as e:
        #     _logger.error("同步订单到POS出现错误，对象: %s，错误信息：%s", self, e)
        # return res

    @api.model
    def action_sync_pos_status_for_stock_status(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncReport?wsdl'  # webservice调用地址
        pageSize = ICPSudo.get_param('e2yun.pos_sync_pageSize') or 20
        client = suds.client.Client(url)
        sale_order = self.env['sale.order']
        sale_order_line = self.env['sale.order.line']

        salesorderids = sale_order.search([('crmstate', 'in', ('生产中', '部分入库'))])

        for salesorderid in salesorderids:
            alldone = True
            partdone = False
            for orderline in salesorderid.order_line:
                if orderline.charg:
                    client = suds.client.Client(url)
                    result = client.service.stockQuery(orderline.product_id.default_code, '', '', orderline.charg, '',
                                                       '')
                    if result:
                        for item in result:
                            if item.labst == orderline.product_uom_qty:
                                partdone = True
                            else:
                                alldone = False
                    else:
                        alldone = False

            if alldone:
                salesorderid.crmstate = '全部入库'
            elif partdone:
                salesorderid.crmstate = '部分入库'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rownum = fields.Char('项目号')
    matnr = fields.Char('商品编号')
    maktx = fields.Char('商品名称')
    itemtype = fields.Char('行项目类别')
    kwmen = fields.Float('销售数量')
    charg = fields.Char('批次')
    xiaoshoujine = fields.Float('销售金额')
    jiesuanjine = fields.Float('结算金额')
    itemtotal = fields.Float('销售小计')
    itemjiesuantotal = fields.Float('结算小计')
    feiyongshishou = fields.Float('费用实收')
    feiyongyingshou = fields.Float('费用应收')
    jiangjiafei1 = fields.Float('降价费1')
    jiangjiafei2 = fields.Float('降价费2')
    tuihuoyuanyintext = fields.Char('退货原因')
    gongchanghetongbianhao = fields.Char('工厂合同编号')
    werkstext = fields.Char('工厂')
    lgorttext = fields.Char('仓库')
    dongjieyuanyintext = fields.Char('冻结原因')
    closed = fields.Char('是否关闭')
    isthird = fields.Char('是否第三方')
    jiagongtext = fields.Char('是否加工')

    shiyebu = fields.Char('事业部')
    qudao = fields.Char('分销渠道')
    daogou = fields.Char('导购员', related='order_id.ywy', store=True)
    mendian = fields.Char('门店', related='order_id.kunnr', store=True)
    confirmdate = fields.Date('确认日期', related='order_id.insertdatetime', store=True)

    # @api.model
    # def create(self, vals):
    #     res = super(SaleOrderLine, self).create(vals)
    #     if 'is_sync' not in vals or not vals['is_sync']:
    #         for item in self:
    #             try:
    #                 if item.order_id.state == 'draft':
    #                     item.order_id.action_sync_sale_to_pos()
    #             except Exception as e:
    #                 _logger.error("同步订单到POS出现错误，对象: %s，错误信息：%s", self, e)
    #     return res
    #
    # @api.multi
    # def write(self, vals):
    #     res = super(SaleOrderLine, self).write(vals)
    #     if 'is_sync' not in vals or not vals['is_sync']:
    #         for item in self:
    #             try:
    #                 if item.order_id.state == 'draft':
    #                     item.order_id.action_sync_sale_to_pos()
    #             except Exception as e:
    #                 _logger.error("同步订单到POS出现错误，对象: %s，错误信息：%s", self, e)
    #     return res

#!/usr/bin/python3
from odoo import http
from odoo.http import request
from werkzeug.datastructures import FileStorage
import json
import os
import re, uuid
from odoo import tools


class ParamsEditor(http.Controller):
    def __init__(self):
        self.login_user = False
        self.login_session = False


    def _generate_image_path(self, model, editor_id, file):
        if not file or not isinstance(file, FileStorage):
            return ''

        def make_dir(main_direction, direction):
            direction = os.path.join(main_direction, direction)
            if not os.path.exists(direction):
                os.mkdir(direction)
            if not os.path.isdir(direction):
                raise ValueError(u'错误, 默认图片文件夹%s已经存在且不是文件夹' % direction)
        direction = request.env['ir.config_parameter'].get_param('e2yun.product_image_folder')
        main_direction = ''
        if direction:
            if not os.path.exists(direction) or not os.path.isdir(direction):
                raise ValueError(u'错误，系统配置中获取到的路径不不是文件夹或不存在')
        else:
            main_direction = tools.config.filestore(request.env.cr.dbname)
            img_direction = 'editor_image'
            first_direction = os.path.join(img_direction, editor_id[0:2])
            direction = os.path.join(first_direction, editor_id)
            make_dir(main_direction, img_direction)
            make_dir(main_direction, first_direction)
            make_dir(main_direction, direction)
        pattern = '(.*?)(\.jpg|\.jpeg|\.png|\.gif)'
        file_new_name = file.filename
        file_name = re.findall(pattern, file_new_name)
        if file_name:
            file_new_name = "%s%s" % (uuid.uuid4().hex, file_name[0][1])
        filename = os.path.join(direction, file_new_name)
        file.save(os.path.join(main_direction, filename))
        return 'editor_image?filename=' + filename


    def write_html_field(self, osv_info, save_field, editor_id, write_model):
        html_list = []
        editor_row_obj = request.env[osv_info.get('model_line', 'description.editor.row')]
        for editor_row in editor_row_obj.search([('product_tmpl_id', '=', int(editor_id))]):
            if editor_row.component == 'image-input':
                html_list.append("""<img style="text-align:center;min-width:400px;max-width:600px;padding:10px;margin:10px;"src="http://%s/%s"/>"""
                                 % (request.httprequest.host, editor_row.value))
            elif editor_row.component == 'text-input':
                html_list.append("""%s""" % editor_row.value)
        write_model_row = write_model.browse(editor_id)
        write_model_row[save_field] = """<div style="text-align:center;min-width:400px;max-width:600px;padding:10px;margin:10px;">%s</div>""" % ''.join(html_list)






    @http.route('/images/add', auth='public', type='http', csrf=False)
    def images_add(self, **kws):
        file = kws.get('file')

        file_url = self._generate_image_path('product.image.ext', kws.get('product_tmpl_id'), file)

        return request.make_response(json.dumps({"code":1,"msg":"操作成功","data":{"id":"0","filepath":file_url,'file_name':file.filename},"url":"","wait":3}))

    @http.route('/images/add_info', auth='public', type='http', csrf=False)
    def images_add_info(self, **kws):
        image_row = request.env['product.image.ext'].create({'product_tmpl_id': kws.get('product_tmpl_id'),
                                             'image_path': kws.get('filepath'),
                                             'file_name': kws.get('file_name'),
                                             'file_md5': kws.get('md5'),
                                             'file_size': kws.get('size'),
                                             'order_sort': 0,
                                             'is_primary': False})
        return request.make_response(json.dumps({"code":1,"msg":"操作成功"}))

    @http.route('/images/get', auth='public', csrf=False)
    def images_get(self, **kws):
        product_tmpl_id = kws.get('product_tmpl_id')
        return request.make_response(json.dumps(
            [{
                'id': row.id,
                'type': 'ss',
                'index': row.order_sort,
                'value': row.image_path,
                'file_name': row.file_name,
                'file_md5': row.file_md5,
                'file_size': row.file_size,
                'component': 'image-input',
            } for row in request.env['product.image.ext'].search([('product_tmpl_id', '=', int(product_tmpl_id))])]
        ))

    @http.route('/editor_image', auth='public')
    def editor_image(self, filename, **kwargs):
        if filename and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            main_direction = tools.config.filestore(request.env.cr.dbname)
            if not os.path.isfile(filename):
                filename = os.path.join(main_direction, filename)
            if not os.path.isfile(filename):
                return ''
            with open(filename, 'rb') as img:
                response = request.make_response(img.read())
                suffix = filename[filename.rfind('.') + 1:]
                response.headers['Content-Type'] = 'image/' + suffix
                response.headers['Content-Disposition'] = 'attachment;filename=%s' % filename
                return response
        return ''

    @http.route('/image/delete', auth='public',csrf=False)
    def images_delete(self, **kws):
        product_tmpl_id = int(kws.get('product_tmpl_id'))
        file_md5 = kws.get('file_md5')
        product_image = request.env['product.image.ext'].search([('product_tmpl_id','=',product_tmpl_id),('file_md5','=',file_md5)],limit = 1)
        if product_image:
            image_path = product_image.image_path
            if image_path:
                image_path = image_path.split('filename=')[1]

                if (os.path.exists(image_path)):
                    os.remove(image_path)
            product_image.unlink()


        #request.env.cr.execute("""DELETE FROM product_image_ext WHERE id=%s""" % request.jsonrequest.get('id'))
        return request.make_response(json.dumps({"code":1,"msg":"操作成功"}))

    @http.route('/image/sort', auth='public', csrf=False)
    def images_sort(self, **kws):
        product_tmpl_id = int(kws.get('product_tmpl_id'))
        md5_data = kws.get('md5_data')
        md5_data = json.loads(md5_data)
        num = 0
        for md5 in md5_data:
            product_image = request.env['product.image.ext'].search(
                [('product_tmpl_id', '=', product_tmpl_id), ('file_md5', '=', md5)], limit=1)
            if product_image:
                product_image.write({'order_sort':num,'is_primary':num == 0 or False})
            num+=1

        return request.make_response(json.dumps({"code": 1, "msg": "操作成功"}))

# -*- coding: utf-8 -*-
from odoo import http
from odoo import http, fields
from odoo.addons.website_blog.controllers import main
from odoo.http import request
import werkzeug
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
import json

class WebsiteBlog(main.WebsiteBlog):

    @http.route([
        '''/blog/<model("blog.blog", "[('website_id', 'in', (False, current_website_id))]"):blog>''',
        '''/blog/<model("blog.blog"):blog>/page/<int:page>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/page/<int:page>''',
    ], type='http', auth="public", website=True)
    def blog(self, blog=None, tag=None, page=1, **opt):
        """ Prepare all values to display the blog.

        :return dict values: values for the templates, containing

         - 'blog': current blog
         - 'blogs': all blogs for navigation
         - 'pager': pager of posts
         - 'active_tag_ids' :  list of active tag ids,
         - 'tags_list' : function to built the comma-separated tag list ids (for the url),
         - 'tags': all tags, for navigation
         - 'state_info': state of published/unpublished filter
         - 'nav_list': a dict [year][month] for archives navigation
         - 'date': date_begin optional parameter, used in archives navigation
         - 'blog_url': help object to create URLs
        """
        if not blog.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')
        published_count, unpublished_count = 0, 0

        domain = request.website.website_domain()

        BlogPost = request.env['blog.post']

        Blog = request.env['blog.blog']
        blogs = Blog.search(domain, order="create_date asc")

        # retrocompatibility to accept tag as slug
        active_tag_ids = tag and [int(unslug(t)[1]) for t in tag.split(',')] or []
        if active_tag_ids:
            domain += [('tag_ids', 'in', active_tag_ids)]
        if blog:
            domain += [('blog_id', '=', blog.id)]
        if date_begin and date_end:
            domain += [("post_date", ">=", date_begin), ("post_date", "<=", date_end)]

        if request.env.user.has_group('website.group_website_designer'):
            count_domain = domain + [("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())]
            published_count = BlogPost.search_count(count_domain)
            unpublished_count = BlogPost.search_count(domain) - published_count

            if state == "published":
                domain += [("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())]
            elif state == "unpublished":
                domain += ['|', ("website_published", "=", False), ("post_date", ">", fields.Datetime.now())]
        else:
            domain += [("post_date", "<=", fields.Datetime.now())]

        blog_url = QueryURL('', ['blog', 'tag'], blog=blog, tag=tag, date_begin=date_begin, date_end=date_end)

        blog_posts = BlogPost.search(domain, order="good_count desc,visits desc")
        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=len(blog_posts),
            page=page,
            step=self._blog_post_per_page,
            url_args=opt,
        )
        pager_begin = (page - 1) * self._blog_post_per_page
        pager_end = page * self._blog_post_per_page
        blog_posts = blog_posts[pager_begin:pager_end]

        all_tags = blog.all_tags()[blog.id]

        # function to create the string list of tag ids, and toggle a given one.
        # used in the 'Tags Cloud' template.
        def tags_list(tag_ids, current_tag):
            tag_ids = list(tag_ids)  # required to avoid using the same list
            if current_tag in tag_ids:
                tag_ids.remove(current_tag)
            else:
                tag_ids.append(current_tag)
            tag_ids = request.env['blog.tag'].browse(tag_ids).exists()
            return ','.join(slug(tag) for tag in tag_ids)

        tag_category = sorted(all_tags.mapped('category_id'), key=lambda category: category.name.upper())
        other_tags = sorted(all_tags.filtered(lambda x: not x.category_id), key=lambda tag: tag.name.upper())

        values = {
            'blog': blog,
            'blogs': blogs,
            'main_object': blog,
            'other_tags': other_tags,
            'state_info': {"state": state, "published": published_count, "unpublished": unpublished_count},
            'active_tag_ids': active_tag_ids,
            'tags_list': tags_list,
            'blog_posts': blog_posts,
            'blog_posts_cover_properties': [json.loads(b.cover_properties) for b in blog_posts],
            'pager': pager,
            'nav_list': self.nav_list(blog),
            'blog_url': blog_url,
            'date': date_begin,
            'tag_category': tag_category,
        }
        response = request.render("website_blog.blog_post_short", values)
        return response


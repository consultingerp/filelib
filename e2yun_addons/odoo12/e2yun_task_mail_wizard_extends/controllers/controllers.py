# -*- coding: utf-8 -*-
import json
import logging
import werkzeug
from datetime import datetime, timedelta
from math import ceil

from odoo import fields, http, SUPERUSER_ID
from odoo.http import request
from odoo.tools import ustr

_logger = logging.getLogger(__name__)

class Survey(http.Controller):

    def _check_bad_cases(self, survey, token=None):
        # In case of bad survey, redirect to surveys list
        if not survey.sudo().exists():
            return werkzeug.utils.redirect("/survey/")

        # In case of auth required, block public user
        if survey.auth_required and request.env.user._is_public():
            return request.render("survey.auth_required", {'survey': survey, 'token': token})

        # In case of non open surveys
        if survey.stage_id.closed:
            return request.render("survey.notopen")

        # If there is no pages
        if not survey.page_ids:
            return request.render("survey.nopages", {'survey': survey})

        # Everything seems to be ok
        return None

    def _check_deadline(self, user_input):
        '''Prevent opening of the survey if the deadline has turned out

        ! This will NOT disallow access to users who have already partially filled the survey !'''
        deadline = user_input.deadline
        if deadline:
            dt_deadline = fields.Datetime.from_string(deadline)
            day = timedelta(days=1)
            dt_deadline += day
            dt_now = datetime.now()
            if dt_now > dt_deadline:  # survey is not open anymore
                return request.render("survey.notopen")
        return None

        # Survey start
        @http.route(['/survey/start/<model("survey.survey"):survey>',
                     '/survey/start/<model("survey.survey"):survey>/<string:token>'],
                    type='http', auth='public', website=True)
        def start_survey(self, survey, token=None, **post):
            UserInput = request.env['survey.user_input']

            # Test mode
            if token and token == "phantom":
                _logger.info("[survey] Phantom mode")
                user_input = UserInput.create({'survey_id': survey.id, 'test_entry': True})
                data = {'survey': survey, 'page': None, 'token': user_input.token}
                return request.render('survey.survey_init', data)
            # END Test mode

            # Controls if the survey can be displayed
            errpage = self._check_bad_cases(survey, token=token)
            if errpage:
                return errpage

            # Manual surveying
            if not token:
                vals = {'survey_id': survey.id}
                if not request.env.user._is_public():
                    vals['partner_id'] = request.env.user.partner_id.id
                user_input = UserInput.create(vals)
            else:
                user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
                if not user_input:
                    return request.render("survey.403", {'survey': survey})

            # Do not open expired survey
            errpage = self._check_deadline(user_input)
            if errpage:
                return errpage

            # Select the right page
            if user_input.state == 'new':  # Intro page
                data = {'survey': survey, 'page': None, 'token': user_input.token}
                return request.render('survey.survey_init', data)
            else:
                return request.redirect('/survey/fill/%s/%s' % (survey.id, user_input.token))# Survey start

    @http.route(['/survey/start/<model("survey.survey"):survey>',
                 '/survey/start/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='public', website=True)
    def start_survey(self, survey, token=None, **post):
        UserInput = request.env['survey.user_input']

        # Test mode
        if token and token == "phantom":
            _logger.info("[survey] Phantom mode")
            user_input = UserInput.create({'survey_id': survey.id, 'test_entry': True})
            data = {'survey': survey, 'page': None, 'token': user_input.token}
            return request.render('survey.survey_init', data)
        # END Test mode

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey, token=token)
        if errpage:
            return errpage

        # Manual surveying
        if not token:
            vals = {'survey_id': survey.id}
            if not request.env.user._is_public():
                vals['partner_id'] = request.env.user.partner_id.id
            user_input = UserInput.create(vals)
        else:
            user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
            if not user_input:
                return request.render("survey.403", {'survey': survey})

        # Do not open expired survey
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = {'survey': survey, 'page': None, 'token': user_input.token}
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s' % (survey.id, user_input.token))
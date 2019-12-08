from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
class Team(models.Model):

    _inherit = 'crm.team'
    #TODO JEM : refactor this stuff with xml action, proper customization,
    @api.model
    def action_your_pipeline(self):
        action = self.env.ref('crm.crm_lead_opportunities_tree_view').read()[0]
        user_team_id = self.env.user.sale_team_id.id
        if not user_team_id:
            user_team_id = self.search([], limit=1).id
            action['help'] = _("""<p class='o_view_nocontent_smiling_face'>Add new opportunities</p><p>
        Looks like you are not a member of a Sales Team. You should add yourself
        as a member of one of the Sales Team.
        </p>""")
            if user_team_id:
                action['help'] += "<p>As you don't belong to any Sales Team, System opens the first one by default.</p>"

        action_context = safe_eval(action['context'], {'uid': self.env.uid})
        if user_team_id:
            action_context['default_team_id'] = user_team_id

        action['context'] = action_context
        return action
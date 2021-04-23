from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    ### TODO: Para crear este campo se debe agregar al res.users del odoo/community y luego sacarlo y dejar que se sincronice en este.
    # email_confirm_token = fields.Char(
    #     string = "Email confirmation token"
    # )

    @api.model
    def check_api_dni_email(self, dni, email):
        dni_search = self.search([("vat", "=", dni)])
        email_search = self.search([("email", "=", email)])
        if len(dni_search) > 0:
            return {
                "dni": {
                    "dni": dni_search.vat,
                    "email": dni_search.email
                }
            }
        elif len(email_search) > 0:
            return {
                "email": email_search.email
            }
        else:
            return False

    @api.model
    def validate_signup_user_token(self, token):
        user = self.search([('email_confirm_token', '=', token)])
        if len(user) > 0:
            user.write({"email_confirm_token": None})
            user.partner_id.write({"status": "active"})
            return True
        else:
            return False

    def send_validation_email(self):
        self.env.ref('labarra_partner.user_confirmation_email').send_mail(self.id, force_send=True)
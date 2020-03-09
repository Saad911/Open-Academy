from odoo import fields, models
from pprint import pprint

class Partner(models.Model):
    _inherit = 'res.partner'
    # Add a new column to the res.partner model, by default partners are not
    # instructors
    instructor = fields.Boolean("Instructor", default=False)
    session_ids = fields.Many2many('openacademy.session',string="Attended Sessions", readonly=True)
    invoice_count = fields.Integer(string="count invoice" ,compute="_compute_invoice_count")
    button_clicked = fields.Boolean(string='Button clicked')
    date = fields.Datetime(required = True, default = fields.Date.context_today)
    instructor_price = fields.Float(type = 'Work for')

    def _compute_invoice_count(self):
        self.invoice_count = self.env['account.move'].search_count([('partner_id', '=', self.id)])

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:

            action['domain'] = [('partner_id', '=', self.id)]
            #pprint(1)
            #pprint(action)
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
            #pprint(2)
            #pprint(action)
        else:
            action = {'type': 'ir.actions.act_window_close'}
            #pprint(3)
            #pprint(action)

        context = {
            'default_type': 'out_invoice',
        }
        action['context'] = context
        return action

    def facturer_client(self):
            self.button_clicked = True

            data = {
                 # 'session_id': self.id,
                 'partner_id': self.id,
                 'type': 'out_invoice',
             # 'partner_shipping_id' : self.instructor_id.address,
                 'invoice_date': self.date,
                 'invoice_line_ids' : [],
                  }
            for i in self.session_ids:
                line = {
                    'name': i.name,
                    'quantity': i.duration,
                        #  'price_unit': self.price_per_hour
                    #'account_id' : self.env.ref[("l10n_ma.1_pcg_611")].id
                    'price_unit' : i.price_per_hour

                     }
                #data['invoice_line_ids'].append((0,0,line))
                data['invoice_line_ids'].append((line))

            invoice2 = self.env['account.move'].create(data)


            #invoice1 = self.env['account.move.line'].create(line)





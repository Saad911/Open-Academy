

from odoo import models, fields, api, exceptions
from datetime import timedelta
from odoo import models, fields, api, exceptions, _



class openacademy(models.Model):
    _name = 'openacademy.course'
    _description = 'openacademy courses'
    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    responsible_id = fields.Many2one('res.users',ondelete='set null', string="Responsible", index=True)
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions")
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', _(u"Copy of {}%").format(self.name))])
        if not copied_count:
            new_name = _(u"Copy of {}").format(self.name)
        else:
            new_name = _(u"Copy of {} ({})").format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)
    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"),
    ]
 ###########################################################################################
class Session(models.Model):
    _name = 'openacademy.session'
    _inherit = 'mail.thread'
    _description = "OpenAcademy Sessions"
    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Integer( help="Duration in Hours ! ")
    seats = fields.Integer(string="Number of seats")
    active = fields.Boolean(default=True)
    color = fields.Integer()
    price_per_hour =  fields.Integer(help = "Price")
    total = fields.Integer( help = "total", compute = 'calc_total')
    instructor_id = fields.Many2one('res.partner', string="Instructor",
        domain=['|', ('instructor', '=', True), ('category_id.name', 'ilike', "Teacher")])
    invoice_ids = fields.One2many("account.move","session_id")
    course_id = fields.Many2one('openacademy.course',
    ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
    end_date = fields.Date(string="End Date", store=True, compute='_get_end_date', inverse='_set_end_date')
    attendees_count = fields.Integer( string="Attendees count", compute='_get_attendees_count', store=True)
    date = fields.Datetime(required = True, default = fields.Date.context_today)
    button_clicked = fields.Boolean(string='Button clicked')
    invoice_count = fields.Integer(string="count invoice" ,compute="_compute_invoice_count")
    price_session = fields.Float(string="Price for Session")
    total_price_sessions = fields.Float(string="Total_to_pay")
    instructor_price = fields.Float(string = "Price per Hour", compute = 'instruct_price')

    state = fields.Selection([
        ('draft', "DRAFT"),
        ('confirm', "CONFIRMED"),
        ('validate', "VALIDATED")], default = 'draft' , string='State')

##############################################################################################
    def _compute_invoice_count(self):
        self.invoice_count = self.env['account.move'].search_count([('session_id', '=', self.id)])
#################################
    @api.depends('instructor_id')
    def instruct_price(self):
        self.instructor_price = self.instructor_id.instructor_price
#####################################
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_type': 'out_invoice',
        }

        action['context'] = context
        return action
    ###############################################
    # def facturer_client(self):
    #         self.button_clicked = True
    #         data = {
    #              # 'session_id': self.id,
    #              'partner_id': self.id,
    #              'type': 'out_invoice',
    #          # 'partner_shipping_id' : self.instructor_id.address,
    #              'invoice_date': self.date,
    #             # 'amount_total' : self.
    #               }
    #
    #     # line = {
    #     #     'name': self.name,
    #     #     # 'quantity': self.duration,
    #     #     'price_unit': self.price_per_hour
    #     # }
    #     #invoice1 = self.env['account.move.line'].create(line)
    #         invoice2 = self.env['account.move'].create(data)
    ################################"
    def _calc_total_sessions(self):
        self.total_price_sessions = sum(self.price_session)
    ###############################################
    def draft_progressbar(self):
     self.write({
	    'state': 'draft'
    })
    def confirm_progressbar(self):
     self.write({
	    'state': 'confirm'
    })
    def validate_progressbar(self):
        self.write({
	    'state': 'validate',
    })
    def calc_total(self):
        self.total = self.duration * self.price_per_hour * len(self.attendee_ids)
        self.price_session = self.total

   #####################################################
    def _calculate_total(self):

        for r in self:
            comm_total = 10
            for line in self.total_price_sessions:
                comm_total += line.price_session
            r.update({'total_price_sessions': comm_total})

    ####################################################
    def facturer(self):
        self.button_clicked = True
        data = {
           'session_id': self.id,
            'partner_id': self.instructor_id.id,
            'type': 'in_invoice',
            'invoice_date': self.date,
            'invoice_line_ids' : [],
          }
        self.taxes = 0
        line = {
            #'product_id' : self.id,
            'name': self.name,
            'quantity': self.duration,
            'price_unit': self.instructor_id.instructor_price,
            'tax_ids' : self.taxes
        }
        data['invoice_line_ids'].append((0,0,line))
        #invoice1 = self.env['account.move.line'].create(line)
        invoice2 = self.env['account.move'].create(data)
######################################################################
    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats
    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': _("Incorrect 'seats' value"),
                    'message': _("The number of available seats may not be negative"),
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': _("Too many attendees"),
                    'message': _("Increase seats or remove excess attendees"),
                },
            }
    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue
            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = r.start_date + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            r.duration = (r.end_date - r.start_date).days + 1
    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)		
    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")
    def send_mail(self):
        template_id= self.env.ref('openacademy.email_template_instructor').id
        ctx={
            'default_model': 'openacademy.session',
            'default_res_id':   self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'email_to':self.instructor_id.email,
        }
        return{
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context':ctx,
        }


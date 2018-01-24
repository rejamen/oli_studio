# -*- coding: utf-8 -*-

from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _
from datetime import datetime, date



class cliente_cliente(models.Model):
    _name = 'cliente.cliente'

    def check_permission(self, cr, uid, ids, context=None):
      for s in self.browse(cr, uid, ids, context=context):
        res = False
        # group_obj = self.pool.get('res.groups')
        # manager_ids = group_obj.search(cr, uid, [('name','=', 'Configuration')])
        # if uid == manager_ids[0]:
        #   res = True
        s.update({'admin': res})

    def set_vip(self, cr, uid, ids, context=None):
      for c in self.browse(cr, uid, ids, context=context):
        self.write(cr, uid, c.id, {'tipo': 'vip'})
      return True

    def set_normal(self, cr, uid, ids, context=None):
      for c in self.browse(cr, uid, ids, context=context):
        self.write(cr, uid, c.id, {'tipo': 'normal'})
      return True

    @api.depends('tipo') #establece color segun el estado
    def _get_color_from_type(self, cr, uid, ids, context=None):
      for record in self.browse(cr, uid, ids, context=context):
        color = 1
        if record.tipo == 'vip':
          color = 2
        record.update({'color': color})

    def clear_historial(self, cr, uid, ids, context=None):
    	for e in self.browse(cr, uid, ids, context=context):
    		self.write(cr, uid, [e.id], {'state': 'contratado'})
    	return True

    @api.depends('historial_line.cliente_id')
    def _get_total_trabajos(self):
    	for order in self:
    		total = 0
    		abonado = 0.0
    		for line in order.historial_line:
    			total += 1
    			abonado += line.costo

    		order.update({'total_abonado': abonado})

    name = fields.Char('Nombre y Apellidos', required=True)

    tipo = fields.Selection([
    	('normal', 'Normal'),
    	('vip', 'VIP'),
    	], 'Tipo', help="Los clientes VIP disfrutan de facilidades segun las estrategias de marketing", default='normal')

    phone = fields.Char('Telefono')
    mobile = fields.Char('Movil')
    mail = fields.Char('e-mail')
    address = fields.Char('Direccion')

    color = fields.Char('Color', compute='_get_color_from_type')

    historial_line = fields.One2many('historial.cliente', 'cliente_id', 'Historial Lines')
    total_abonado = fields.Float(compute='_get_total_trabajos', string='Total abonado')

    admin = fields.Boolean(compute='check_permission', string='Admin')
    

    # @api.multi
    # def unlink(self):
    #     if not self.admin:
    #         raise UserError(_('No se puede eliminar un cliente pues se afectan los registros que dependen de él.'))
    #     ret = super(cliente_cliente, self).unlink()
    #     return ret

    def name_get(self, cr, uid, ids, context=None):
  		res = []
  		for e in self.browse(cr,uid, ids, context=context):
  			name = e.name
  			res.append((e['id'],name))
  		return res


class historial_cliente(models.Model):

	_name="historial.cliente"
	_order = "fecha desc"

	def preparar_historial(self, cr, uid, cliente, fecha, description, costo, context=None):
		historial_vals = {
			'cliente_id': cliente.id,
			'fecha': fecha, 
			'description': description,
			'costo': costo,
		}
		return historial_vals

  	cliente_id = fields.Many2one('cliente.cliente', 'Cliente', select=True, ondelete='cascade')
  	fecha = fields.Date('Fecha', default=fields.Date.context_today)
  	description = fields.Char('Descripcion')
  	costo = fields.Float('Costo', help="Costo del trabajo realizado")
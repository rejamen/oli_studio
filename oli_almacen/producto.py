# -*- coding: utf-8 -*-

from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _
from datetime import datetime, date



class producto_producto(models.Model):
    _name = 'producto.producto'

    def check_permission(self, cr, uid, ids, context=None):
      for s in self.browse(cr, uid, ids, context=context):
        res = False
        # group_obj = self.pool.get('res.groups')
        # manager_ids = group_obj.search(cr, uid, [('name','=', 'Configuration')])
        # if uid == manager_ids[0]:
        #   res = True
        s.update({'admin': res})

    def check_alert(self, cr, uid, ids, context=None):
      for s in self.browse(cr, uid, ids, context=context):
        res = False
        if s.stock <= s.total_alerta:
          res = True
        s.update({'alerta': res})

    def header_button(self, cr, uid, ids, context=None):
        return True

    def ingresar(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            t = record.stock + record.total_in
            record.update({'stock': t, 'total_in': 0, 'total_out': 0})
        return True

    def extraer(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            t = record.stock - record.total_out
            record.update({'stock': t, 'total_in': 0, 'total_out': 0})
        return True

    @api.depends('alerta') #establece color segun el estado
    def _get_color_from_alert(self, cr, uid, ids, context=None):
      for record in self.browse(cr, uid, ids, context=context):
        color = 0
        if record.alerta:
          color = 1
        record.update({'color': color})

    name = fields.Char('Nombre', required=True)

    ubicacion = fields.Selection([
    	('reserva', 'Reserva'),
    	('diario', 'Uso diario'),
    	], 'Ubicacion', help="Se considera uso diario aquellos productos que se encuentran en el estudio; y reserva los que se encuentran en el almacen.", default='reserva')

    stock = fields.Integer('Cantidad')
    unidad = fields.Many2one('unidad.medida', 'Unidad', help="Se refiere a la unidad de medida en que se controla dicho producto. Por ejemplo: unidades, litros, metros, etc.")

    total_in = fields.Integer('Inreso', help="Indica la cantidad de este producto que se suma al stock total.")
    total_out = fields.Integer('Salida', help="Indica la cantidad de este producto que se resta del stock total.")
    
    total_alerta = fields.Integer('Alerta en', help="Se genera automaticamente una alerta cuando el stock de este producto alcance la cifra indicada por este campo.")
    alerta = fields.Boolean(compute='check_alert', string='Alerta')

    description = fields.Text('Descripcion')

    admin = fields.Boolean(compute='check_permission', string='Admin')

    color = fields.Char('Color', compute='_get_color_from_alert')

    costo = fields.Float('Costo', help="Precio de compra (en MN) por unidad de este producto")


    _order = "name"
    

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


class unidad_medida(models.Model):
    _name="unidad.medida"
    
    name = fields.Char('Nombre')

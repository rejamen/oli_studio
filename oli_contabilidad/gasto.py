# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _



class gasto_gasto(models.Model):
    _name = 'gasto.gasto'

    def name_get(self, cr, uid, ids, context=None):
	  	res = []
	  	for e in self.browse(cr,uid, ids, context=context):
	  		name = e.name.name
	  		res.append((e['id'],name))
	  	return res

    def confirmar(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
        	#registrar en la nomina del empleado el valor negativo referido a este gasto...
            cobro_pendiente_obj = self.pool.get('cobros.pendientes.line')
            cobrar = 0 - record.importe #valor negativo, implica un descuento en la nomina del empleado
            name = record.name.name
            vals = cobro_pendiente_obj.preparar_cobro(self, cr, record.empleado_id.id, cobrar, name)
            cobro_pendiente_obj.create(cr, uid, vals, context=context)
            
            self.write(cr, uid, record.id, {'state': 'done'}, context=context)
        
        return True

    def reiniciar_cuenta(self, cr, uid, ids, context=None):
        '''for record in self.browse(cr, uid, ids, context=context):
            record.update({'pagado': 0})'''
        return True


    name = fields.Many2one('nombre.gasto','Nombre', required=True)
    importe = fields.Float('Importe', required=True, help="Indica el importe del gasto.")
    # pagado = fields.Float('Pagado', help="Indica el importe que se ha pagado.")
    # debe = fields.Float('Debe', help="Indica el importe que falta por pagar.", store=True, compute="_get_saldo_pendiente")
    empleado_id = fields.Many2one('empleado.empleado', 'Empleado', required=True, help="Indica el empleado que paga este gasto. ")
    description = fields.Text('Descripcion')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Confirmado'),
        ], 'Estado', default='draft')

    fecha = fields.Date('Fecha', help="Fecha en que se registra el gasto.")

    _defaults={
        'fecha': fields.Date.today,
    }

    _order='fecha desc'

class nombre_gasto(models.Model):
    _name = 'nombre.gasto'

    name = fields.Char('Nombre')
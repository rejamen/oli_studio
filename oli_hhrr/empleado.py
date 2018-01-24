# -*- coding: utf-8 -*-

from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _
from datetime import datetime, date



class empleado_empleado(models.Model):
    _name = 'empleado.empleado'

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    @api.depends('cobros_line')
    def _get_total(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            cobrar = 0
            if record.cobros_line:
                for line in record.cobros_line:
                    cobrar += line.total
            record.update({'total_cobrar': cobrar})

    def pagar(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if not record.cobros_line:
                raise osv.except_osv(_('Error!'),_("No existen pagos pendientes para este empleado."))
            else:
                total = 0
                nomina_obj = self.pool.get('nomina.nomina')
                cobro_line_obj = self.pool.get('cobros.pendientes.line')
                for line in record.cobros_line:
                    total += line.total
                    cobro_line_obj.unlink(cr, uid, line.id, context=context)

                vals = nomina_obj.preparar_nomina(self, cr, record.id, total)
                nomina_obj.create(cr, uid, vals, context=context)


        return True
        


    

    name = fields.Char('Nombre', required=True)
    salario = fields.Integer('Salario')

    image = fields.Binary("Photo")

    cobros_line = fields.One2many('cobros.pendientes.line', 'empleado_id', 'Cobros Line')
    total_cobrar = fields.Integer("Total", compute='_get_total')

    
    def name_get(self, cr, uid, ids, context=None):
  		res = []
  		for e in self.browse(cr,uid, ids, context=context):
  			name = e.name
  			res.append((e['id'],name))
  		return res

class cobros_pendientes_line(models.Model):
    _name = 'cobros.pendientes.line'

    def preparar_cobro(self, cr, uid, empleado, total, name, context=None):
        vals = {
            'empleado_id': empleado,
            'total': total,
            'name': name,
            }
        return vals

    fecha = fields.Date('Fecha')
    name = fields.Char('Concepto')
    total = fields.Float('Total')
    empleado_id = fields.Many2one('empleado.empleado', 'Empleado', select=True, ondelete='cascade')

    _defaults={
        'fecha': fields.Date.today,
    }

    _order = "fecha desc"


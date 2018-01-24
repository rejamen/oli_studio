# -*- coding: utf-8 -*-

from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _
from datetime import datetime, date



class nomina_nomina(models.Model):
    _name = 'nomina.nomina'

    def preparar_nomina(self, cr, uid, empleado, total, context=None):
        vals = {
            'empleado_id': empleado,
            'total': total,
            }
        return vals

    empleado_id = fields.Many2one('empleado.empleado', 'Empleado')
    fecha = fields.Date('Fecha')
    total = fields.Integer("Total")

    
    def name_get(self, cr, uid, ids, context=None):
  		res = []
  		for e in self.browse(cr,uid, ids, context=context):
  			name = e.empleado_id.name
  			res.append((e['id'],name))
  		return res

    _defaults={
        'fecha': fields.Date.today,
    }

    _order="fecha desc"


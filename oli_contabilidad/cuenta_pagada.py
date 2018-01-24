# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _



class cuenta_pagada(models.Model):
    _name = 'cuenta.pagada'

    def name_get(self, cr, uid, ids, context=None):
	  	res = []
	  	for e in self.browse(cr,uid, ids, context=context):
	  		name = e.name
	  		res.append((e['id'],name))
	  	return res

    def preparar_cuenta_pagada(self, cr, uid, ids, name, importe, fecha_inicio, fecha_fin, context=None):
        vals = {
            'name': name,
            'importe': importe,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        }
        return vals

    name = fields.Char('Nombre')
    importe = fields.Float('Importe', required=True, help="Indica el total a pagar de esta cuenta.")

    fecha_inicio = fields.Date('Fecha creacion', help="Fecha en que se creo la cuenta por pagar.")
    fecha_fin = fields.Date('Fecha pago', help="Fecha en que se pago la cuenta.")
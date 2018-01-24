# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _



class predefinida_predefinida(models.Model):
    _name = 'predefinida.predefinida'

    def name_get(self, cr, uid, ids, context=None):
	  	res = []
	  	for e in self.browse(cr,uid, ids, context=context):
	  		name = e.name
	  		res.append((e['id'],name))
	  	return res

    name = fields.Char('Nombre')
    costo = fields.Float('Costo')
    control_stock = fields.Boolean('Control stock', help="Si esta marcado significa que para este trabajo es obligatorio controlar el stock. Es decir, si fuera un trabajo de impresion es necesario controlar la cantidad de hojas utilizadas.")
    


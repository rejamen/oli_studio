# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _



class nota_nota(models.Model):
    _name = 'nota.nota'

    def name_get(self, cr, uid, ids, context=None):
	  	res = []
	  	for e in self.browse(cr,uid, ids, context=context):
	  		name = e.fecha
	  		res.append((e['id'],name))
	  	return res

    fecha = fields.Date('Fecha')
    name = fields.Char('Nombre')

    _defaults={
        'fecha': fields.Date.today,
    }

    _order="fecha desc"
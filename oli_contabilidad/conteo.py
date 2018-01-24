# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _
from dateutil.parser import parse
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from datetime import date
# import time
# from time import strftime




class conteo_conteo(models.Model):
    _name = 'conteo.conteo'

    # def name_get(self, cr, uid, ids, context=None):
	  	# res = []
	  	# for e in self.browse(cr,uid, ids, context=context):
	  	# 	name = e.name
	  	# 	res.append((e['id'],name))
	  	# return res

    
    @api.depends('cinco_cents_cuc','diez_cents_cuc','veinticinco_cents_cuc','cincuenta_cents_cuc','un_cuc','tres_cuc','cinco_cuc','diez_cuc','veinte_cuc','cincuenta_cuc','cien_cuc','un_mn','tres_mn','cinco_mn','diez_mn','veinte_mn','cincuenta_mn','cien_mn','doscientos_mn','quinientos_mn','mil_mn')
    def _get_importe(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            total_mn = total_cuc = equivalente_cuc = cuc = mn = 0.00
            tasa_obj = self.pool.get('tasa.cambiaria')
            tasa_ids = tasa_obj.search(cr, uid, [])
            tasa_id = tasa_obj.browse(cr, uid, tasa_ids[0])

            total_mn = record.un_mn + 3*record.tres_mn + 5*record.cinco_mn + 10*record.diez_mn + 20*record.veinte_mn + 50*record.cincuenta_mn + 100*record.cien_mn + 200*record.doscientos_mn + 500*record.quinientos_mn + 1000*record.mil_mn
            total_cuc = 0.05*record.cinco_cents_cuc + 0.1*record.diez_cents_cuc + 0.25*record.veinticinco_cents_cuc + 0.5*record.cincuenta_cents_cuc + record.un_cuc + 3*record.tres_cuc + 5*record.cinco_cuc + 10*record.diez_cuc + 20*record.veinte_cuc + 50*record.cincuenta_cuc 
            
            cuc = total_mn/tasa_id.cup
            cuc += total_cuc

            mn = total_cuc * tasa_id.cup
            mn += total_mn

            record.update({'total_mn': total_mn,'total_cuc': total_cuc, 'equivalente_mn': mn, 'equivalente_cuc': cuc})

    # @api.depends('fecha','fecha_prueba')
    # def _get_week(self, cr, uid, ids, context=None):
    #     for record in self.browse(cr, uid, ids, context=context):
    #         f = 0
    #         DATETIME_FORMAT = "%U"
    #         aux = datetime.strptime(record.fecha,DATETIME_FORMAT)
    #         f = aux.day

            
    #         record.update({'week': f})


    cinco_cents_cuc = fields.Integer('0.05')
    diez_cents_cuc = fields.Integer('0.10')
    veinticinco_cents_cuc = fields.Integer('0.25')
    cincuenta_cents_cuc = fields.Integer('0.50')
    un_cuc = fields.Integer('1.0')
    tres_cuc = fields.Integer('3.0')
    cinco_cuc = fields.Integer('5.0')
    diez_cuc = fields.Integer('10.0')
    veinte_cuc = fields.Integer('20.0')
    cincuenta_cuc = fields.Integer('50.0')
    cien_cuc = fields.Integer('100.0')

    un_mn = fields.Integer('1.0')
    tres_mn = fields.Integer('3.0')
    cinco_mn = fields.Integer('5.0')
    diez_mn = fields.Integer('10.0')
    veinte_mn = fields.Integer('20.0')
    cincuenta_mn = fields.Integer('50.0')
    cien_mn = fields.Integer('100.0')
    doscientos_mn = fields.Integer('200.0')
    quinientos_mn = fields.Integer('500.0')
    mil_mn = fields.Integer('1000.0')

    fecha = fields.Date('Fecha')
    # fecha_prueba = fields.Date('Fecha Prueba')

    total_mn = fields.Float('Total MN', compute="_get_importe")
    total_cuc = fields.Float('Total CUC', compute="_get_importe")

    equivalente_mn = fields.Float('Equivalente MN', compute="_get_importe")
    equivalente_cuc = fields.Float('Equivalente CUC', compute="_get_importe")

    # week = fields.Integer('semana', compute="_get_week")

    _defaults={
        'fecha': fields.Date.today,
    }



















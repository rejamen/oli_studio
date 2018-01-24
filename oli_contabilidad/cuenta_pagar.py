# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _



class cuenta_pagar(models.Model):
    _name = 'cuenta.pagar'

    def name_get(self, cr, uid, ids, context=None):
	  	res = []
	  	for e in self.browse(cr,uid, ids, context=context):
	  		name = e.name
	  		res.append((e['id'],name))
	  	return res

    def _read_group_stage_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        access_rights_uid = access_rights_uid or uid
        stage_obj = self.pool.get('plazo.pago')
        order = stage_obj._order
        if read_group_order == 'stage_id desc':
            order = "%s desc" % order
        search_domain = []
        stage_ids = stage_obj._search(cr, uid, search_domain, order=order, access_rights_uid=access_rights_uid, context=context)
        result = stage_obj.name_get(cr, access_rights_uid, stage_ids, context=context)
        result.sort(lambda x, y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))

        fold = {}
        for stage in stage_obj.browse(cr, access_rights_uid, stage_ids, context=context):
            fold[stage.id] = False
        return result, fold

    @api.model
    def _get_default_stage(self):
        stage_id = self.env['plazo.pago'].search([], limit=1)
        return stage_id

    @api.depends('state') #establece stage_id segun el estado
    def _get_stage_from_state(self, cr, uid, ids, context=None):
    	for record in self.browse(cr, uid, ids, context=context):
    		stage_ids = self.pool.get('plazo.pago').search(cr, uid, [])
    		if record.state == 'corto_plazo':
    			record.update({'stage_id': stage_ids[0]})
    		elif record.state == 'mediano_plazo':
    			record.update({'stage_id': stage_ids[1]})
    		elif record.state == 'largo_plazo':
    			record.update({'stage_id': stage_ids[2]})

    @api.depends('stage_id') #establece color segun el estado
    def _get_color_from_stage(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            etapa_obj = self.pool.get('plazo.pago')
            etapa_id = etapa_obj.browse(cr, uid, record.stage_id.id)
            record.update({'color': etapa_id.color, 'prioridad': etapa_id.color})

    @api.depends('importe','pagado')
    def _get_saldo_pendiente(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            debe = record.importe - record.pagado
            record.update({'debe': debe})

    def header_button(self, cr, uid, ids, context=None):
        return True

    def cuenta_pagada(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            #crear la cuenta pagada
            cuenta_pagada_obj = self.pool.get('cuenta.pagada')
            name = record.name
            importe = record.pagado
            fecha_inicio = record.fecha_creacion 
            fecha_fin = fields.date.today()
            cid = cuenta_pagada_obj.preparar_cuenta_pagada(self, cr, uid, name, importe, fecha_inicio, fecha_fin, context=context)
            cuenta_pagada_obj.create(cr, uid, cid, context=context)

            self.unlink(cr, uid, record.id, context=context)
        return True

    def reiniciar_cuenta(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record.update({'pagado': 0})
        return True


    name = fields.Char('Nombre')
    importe = fields.Float('Importe', required=True, help="Indica el total a pagar de esta cuenta.")
    pagado = fields.Float('Pagado', help="Indica el importe que se ha pagado.")
    debe = fields.Float('Debe', help="Indica el importe que falta por pagar.", store=True, compute="_get_saldo_pendiente")

    stage_id = fields.Many2one('plazo.pago', 'Etapa', store=True, select=True, default=_get_default_stage, compute='_get_stage_from_state')
    color = fields.Char('Color', compute='_get_color_from_stage')
    prioridad = fields.Integer('Prioridad', compute='_get_stage_from_state')

    state = fields.Selection([
        ('corto_plazo', 'Corto Plazo'),
        ('mediano_plazo', 'Mediano Plazo'),
        ('largo_plazo', 'Largo Plazo'),
        ], 'Plazo', help="Plazo estimado para pagar esta cuenta.", default='corto_plazo')

    fecha_creacion = fields.Date('Fecha', help="Fecha en que se crea la cuenta por pagar.")

    _group_by_full = {
        'stage_id': _read_group_stage_ids
    }

    _defaults={
        'fecha_creacion': fields.Date.today,
    }

    _order='stage_id asc'

class plazo_pago(models.Model):
    _name = 'plazo.pago'
    _description = 'Plazos para pagar esta cuenta'

    name = fields.Char('Nombre del plazo', required=True)
    sequence = fields.Integer('Sequence')
    color = fields.Char('Color')

    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Error!'),_("No se puede eliminar."))
    
    _order = 'sequence'
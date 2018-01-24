# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _



class encargo_encargo(models.Model):
    _name = 'encargo.encargo'

    def name_get(self, cr, uid, ids, context=None):
	  	res = []
	  	for e in self.browse(cr,uid, ids, context=context):
	  		name = e.cliente_id.name
	  		res.append((e['id'],name))
	  	return res

    def print_contrato(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        return self.pool['report'].get_action(cr, uid, ids, 'oli_recepcion.contrato_encargo', context=context)    

    def pagar_encargo(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            #crear un trabajo
            trabajo_obj = self.pool.get('trabajo.trabajo')
            predef_ob = self.pool.get('predefinida.predefinida')
            predef_id = predef_ob.search(cr, uid, [('name','=','Pago de encargo')])
            total = record.importe_mn
            cliente_id = record.cliente_id.id
            vals = {
                'costo': total,
                'cliente': cliente_id,
                'name': predef_id[0],
                }
            nid = trabajo_obj.create(cr, uid, vals)
            self.write(cr,uid, record.id, {'state': 'done'})


    def confirmar(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if not record.pedido_line:
                raise osv.except_osv(_('Error!'),_("No se puede archivar este encargo sin especificar al menos un elemento en la Línea de pedido."))
            if record.forma_pago == 'Varios Pagos' and not record.pagos_line:
                raise osv.except_osv(_('Error!'),_("Se ha seleccionado como forma de pago Varios pagos; debe especificar al menos una fecha en la sección Pagos pendientes y realizados."))
            if record.flag:
                raise osv.except_osv(_('Error!'),_("No se puede archivar este encargo pues no se corresponde el total especificado en la línea de Pagos pendientes y realizados con el importe total del pedido."))
            if record.forma_pago == 'Varios Pagos' and record.importe_pendiente != 0:
                raise osv.except_osv(_('Error!'),_("No se puede archivar este encargo mientras tenga pagos pendientes."))
            
            self.write(cr,uid, record.id, {'state': 'archivado'})

        return True

    @api.depends('pedido_line')
    def _get_importe(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            total_mn = equivalente_cuc = 0
            tasa_obj = self.pool.get('tasa.cambiaria')
            tasa_ids = tasa_obj.search(cr, uid, [])
            tasa_id = tasa_obj.browse(cr, uid, tasa_ids[0])
            for line in record.pedido_line:
                total_mn += line.unidades * line.precio_unidad
            cuc = total_mn/tasa_id.cup
            record.update({'importe_mn': total_mn, 'importe_cuc': cuc})

    @api.depends('pagos_line')
    def _get_importe_pendiente(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            a_pagar = record.importe_mn
            pagado = debe = 0
            if record.forma_pago == 'Varios Pagos':
                for line in record.pagos_line:
                    if line.state == 'draft':
                        debe += line.importe
                    else:
                        pagado += line.importe

            record.update({'importe_pagado': pagado, 'importe_pendiente': debe})

    @api.depends('pedido_line')
    def _get_flag(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            flag = False
            if record.pagos_line and record.forma_pago == 'Varios Pagos':
                total = 0
                for line in record.pagos_line:
                    total += line.importe
                if total != record.importe_mn:
                    flag = True


            record.update({'flag': flag})

    cliente_id = fields.Many2one('cliente.cliente', 'Cliente')
    fecha = fields.Date('Fecha encargo')
    fecha_entrega = fields.Date('Fecha entrega')

    description = fields.Text('Descripcion')

    importe_mn = fields.Float('Importe (MN)', compute="_get_importe")
    importe_cuc = fields.Float('Equivalente (CUC)', compute="_get_importe")

    importe_pagado = fields.Float('Importe pagado (MN)', compute="_get_importe_pendiente")
    importe_pendiente = fields.Float('Importe pendiente (MN)', compute="_get_importe_pendiente")

    flag = fields.Boolean('Error',compute="_get_flag")
    company_id = fields.Many2one('res.company', string='Company')




    pedido_line = fields.One2many('pedido.encargo.line', 'encargo_id', 'Encargo Line')
    pagos_line = fields.One2many('pagos.encargo.line', 'encargo_id', 'Pagos Line')

    forma_pago = fields.Selection([
        ('Pago Unico', 'Pago Unico'),
        ('Varios Pagos', 'Varios Pagos'),
        ], 'Forma de pago', default='Pago Unico')

    state = fields.Selection([
        ('draft', 'Pagos pendientes'),
        ('done', 'Pagado'),
        ('archivado', 'Archivado'),
        ], 'Estado', default='draft')

    _defaults={
        'fecha': fields.Date.today,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'encargo.encargo', context=c),

    }

    _order="fecha desc"

class pedido_encargo_line(models.Model):
    _name="pedido.encargo.line"

    @api.depends('unidades','precio_unidad')
    def _get_importe(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            importe = 0
            importe = record.unidades * record.precio_unidad
            record.update({'importe': importe})

    encargo_id = fields.Many2one('encargo.encargo', 'encargo',  select=True, ondelete='cascade')
    trabajo = fields.Char('Trabajo')
    unidades = fields.Integer('Unidades')
    precio_unidad = fields.Float('Precio udad (MN).')
    importe = fields.Float('Importe (MN)', compute="_get_importe")

    _order="trabajo"

class pagos_encargo_line(models.Model):
    _name='pagos.encargo.line'

    def confirmar(self, cr, uid, ids, context=None):
    	for record in self.browse(cr, uid, ids, context=context):
    		self.write(cr,uid, record.id, {'state': 'done'})
    	return True

    encargo_id = fields.Many2one('encargo.encargo', 'encargo',  select=True, ondelete='cascade')
    fecha = fields.Date('Fecha')
    importe = fields.Float('Importe (MN)')

    state = fields.Selection([
        ('draft', 'Pendiente'),
        ('done', 'Pagado'),
        ], 'Estado', default='draft')

    _defaults={
        'fecha': fields.Date.today,
    }

    _order="fecha asc"
